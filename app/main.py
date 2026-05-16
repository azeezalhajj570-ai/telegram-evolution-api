import asyncio
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import generate_latest

from app.api import admin, auth, chats, instances, messages, webhooks
from app.config import settings
from app.db.database import Base, async_session, engine
from app.db.repositories import InstanceRepository
from app.metrics import ACTIVE_CLIENTS
from app.middleware import RequestLogMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_start_time = time.time()


async def _reconnect_instances():
    async with async_session() as db:
        repo = InstanceRepository(db)
        connected = await repo.get_by_status("connected")
        for inst in connected:
            if inst.session_encrypted:
                try:
                    from app.services.telegram_manager import client_manager
                    await client_manager.start_client(str(inst.id), inst.session_encrypted)
                    logger.info("Reconnected instance %s on startup", inst.id)
                except Exception as e:
                    await repo.update(inst.id, status="auth_required")
                    logger.warning("Failed to reconnect instance %s: %s", inst.id, e)
        await db.commit()


_worker_task = None
_msg_worker = None


async def _update_metrics():
    from app.services.telegram_manager import client_manager
    connected = client_manager.get_connected_ids()
    ACTIVE_CLIENTS.set(len(connected))


async def lifespan(app: FastAPI):
    global _worker_task, _msg_worker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.api_keys:
        async with async_session() as db:
            from app.db.models import ApiKey
            from app.security.api_keys import hash_api_key
            from sqlalchemy import select

            for raw_key in settings.api_keys_list:
                result = await db.execute(select(ApiKey).where(ApiKey.name == f"auto:{raw_key[:8]}"))
                if not result.scalar_one_or_none():
                    db.add(ApiKey(
                        name=f"auto:{raw_key[:8]}",
                        key_hash=hash_api_key(raw_key),
                        is_active=True,
                    ))
            await db.commit()

    await _reconnect_instances()
    await _update_metrics()

    from app.workers.message_worker import run_worker_loop as run_msg_worker
    _msg_worker = asyncio.create_task(run_msg_worker(interval=2.0))
    logger.info("Message queue worker started")

    from app.workers.webhook_worker import run_worker_loop as run_wh_worker
    _worker_task = asyncio.create_task(run_wh_worker(interval=60))
    logger.info("Webhook retry worker started")

    yield

    for t in (_msg_worker, _worker_task):
        if t:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
    from app.services.telegram_manager import client_manager
    await _update_metrics()
    await client_manager.stop_all()


app = FastAPI(
    title="Telegram API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLogMiddleware)

app.include_router(instances.router)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(chats.router)
app.include_router(webhooks.router)
app.include_router(admin.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred"},
    )


@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    try:
        from app.services.message_queue import get_redis
        r = await get_redis()
        await r.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    status = "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy"
    return {
        "status": status,
        "version": "0.1.0",
        "uptime_seconds": int(time.time() - _start_time),
        "db": db_status,
        "redis": redis_status,
    }


@app.get("/ready")
async def ready():
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    try:
        from app.services.message_queue import get_redis
        r = await get_redis()
        await r.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    status = "ready" if db_status == "connected" and redis_status == "connected" else "not_ready"
    code = 200 if status == "ready" else 503
    return JSONResponse(
        status_code=code,
        content={"status": status, "db": db_status, "redis": redis_status},
    )


@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest())
