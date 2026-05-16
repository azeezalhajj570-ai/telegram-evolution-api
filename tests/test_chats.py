import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_chats_not_connected(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Chats Test"})
    inst_id = inst_resp.json()["id"]
    resp = await client.get(f"/instances/{inst_id}/chats")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_chats_missing_instance(client: AsyncClient):
    resp = await client.get("/instances/00000000-0000-0000-0000-000000000000/chats")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_messages_not_connected(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Msgs Test"})
    inst_id = inst_resp.json()["id"]
    resp = await client.get(f"/instances/{inst_id}/chats/12345/messages")
    assert resp.status_code == 400
