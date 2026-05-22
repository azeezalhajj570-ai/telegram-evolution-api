import uuid
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP

from app.mcp.handler import create_handler, require_instance_id
from app.mcp.sanitize import sanitize_message
from app.services.messaging import send_message as svc_send_message


def register_messaging_tools(mcp: FastMCP):

    @mcp.tool(name="messages.send", description="Send a plain text message to a Telegram chat, group, or user by chat_id, username, or phone number. Provide one of: chat_id, username, or phone_number.")
    async def send_message(
        text: Annotated[str, "Message text content"],
        chat_id: Annotated[Optional[int], "Telegram chat/group/user ID (numeric). Provide this OR username OR phone_number."] = None,
        username: Annotated[Optional[str], "Telegram username without @ (e.g. 'johndoe'). Provide this OR chat_id OR phone_number."] = None,
        phone_number: Annotated[Optional[str], "Phone number in international format (e.g. '+5511999999999'). Provide this OR chat_id OR username."] = None,
        instance_id: Annotated[Optional[str], "Instance ID (omit if using scoped key)"] = None,
    ) -> dict:
        resolved_id = require_instance_id(instance_id)
        return await create_handler("messages.send", lambda: svc_send_message(uuid.UUID(resolved_id), text, chat_id=chat_id, username=username, phone_number=phone_number))

    @mcp.tool(name="messages.send_media", description="Send a photo, document, or video to a Telegram chat from a local file path or URL")
    async def send_media(chat_id: int, file_path: str, caption: str = "", media_type: str = "photo", instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            result = await client.send_file(chat_id, file_path, caption=caption or None)
            return {"message_id": result.id, "chat_id": chat_id, "status": "sent"}
        return await create_handler("send_media", _run)

    @mcp.tool(name="messages.list", description="Get the most recent messages from a Telegram chat, with pagination via offset")
    async def get_messages(chat_id: int, limit: int = 20, offset: int = 0, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.chats import get_messages as svc_get_messages
        async def _run():
            msgs = await svc_get_messages(uuid.UUID(resolved_id), chat_id, limit=limit, offset_id=offset)
            return {"messages": [sanitize_message(m) for m in msgs]}
        return await create_handler("get_messages", _run)

    @mcp.tool(name="messages.reply", description="Reply to an existing message in a Telegram chat by specifying the message ID to reply to")
    async def reply_message(chat_id: int, reply_to_msg_id: int, text: str, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            result = await client.send_message(chat_id, text, reply_to=reply_to_msg_id)
            return {"message_id": result.id, "chat_id": chat_id, "status": "replied"}
        return await create_handler("reply_message", _run)

    @mcp.tool(name="messages.forward", description="Forward a message from one Telegram chat to another by message ID")
    async def forward_message(from_chat_id: int, to_chat_id: int, message_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            result = await client.forward_messages(to_chat_id, message_id, from_chat_id)
            return {"message_id": result.id, "status": "forwarded"}
        return await create_handler("forward_message", _run)

    @mcp.tool(name="messages.edit", description="Edit the text of a previously sent message in a Telegram chat")
    async def edit_message(chat_id: int, message_id: int, text: str, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            await client.edit_message(chat_id, message_id, text)
            return {"status": "edited"}
        return await create_handler("edit_message", _run)

    @mcp.tool(name="messages.delete", description="Delete a message from a Telegram chat permanently")
    async def delete_message(chat_id: int, message_id: int, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            await client.delete_messages(chat_id, [message_id])
            return {"status": "deleted"}
        return await create_handler("delete_message", _run)

    @mcp.tool(name="messages.react", description="Add an emoji reaction to a message in a Telegram chat")
    async def add_reaction(chat_id: int, message_id: int, emoji: str, instance_id: Optional[str] = None) -> dict:
        resolved_id = require_instance_id(instance_id)
        from app.services.telegram_manager import client_manager
        async def _run():
            client = client_manager.get_client(resolved_id)
            if client is None or not client.is_connected():
                raise ValueError("Instance not connected")
            from telethon.tl.functions.messages import SendReactionRequest
            from telethon.tl.types import ReactionEmoji
            await client(SendReactionRequest(peer=chat_id, msg_id=message_id, reaction=[ReactionEmoji(emoticon=emoji)]))
            return {"status": "reaction_added"}
        return await create_handler("add_reaction", _run)
