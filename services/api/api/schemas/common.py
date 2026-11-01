"""Common schemas for pagination, health, and metadata."""

from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    count: int = Field(..., ge=0)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    project: str = "GigPulse AI"
    database_status: str = "connected"
    synthetic_mode: bool = True
    server_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

