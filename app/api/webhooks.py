import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories import InstanceRepository, WebhookRepository
from app.schemas.webhooks import WebhookCreateRequest, WebhookResponse, WebhookTestResponse
from app.security.api_keys import require_api_key
from app.services.webhook_dispatcher import dispatch as svc_dispatch

router = APIRouter(prefix="/instances/{instance_id}/webhook", tags=["Webhooks"], dependencies=[Depends(require_api_key)])


def _to_response(wh) -> dict:
    return {
        "id": str(wh.id),
        "url": wh.url,
        "is_active": wh.is_active,
        "max_retries": wh.max_retries,
        "secret": "****",
        "created_at": wh.created_at,
        "updated_at": wh.updated_at,
    }


@router.post("", response_model=WebhookResponse, status_code=201)
async def create_webhook(instance_id: str, body: WebhookCreateRequest, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    inst_repo = InstanceRepository(db)
    inst = await inst_repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")

    wh_repo = WebhookRepository(db)
    existing = await wh_repo.get_by_instance(uid)
    if existing:
        raise HTTPException(status_code=400, detail="Webhook already configured")

    secret = secrets.token_hex(32)
    wh = await wh_repo.create(uid, str(body.url), secret)
    return WebhookResponse(**_to_response(wh))


@router.get("", response_model=WebhookResponse)
async def get_webhook(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    wh_repo = WebhookRepository(db)
    wh = await wh_repo.get_by_instance(uid)
    if not wh:
        raise HTTPException(status_code=404, detail="No webhook configured")
    return WebhookResponse(**_to_response(wh))


@router.delete("", status_code=204)
async def delete_webhook(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    wh_repo = WebhookRepository(db)
    deleted = await wh_repo.delete(uid)
    if not deleted:
        raise HTTPException(status_code=404, detail="No webhook configured")
    return Response(status_code=204)


@router.post("/test", response_model=WebhookTestResponse)
async def test_webhook(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    wh_repo = WebhookRepository(db)
    wh = await wh_repo.get_by_instance(uid)
    if not wh:
        raise HTTPException(status_code=400, detail="No webhook configured")

    test_payload = {
        "message_id": 0,
        "chat_id": 0,
        "chat_title": "Test",
        "sender_id": 0,
        "sender_name": "Test",
        "text": "This is a test webhook event.",
        "date": "2026-01-01T00:00:00Z",
    }
    await svc_dispatch(instance_id, "test", test_payload, wh_repo)
    return WebhookTestResponse(status="delivered")
