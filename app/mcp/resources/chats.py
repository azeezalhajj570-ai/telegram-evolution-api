import json

from mcp.server.fastmcp import FastMCP


def register_chat_resources(mcp: FastMCP):
    @mcp.resource(
        uri="telegram://chats",
        name="Recent Chats",
        description="Recent Telegram chats across all connected instances",
        mime_type="application/json",
    )
    async def chats_list() -> str:
        from app.db.database import async_session
        from app.db.repositories import InstanceRepository

        async with async_session() as db:
            repo = InstanceRepository(db)
            connected = await repo.get_by_status("connected")
            all_chats = []
            for inst in connected:
                try:
                    from app.services.telegram_manager import client_manager
                    client = client_manager.get_client(str(inst.id))
                    if client and client.is_connected():
                        dialogs = await client.get_dialogs()
                        for d in dialogs[:50]:
                            all_chats.append({
                                "instance_id": str(inst.id),
                                "chat_id": d.entity.id,
                                "title": d.title or "Unknown",
                                "type": d.name or d.entity.__class__.__name__.lower(),
                                "unread_count": d.unread_count,
                            })
                except Exception:
                    pass
            return json.dumps(all_chats)

    @mcp.resource(
        uri="telegram://chats/{chat_id}",
        name="Chat Details",
        description="Details of a specific Telegram chat",
        mime_type="application/json",
    )
    async def chat_detail(chat_id: str) -> str:
        from app.db.database import async_session
        from app.db.repositories import InstanceRepository

        async with async_session() as db:
            repo = InstanceRepository(db)
            connected = await repo.get_by_status("connected")
            for inst in connected:
                try:
                    from app.services.telegram_manager import client_manager
                    client = client_manager.get_client(str(inst.id))
                    if client and client.is_connected():
                        entity = await client.get_entity(int(chat_id))
                        return json.dumps({
                            "instance_id": str(inst.id),
                            "chat_id": entity.id,
                            "title": getattr(entity, "title", None) or getattr(entity, "first_name", ""),
                            "username": getattr(entity, "username", None),
                            "type": entity.__class__.__name__.lower(),
                        })
                except Exception:
                    pass
            return json.dumps({"error": "Chat not found"})
