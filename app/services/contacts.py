import logging
import uuid

from telethon.tl.functions.contacts import DeleteContactsRequest, ImportContactsRequest
from telethon.tl.types import InputPhoneContact

from app.services.telegram_manager import client_manager

logger = logging.getLogger(__name__)


async def list_contacts(instance_id: uuid.UUID) -> list:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    result = await client.get_contacts()
    return [
        {
            "user_id": c.id,
            "phone_number": c.phone,
            "first_name": c.first_name or "",
            "last_name": c.last_name or "",
        }
        for c in result
    ]


async def import_contact(instance_id: uuid.UUID, phone_number: str, first_name: str, last_name: str = "") -> dict:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    contact = InputPhoneContact(client_id=0, phone=phone_number, first_name=first_name, last_name=last_name)
    result = await client(ImportContactsRequest([contact]))
    if not result.users:
        raise ValueError("User not found on Telegram")

    user = result.users[0]
    return {"user_id": user.id, "phone_number": phone_number, "first_name": first_name, "last_name": last_name}


async def delete_contact(instance_id: uuid.UUID, user_id: int) -> None:
    client = client_manager.get_client(str(instance_id))
    if not client or not client.is_connected():
        raise ValueError("Instance not connected")

    entity = await client.get_entity(user_id)
    await client(DeleteContactsRequest([entity]))
