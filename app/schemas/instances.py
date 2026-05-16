from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class InstanceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)


class InstanceResponse(BaseModel):
    id: str
    name: str
    phone_number: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InstanceStatusResponse(InstanceResponse):
    has_webhook: bool = False


class InstanceListResponse(BaseModel):
    instances: List[InstanceResponse]
