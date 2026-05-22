from typing import Optional

from mcp.server.fastmcp import FastMCP

from app.mcp.handler import create_handler, require_instance_id
from app.mcp.sanitize import sanitize_group
from app.services.telegram_manager import client_manager


def register_channel_tools(mcp: FastMCP):

    @mcp.tool(name="list_channels", description="List all Telegram channels the user follows")
    async def list_channels(instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            dialogs = await client.get_dialogs()
            raw = [{"channel_id": d.entity.id, "title": d.title or "Unknown", "username": getattr(d.entity, "username", None), "participants_count": getattr(d.entity, "participants_count", None)} for d in dialogs if d.is_channel and not d.is_group]
            return {"channels": [sanitize_group(c) for c in raw]}
        return await create_handler("list_channels", _run)

    @mcp.tool(name="join_channel", description="Join a Telegram channel by its ID or username")
    async def join_channel(channel_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.channels import JoinChannelRequest
            await client(JoinChannelRequest(channel=channel_id))
            return {"status": "joined"}
        return await create_handler("join_channel", _run)

    @mcp.tool(name="leave_channel", description="Leave a Telegram channel")
    async def leave_channel(channel_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.channels import LeaveChannelRequest
            await client(LeaveChannelRequest(channel=channel_id))
            return {"status": "left"}
        return await create_handler("leave_channel", _run)
