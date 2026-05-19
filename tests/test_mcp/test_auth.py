import os

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.asyncio


async def test_sse_auth_no_key_returns_401():
    from app.mcp.sse import sse_app

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/sse")
        assert resp.status_code == 401
        data = resp.json()
        assert data["error"] == "unauthorized"


async def test_sse_auth_invalid_key_returns_401():
    from app.mcp.sse import sse_app

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/sse", headers={"X-API-Key": "invalid-key"})
        assert resp.status_code == 401


async def test_sse_health_skips_auth():
    from app.mcp.sse import sse_app

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200


@pytest.mark.skipif(not os.environ.get("DATABASE_URL", "").startswith("sqlite"), reason="Requires sqlite DB")
async def test_sse_auth_passes_with_valid_x_api_key():
    from app.config import settings
    from app.mcp.sse import sse_app

    old_keys = settings.api_keys
    settings.api_keys = "valid-test-key"

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/sse", headers={"X-API-Key": "valid-test-key"})
        assert resp.status_code != 401

    settings.api_keys = old_keys


@pytest.mark.skipif(not os.environ.get("DATABASE_URL", "").startswith("sqlite"), reason="Requires sqlite DB")
async def test_sse_auth_passes_with_bearer_token():
    from app.config import settings
    from app.mcp.sse import sse_app

    old_keys = settings.api_keys
    settings.api_keys = "bearer-test-key"

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/sse", headers={"Authorization": "Bearer bearer-test-key"})
        assert resp.status_code != 401

    settings.api_keys = old_keys


async def test_sse_auth_rejects_empty_bearer():
    from app.mcp.sse import sse_app

    async with AsyncClient(transport=ASGITransport(app=sse_app), base_url="http://localhost") as client:
        resp = await client.get("/sse", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401


async def test_authenticate_stdio_from_env():
    os.environ["MCP_API_KEY"] = "stdio-test-key"
    old_keys = os.environ.get("API_KEYS", "")
    os.environ["API_KEYS"] = "stdio-test-key"

    from importlib import reload

    import app.config
    reload(app.config)

    from app.mcp.auth import authenticate_stdio
    assert authenticate_stdio() is True

    os.environ["API_KEYS"] = old_keys
    reload(app.config)
    del os.environ["MCP_API_KEY"]


async def test_authenticate_stdio_with_explicit_key():
    from app.mcp.auth import authenticate_stdio

    old_keys = os.environ.get("API_KEYS", "")
    os.environ["API_KEYS"] = "explicit-key"

    from importlib import reload

    import app.config
    reload(app.config)

    assert authenticate_stdio("explicit-key") is True

    os.environ["API_KEYS"] = old_keys
    reload(app.config)


async def test_authenticate_stdio_invalid_key():
    from app.mcp.auth import authenticate_stdio
    assert authenticate_stdio("wrong-key") is False
