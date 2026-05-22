from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import FloodWaitError

from app.config import settings
from app.core.error_codes import ErrorCodes
from app.core.response import rest_error, rest_success
from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.auth import SendCodeRequest, TwoFARequest, VerifyCodeRequest
from app.security.api_keys import require_api_key
from app.services.telegram_auth import send_code as auth_send_code
from app.services.telegram_auth import submit_2fa as auth_submit_2fa
from app.services.telegram_auth import verify_code as auth_verify_code
from app.services.telegram_manager import client_manager

router = APIRouter(prefix="/instances/{instance_id}/auth", tags=["Auth"], dependencies=[Depends(require_api_key)])


def _parse_id(instance_id: str) -> UUID:
    try:
        return UUID(instance_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=rest_error("auth", ErrorCodes.INVALID_INPUT, "Invalid instance ID"))


def _get_instance_or_404(repo, uid):
    inst = repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("auth", ErrorCodes.NOT_FOUND, "Instance not found"))
    return inst


@router.post("/send-code")
async def send_code(instance_id: str, body: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("auth.send_code", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status == "connected":
        raise HTTPException(status_code=400, detail=rest_error("auth.send_code", ErrorCodes.INVALID_INPUT, "Already connected"))
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        raise HTTPException(status_code=500, detail=rest_error("auth.send_code", ErrorCodes.INTERNAL_ERROR, "Telegram API credentials not configured"))
    try:
        await auth_send_code(uid, body.phone_number, repo)
    except FloodWaitError as e:
        raise HTTPException(status_code=429, detail=rest_error("auth.send_code", ErrorCodes.RATE_LIMIT_EXCEEDED, f"Flood wait {e.seconds}s", retryable=True))
    return rest_success({"status": "code_sent"}, "auth.send_code")


@router.post("/verify-code")
async def verify_code(instance_id: str, body: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("auth.verify_code", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status not in ("code_sent", "pending"):
        raise HTTPException(status_code=400, detail=rest_error("auth.verify_code", ErrorCodes.INVALID_INPUT, "Invalid state for code verification"))
    try:
        result = await auth_verify_code(uid, body.code, repo)
        return rest_success(result, "auth.verify_code")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=rest_error("auth.verify_code", ErrorCodes.INVALID_INPUT, str(e)))


@router.post("/2fa")
async def verify_2fa(instance_id: str, body: TwoFARequest, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("auth.2fa", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status != "awaiting_2fa":
        raise HTTPException(status_code=400, detail=rest_error("auth.2fa", ErrorCodes.INVALID_INPUT, "2FA not required"))
    try:
        result = await auth_submit_2fa(uid, body.password, repo)
        return rest_success(result, "auth.2fa")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=rest_error("auth.2fa", ErrorCodes.INVALID_INPUT, str(e)))


@router.post("/connect")
async def connect_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("auth.connect", ErrorCodes.NOT_FOUND, "Instance not found"))
    if not inst.session_encrypted:
        raise HTTPException(status_code=400, detail=rest_error("auth.connect", ErrorCodes.INVALID_INPUT, "No saved session"))
    if inst.status == "connected":
        return rest_success({"status": "connected"}, "auth.connect")
    try:
        await client_manager.start_client(instance_id, inst.session_encrypted)
        await repo.update(uid, status="connected")
        return rest_success({"status": "connected"}, "auth.connect")
    except Exception as e:
        await repo.update(uid, status="auth_required")
        raise HTTPException(status_code=400, detail=rest_error("auth.connect", ErrorCodes.TELEGRAM_API_ERROR, str(e)))


@router.post("/disconnect")
async def disconnect_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("auth.disconnect", ErrorCodes.NOT_FOUND, "Instance not found"))
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail=rest_error("auth.disconnect", ErrorCodes.INVALID_INPUT, "Not connected"))
    await client_manager.stop_client(instance_id)
    await repo.update(uid, status="disconnected")
    return rest_success({"status": "disconnected"}, "auth.disconnect")
