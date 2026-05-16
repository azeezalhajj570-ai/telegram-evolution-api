import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_message_not_connected(client: AsyncClient):
    inst_resp = await client.post("/instances", json={"name": "Msg Test"})
    inst_id = inst_resp.json()["id"]
    resp = await client.post(f"/instances/{inst_id}/send-message",
                             json={"chat_id": 12345, "text": "Hello"})
    assert resp.status_code == 400
    assert "not connected" in resp.text


@pytest.mark.asyncio
async def test_send_message_missing_instance(client: AsyncClient):
    resp = await client.post("/instances/00000000-0000-0000-0000-000000000000/send-message",
                             json={"chat_id": 12345, "text": "Hello"})
    assert resp.status_code == 404
