import logging
import uuid
from typing import Optional

from telethon.errors import FloodWaitError, RPCError

from app.services.telegram_manager import client_manager

logger = logging.getLogger(__name__)


async def send_message(
    instance_id: uuid.UUID,
    text: str,
    chat_id: Optional[int] = None,
    username: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        if chat_id is not None:
            try:
                entity = await client.get_entity(chat_id)
            except (ValueError, TypeError):
                await client.get_dialogs()
                entity = await client.get_entity(chat_id)
            resolved_id = chat_id
        elif username is not None:
            entity = await client.get_entity(username)
            resolved_id = entity.id
        elif phone_number is not None:
            entity = await client.get_entity(phone_number)
            resolved_id = entity.id
        else:
            raise ValueError("No recipient specified")

        result = await client.send_message(entity, text)
        return {"message_id": result.id, "chat_id": resolved_id, "status": "delivered"}
    except FloodWaitError as e:
        raise FloodWaitError(e.seconds)
    except RPCError as e:
        logger.warning("RPC error sending message for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to send message: {e}")
