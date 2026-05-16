from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import FloodWaitError

from app.config import settings
from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.auth import AuthStatusResponse, SendCodeRequest, TwoFARequest, VerifyCodeRequest
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid instance ID")


@router.post("/send-code", response_model=AuthStatusResponse)
async def send_code(instance_id: str, body: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if inst.status == "connected":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already connected")

    if not settings.telegram_api_id or not settings.telegram_api_hash:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Telegram API credentials not configured")

    try:
        await auth_send_code(uid, body.phone_number, repo)
    except FloodWaitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Flood wait {e.seconds}s")
    return AuthStatusResponse(status="code_sent")


@router.post("/verify-code", response_model=AuthStatusResponse)
async def verify_code(instance_id: str, body: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if inst.status not in ("code_sent", "pending"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state for code verification")

    try:
        result = await auth_verify_code(uid, body.code, repo)
        return AuthStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/2fa", response_model=AuthStatusResponse)
async def verify_2fa(instance_id: str, body: TwoFARequest, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if inst.status != "awaiting_2fa":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA not required")

    try:
        result = await auth_submit_2fa(uid, body.password, repo)
        return AuthStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/connect", response_model=AuthStatusResponse)
async def connect_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if not inst.session_encrypted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No saved session")
    if inst.status == "connected":
        return AuthStatusResponse(status="connected")

    try:
        await client_manager.start_client(instance_id, inst.session_encrypted)
        await repo.update(uid, status="connected")
        return AuthStatusResponse(status="connected")
    except Exception as e:
        await repo.update(uid, status="auth_required")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/disconnect", response_model=AuthStatusResponse)
async def disconnect_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = _parse_id(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not connected")

    await client_manager.stop_client(instance_id)
    await repo.update(uid, status="disconnected")
    return AuthStatusResponse(status="disconnected")
