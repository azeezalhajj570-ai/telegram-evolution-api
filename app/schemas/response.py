from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class Metadata(BaseModel):
    requestId: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    durationMs: Optional[int] = None
    tool: str = ""
    version: str = "0.2.0"
    tenantId: str = ""


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    metadata: Metadata


class ErrorResponse(BaseModel):
    success: bool = False
    code: str
    message: str
    retryable: bool = False
    details: Any = None
    metadata: Metadata
