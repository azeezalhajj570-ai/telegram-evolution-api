from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_organization(client: AsyncClient):
    resp = await client.post("/organizations", json={"name": "Test Org"})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Test Org"


@pytest.mark.asyncio
async def test_get_organization_not_found(client: AsyncClient):
    resp = await client.get("/organizations/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient):
    org_resp = await client.post("/organizations", json={"name": "Key Org"})
    org_id = org_resp.json()["id"]

    with patch("app.api.organizations.svc.create_api_key") as mock_create:
        mock_create.return_value = "tev_test_key_123"
        resp = await client.post(f"/organizations/{org_id}/api-keys", json={"name": "test-key", "scopes": ["messages:send"]})
    assert resp.status_code == 201
    assert resp.json()["key"] == "tev_test_key_123"


@pytest.mark.asyncio
async def test_delete_api_key_not_found(client: AsyncClient):
    resp = await client.delete("/organizations/00000000-0000-0000-0000-000000000000/api-keys/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_member(client: AsyncClient):
    org_resp = await client.post("/organizations", json={"name": "Member Org"})
    org_id = org_resp.json()["id"]

    with patch("app.api.organizations.svc.add_member") as mock_add:
        mock_add.return_value = {"id": "123", "user_id": "abc", "role": "viewer"}
        resp = await client.post(f"/organizations/{org_id}/members", json={"user_id": "00000000-0000-0000-0000-000000000002"})
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_get_usage(client: AsyncClient):
    org_resp = await client.post("/organizations", json={"name": "Usage Org"})
    org_id = org_resp.json()["id"]

    resp = await client.get(f"/organizations/{org_id}/usage")
    assert resp.status_code == 200
