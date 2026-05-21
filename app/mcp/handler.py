import inspect
import time
from typing import Any, Callable, Optional

from app.core.error_codes import ErrorCodes
from app.core.response import error_tool, success_tool
from app.mcp.context import resolve_instance_id
from app.mcp.errors import mcp_error_from_telegram

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
    """Execute a handler with timing, error mapping, and standardized response.

    Usage inside an @mcp.tool():
        return await create_handler("send_message", lambda: _do_work())
    """
    start = time.monotonic()
    try:
        result = await fn() if inspect.iscoroutinefunction(fn) else fn()
        duration_ms = int((time.monotonic() - start) * 1000)
        return success_tool(tool_name, result, duration_ms)
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        err = mcp_error_from_telegram(e)
        mapped = CODE_MAP.get(err["code"], ErrorCodes.TELEGRAM_API_ERROR)
        retryable = err["code"] in RETRYABLE_CODES
        return error_tool(tool_name, mapped.value, err["message"], retryable=retryable)
