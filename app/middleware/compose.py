import inspect
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional


@dataclass
class RequestContext:
    requestId: str = ""
    startTime: float = 0.0
    tool: str = ""
    userId: str = ""
    instanceId: str = ""
    input: Any = None
    response: Any = None
    error: Any = None


def compose(middlewares: list) -> Callable:
    """Create a middleware runner from a list of middleware functions.

    Usage:
        pipeline = compose([mw1, mw2, mw3])
        result = await pipeline(ctx, handler)
    """
    async def run(ctx: RequestContext, handler: Callable[[], Awaitable[Any]]) -> Any:
        index = -1

        async def dispatch(i: int) -> Any:
            nonlocal index
            if i <= index:
                raise RuntimeError("next() called multiple times")
            index = i
            if i >= len(middlewares):
                result = handler()
                if inspect.isawaitable(result):
                    return await result
                return result
            return await middlewares[i](ctx, lambda: dispatch(i + 1))

        return await dispatch(0)

    return run
