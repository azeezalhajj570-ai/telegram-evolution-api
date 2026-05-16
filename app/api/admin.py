from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import WebhookDelivery
from app.db.repositories import InstanceRepository, WebhookRepository
from app.security.api_keys import require_api_key
from app.services.telegram_manager import client_manager

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_api_key)])


@router.get("/instances")
async def admin_list_instances(db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    instances = await repo.get_all()
    connected_ids = client_manager.get_connected_ids()
    return {
        "instances": [
            {
                "id": str(i.id),
                "name": i.name,
                "status": i.status,
                "connected": str(i.id) in connected_ids,
            }
            for i in instances
        ]
    }


@router.get("/instances/{instance_id}/diagnostics")
async def admin_instance_diagnostics(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")

    connected = str(inst.id) in client_manager.get_connected_ids()
    return {
        "instance_id": str(inst.id),
        "name": inst.name,
        "status": inst.status,
        "client_connected": connected,
        "has_session": bool(inst.session_encrypted),
        "phone_number": inst.phone_number,
    }


@router.post("/instances/{instance_id}/restart")
async def admin_restart_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")

    if not inst.session_encrypted:
        raise HTTPException(status_code=400, detail="No saved session — re-authenticate")

    await client_manager.stop_client(instance_id)
    try:
        await client_manager.start_client(instance_id, inst.session_encrypted)
        await repo.update(uid, status="connected")
        return {"status": "restarted", "instance_id": instance_id}
    except Exception as e:
        await repo.update(uid, status="auth_required")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/webhook-deliveries")
async def admin_list_webhook_deliveries(webhook_id: str = None, db: AsyncSession = Depends(get_db)):
    from app.db.repositories import WebhookDeliveryRepository
    repo = WebhookDeliveryRepository(db)
    result = await db.execute(select(WebhookDelivery).order_by(WebhookDelivery.created_at.desc()).limit(50))
    deliveries = result.scalars().all()
    return {
        "deliveries": [
            {
                "id": str(d.id),
                "webhook_id": str(d.webhook_id),
                "event_type": d.event_type,
                "status": d.status,
                "attempt_count": d.attempt_count,
                "last_status_code": d.last_status_code,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in deliveries
        ]
    }


@router.post("/webhook-deliveries/{delivery_id}/retry")
async def admin_retry_webhook(delivery_id: str, db: AsyncSession = Depends(get_db)):
    uid = UUID(delivery_id)
    from app.db.repositories import WebhookDeliveryRepository
    repo = WebhookDeliveryRepository(db)
    delivery = await db.get(WebhookDelivery, uid)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    await repo.mark_failed(uid)
    return {"status": "retry_queued", "delivery_id": delivery_id}
