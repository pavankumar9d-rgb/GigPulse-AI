"""Schemas for Worker Profiles."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.common import PaginationMeta


class WorkerProfileCreate(BaseModel):
    worker_ref: str = Field(..., min_length=1, max_length=64)
    display_name: Optional[str] = Field(default=None, max_length=128)
    home_zone_code: Optional[str] = Field(default=None, max_length=64)
    preferred_currency: str = Field(default="INR", min_length=3, max_length=3)


class WorkerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    worker_ref: str
    display_name: Optional[str]
    home_zone_code: Optional[str]
    preferred_currency: str
    created_at: datetime
    updated_at: datetime


class WorkerProfileListResponse(BaseModel):
    items: List[WorkerProfileResponse]
    meta: PaginationMeta
