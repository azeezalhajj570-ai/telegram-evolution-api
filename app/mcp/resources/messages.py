import json

from mcp.server.fastmcp import FastMCP


def register_message_resources(mcp: FastMCP):
    @mcp.resource(
        uri="telegram://messages/{chat_id}",
        name="Chat Messages",
        description="Recent messages in a specific Telegram chat",
        mime_type="application/json",
    )
    async def chat_messages(chat_id: str) -> str:
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
                        messages = await client.get_messages(int(chat_id), limit=50)
                        return json.dumps([
                            {
                                "message_id": m.id,
                                "chat_id": int(chat_id),
                                "sender_id": m.sender_id,
                                "text": m.text or "",
                                "date": m.date.isoformat() if m.date else None,
                                "is_outgoing": m.out,
                            }
                            for m in messages if m
                        ])
                except Exception:
                    pass
            return json.dumps([])

    @mcp.resource(
        uri="telegram://messages/{chat_id}/{message_id}",
        name="Single Message",
        description="Details of a single message in a Telegram chat",
        mime_type="application/json",
    )
    async def single_message(chat_id: str, message_id: str) -> str:
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
                        msg = await client.get_messages(int(chat_id), ids=int(message_id))
                        if msg:
                            return json.dumps({
                                "message_id": msg.id,
                                "chat_id": int(chat_id),
                                "sender_id": msg.sender_id,
                                "text": msg.text or "",
                                "date": msg.date.isoformat() if msg.date else None,
                                "is_outgoing": msg.out,
                            })
                except Exception:
                    pass
            return json.dumps({"error": "Message not found"})
