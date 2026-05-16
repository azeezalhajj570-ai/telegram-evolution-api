from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.messages import ChatListResponse, ChatInfo, MessagesResponse, MessageInfo
from app.security.api_keys import require_api_key
from app.services.chats import get_messages as svc_get_messages
from app.services.chats import list_chats as svc_list_chats

router = APIRouter(prefix="/instances/{instance_id}", tags=["Chats"], dependencies=[Depends(require_api_key)])


@router.get("/chats", response_model=ChatListResponse)
async def list_chats(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")

    try:
        chats = await svc_list_chats(uid)
        return ChatListResponse(chats=[ChatInfo(**c) for c in chats])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/chats/{chat_id}/messages", response_model=MessagesResponse)
async def get_chat_messages(
    instance_id: str,
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")

    try:
        msgs = await svc_get_messages(uid, chat_id, limit, offset_id)
        return MessagesResponse(messages=[MessageInfo(**m) for m in msgs])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
