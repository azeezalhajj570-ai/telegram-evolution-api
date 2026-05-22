from typing import Any, Callable, Optional

from app.core.error_codes import ErrorCodes
from app.core.jwt import decode_token
from app.core.response import error_tool
from app.middleware.compose import RequestContext


async def jwt_auth_middleware(ctx: RequestContext, next_fn: Callable) -> Any:
    """Authenticate using JWT Bearer token.

    If no token is present or the token is invalid, ctx.userId stays as "anonymous".
    With a valid token, ctx.userId, ctx.instanceId (tenant_id), and error fallback are set.
    """
    token = _extract_token(ctx)
    if token:
        payload = decode_token(token)
        if payload:
            ctx.userId = payload.get("sub", "anonymous")
            ctx.instanceId = payload.get("tenant_id", ctx.instanceId)
            return await next_fn()
    return await next_fn()


def _extract_token(ctx: RequestContext) -> Optional[str]:
    """Extract Bearer token from ctx.input headers.

    For MCP tools, the input carries headers from the transport layer.
    For REST endpoints, the ASGI middleware sets ctx.input from the request.
    """
    if not ctx.input:
        return None
    headers = ctx.input if isinstance(ctx.input, dict) else {}
    auth = headers.get("Authorization", headers.get("authorization", ""))
    if auth.startswith("Bearer "):
        return auth[7:]
    return None
