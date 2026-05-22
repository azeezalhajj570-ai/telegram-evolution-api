import time
from typing import Any, Callable

from app.middleware.compose import RequestContext


async def response_middleware(ctx: RequestContext, next_fn: Callable) -> Any:
    result = await next_fn()
    duration_ms = int((time.monotonic() - ctx.startTime) * 1000)
    if result and hasattr(result, "metadata"):
        result.metadata.requestId = ctx.requestId
        result.metadata.durationMs = duration_ms
        if ctx.userId:
            result.metadata.tenantId = ctx.userId
    return result
