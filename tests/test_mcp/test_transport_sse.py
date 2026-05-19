import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_sse_health_endpoint():
    from app.mcp.sse import sse_app

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["transport"] == "sse"
