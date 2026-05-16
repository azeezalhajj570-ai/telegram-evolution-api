from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


def _connected_instance():
    inst = MagicMock()
    inst.id = __import__("uuid").uuid4()
    inst.status = "connected"
    inst.name = "Test"
    inst.phone_number = "+123"
    inst.session_encrypted = "encrypted:data"
    return inst


@pytest.mark.asyncio
async def test_health_returns_json(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code in (200, 503)
    assert "status" in resp.json()


@pytest.mark.asyncio
async def test_ready_returns_json(client: AsyncClient):
    resp = await client.get("/ready")
    assert resp.status_code in (200, 503)


@pytest.mark.asyncio
async def test_metrics_returns_prometheus(client: AsyncClient):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_admin_diagnostics(client: AsyncClient):
    inst = _connected_instance()

    with patch("app.api.admin.InstanceRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get.return_value = inst
        MockRepo.return_value = mock_repo

        resp = await client.get(f"/admin/instances/{inst.id}/diagnostics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["instance_id"] == str(inst.id)
        assert data["status"] == "connected"
