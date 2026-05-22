import uuid
from typing import Optional

from mcp.server.fastmcp import FastMCP

from app.mcp.handler import create_handler, require_instance_id
from app.mcp.sanitize import sanitize_chat, sanitize_message
from app.services.chats import list_chats as svc_list_chats


def register_chat_tools(mcp: FastMCP):

    @mcp.tool(name="list_chats", description="List recent Telegram chats for an instance")
    async def list_chats(limit: int = 50, offset: int = 0, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            chats = await svc_list_chats(uuid.UUID(resolved_id))
            return {"chats": [sanitize_chat(c) for c in chats]}
        return await create_handler("list_chats", _run)

    @mcp.tool(name="get_chat_info", description="Get details about a specific Telegram chat")
    async def get_chat_info(chat_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            entity = await client.get_entity(chat_id)
            return {
                "chat": {
                    "chat_id": entity.id,
                    "title": getattr(entity, "title", None) or getattr(entity, "first_name", ""),
                    "username": getattr(entity, "username", None),
                    "type": entity.__class__.__name__.lower(),
                }
            }
        return await create_handler("get_chat_info", _run)

    @mcp.tool(name="search_messages", description="Search messages in a Telegram chat by query text")
    async def search_messages(chat_id: int, query: str, limit: int = 20, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            results = await client.get_messages(chat_id, limit=limit, search=query)
            raw = [{"message_id": m.id, "sender_id": m.sender_id, "text": m.text or "", "date": m.date.isoformat() if m.date else None} for m in results if m]
            return {"messages": [sanitize_message(m) for m in raw]}
        return await create_handler("search_messages", _run)
