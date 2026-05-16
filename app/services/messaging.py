import logging
import uuid

from telethon.errors import FloodWaitError, RPCError

from app.services.telegram_manager import client_manager

logger = logging.getLogger(__name__)


async def send_message(instance_id: uuid.UUID, chat_id: int, text: str) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        result = await client.send_message(chat_id, text)
        return {"message_id": result.id, "chat_id": chat_id, "status": "delivered"}
    except FloodWaitError as e:
        raise FloodWaitError(e.seconds)
    except RPCError as e:
        logger.warning("RPC error sending message for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to send message: {e}")
