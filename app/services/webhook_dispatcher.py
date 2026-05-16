import json
import logging
import uuid

import httpx
from telethon.events import NewMessage

from app.db.repositories import WebhookDeliveryRepository, WebhookRepository
from app.security.webhook_signing import sign_payload

logger = logging.getLogger(__name__)


def normalize_message(event: NewMessage.Event) -> dict:
    sender = event.sender
    chat = event.chat
    return {
        "message_id": event.message.id,
        "chat_id": event.chat_id,
        "chat_title": getattr(chat, "title", None) or getattr(sender, "first_name", ""),
        "sender_id": event.sender_id,
        "sender_name": f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip(),
        "text": event.message.text or "",
        "date": event.message.date.isoformat() if event.message.date else None,
    }


async def dispatch(instance_id: str, event_type: str, event_data: dict, wh_repo: WebhookRepository):
    wh = await wh_repo.get_by_instance(uuid.UUID(instance_id))
    if not wh or not wh.is_active:
        return

    delivery_repo = WebhookDeliveryRepository(wh_repo.db)

    payload = json.dumps({
        "event": event_type,
        "instance_id": instance_id,
        "timestamp": event_data.get("date"),
        "payload": event_data,
    }).encode()

    signature = sign_payload(payload, wh.secret)

    delivery = await delivery_repo.create(wh.id, event_type, event_data)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(wh.url, content=payload, headers={
                "Content-Type": "application/json",
                "X-Signature-256": signature,
            })
        if resp.is_success:
            await delivery_repo.mark_delivered(delivery.id, resp.status_code)
            logger.info("Webhook delivered for instance %s (%s)", instance_id, resp.status_code)
        else:
            logger.warning("Webhook returned %s for instance %s", resp.status_code, instance_id)
    except httpx.RequestError as e:
        logger.error("Webhook request failed for instance %s: %s", instance_id, e)
