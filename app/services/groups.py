import logging
import uuid

from telethon.tl.functions.channels import GetChannelsRequest
from telethon.tl.functions.messages import AddChatUserRequest, CreateChatRequest, GetDialogsRequest

from app.services.telegram_manager import client_manager

logger = logging.getLogger(__name__)


async def create_group(instance_id: uuid.UUID, name: str) -> dict:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    result = await client(CreateChatRequest([], name))
    chat = result.chats[0] if result.chats else result
    return {"group_id": chat.id, "title": name}


async def list_groups(instance_id: uuid.UUID) -> list:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    dialogs = await client.get_dialogs()
    return [
        {
            "group_id": d.entity.id,
            "title": d.name or "",
            "type": d.entity.__class__.__name__,
        }
        for d in dialogs if hasattr(d.entity, "title")
    ]


async def add_member(instance_id: uuid.UUID, group_id: int, user_id: int) -> None:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    entity = await client.get_entity(user_id)
    await client(AddChatUserRequest(chat_id=group_id, user_id=entity, fwd_limit=0))


async def remove_member(instance_id: uuid.UUID, group_id: int, user_id: int) -> None:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    from telethon.tl.functions.channels import EditBannedRequest
    from telethon.tl.types import ChatBannedRights

    entity = await client.get_entity(user_id)
    rights = ChatBannedRights(until_date=None, view_messages=True)
    await client(EditBannedRequest(channel=group_id, participant=entity, banned_rights=rights))
