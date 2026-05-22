import pytest
from httpx import AsyncClient


def _d(resp):
    return resp.json()["data"]


@pytest.mark.asyncio
async def test_create_instance(client: AsyncClient):
    resp = await client.post("/instances", json={"name": "Test Instance"})
    assert resp.status_code == 201
    data = _d(resp)
    assert data["name"] == "Test Instance"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_instances(client: AsyncClient):
    await client.post("/instances", json={"name": "Instance 1"})
    await client.post("/instances", json={"name": "Instance 2"})
    resp = await client.get("/instances")
    assert resp.status_code == 200
    data = _d(resp)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_instance(client: AsyncClient):
    create_resp = await client.post("/instances", json={"name": "My Instance"})
    inst_id = _d(create_resp)["id"]
    resp = await client.get(f"/instances/{inst_id}")
    assert resp.status_code == 200
    assert _d(resp)["name"] == "My Instance"


@pytest.mark.asyncio
async def test_get_instance_not_found(client: AsyncClient):
    resp = await client.get("/instances/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_instance(client: AsyncClient):
    create_resp = await client.post("/instances", json={"name": "To Delete"})
    inst_id = _d(create_resp)["id"]
    resp = await client.delete(f"/instances/{inst_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/instances/{inst_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_instance_status(client: AsyncClient):
    create_resp = await client.post("/instances", json={"name": "Status Check"})
    inst_id = _d(create_resp)["id"]
    resp = await client.get(f"/instances/{inst_id}/status")
    assert resp.status_code == 200
    assert _d(resp)["has_webhook"] is False
