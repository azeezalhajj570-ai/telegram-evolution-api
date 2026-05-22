from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCodes
from app.core.response import rest_error, rest_success
from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.security.api_keys import require_api_key
from app.services.chats import get_messages as svc_get_messages
from app.services.chats import list_chats as svc_list_chats

router = APIRouter(prefix="/instances/{instance_id}", tags=["Chats"], dependencies=[Depends(require_api_key)])


@router.get("/chats")
async def list_chats(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("chats.list", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail=rest_error("chats.list", ErrorCodes.INVALID_INPUT, "Instance not connected"))
    try:
        chats = await svc_list_chats(uid)
        return rest_success({"chats": chats}, "chats.list")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=rest_error("chats.list", ErrorCodes.INVALID_INPUT, str(e)))


@router.get("/chats/{chat_id}/messages")
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
        raise HTTPException(status_code=404, detail=rest_error("chats.history", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail=rest_error("chats.history", ErrorCodes.INVALID_INPUT, "Instance not connected"))
    try:
        msgs = await svc_get_messages(uid, chat_id, limit, offset_id)
        return rest_success({"messages": msgs}, "chats.history")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=rest_error("chats.history", ErrorCodes.INVALID_INPUT, str(e)))
