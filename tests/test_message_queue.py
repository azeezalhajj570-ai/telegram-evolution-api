from unittest.mock import AsyncMock, patch

import pytest

from app.services.message_queue import enqueue, get_job


@pytest.mark.asyncio
async def test_enqueue_returns_job_id():
    with patch("app.services.message_queue.get_redis") as mock_get:
        mock_redis = AsyncMock()
        mock_redis.hset.return_value = None
        mock_redis.expire.return_value = None
        mock_redis.lpush.return_value = None
        mock_get.return_value = mock_redis

        job_id = await enqueue("inst-1", "send_text", {"chat_id": 1, "text": "hello"})
    assert job_id is not None
    assert len(job_id) > 10


@pytest.mark.asyncio
async def test_enqueue_with_idempotency_returns_same_id():
    with patch("app.services.message_queue.get_redis") as mock_get:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_redis.hset.return_value = None
        mock_redis.expire.return_value = None
        mock_redis.lpush.return_value = None
        mock_redis.setex.return_value = None
        mock_get.return_value = mock_redis

        job_id1 = await enqueue("inst-1", "send_text", {"chat_id": 1}, idempotency_key="key-1")
        mock_redis.get.return_value = job_id1
        job_id2 = await enqueue("inst-1", "send_text", {"chat_id": 1}, idempotency_key="key-1")
    assert job_id1 == job_id2


@pytest.mark.asyncio
async def test_get_job_returns_none_for_missing():
    with patch("app.services.message_queue.get_redis") as mock_get:
        mock_redis = AsyncMock()
        mock_redis.hgetall.return_value = None
        mock_get.return_value = mock_redis

        job = await get_job("nonexistent")
    assert job is None


@pytest.mark.asyncio
async def test_get_job_returns_job_data():
    with patch("app.services.message_queue.get_redis") as mock_get:
        mock_redis = AsyncMock()
        mock_redis.hgetall.return_value = {
            "job_id": "abc-123",
            "status": "queued",
            "type": "send_text",
            "attempt_count": "0",
        }
        mock_get.return_value = mock_redis

        job = await get_job("abc-123")
    assert job["status"] == "queued"
    assert job["job_id"] == "abc-123"
