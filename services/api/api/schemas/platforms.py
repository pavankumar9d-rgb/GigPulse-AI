"""Schemas for Platforms."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.common import PaginationMeta


class PlatformCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    display_name: str = Field(..., min_length=1, max_length=128)
    active: bool = True


class PlatformResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    display_name: str
    active: bool
    created_at: datetime


class PlatformListResponse(BaseModel):
    items: List[PlatformResponse]
    meta: PaginationMeta
