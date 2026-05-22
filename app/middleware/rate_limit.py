import time
from typing import Any, Callable, Optional

from app.core.error_codes import ErrorCodes
from app.core.response import error_tool
from app.middleware.compose import RequestContext

WINDOW_MS = 60_000
MAX_REQUESTS = 100
_RATE_STORE: dict = {}
_LAST_CLEANUP = 0.0


def _cleanup():
    global _LAST_CLEANUP
    now = time.monotonic()
    if now - _LAST_CLEANUP < 60:
        return
    _LAST_CLEANUP = now
    cutoff = now * 1000
    for key in list(_RATE_STORE.keys()):
        if _RATE_STORE[key]["reset_at"] <= cutoff:
            del _RATE_STORE[key]


def rate_limit_middleware(max_requests: Optional[int] = None, window_ms: Optional[int] = None) -> Callable:
    max_r = max_requests or MAX_REQUESTS
    window = window_ms or WINDOW_MS

    async def middleware(ctx: RequestContext, next_fn: Callable) -> Any:
        _cleanup()
        key = ctx.userId or ctx.instanceId or "anonymous"
        now_ms = time.monotonic() * 1000
        entry = _RATE_STORE.get(key)
        if not entry or entry["reset_at"] <= now_ms:
            entry = {"count": 0, "reset_at": now_ms + window}
            _RATE_STORE[key] = entry
        entry["count"] += 1
        if entry["count"] > max_r:
            return error_tool(ctx.tool, ErrorCodes.RATE_LIMIT_EXCEEDED.value, "Rate limit exceeded", retryable=True)
        return await next_fn()

    return middleware
