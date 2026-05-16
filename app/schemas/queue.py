from typing import Optional

from pydantic import BaseModel, Field


class SendTextQueuedRequest(BaseModel):
    chat_id: int
    text: str = Field(..., min_length=1, max_length=4096)
    idempotency_key: Optional[str] = None


class JobQueuedResponse(BaseModel):
    job_id: str
    status: str = "queued"


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    type: str = ""
    attempt_count: int = 0
    message_id: Optional[int] = None
    error: Optional[str] = None
    created_at: Optional[float] = None
    updated_at: Optional[float] = None


class RateLimitResponse(BaseModel):
    remaining: int
    limit: int
    window_seconds: int
    is_paused: bool
    pause_remaining: int
    reset_at: float
