from typing import Optional

from mcp.server.fastmcp import FastMCP
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest

from app.mcp.context import resolve_instance_id
from app.mcp.errors import mcp_error_from_telegram
from app.services.telegram_manager import client_manager


def _require_instance_id(instance_id: Optional[str]) -> str:
    resolved = resolve_instance_id(instance_id)
    if not resolved:
        raise ValueError(
            "Instance ID required — pass as a parameter, x-instance-id header, "
            "or use an instance-scoped API key"
        )
    return resolved


def register_channel_tools(mcp: FastMCP):
    @mcp.tool(
        name="list_channels",
        description="List all Telegram channels the user follows",
    )
    async def list_channels(
        instance_id: Optional[str] = None,
    ) -> dict:
        resolved_id = _require_instance_id(instance_id)
        client = client_manager.get_client(resolved_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            dialogs = await client.get_dialogs()
            channels = []
            for d in dialogs:
                if d.is_channel and not d.is_group:
                    channels.append({
                        "channel_id": d.entity.id,
                        "title": d.title or "Unknown",
                        "username": getattr(d.entity, "username", None),
                        "participants_count": getattr(d.entity, "participants_count", None),
                    })
            return {"channels": channels}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="join_channel",
        description="Join a Telegram channel by its ID or username",
    )
    async def join_channel(
        channel_id: int,
        instance_id: Optional[str] = None,
    ) -> dict:
        resolved_id = _require_instance_id(instance_id)
        client = client_manager.get_client(resolved_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client(JoinChannelRequest(channel=channel_id))
            return {"status": "joined"}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="leave_channel",
        description="Leave a Telegram channel",
    )
    async def leave_channel(
        channel_id: int,
        instance_id: Optional[str] = None,
    ) -> dict:
        resolved_id = _require_instance_id(instance_id)
        client = client_manager.get_client(resolved_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client(LeaveChannelRequest(channel=channel_id))
            return {"status": "left"}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
