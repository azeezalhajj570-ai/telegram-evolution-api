import json
import logging
import uuid
from typing import Optional

from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)

JOB_TTL = 7 * 86400
IDEMPOTENCY_TTL = 86400

_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = await Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def enqueue(instance_id: str, job_type: str, payload: dict, idempotency_key: Optional[str] = None) -> str:
    r = await get_redis()
    job_id = str(uuid.uuid4())

    if idempotency_key:
        existing = await r.get(f"idempotency:{idempotency_key}")
        if existing:
            return existing

    job = {
        "job_id": job_id,
        "status": "queued",
        "instance_id": instance_id,
        "type": job_type,
        "payload": json.dumps(payload),
        "idempotency_key": idempotency_key or "",
        "attempt_count": 0,
        "max_retries": 3,
        "error": "",
        "message_id": 0,
        "created_at": __import__("time").time(),
        "updated_at": __import__("time").time(),
    }
    await r.hset(f"job:{job_id}", mapping=job)
    await r.expire(f"job:{job_id}", JOB_TTL)
    await r.lpush(f"queue:{instance_id}", job_id)

    if idempotency_key:
        await r.setex(f"idempotency:{idempotency_key}", IDEMPOTENCY_TTL, job_id)

    logger.info("Enqueued job %s for instance %s", job_id, instance_id)
    return job_id


async def dequeue(instance_id: str) -> Optional[dict]:
    r = await get_redis()
    result = await r.brpop(f"queue:{instance_id}", timeout=5)
    if not result:
        return None
    job_id = result[1]
    job = await r.hgetall(f"job:{job_id}")
    if not job:
        return None
    return job


async def get_job(job_id: str) -> Optional[dict]:
    r = await get_redis()
    return await r.hgetall(f"job:{job_id}")


async def update_job(job_id: str, **fields):
    r = await get_redis()
    fields["updated_at"] = __import__("time").time()
    await r.hset(f"job:{job_id}", mapping=fields)


async def set_flood_wait(instance_id: str, seconds: int):
    r = await get_redis()
    await r.setex(f"flood_wait:{instance_id}", seconds, "1")


async def is_paused(instance_id: str) -> bool:
    r = await get_redis()
    return await r.exists(f"flood_wait:{instance_id}")


async def get_pause_remaining(instance_id: str) -> int:
    r = await get_redis()
    ttl = await r.ttl(f"flood_wait:{instance_id}")
    return max(0, ttl)


async def dead_letter(instance_id: str, job_id: str):
    r = await get_redis()
    await r.lpush(f"queue:dead_letter:{instance_id}", job_id)
    await update_job(job_id, status="dead_letter")
    await r.expire(f"queue:dead_letter:{instance_id}", JOB_TTL)
