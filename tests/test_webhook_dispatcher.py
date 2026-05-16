import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import WebhookDelivery
from app.db.repositories import InstanceRepository, WebhookRepository
from app.services.webhook_dispatcher import dispatch

from tests.conftest import _test_engine

_test_session = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_dispatch_posts_to_correct_url_with_signature():
    async with _test_session() as db:
        inst_repo = InstanceRepository(db)
        inst = await inst_repo.create("Test")
        wh_repo = WebhookRepository(db)
        await wh_repo.create(inst.id, "https://example.com/wh", "test-secret-123")
        await db.commit()

    event_data = {"message_id": 42, "chat_id": 123, "chat_title": "C", "sender_id": 1, "sender_name": "T", "text": "Hello", "date": "2026-01-01T00:00:00Z"}

    mock_post = AsyncMock()
    mock_post.is_success = True
    mock_post.status_code = 200

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_post) as mock:
        async with _test_session() as db:
            wh_repo = WebhookRepository(db)
            await dispatch(str(inst.id), "message", event_data, wh_repo)
            await db.commit()

    mock.assert_called_once()
    args, kwargs = mock.call_args
    assert args[0] == "https://example.com/wh"
    assert "X-Signature-256" in kwargs["headers"]
    assert kwargs["headers"]["Content-Type"] == "application/json"

    sent_body = json.loads(kwargs["content"])
    assert sent_body["event"] == "message"
    assert sent_body["instance_id"] == str(inst.id)
    assert sent_body["payload"]["text"] == "Hello"


@pytest.mark.asyncio
async def test_successful_delivery_records_delivered():
    async with _test_session() as db:
        inst_repo = InstanceRepository(db)
        inst = await inst_repo.create("Test")
        wh_repo = WebhookRepository(db)
        wh = await wh_repo.create(inst.id, "https://example.com/wh", "secret")
        await db.commit()

    event_data = {"message_id": 1, "text": "ok"}
    mock_post = AsyncMock()
    mock_post.is_success = True
    mock_post.status_code = 200

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_post):
        async with _test_session() as db:
            wh_repo = WebhookRepository(db)
            await dispatch(str(inst.id), "message", event_data, wh_repo)
            await db.commit()

    async with _test_session() as db:
        result = await db.execute(select(WebhookDelivery))
        deliveries = result.scalars().all()
    assert len(deliveries) == 1
    assert deliveries[0].status == "delivered"
    assert deliveries[0].event_type == "message"
    assert deliveries[0].last_status_code == 200


@pytest.mark.asyncio
async def test_failed_delivery_leaves_pending():
    async with _test_session() as db:
        inst_repo = InstanceRepository(db)
        inst = await inst_repo.create("Test")
        wh_repo = WebhookRepository(db)
        wh = await wh_repo.create(inst.id, "https://example.com/fail", "secret")
        await db.commit()

    event_data = {"message_id": 1, "text": "fail"}
    mock_post = AsyncMock()
    mock_post.is_success = False
    mock_post.status_code = 500

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_post):
        async with _test_session() as db:
            wh_repo = WebhookRepository(db)
            await dispatch(str(inst.id), "message", event_data, wh_repo)
            await db.commit()

    async with _test_session() as db:
        result = await db.execute(select(WebhookDelivery))
        deliveries = result.scalars().all()
    assert len(deliveries) == 1
    assert deliveries[0].status == "pending"
    assert deliveries[0].last_status_code is None


@pytest.mark.asyncio
async def test_dispatch_request_error_leaves_pending():
    async with _test_session() as db:
        inst_repo = InstanceRepository(db)
        inst = await inst_repo.create("Test")
        wh_repo = WebhookRepository(db)
        await wh_repo.create(inst.id, "https://example.com/err", "secret")
        await db.commit()

    event_data = {"message_id": 1, "text": "err"}

    with patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("connection refused")):
        async with _test_session() as db:
            wh_repo = WebhookRepository(db)
            await dispatch(str(inst.id), "message", event_data, wh_repo)
            await db.commit()

    async with _test_session() as db:
        result = await db.execute(select(WebhookDelivery))
        deliveries = result.scalars().all()
    assert len(deliveries) == 1
    assert deliveries[0].status == "pending"


@pytest.mark.asyncio
async def test_dispatch_noop_when_no_webhook():
    async with _test_session() as db:
        inst_repo = InstanceRepository(db)
        inst = await inst_repo.create("Test")
        await db.commit()

    mock_post = AsyncMock()
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_post) as mock:
        async with _test_session() as db:
            wh_repo = WebhookRepository(db)
            await dispatch(str(inst.id), "message", {}, wh_repo)
            await db.commit()

    mock.assert_not_called()
