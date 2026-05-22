import inspect
import time
from typing import Any, Callable, Optional

from app.core.error_codes import ErrorCodes
from app.core.response import error_tool, success_tool
from app.mcp.context import resolve_instance_id
from app.mcp.errors import mcp_error_from_telegram
from app.middleware.compose import compose, RequestContext
from app.middleware.request_context import request_context_middleware
from app.middleware.logging import logging_middleware
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.auth import auth_middleware
from app.middleware.response import response_middleware

CODE_MAP: dict[int, ErrorCodes] = {
    -32000: ErrorCodes.RATE_LIMIT_EXCEEDED,
    -32001: ErrorCodes.TELEGRAM_API_ERROR,
    -32002: ErrorCodes.NOT_FOUND,
    -32003: ErrorCodes.NOT_FOUND,
    -32004: ErrorCodes.AUTH_REQUIRED,
    -32005: ErrorCodes.INVALID_INPUT,
    -32006: ErrorCodes.AUTH_REQUIRED,
    -32007: ErrorCodes.AUTH_REQUIRED,
    -32008: ErrorCodes.AUTH_REQUIRED,
    -32602: ErrorCodes.INVALID_INPUT,
    -32603: ErrorCodes.INTERNAL_ERROR,
    -32099: ErrorCodes.TELEGRAM_API_ERROR,
}

RETRYABLE_CODES: set[int] = {-32000, -32001}

_PIPELINE = compose([
    request_context_middleware,
    logging_middleware,
    rate_limit_middleware(),
    auth_middleware,
    response_middleware,
])


def require_instance_id(instance_id: Optional[str]) -> str:
    """Resolve and validate instance ID from parameter, context, or scoped key."""
    resolved = resolve_instance_id(instance_id)
    if not resolved:
        raise ValueError(
            "Instance ID required — pass as a parameter, x-instance-id header, "
            "or use an instance-scoped API key"
        )
    return resolved


async def create_handler(tool_name: str, fn: Callable[[], Any]) -> Any:
    """Execute a handler through the middleware pipeline.

    Middleware order: requestContext → logging → rateLimit → auth → response → handler

    Usage inside an @mcp.tool():
        return await create_handler("send_message", lambda: _do_work())
    """
    ctx = RequestContext(tool=tool_name)
    try:
        return await _PIPELINE(ctx, lambda: _exec(tool_name, fn))
    except Exception as e:
        err = mcp_error_from_telegram(e)
        mapped = CODE_MAP.get(err["code"], ErrorCodes.TELEGRAM_API_ERROR)
        retryable = err["code"] in RETRYABLE_CODES
        return error_tool(tool_name, mapped.value, err["message"], retryable=retryable)


async def _exec(tool_name: str, fn: Callable[[], Any]) -> Any:
    """Execute the actual handler with timing and standardized response."""
    start = time.monotonic()
    try:
        result = fn()
        if inspect.isawaitable(result):
            result = await result
        duration_ms = int((time.monotonic() - start) * 1000)
        return success_tool(tool_name, result, duration_ms)
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        err = mcp_error_from_telegram(e)
        mapped = CODE_MAP.get(err["code"], ErrorCodes.TELEGRAM_API_ERROR)
        retryable = err["code"] in RETRYABLE_CODES
        return error_tool(tool_name, mapped.value, err["message"], retryable=retryable)
