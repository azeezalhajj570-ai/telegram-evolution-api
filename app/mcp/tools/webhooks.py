import uuid

from mcp.server.fastmcp import FastMCP

from app.db.database import async_session
from app.db.repositories import WebhookRepository


def register_webhook_tools(mcp: FastMCP):
    @mcp.tool(
        name="configure_webhook",
        description="Configure a webhook URL for a Telegram instance to receive real-time events",
    )
    async def configure_webhook(
        instance_id: str,
        url: str,
    ) -> dict:
        async with async_session() as db:
            repo = WebhookRepository(db)
            existing = await repo.get_by_instance(uuid.UUID(instance_id))
            import secrets
            secret = secrets.token_hex(16)
            if existing:
                existing.url = url
                existing.secret = secret
                await db.commit()
                return {"webhook_id": str(existing.id), "status": "configured"}
            wh = await repo.create(uuid.UUID(instance_id), url, secret)
            await db.commit()
            return {"webhook_id": str(wh.id), "status": "configured"}

    @mcp.tool(
        name="test_webhook",
        description="Test the webhook configuration for a Telegram instance",
    )
    async def test_webhook(
        instance_id: str,
    ) -> dict:
        import httpx

        async with async_session() as db:
            repo = WebhookRepository(db)
            wh = await repo.get_by_instance(uuid.UUID(instance_id))
            if not wh:
                raise ValueError("No webhook configured for this instance")
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(wh.url, json={"event": "test", "instance_id": instance_id})
                    return {"status": "delivered" if resp.is_success else "failed", "status_code": resp.status_code}
            except httpx.RequestError as e:
                return {"status": "failed", "status_code": 0, "error": str(e)}
