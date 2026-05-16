from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class WebhookCreateRequest(BaseModel):
    url: AnyHttpUrl


class WebhookResponse(BaseModel):
    id: str
    url: str
    is_active: bool
    max_retries: int
    secret: str = "****"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WebhookTestResponse(BaseModel):
    status: str
    status_code: Optional[int] = None
