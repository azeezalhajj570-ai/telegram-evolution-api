import asyncio
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import auth, chats, instances, messages, organizations, webhooks
from app.config import settings
from app.core.response import rest_error, rest_success
from app.core.error_codes import ErrorCodes
from app.db.database import Base, async_session, engine
from app.db.repositories import InstanceRepository
from app.middleware.asgi import RequestContextMiddleware

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


async def lifespan(app: FastAPI):
    global _worker_task

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
                    db.add(ApiKey(name=f"auto:{raw_key[:8]}", key_hash=hash_api_key(raw_key), is_active=True))
            await db.commit()

    await _reconnect_instances()

    from app.workers.webhook_worker import run_worker_loop
    _worker_task = asyncio.create_task(run_worker_loop(interval=60))
    logger.info("Webhook retry worker started")

    yield

    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    from app.services.telegram_manager import client_manager
    await client_manager.stop_all()


app = FastAPI(
    title="RelayStack API",
    description="Self-hosted messaging automation API. Current provider: Telegram via MTProto.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)

app.include_router(instances.router)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(chats.router)
app.include_router(webhooks.router)
app.include_router(organizations.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    err = rest_error("", ErrorCodes.INTERNAL_ERROR.value, "An unexpected error occurred")
    return JSONResponse(status_code=500, content=err)


@app.get("/health")
async def health():
    return rest_success({
        "status": "healthy",
        "version": "0.1.0",
        "uptime_seconds": int(time.time() - _start_time),
    }, "health")
