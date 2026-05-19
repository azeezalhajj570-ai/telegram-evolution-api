import json

from mcp.server.fastmcp import FastMCP
from telethon.tl.functions.contacts import GetContactsRequest


def register_contact_resources(mcp: FastMCP):
    @mcp.resource(
        uri="telegram://contacts",
        name="Contact List",
        description="All Telegram contacts from the connected instances",
        mime_type="application/json",
    )
    async def contacts_list() -> str:
        from app.db.database import async_session
        from app.db.repositories import InstanceRepository

        async with async_session() as db:
            repo = InstanceRepository(db)
            connected = await repo.get_by_status("connected")
            all_contacts = []
            for inst in connected:
                try:
                    from app.services.telegram_manager import client_manager
                    client = client_manager.get_client(str(inst.id))
                    if client and client.is_connected():
                        result = await client(GetContactsRequest(hash=0))
                        for u in result.users:
                            if u:
                                all_contacts.append({
                                    "instance_id": str(inst.id),
                                    "user_id": u.id,
                                    "first_name": u.first_name or "",
                                    "last_name": u.last_name or "",
                                    "phone": u.phone or "",
                                    "username": u.username or "",
                                })
                except Exception:
                    pass
            return json.dumps(all_contacts)
