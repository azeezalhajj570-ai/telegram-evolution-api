import uuid

from mcp.server.fastmcp import FastMCP

from app.mcp.errors import mcp_error_from_telegram
from app.services.chats import list_chats as svc_list_chats


def register_chat_tools(mcp: FastMCP):
    @mcp.tool(
        name="list_chats",
        description="List recent Telegram chats for an instance",
    )
    async def list_chats(
        instance_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        try:
            chats = await svc_list_chats(uuid.UUID(instance_id))
            if limit:
                chats = chats[offset or 0:offset or 0 + limit]
            return {"chats": chats}
        except ValueError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="get_chat_info",
        description="Get details about a specific Telegram chat",
    )
    async def get_chat_info(
        instance_id: str,
        chat_id: int,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            entity = await client.get_entity(chat_id)
            return {
                "chat": {
                    "chat_id": entity.id,
                    "title": getattr(entity, "title", None) or getattr(entity, "first_name", ""),
                    "username": getattr(entity, "username", None),
                    "type": entity.__class__.__name__.lower(),
                }
            }
        except ValueError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="search_messages",
        description="Search messages in a Telegram chat by query text",
    )
    async def search_messages(
        instance_id: str,
        chat_id: int,
        query: str,
        limit: int = 20,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            results = await client.get_messages(chat_id, limit=limit, search=query)
            messages = [
                {
                    "message_id": m.id,
                    "chat_id": chat_id,
                    "sender_id": m.sender_id,
                    "text": m.text or "",
                    "date": m.date.isoformat() if m.date else None,
                }
                for m in results if m
            ]
            return {"messages": messages}
        except ValueError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
