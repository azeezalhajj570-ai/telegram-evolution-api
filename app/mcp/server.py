import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    from app.db.database import Base, async_session, engine
    from app.db.repositories import InstanceRepository

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.api_keys:
        async with async_session() as db:
            from sqlalchemy import select

            from app.db.models import ApiKey
            from app.security.api_keys import hash_api_key

            for raw_key in settings.api_keys_list:
                result = await db.execute(select(ApiKey).where(ApiKey.name == f"auto:{raw_key[:8]}"))
                if not result.scalar_one_or_none():
                    db.add(ApiKey(
                        name=f"auto:{raw_key[:8]}",
                        key_hash=hash_api_key(raw_key),
                        is_active=True,
                    ))
            await db.commit()

    async with async_session() as db:
        repo = InstanceRepository(db)
        connected = await repo.get_by_status("connected")
        for inst in connected:
            if inst.session_encrypted:
                try:
                    from app.services.telegram_manager import client_manager
                    await client_manager.start_client(str(inst.id), inst.session_encrypted)
                    logger.info("Reconnected instance %s on MCP startup", inst.id)
                except Exception as e:
                    await repo.update(inst.id, status="auth_required")
                    logger.warning("Failed to reconnect instance %s: %s", inst.id, e)
        await db.commit()

    logger.info("MCP server lifespan started")
    yield {}
    from app.services.telegram_manager import client_manager
    await client_manager.stop_all()
    logger.info("MCP server lifespan ended")


mcp_app = FastMCP(
    name="RelayStack",
    instructions="Model Context Protocol server for RelayStack Telegram API. "
                "Provides tools to send/receive messages, manage chats, contacts, "
                "groups, channels, and Telegram instances.",
    lifespan=mcp_lifespan,
)

mcp_app.settings.transport_security.allowed_hosts.extend([
    "localhost", "127.0.0.1", "[::1]",
    "tele.dev.hamedco.com", "*.hamedco.com",
])
mcp_app.settings.transport_security.allowed_origins.extend([
    "http://localhost", "http://127.0.0.1", "http://[::1]",
    "https://tele.dev.hamedco.com", "https://*.hamedco.com",
])


def _register_all_tools():
    from app.mcp.tools import messaging

    messaging.register_messaging_tools(mcp_app)

    try:
        from app.mcp.tools import chats as chats_tools
        chats_tools.register_chat_tools(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.tools import contacts
        contacts.register_contact_tools(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.tools import groups
        groups.register_group_tools(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.tools import channels
        channels.register_channel_tools(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.tools import instances
        instances.register_instance_tools(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.tools import webhooks
        webhooks.register_webhook_tools(mcp_app)
    except ImportError:
        pass


def _register_all_resources():
    try:
        from app.mcp.resources import instances as inst_res
        inst_res.register_instance_resources(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.resources import chats
        chats.register_chat_resources(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.resources import contacts
        contacts.register_contact_resources(mcp_app)
    except ImportError:
        pass

    try:
        from app.mcp.resources import messages
        messages.register_message_resources(mcp_app)
    except ImportError:
        pass


def _register_all_prompts():
    try:
        from app.mcp.prompts import templates
        templates.register_prompts(mcp_app)
    except ImportError:
        pass


_register_all_tools()
_register_all_resources()
_register_all_prompts()
