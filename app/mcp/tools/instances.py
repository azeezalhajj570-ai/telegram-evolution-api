import uuid

from mcp.server.fastmcp import FastMCP
from telethon.errors import FloodWaitError

from app.db.database import async_session
from app.db.repositories import InstanceRepository
from app.mcp.errors import mcp_error_from_telegram
from app.services.telegram_auth import send_code as auth_send_code
from app.services.telegram_auth import submit_2fa as auth_submit_2fa
from app.services.telegram_auth import verify_code as auth_verify_code
from app.services.telegram_manager import client_manager


def register_instance_tools(mcp: FastMCP):
    @mcp.tool(
        name="create_instance",
        description="Create a new Telegram instance",
    )
    async def create_instance_tool(
        name: str,
    ) -> dict:
        async with async_session() as db:
            repo = InstanceRepository(db)
            inst = await repo.create(name)
            await db.commit()
            return {
                "id": str(inst.id),
                "name": inst.name,
                "status": inst.status,
            }

    @mcp.tool(
        name="list_instances",
        description="List all Telegram instances with their status",
    )
    async def list_instances_tool() -> dict:
        async with async_session() as db:
            repo = InstanceRepository(db)
            instances = await repo.get_all()
            return {
                "instances": [
                    {
                        "id": str(inst.id),
                        "name": inst.name,
                        "phone_number": inst.phone_number,
                        "status": inst.status,
                        "created_at": inst.created_at.isoformat() if inst.created_at else None,
                    }
                    for inst in instances
                ]
            }

    @mcp.tool(
        name="get_instance_status",
        description="Get the current status of a specific Telegram instance",
    )
    async def get_instance_status_tool(
        instance_id: str,
    ) -> dict:
        async with async_session() as db:
            repo = InstanceRepository(db)
            inst = await repo.get(uuid.UUID(instance_id))
            if not inst:
                raise ValueError("Instance not found")
            return {
                "id": str(inst.id),
                "name": inst.name,
                "phone_number": inst.phone_number,
                "status": inst.status,
            }

    @mcp.tool(
        name="send_auth_code",
        description="Send a login code to a phone number for a Telegram instance",
    )
    async def send_auth_code_tool(
        instance_id: str,
        phone_number: str,
    ) -> dict:
        try:
            async with async_session() as db:
                repo = InstanceRepository(db)
                await auth_send_code(uuid.UUID(instance_id), phone_number, repo)
                await db.commit()
            return {"status": "code_sent"}
        except FloodWaitError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="verify_auth_code",
        description="Verify the login code received via SMS for a Telegram instance",
    )
    async def verify_auth_code_tool(
        instance_id: str,
        code: str,
    ) -> dict:
        try:
            async with async_session() as db:
                repo = InstanceRepository(db)
                result = await auth_verify_code(uuid.UUID(instance_id), code, repo)
                await db.commit()
            return result
        except ValueError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="submit_2fa",
        description="Submit a 2FA password for a Telegram instance",
    )
    async def submit_2fa_tool(
        instance_id: str,
        password: str,
    ) -> dict:
        try:
            async with async_session() as db:
                repo = InstanceRepository(db)
                result = await auth_submit_2fa(uuid.UUID(instance_id), password, repo)
                await db.commit()
            return result
        except ValueError as e:
            raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="connect_instance",
        description="Connect an authenticated Telegram instance so it can send/receive messages",
    )
    async def connect_instance_tool(
        instance_id: str,
    ) -> dict:
        async with async_session() as db:
            repo = InstanceRepository(db)
            uid = uuid.UUID(instance_id)
            inst = await repo.get(uid)
            if not inst:
                raise ValueError("Instance not found")
            if not inst.session_encrypted:
                raise ValueError("No saved session — authenticate first")
            if inst.status == "connected":
                return {"status": "connected"}
            try:
                await client_manager.start_client(instance_id, inst.session_encrypted)
                await repo.update(uid, status="connected")
                await db.commit()
                return {"status": "connected"}
            except Exception as e:
                await repo.update(uid, status="auth_required")
                await db.commit()
                raise ValueError(mcp_error_from_telegram(e)["message"])

    @mcp.tool(
        name="set_instance_api_key",
        description="Generate or rotate an MCP API key for a specific Telegram instance. "
                    "Returns the new key once — save it securely.",
    )
    async def set_instance_api_key_tool(
        instance_id: str,
    ) -> dict:
        from app.mcp.auth import generate_instance_api_key

        raw_key = await generate_instance_api_key(instance_id)
        return {"instance_id": instance_id, "api_key": raw_key, "status": "created"}

    @mcp.tool(
        name="get_scoped_instance",
        description="Return the instance_id scoped to the current API key. "
                    "If using a global API key, returns null and instance_id must be passed explicitly.",
    )
    async def get_scoped_instance_tool() -> dict:
        from app.mcp.context import get_current_instance

        instance_id = get_current_instance()
        return {"instance_id": instance_id}
