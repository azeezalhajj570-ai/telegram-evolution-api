import uuid
from typing import Any, Dict, List, Optional

from app.services.telegram_manager import client_manager


async def list_chats(instance_id: uuid.UUID) -> List[Dict[str, Any]]:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    dialogs = await client.get_dialogs()
    return [
        {
            "chat_id": d.entity.id,
            "title": d.title or "Unknown",
            "type": d.name or d.entity.__class__.__name__.lower(),
            "unread_count": d.unread_count,
            "last_message": {
                "text": d.message.text[:200] if d.message and d.message.text else "",
                "sender_id": d.message.sender_id if d.message else None,
                "date": d.message.date.isoformat() if d.message and d.message.date else None,
            } if d.message else None,
        }
        for d in dialogs
    ]


async def get_messages(instance_id: uuid.UUID, chat_id: int, limit: int = 50, offset_id: Optional[int] = None) -> List[Dict[str, Any]]:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        entity = await client.get_entity(chat_id)
    except (ValueError, TypeError):
        await client.get_dialogs()
        entity = await client.get_entity(chat_id)
    messages = await client.get_messages(entity, limit=limit, offset_id=offset_id or 0)
    return [
        {
            "message_id": m.id,
            "chat_id": chat_id,
            "sender_id": m.sender_id,
            "text": m.text or "",
            "date": m.date.isoformat() if m.date else None,
            "is_outgoing": m.out,
        }
        for m in messages if m
    ]
