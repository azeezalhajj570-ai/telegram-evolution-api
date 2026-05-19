from mcp.server.fastmcp import FastMCP
from telethon.tl.functions.messages import AddChatUserRequest, CreateChatRequest, DeleteChatUserRequest

from app.mcp.errors import mcp_error_from_telegram
from app.services.telegram_manager import client_manager


def register_group_tools(mcp: FastMCP):
    @mcp.tool(
        name="list_groups",
        description="List all Telegram groups the user is a member of",
    )
    async def list_groups(
        instance_id: str,
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            dialogs = await client.get_dialogs()
            groups = []
            for d in dialogs:
                if d.is_group:
                    groups.append({
                        "group_id": d.entity.id,
                        "title": d.title or "Unknown",
                        "participants_count": getattr(d.entity, "participants_count", None),
                    })
            return {"groups": groups}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="create_group",
        description="Create a new Telegram group",
    )
    async def create_group(
        instance_id: str,
        title: str,
        member_ids: str = "",
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            parsed_ids = [int(x.strip()) for x in member_ids.split(",") if x.strip()] if member_ids else []
            result = await client(CreateChatRequest(
                title=title,
                users=parsed_ids,
            ))
            return {"group_id": result.chats[0].id if result.chats else 0, "status": "created"}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="add_group_member",
        description="Add a member to a Telegram group",
    )
    async def add_group_member(
        instance_id: str,
        group_id: int,
        user_id: int,
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client(AddChatUserRequest(
                chat_id=group_id,
                user_id=user_id,
                fwd_limit=0,
            ))
            return {"status": "added"}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="remove_group_member",
        description="Remove a member from a Telegram group",
    )
    async def remove_group_member(
        instance_id: str,
        group_id: int,
        user_id: int,
    ) -> dict:
        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client(DeleteChatUserRequest(
                chat_id=group_id,
                user_id=user_id,
            ))
            return {"status": "removed"}
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
