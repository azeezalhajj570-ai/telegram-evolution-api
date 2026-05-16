import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.time()

        response = await call_next(request)

        duration = (time.time() - start) * 1000
        logger.info(
            "request_id=%s method=%s path=%s status=%d duration_ms=%.1f",
            request_id, request.method, request.url.path, response.status_code, duration,
        )
        response.headers["X-Request-ID"] = request_id
        return response
