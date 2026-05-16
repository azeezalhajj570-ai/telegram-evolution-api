import asyncio
import json
import logging

from telethon.errors import FloodWaitError

from app.db.repositories import InstanceRepository
from app.services.message_queue import (
    dead_letter,
    dequeue,
    is_paused,
    set_flood_wait,
    update_job,
)
from app.services.messaging import send_message as svc_send_message
from app.services.rate_limits import check_rate_limit as check_ratelimit

logger = logging.getLogger(__name__)


async def process_instance(instance_id: str):
    while True:
        paused = await is_paused(instance_id)
        if paused:
            return

        allowed, _ = await check_ratelimit(instance_id)
        if not allowed:
            return

        job = await dequeue(instance_id)
        if not job:
            return

        job_id = job.get("job_id", "")
        await update_job(job_id, status="processing")

        payload = json.loads(job.get("payload", "{}"))
        chat_id = payload.get("chat_id")
        text = payload.get("text", "")

        try:
            result = await svc_send_message(__import__("uuid").UUID(instance_id), chat_id, text)
            await update_job(job_id, status="delivered", message_id=result.get("message_id", 0))
            logger.info("Job %s delivered to chat %s", job_id, chat_id)
        except FloodWaitError as e:
            await set_flood_wait(instance_id, e.seconds)
            await update_job(job_id, status="queued")
            await _requeue(instance_id, job_id)
            logger.warning("FloodWait %ss for instance %s, job %s requeued", e.seconds, instance_id, job_id)
            return
        except ValueError as e:
            attempt = int(job.get("attempt_count", 0)) + 1
            max_retries = int(job.get("max_retries", 3))
            await update_job(job_id, status="queued" if attempt < max_retries else "failed",
                             attempt_count=attempt, error=str(e))
            if attempt >= max_retries:
                await dead_letter(instance_id, job_id)
                logger.warning("Job %s failed after %d attempts, moved to dead-letter", job_id, attempt)
            else:
                await _requeue(instance_id, job_id)
                logger.info("Job %s failed (attempt %d/%d), requeued", job_id, attempt, max_retries)


async def _requeue(instance_id: str, job_id: str):
    from app.services.message_queue import get_redis
    r = await get_redis()
    await r.lpush(f"queue:{instance_id}", job_id)


async def run_worker_loop(interval: float = 2.0):
    from app.db.database import async_session

    while True:
        try:
            async with async_session() as db:
                repo = InstanceRepository(db)
                instances = await repo.get_all()
                for inst in instances:
                    await process_instance(str(inst.id))
                await db.commit()
        except Exception as e:
            logger.error("Worker error: %s", e)
        await asyncio.sleep(interval)
