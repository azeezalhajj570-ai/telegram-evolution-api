import json
import logging
import time
from typing import Any, Callable

from app.middleware.compose import RequestContext

logger = logging.getLogger(__name__)


async def logging_middleware(ctx: RequestContext, next_fn: Callable) -> Any:
    result = await next_fn()
    duration_ms = int((time.monotonic() - ctx.startTime) * 1000)
    is_error = getattr(result, "success", True) is False
    entry = {"requestId": ctx.requestId, "tool": ctx.tool, "durationMs": duration_ms, "success": not is_error}
    if is_error:
        logger.error(json.dumps(entry))
    else:
        logger.info(json.dumps(entry))
    return result
