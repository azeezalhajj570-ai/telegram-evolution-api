import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApiKey, Instance, Webhook, WebhookDelivery


class InstanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str) -> Instance:
        inst = Instance(id=uuid.uuid4(), name=name)
        self.db.add(inst)
        await self.db.flush()
        return inst

    async def get(self, instance_id: uuid.UUID) -> Optional[Instance]:
        return await self.db.get(Instance, instance_id)

    async def get_all(self) -> List[Instance]:
        result = await self.db.execute(select(Instance).order_by(Instance.created_at))
        return list(result.scalars().all())

    async def update(self, instance_id: uuid.UUID, **kwargs) -> Optional[Instance]:
        kwargs["updated_at"] = datetime.utcnow()
        await self.db.execute(update(Instance).where(Instance.id == instance_id).values(**kwargs))
        return await self.get(instance_id)

    async def delete(self, instance_id: uuid.UUID) -> bool:
        inst = await self.get(instance_id)
        if inst:
            await self.db.delete(inst)
            return True
        return False

    async def get_by_status(self, status: str) -> List[Instance]:
        result = await self.db.execute(select(Instance).where(Instance.status == status))
        return list(result.scalars().all())

    async def get_by_phone(self, phone: str) -> Optional[Instance]:
        result = await self.db.execute(select(Instance).where(Instance.phone_number == phone))
        return result.scalar_one_or_none()

    async def get_by_mcp_api_key_hash(self, key_hash: str) -> Optional[Instance]:
        result = await self.db.execute(
            select(Instance).where(Instance.mcp_api_key_hash == key_hash)
        )
        return result.scalar_one_or_none()


class WebhookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, instance_id: uuid.UUID, url: str, secret: str) -> Webhook:
        wh = Webhook(id=uuid.uuid4(), instance_id=instance_id, url=url, secret=secret)
        self.db.add(wh)
        await self.db.flush()
        return wh

    async def get_by_instance(self, instance_id: uuid.UUID) -> Optional[Webhook]:
        result = await self.db.execute(select(Webhook).where(Webhook.instance_id == instance_id))
        return result.scalar_one_or_none()

    async def delete(self, instance_id: uuid.UUID) -> bool:
        wh = await self.get_by_instance(instance_id)
        if wh:
            await self.db.delete(wh)
            return True
        return False


class WebhookDeliveryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, webhook_id: uuid.UUID, event_type: str, payload: dict) -> WebhookDelivery:
        delivery = WebhookDelivery(
            id=uuid.uuid4(), webhook_id=webhook_id, event_type=event_type, payload=payload
        )
        self.db.add(delivery)
        await self.db.flush()
        return delivery

    async def get_pending(self) -> List[WebhookDelivery]:
        result = await self.db.execute(
            select(WebhookDelivery)
            .where(WebhookDelivery.status == "pending")
            .order_by(WebhookDelivery.created_at)
        )
        return list(result.scalars().all())

    async def mark_delivered(self, delivery_id: uuid.UUID, status_code: int):
        await self.db.execute(
            update(WebhookDelivery)
            .where(WebhookDelivery.id == delivery_id)
            .values(status="delivered", last_status_code=status_code, last_attempt_at=datetime.utcnow())
        )

    async def mark_failed(self, delivery_id: uuid.UUID, status_code: Optional[int] = None):
        await self.db.execute(
            update(WebhookDelivery)
            .where(WebhookDelivery.id == delivery_id)
            .values(status="failed", last_status_code=status_code, last_attempt_at=datetime.utcnow())
        )
