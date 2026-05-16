from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


def _connected_inst():
    inst = MagicMock()
    inst.id = __import__("uuid").uuid4()
    inst.status = "connected"
    inst.name = "Test"
    return inst


@pytest.mark.asyncio
async def test_list_contacts_not_connected(client: AsyncClient):
    inst = _connected_inst()
    inst.status = "pending"

    with patch("app.api.contacts_groups.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        resp = await client.get(f"/instances/{inst.id}/contacts")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_contacts_missing_instance(client: AsyncClient):
    with patch("app.api.contacts_groups.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = None
        MockRepo.return_value = mock_repo

        resp = await client.get("/instances/00000000-0000-0000-0000-000000000000/contacts")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_groups_not_connected(client: AsyncClient):
    inst = _connected_inst()
    inst.status = "pending"

    with patch("app.api.contacts_groups.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        resp = await client.get(f"/instances/{inst.id}/groups")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_join_channel_not_connected(client: AsyncClient):
    inst = _connected_inst()
    inst.status = "pending"

    with patch("app.api.contacts_groups.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        resp = await client.post(f"/instances/{inst.id}/channels/join", json={"username": "@test"})
    assert resp.status_code == 400
