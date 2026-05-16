import logging
import uuid
from typing import Optional

from telethon.errors import FloodWaitError, RPCError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

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


async def send_media(instance_id: uuid.UUID, chat_id: int, file_path: str, media_type: str, caption: Optional[str] = None) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        result = await client.send_file(chat_id, file_path, caption=caption)
        return {"message_id": result.id, "chat_id": chat_id, "type": media_type, "status": "delivered"}
    except FloodWaitError as e:
        raise FloodWaitError(e.seconds)
    except RPCError as e:
        logger.warning("RPC error sending media for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to send media: {e}")


async def reply_message(instance_id: uuid.UUID, chat_id: int, text: str, reply_to: int) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        result = await client.send_message(chat_id, text, reply_to=reply_to)
        return {"message_id": result.id, "status": "delivered"}
    except RPCError as e:
        logger.warning("RPC error replying for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to reply: {e}")


async def forward_message(instance_id: uuid.UUID, from_chat_id: int, message_id: int, to_chat_id: int) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        result = await client.forward_messages(to_chat_id, message_id, from_chat_id)
        msg = result[0] if isinstance(result, list) else result
        return {"message_id": msg.id, "status": "delivered"}
    except RPCError as e:
        logger.warning("RPC error forwarding for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to forward: {e}")


async def edit_message(instance_id: uuid.UUID, chat_id: int, message_id: int, text: str) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        result = await client.edit_message(chat_id, message_id, text)
        return {"message_id": result.id, "status": "edited"}
    except RPCError as e:
        logger.warning("RPC error editing for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to edit: {e}")


async def delete_message(instance_id: uuid.UUID, chat_id: int, message_id: int) -> None:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        await client.delete_messages(chat_id, message_id)
    except RPCError as e:
        logger.warning("RPC error deleting for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to delete: {e}")


async def send_reaction(instance_id: uuid.UUID, chat_id: int, message_id: int, emoji: Optional[str] = None) -> dict:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        reaction = emoji if emoji and emoji not in ("remove", "") else None
        await client.send_reaction(chat_id, message_id, reaction=reaction)
        return {"message_id": message_id, "reaction": emoji or "", "status": "applied"}
    except RPCError as e:
        logger.warning("RPC error reacting for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to react: {e}")


async def download_media(instance_id: uuid.UUID, chat_id: int, message_id: int) -> tuple[str, str]:
    client = client_manager.get_client(str(instance_id))
    if client is None or not client.is_connected():
        raise ValueError("Instance not connected")

    try:
        msg = await client.get_messages(chat_id, ids=message_id)
        if not msg or not msg.media:
            raise ValueError("Message has no media")

        from app.utils.file_utils import get_temp_path
        ext = ""
        if isinstance(msg.media, MessageMediaPhoto):
            ext = ".jpg"
        elif isinstance(msg.media, MessageMediaDocument):
            ext = ".bin"
        dest = get_temp_path(f"download{ext}")
        path = await client.download_media(msg, file=dest)
        mime = "application/octet-stream"
        if isinstance(msg.media, MessageMediaPhoto):
            mime = "image/jpeg"
        return path, mime
    except RPCError as e:
        logger.warning("RPC error downloading for instance %s: %s", instance_id, e)
        raise ValueError(f"Failed to download: {e}")
