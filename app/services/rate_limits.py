import time
from typing import Optional

from redis.asyncio import Redis

from app.config import settings

_redis: Optional[Redis] = None

INSTANCE_MAX = 20
INSTANCE_WINDOW = 60
USER_MAX = 100
USER_WINDOW = 60


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = await Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def check_rate_limit(instance_id: str, user_id: str = "default") -> tuple[bool, int]:
    r = await get_redis()
    now = time.time()

    allowed, retry_after = await _check_window(r, f"ratelimit:instance:{instance_id}", now, INSTANCE_MAX, INSTANCE_WINDOW)
    if not allowed:
        return False, retry_after

    allowed, retry_after = await _check_window(r, f"ratelimit:user:{user_id}", now, USER_MAX, USER_WINDOW)
    if not allowed:
        return False, retry_after

    return True, 0


async def _check_window(r: Redis, key: str, now: float, max_reqs: int, window: int) -> tuple[bool, int]:
    window_start = now - window
    await r.zremrangebyscore(key, 0, window_start)
    count = await r.zcard(key)

    if count >= max_reqs:
        oldest = await r.zrange(key, 0, 0, withscores=True)
        retry_after = int(window - (now - oldest[0][1])) + 1 if oldest else window
        return False, retry_after

    await r.zadd(key, {str(now): now})
    await r.expire(key, window)
    return True, 0


async def get_rate_limit_status(instance_id: str, user_id: str = "default") -> dict:
    r = await get_redis()
    now = time.time()
    ws = now - INSTANCE_WINDOW
    await r.zremrangebyscore(f"ratelimit:instance:{instance_id}", 0, ws)
    remaining = max(0, INSTANCE_MAX - await r.zcard(f"ratelimit:instance:{instance_id}"))

    from app.services.message_queue import get_pause_remaining, is_paused
    paused = await is_paused(instance_id)
    pause_remaining = await get_pause_remaining(instance_id)

    return {
        "remaining": remaining,
        "limit": INSTANCE_MAX,
        "window_seconds": INSTANCE_WINDOW,
        "is_paused": paused,
        "pause_remaining": pause_remaining,
        "reset_at": now + INSTANCE_WINDOW,
    }
