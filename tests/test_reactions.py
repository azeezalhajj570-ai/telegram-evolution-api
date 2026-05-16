from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_reaction(client: AsyncClient):
    inst = MagicMock()
    inst.id = __import__("uuid").uuid4()
    inst.status = "connected"

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_client.send_reaction = AsyncMock()
        mock_get.return_value = mock_client

        resp = await client.post(
            f"/instances/{inst.id}/messages/42/reaction?chat_id=123",
            json={"emoji": "👍"},
        )
    assert resp.status_code == 200
    assert resp.json()["reaction"] == "👍"


@pytest.mark.asyncio
async def test_remove_reaction(client: AsyncClient):
    inst = MagicMock()
    inst.id = __import__("uuid").uuid4()
    inst.status = "connected"

    with patch("app.api.messages.InstanceRepository") as MockRepo, \
         patch("app.services.messaging.client_manager.get_client") as mock_get:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        mock_client = AsyncMock()
        mock_client.is_connected.return_value = True
        mock_client.send_reaction = AsyncMock()
        mock_get.return_value = mock_client

        resp = await client.post(
            f"/instances/{inst.id}/messages/42/reaction?chat_id=123",
            json={"emoji": ""},
        )
    assert resp.status_code == 200
