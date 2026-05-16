import os
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import FloodWaitError

from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.media import (
    EditMessageRequest,
    ForwardRequest,
    MediaMessageResponse,
    MessageActionResponse,
    ReactionRequest,
    ReactionResponse,
    ReplyRequest,
)
from app.schemas.messages import SendMessageRequest, SendMessageResponse
from app.security.api_keys import require_api_key
from app.services import messaging as svc
from app.services.rate_limits import check_rate_limit
from app.utils.file_utils import cleanup_temp, get_temp_path, MAX_FILE_SIZE

router = APIRouter(prefix="/instances/{instance_id}", tags=["Messages"], dependencies=[Depends(require_api_key)])

MEDIA_TYPES = {
    "send-photo": "photo",
    "send-document": "document",
    "send-video": "video",
    "send-audio": "audio",
    "send-voice": "voice",
}


def _check_instance(inst) -> UUID:
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Instance not connected")
    return inst.id


@router.post("/send-message", response_model=SendMessageResponse)
async def send_message(instance_id: str, body: SendMessageRequest, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Instance not connected")

    allowed, retry_after = await check_rate_limit(instance_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "retry_after_seconds": retry_after},
        )

    try:
        return await svc.send_message(uid, body.chat_id, body.text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FloodWaitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "retry_after_seconds": e.seconds,
                    "detail": f"Telegram rate limit applied. Wait {e.seconds} seconds."},
        )


# ── Specific routes (BEFORE wildcard {media_type}) ──


@router.post("/messages/reply", response_model=MessageActionResponse)
async def reply(instance_id: str, body: ReplyRequest, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)
    try:
        return await svc.reply_message(uid, body.chat_id, body.text, body.reply_to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/messages/forward", response_model=MessageActionResponse)
async def forward(instance_id: str, body: ForwardRequest, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)
    try:
        return await svc.forward_message(uid, body.from_chat_id, body.message_id, body.to_chat_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/messages/{message_id}", response_model=MessageActionResponse)
async def edit(instance_id: str, message_id: int, body: EditMessageRequest, chat_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)
    try:
        return await svc.edit_message(uid, chat_id, message_id, body.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/messages/{message_id}", status_code=204)
async def delete(instance_id: str, message_id: int, chat_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)
    try:
        await svc.delete_message(uid, chat_id, message_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/messages/{message_id}/reaction", response_model=ReactionResponse)
async def react(instance_id: str, message_id: int, body: ReactionRequest, chat_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)
    try:
        return await svc.send_reaction(uid, chat_id, message_id, body.emoji)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/messages/{message_id}/media")
async def download(instance_id: str, message_id: int, chat_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)
    try:
        path, mime = await svc.download_media(uid, chat_id, message_id)
        return FileResponse(path, media_type=mime, filename=os.path.basename(path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Wildcard media type routes (after specific) ──


@router.post("/messages/{media_type}", response_model=MediaMessageResponse)
async def send_media(
    instance_id: str,
    media_type: str,
    chat_id: int = Form(...),
    file: UploadFile = File(...),
    caption: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if media_type not in MEDIA_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown media type: {media_type}")

    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    _check_instance(inst)

    size = 0
    if file.size is not None:
        size = file.size
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit")

    temp_path = get_temp_path(file.filename or "upload")
    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                detail=f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit")
        with open(temp_path, "wb") as f:
            f.write(content)

        return await svc.send_media(uid, chat_id, temp_path, MEDIA_TYPES[media_type], caption)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FloodWaitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "retry_after_seconds": e.seconds},
        )
    finally:
        cleanup_temp(temp_path)
