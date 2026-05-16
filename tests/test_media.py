import io
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


def _connected_instance():
    inst = MagicMock()
    inst.id = uuid4()
    inst.status = "connected"
    inst.name = "Test"
    inst.phone_number = "+123"
    return inst


@pytest.mark.asyncio
async def test_send_photo_success(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_result = MagicMock()
        mock_result.id = 100
        mock_client.send_file = AsyncMock(return_value=mock_result)
        mock_get.return_value = mock_client

        resp = await client.post(
            f"/instances/{inst.id}/messages/send-photo",
            data={"chat_id": "12345", "caption": "test"},
            files={"file": ("test.jpg", io.BytesIO(b"fake-image-data"), "image/jpeg")},
        )
    assert resp.status_code == 200
    assert resp.json()["message_id"] == 100
    assert resp.json()["type"] == "photo"


@pytest.mark.asyncio
async def test_send_media_file_too_large(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_get.return_value = mock_client

        large_data = b"x" * (51 * 1024 * 1024)
        resp = await client.post(
            f"/instances/{inst.id}/messages/send-photo",
            data={"chat_id": "12345"},
            files={"file": ("big.jpg", io.BytesIO(large_data), "image/jpeg")},
        )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_send_media_not_connected(client: AsyncClient):
    inst = _connected_instance()
    inst.status = "pending"

    with patch("app.api.messages.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        resp = await client.post(
            f"/instances/{inst.id}/messages/send-photo",
            data={"chat_id": "12345"},
            files={"file": ("test.jpg", b"data", "image/jpeg")},
        )
    assert resp.status_code == 400
