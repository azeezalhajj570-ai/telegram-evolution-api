import logging
import uuid

from app.services.telegram_manager import client_manager

logger = logging.getLogger(__name__)


async def join_channel(instance_id: uuid.UUID, username: str) -> dict:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    entity = await client.get_entity(username)
    await client.join_channel(entity)
    return {"channel_id": entity.id, "title": entity.title}


async def leave_channel(instance_id: uuid.UUID, channel_id: int) -> None:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    entity = await client.get_entity(channel_id)
    await client.delete_dialog(entity)


async def list_channels(instance_id: uuid.UUID) -> list:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    dialogs = await client.get_dialogs()
    return [
        {
            "channel_id": d.entity.id,
            "title": d.name or "",
            "username": getattr(d.entity, "username", None),
        }
        for d in dialogs if hasattr(d.entity, "title") and getattr(d.entity, "broadcast", False)
    ]


async def get_channel_messages(instance_id: uuid.UUID, channel_id: int, limit: int = 50) -> list:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    messages = await client.get_messages(channel_id, limit=limit)
    return [
        {
            "message_id": m.id,
            "text": m.text or "",
            "date": m.date.isoformat() if m.date else None,
        }
        for m in messages if m
    ]
