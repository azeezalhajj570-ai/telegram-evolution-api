import json
import logging
import urllib.parse

from app.mcp.auth import authenticate_sse, resolve_instance_key
from app.mcp.context import set_current_instance
from app.mcp.server import mcp_app

logger = logging.getLogger(__name__)


async def send_health(send):
    body = json.dumps({"status": "healthy", "transport": "sse"}).encode()
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({"type": "http.response.body", "body": body})


async def send_json(send, status: int, data: dict):
    body = json.dumps(data).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({"type": "http.response.body", "body": body})


def _build_auth_wrapped_sse():
    inner = mcp_app.sse_app()

    async def auth_wrapper(scope, receive, send):
        if scope["type"] != "http":
            await inner(scope, receive, send)
            return

        path = scope.get("path", "")
        if path == "/health":
            return await send_health(send)

        method = scope.get("method", "GET")
        is_message = path.startswith("/messages/") and method in ("POST", "OPTIONS")

        if is_message:
            return await inner(scope, receive, send)

        headers = dict(scope.get("headers", []))
        api_key = (
            headers.get(b"x-api-key", b"").decode()
            or headers.get(b"authorization", b"").decode().removeprefix("Bearer ")
        )
        if not api_key:
            params = urllib.parse.parse_qs(scope.get("query_string", b"").decode())
            api_key = params.get("api_key", [None])[0]

        if not api_key or not await authenticate_sse(api_key):
            client_addr = scope.get("client")
            client_host = client_addr[0] if client_addr else "unknown"
            logger.warning("MCP SSE auth rejected for %s from %s", path, client_host)
            return await send_json(send, 401, {"error": "unauthorized", "detail": "Invalid or missing API key"})

        instance_id = (
            headers.get(b"x-instance-id", b"").decode()
            or headers.get(b"instance-id", b"").decode()
        )
        if not instance_id:
            instance_id = await resolve_instance_key(api_key)
        if instance_id:
            set_current_instance(instance_id)

        await inner(scope, receive, send)

    return auth_wrapper


sse_app = _build_auth_wrapped_sse()
