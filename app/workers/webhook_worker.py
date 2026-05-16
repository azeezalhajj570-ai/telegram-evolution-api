import asyncio
import json
import logging
import uuid

import httpx

from app.config import settings
from app.db.database import async_session
from app.db.repositories import WebhookDeliveryRepository, WebhookRepository
from app.security.webhook_signing import sign_payload

logger = logging.getLogger(__name__)


async def process_retries():
    async with async_session() as db:
        delivery_repo = WebhookDeliveryRepository(db)
        pendings = await delivery_repo.get_pending()

        for delivery in pendings:
            if delivery.attempt_count >= (delivery.webhook.max_retries if delivery.webhook else settings.webhook_retry_max):
                await delivery_repo.mark_failed(delivery.id)
                continue

            payload = json.dumps({
                "event": delivery.event_type,
                "instance_id": str(delivery.webhook.instance_id),
                "timestamp": delivery.created_at.isoformat(),
                "payload": delivery.payload,
            }).encode()

            signature = sign_payload(payload, delivery.webhook.secret)
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(delivery.webhook.url, content=payload, headers={
                        "Content-Type": "application/json",
                        "X-Signature-256": signature,
                    })
                if resp.is_success:
                    await delivery_repo.mark_delivered(delivery.id, resp.status_code)
                    logger.info("Retry delivered for delivery %s", delivery.id)
                else:
                    logger.warning("Retry returned %s for delivery %s", resp.status_code, delivery.id)
            except httpx.RequestError as e:
                logger.warning("Retry failed for delivery %s: %s", delivery.id, e)

            await db.commit()

        await db.commit()


async def run_worker_loop(interval: int = 60):
    while True:
        try:
            await process_retries()
        except Exception as e:
            logger.error("Webhook worker error: %s", e)
        await asyncio.sleep(interval)
