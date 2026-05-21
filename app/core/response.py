from typing import Any, Optional

from app.schemas.response import ErrorResponse, Metadata, SuccessResponse

VERSION = "0.2.0"


def _metadata(tool: str = "", tenant_id: str = "") -> Metadata:
    return Metadata(tool=tool, version=VERSION, tenantId=tenant_id)


def success_tool(tool: str, data: Any, duration_ms: Optional[int] = None, tenant_id: str = "") -> SuccessResponse:
    m = _metadata(tool, tenant_id)
    if duration_ms is not None:
        m.durationMs = duration_ms
    return SuccessResponse(data=data, metadata=m)


def error_tool(
    tool: str,
    code: str,
    message: str,
    retryable: bool = False,
    details: Any = None,
    tenant_id: str = "",
) -> ErrorResponse:
    return ErrorResponse(
        code=code,
        message=message,
        retryable=retryable,
        details=details,
        metadata=_metadata(tool, tenant_id),
    )
