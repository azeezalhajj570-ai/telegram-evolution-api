from mcp.server.fastmcp import FastMCP
from telethon.tl.functions.contacts import DeleteContactsRequest, ImportContactsRequest
from telethon.tl.types import InputPhoneContact

from app.mcp.errors import mcp_error_from_telegram
from app.services.telegram_manager import client_manager


def register_contact_tools(mcp: FastMCP):
    @mcp.tool(
        name="list_contacts",
        description="List all Telegram contacts for an instance",
    )
    async def list_contacts(
        instance_id: str,
        limit: int = 100,
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            from telethon.tl.functions.contacts import GetContactsRequest

            result = await client(GetContactsRequest(hash=0))
            contacts = [
                {
                    "user_id": u.id,
                    "first_name": u.first_name or "",
                    "last_name": u.last_name or "",
                    "phone": u.phone or "",
                    "username": u.username or "",
                }
                for u in result.users if u
            ]
            if limit:
                contacts = contacts[:limit]
            return {"contacts": contacts}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="import_contact",
        description="Import a contact by phone number into Telegram",
    )
    async def import_contact(
        instance_id: str,
        phone: str,
        first_name: str,
        last_name: str = "",
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            result = await client(ImportContactsRequest([
                InputPhoneContact(
                    client_id=0,
                    phone=phone,
                    first_name=first_name,
                    last_name=last_name or "",
                )
            ]))
            users = result.users
            if users:
                u = users[0]
                return {
                    "contact": {
                        "user_id": u.id,
                        "first_name": u.first_name or "",
                        "last_name": u.last_name or "",
                        "phone": u.phone or "",
                        "username": u.username or "",
                    }
                }
            return {"contact": {"phone": phone, "first_name": first_name, "status": "imported"}}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="delete_contact",
        description="Delete a contact from Telegram",
    )
    async def delete_contact(
        instance_id: str,
        contact_id: int,
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client(DeleteContactsRequest(id=[contact_id]))
            return {"status": "deleted"}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
