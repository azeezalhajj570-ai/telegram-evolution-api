from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


def _connected_instance():
    inst = MagicMock()
    inst.id = uuid4()
    inst.status = "connected"
    return inst


@pytest.mark.asyncio
async def test_reply_success(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_result = MagicMock()
        mock_result.id = 200
        mock_client.send_message = AsyncMock(return_value=mock_result)
        mock_get.return_value = mock_client

        resp = await client.post(
            f"/instances/{inst.id}/messages/reply",
            json={"chat_id": 123, "text": "Reply text", "reply_to": 42},
        )
    assert resp.status_code == 200
    assert resp.json()["message_id"] == 200


@pytest.mark.asyncio
async def test_forward_success(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_result = MagicMock()
        mock_result.id = 300
        mock_client.forward_messages = AsyncMock(return_value=[mock_result])
        mock_get.return_value = mock_client

        resp = await client.post(
            f"/instances/{inst.id}/messages/forward",
            json={"from_chat_id": 1, "message_id": 42, "to_chat_id": 2},
        )
    assert resp.status_code == 200
    assert resp.json()["message_id"] == 300


@pytest.mark.asyncio
async def test_edit_success(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_result = MagicMock()
        mock_result.id = 42
        mock_client.edit_message = AsyncMock(return_value=mock_result)
        mock_get.return_value = mock_client

        resp = await client.patch(
            f"/instances/{inst.id}/messages/42?chat_id=123",
            json={"text": "Updated!"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "edited"


@pytest.mark.asyncio
async def test_delete_success(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_client.delete_messages = AsyncMock()
        mock_get.return_value = mock_client

        resp = await client.delete(f"/instances/{inst.id}/messages/42?chat_id=123")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_action_not_connected(client: AsyncClient):
    inst = _connected_instance()
    inst.status = "pending"

    with patch("app.api.messages.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        resp = await client.post(
            f"/instances/{inst.id}/messages/reply",
            json={"chat_id": 1, "text": "x", "reply_to": 1},
        )
    assert resp.status_code == 400
