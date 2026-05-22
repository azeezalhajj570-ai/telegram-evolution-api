import pytest
from httpx import AsyncClient


def _d(resp):
    return resp.json()["data"]


@pytest.mark.asyncio
async def test_create_webhook(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Webhook Test"})
    inst_id = _d(inst_resp)["id"]
    resp = await client.post(f"/instances/{inst_id}/webhook", json={"url": "https://example.com/webhook"})
    assert resp.status_code == 201
    data = _d(resp)
    assert data["url"] == "https://example.com/webhook"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_webhook(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Get Webhook"})
    inst_id = _d(inst_resp)["id"]
    await client.post(f"/instances/{inst_id}/webhook", json={"url": "https://example.com/wh"})
    resp = await client.get(f"/instances/{inst_id}/webhook")
    assert resp.status_code == 200
    assert _d(resp)["url"] == "https://example.com/wh"


@pytest.mark.asyncio
async def test_delete_webhook(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Delete Webhook"})
    inst_id = _d(inst_resp)["id"]
    await client.post(f"/instances/{inst_id}/webhook", json={"url": "https://example.com/wh"})
    resp = await client.delete(f"/instances/{inst_id}/webhook")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_no_webhook_returns_404(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "No Webhook"})
    inst_id = _d(inst_resp)["id"]
    resp = await client.get(f"/instances/{inst_id}/webhook")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_webhook_fails(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Dup Webhook"})
    inst_id = _d(inst_resp)["id"]
    await client.post(f"/instances/{inst_id}/webhook", json={"url": "https://example.com/wh"})
    resp = await client.post(f"/instances/{inst_id}/webhook", json={"url": "https://example.com/wh2"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_webhook_on_missing_instance(client: AsyncClient):
    resp = await client.post("/instances/00000000-0000-0000-0000-000000000000/webhook",
                             json={"url": "https://example.com/wh"})
    assert resp.status_code == 404
