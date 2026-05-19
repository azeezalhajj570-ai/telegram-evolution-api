import uuid

from mcp.server.fastmcp import FastMCP
from telethon.errors import FloodWaitError

from app.mcp.errors import mcp_error_from_telegram
from app.services.messaging import send_message as svc_send_message


def register_messaging_tools(mcp: FastMCP):
    @mcp.tool(
        name="send_message",
        description="Send a text message to a Telegram chat",
    )
    async def send_message(
        instance_id: str,
        chat_id: int,
        text: str,
    ) -> dict:
        try:
            result = await svc_send_message(uuid.UUID(instance_id), text, chat_id=chat_id)
            return result
        except (ValueError, FloodWaitError) as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="send_media",
        description="Send a photo, document, or video to a Telegram chat",
    )
    async def send_media(
        instance_id: str,
        chat_id: int,
        file_path: str,
        caption: str = "",
        media_type: str = "photo",
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            result = await client.send_file(chat_id, file_path, caption=caption or None)
            return {"message_id": result.id, "chat_id": chat_id, "status": "sent"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="get_messages",
        description="Get recent messages from a Telegram chat",
    )
    async def get_messages(
        instance_id: str,
        chat_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        from app.services.chats import get_messages as svc_get_messages

        try:
            messages = await svc_get_messages(uuid.UUID(instance_id), chat_id, limit=limit, offset_id=offset or None)
            return {"messages": messages}
        except ValueError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="reply_message",
        description="Reply to a specific message in a Telegram chat",
    )
    async def reply_message(
        instance_id: str,
        chat_id: int,
        reply_to_msg_id: int,
        text: str,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            result = await client.send_message(chat_id, text, reply_to=reply_to_msg_id)
            return {"message_id": result.id, "chat_id": chat_id, "status": "replied"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="forward_message",
        description="Forward a message from one chat to another",
    )
    async def forward_message(
        instance_id: str,
        from_chat_id: int,
        to_chat_id: int,
        message_id: int,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            result = await client.forward_messages(to_chat_id, message_id, from_chat_id)
            return {"message_id": result.id, "status": "forwarded"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="edit_message",
        description="Edit a previously sent message in a Telegram chat",
    )
    async def edit_message(
        instance_id: str,
        chat_id: int,
        message_id: int,
        text: str,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client.edit_message(chat_id, message_id, text)
            return {"status": "edited"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="delete_message",
        description="Delete a message from a Telegram chat",
    )
    async def delete_message(
        instance_id: str,
        chat_id: int,
        message_id: int,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            await client.delete_messages(chat_id, [message_id])
            return {"status": "deleted"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="add_reaction",
        description="Add an emoji reaction to a message in a Telegram chat",
    )
    async def add_reaction(
        instance_id: str,
        chat_id: int,
        message_id: int,
        emoji: str,
    ) -> dict:
        from app.services.telegram_manager import client_manager

        client = client_manager.get_client(instance_id)
        if client is None or not client.is_connected():
            raise ValueError("Instance not connected")

        try:
            from telethon.tl.functions.messages import SendReactionRequest
            from telethon.tl.types import ReactionEmoji

            reaction = ReactionEmoji(emoticon=emoji)
            await client(SendReactionRequest(
                peer=chat_id,
                msg_id=message_id,
                reaction=[reaction],
            ))
            return {"status": "reaction_added"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
        except Exception as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])
