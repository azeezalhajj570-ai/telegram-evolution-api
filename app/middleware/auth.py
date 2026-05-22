from typing import Any, Callable

from app.middleware.compose import RequestContext


async def auth_middleware(ctx: RequestContext, next_fn: Callable) -> Any:
    if not ctx.userId:
        ctx.userId = "anonymous"
    return await next_fn()
