import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_instance(client: AsyncClient):
    resp = await client.post("/instances", json={"name": "Test Instance"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Instance"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_instances(client: AsyncClient):
    await client.post("/instances", json={"name": "Instance 1"})
    await client.post("/instances", json={"name": "Instance 2"})
    resp = await client.get("/instances")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["instances"]) == 2


@pytest.mark.asyncio
async def test_get_instance(client: AsyncClient):
    create_resp = await client.post("/instances", json={"name": "My Instance"})
    inst_id = create_resp.json()["id"]
    resp = await client.get(f"/instances/{inst_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Instance"


@pytest.mark.asyncio
async def test_get_instance_not_found(client: AsyncClient):
    resp = await client.get("/instances/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_instance(client: AsyncClient):
    create_resp = await client.post("/instances", json={"name": "To Delete"})
    inst_id = create_resp.json()["id"]
    resp = await client.delete(f"/instances/{inst_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/instances/{inst_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_instance_status(client: AsyncClient):
    create_resp = await client.post("/instances", json={"name": "Status Check"})
    inst_id = create_resp.json()["id"]
    resp = await client.get(f"/instances/{inst_id}/status")
    assert resp.status_code == 200
    assert resp.json()["has_webhook"] is False
