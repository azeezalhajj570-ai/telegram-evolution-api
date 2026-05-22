from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import FloodWaitError

from app.core.error_codes import ErrorCodes
from app.core.response import rest_error, rest_success
from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.messages import SendMessageRequest
from app.security.api_keys import require_api_key
from app.services.messaging import send_message as svc_send_message
from app.services.rate_limits import check_rate_limit

router = APIRouter(prefix="/instances/{instance_id}", tags=["Messages"], dependencies=[Depends(require_api_key)])


@router.post("/send-message")
async def send_message(instance_id: str, body: SendMessageRequest, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("messages.send", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail=rest_error("messages.send", ErrorCodes.INVALID_INPUT, "Instance not connected"))

    allowed, retry_after = await check_rate_limit(instance_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=rest_error("messages.send", ErrorCodes.RATE_LIMIT_EXCEEDED, "Rate limit exceeded", retryable=True, details={"retry_after_seconds": retry_after}))

    try:
        result = await svc_send_message(uid, body.text, chat_id=body.chat_id, username=body.username, phone_number=body.phone_number)
        return rest_success(result, "messages.send")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=rest_error("messages.send", ErrorCodes.INVALID_INPUT, str(e)))
    except FloodWaitError as e:
        raise HTTPException(status_code=429, detail=rest_error("messages.send", ErrorCodes.RATE_LIMIT_EXCEEDED, f"Telegram rate limit. Wait {e.seconds}s", retryable=True, details={"retry_after_seconds": e.seconds}))
