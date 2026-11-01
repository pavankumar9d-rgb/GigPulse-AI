"""Schemas for Zones."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.common import PaginationMeta


class ZoneCreate(BaseModel):
    zone_code: str = Field(..., min_length=1, max_length=64)
    zone_system: str = Field(default="study_area", max_length=32)
    resolution: Optional[int] = None
    display_name: Optional[str] = Field(default=None, max_length=128)
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None
    boundary_ref: Optional[str] = None


class ZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zone_system: str
    zone_code: str
    resolution: Optional[int]
    display_name: Optional[str]
    centroid_lat: Optional[float]
    centroid_lon: Optional[float]
    boundary_ref: Optional[str]
    created_at: datetime


class ZoneListResponse(BaseModel):
    items: List[ZoneResponse]
    meta: PaginationMeta
