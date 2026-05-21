from typing import Optional

from mcp.server.fastmcp import FastMCP

from app.mcp.handler import create_handler, require_instance_id
from app.services.telegram_manager import client_manager


def register_group_tools(mcp: FastMCP):

    @mcp.tool(name="list_groups", description="List all Telegram groups the user is a member of")
    async def list_groups(instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            dialogs = await client.get_dialogs()
            groups = [
                {"group_id": d.entity.id, "title": d.title or "Unknown", "participants_count": getattr(d.entity, "participants_count", None)}
                for d in dialogs if d.is_group
            ]
            return {"groups": groups}
        return await create_handler("list_groups", _run)

    @mcp.tool(name="create_group", description="Create a new Telegram group")
    async def create_group(title: str, member_ids: str = "", instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.messages import CreateChatRequest
            parsed_ids = [int(x.strip()) for x in member_ids.split(",") if x.strip()] if member_ids else []
            result = await client(CreateChatRequest(title=title, users=parsed_ids))
            return {"group_id": result.chats[0].id if result.chats else 0, "status": "created"}
        return await create_handler("create_group", _run)

    @mcp.tool(name="add_group_member", description="Add a member to a Telegram group")
    async def add_group_member(group_id: int, user_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.messages import AddChatUserRequest
            await client(AddChatUserRequest(chat_id=group_id, user_id=user_id, fwd_limit=0))
            return {"status": "added"}
        return await create_handler("add_group_member", _run)

    @mcp.tool(name="remove_group_member", description="Remove a member from a Telegram group")
    async def remove_group_member(group_id: int, user_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.messages import DeleteChatUserRequest
            await client(DeleteChatUserRequest(chat_id=group_id, user_id=user_id))
            return {"status": "removed"}
        return await create_handler("remove_group_member", _run)
