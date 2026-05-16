from unittest.mock import AsyncMock, patch

import pytest

from app.services.rate_limits import check_rate_limit


@pytest.mark.asyncio
async def test_check_rate_limit_allows():
    mock_redis = AsyncMock()
    mock_redis.zremrangebyscore.return_value = 0
    mock_redis.zcard.return_value = 0
    mock_redis.zadd.return_value = 1
    mock_redis.expire.return_value = True

    with patch("app.services.rate_limits.get_redis", AsyncMock(return_value=mock_redis)):
        allowed, retry_after = await check_rate_limit("inst-1")
    assert allowed is True
    assert retry_after == 0


@pytest.mark.asyncio
async def test_check_rate_limit_blocks():
    mock_redis = AsyncMock()
    mock_redis.zremrangebyscore.return_value = 0
    mock_redis.zcard.return_value = 25
    mock_redis.zrange.return_value = [("1", 100.0)]
    mock_redis.ttl.return_value = 30

    with patch("app.services.rate_limits.get_redis", AsyncMock(return_value=mock_redis)):
        allowed, retry_after = await check_rate_limit("inst-1")
    assert allowed is False
    assert isinstance(retry_after, int)
