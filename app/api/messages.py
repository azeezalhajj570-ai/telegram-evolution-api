from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import FloodWaitError

from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.messages import SendMessageRequest, SendMessageResponse
from app.security.api_keys import require_api_key
from app.services.messaging import send_message as svc_send_message
from app.services.rate_limits import check_rate_limit

router = APIRouter(prefix="/instances/{instance_id}", tags=["Messages"], dependencies=[Depends(require_api_key)])


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
        return await svc_send_message(uid, body.chat_id, body.text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FloodWaitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "retry_after_seconds": e.seconds,
                    "detail": f"Telegram rate limit applied. Wait {e.seconds} seconds."},
        )
