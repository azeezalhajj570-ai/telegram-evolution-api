import time
from typing import Optional

from redis.asyncio import Redis

from app.config import settings

_rate_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    global _rate_redis
    if _rate_redis is None:
        _rate_redis = await Redis.from_url(settings.redis_url, decode_responses=True)
    return _rate_redis


async def check_rate_limit(instance_id: str, max_requests: int = 5, window_seconds: int = 60) -> tuple[bool, int]:
    r = await get_redis()
    key = f"ratelimit:{instance_id}"
    now = time.time()
    window_start = now - window_seconds

    await r.zremrangebyscore(key, 0, window_start)
    count = await r.zcard(key)

    if count >= max_requests:
        oldest = await r.zrange(key, 0, 0, withscores=True)
        retry_after = int(window_seconds - (now - oldest[0][1])) + 1 if oldest else 0
        return False, retry_after

    await r.zadd(key, {str(now): now})
    await r.expire(key, window_seconds)
    return True, 0
