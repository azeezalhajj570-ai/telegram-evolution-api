import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _id(resp):
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_send_code_no_session(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Auth Test"})
    inst_id = _id(inst_resp)
    resp = await client.post(f"/instances/{inst_id}/auth/send-code", json={"phone_number": "+5511999999999"})
    assert resp.status_code in (200, 500)


@pytest.mark.asyncio
async def test_verify_code_no_session(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Auth Verify"})
    inst_id = _id(inst_resp)
    resp = await client.post(f"/instances/{inst_id}/auth/verify-code", json={"code": "12345"})
    assert resp.status_code in (200, 400)


@pytest.mark.asyncio
async def test_connect_no_session(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Connect Test"})
    inst_id = _id(inst_resp)
    resp = await client.post(f"/instances/{inst_id}/auth/connect")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_disconnect_not_connected(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Disconnect Test"})
    inst_id = _id(inst_resp)
    resp = await client.post(f"/instances/{inst_id}/auth/disconnect")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_auth_on_missing_instance(client: AsyncClient):
    resp = await client.post("/instances/00000000-0000-0000-0000-000000000000/auth/send-code", json={"phone_number": "+5511999999999"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_no_api_key_returns_401():
    anon = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    resp = await anon.get("/instances")
    assert resp.status_code == 401
    await anon.aclose()
