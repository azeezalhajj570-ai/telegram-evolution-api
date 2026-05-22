import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.middleware.compose import RequestContext


class RequestContextMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that injects requestId and timing into every FastAPI request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid4())
        start = time.monotonic()
        try:
            response = await call_next(request)
            duration_ms = int((time.monotonic() - start) * 1000)
            response.headers["X-Request-Id"] = request_id
            response.headers["X-Duration-Ms"] = str(duration_ms)
            return response
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            return JSONResponse(
                status_code=500,
                content={"success": False, "code": "INTERNAL_ERROR", "message": str(e), "metadata": {"requestId": request_id, "durationMs": duration_ms}},
            )
