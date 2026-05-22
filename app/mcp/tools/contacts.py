from typing import Optional

from mcp.server.fastmcp import FastMCP

from app.mcp.handler import create_handler, require_instance_id
from app.mcp.sanitize import sanitize_contact
from app.services.telegram_manager import client_manager


def register_contact_tools(mcp: FastMCP):

    @mcp.tool(name="contacts.list", description="List all Telegram contacts saved in the account, with optional limit")
    async def list_contacts(limit: int = 100, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.contacts import GetContactsRequest
            result = await client(GetContactsRequest(hash=0))
            raw = [{"user_id": u.id, "first_name": u.first_name or "", "last_name": u.last_name or "", "phone": u.phone or "", "username": u.username or ""} for u in result.users if u]
            return {"contacts": [sanitize_contact(c) for c in raw[:limit]]}
        return await create_handler("list_contacts", _run)

    @mcp.tool(name="contacts.import", description="Import/save a new contact by phone number into the Telegram address book")
    async def import_contact(phone: str, first_name: str, last_name: str = "", instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.contacts import ImportContactsRequest
            from telethon.tl.types import InputPhoneContact
            result = await client(ImportContactsRequest([InputPhoneContact(client_id=0, phone=phone, first_name=first_name, last_name=last_name or "")]))
            if result.users:
                u = result.users[0]
                return {"contact": {"user_id": u.id, "first_name": u.first_name or "", "last_name": u.last_name or "", "phone": u.phone or "", "username": u.username or ""}}
            return {"contact": {"phone": phone, "first_name": first_name, "status": "imported"}}
        return await create_handler("import_contact", _run)

    @mcp.tool(name="contacts.delete", description="Delete a contact from the Telegram address book by contact user ID")
    async def delete_contact(contact_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.contacts import DeleteContactsRequest
            await client(DeleteContactsRequest(id=[contact_id]))
            return {"status": "deleted"}
        return await create_handler("delete_contact", _run)
