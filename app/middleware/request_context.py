import time
from typing import Any, Callable
from uuid import uuid4

from app.middleware.compose import RequestContext


async def request_context_middleware(ctx: RequestContext, next_fn: Callable) -> Any:
    ctx.requestId = str(uuid4())
    ctx.startTime = time.monotonic()
    return await next_fn()
