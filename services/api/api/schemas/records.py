"""Schemas for work sessions, deliveries, expenses, and zone demand."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from api.schemas.common import PaginationMeta
from gigpulse_core.enums import (
    DeliveryStatus,
    ExpenseCategory,
    SessionStatus,
    SourceType,
    TargetQuality,
    TargetType,
)


# --- Work Sessions ---
class WorkSessionCreate(BaseModel):
    worker_ref: str = Field(..., min_length=1)
    platform_code: str = Field(..., min_length=1)
    started_at: datetime
    ended_at: datetime
    status: SessionStatus = SessionStatus.COMPLETED
    source_type: SourceType = SourceType.MANUAL
    timezone: str = "Asia/Kolkata"


class WorkSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    worker_ref: str
    platform_code: str
    started_at: datetime
    ended_at: datetime
    status: str
    source_type: str
    timezone: str
    import_batch_id: Optional[str]
    created_at: datetime


class WorkSessionListResponse(BaseModel):
    items: List[WorkSessionResponse]
    meta: PaginationMeta


# --- Deliveries ---
class DeliveryCreate(BaseModel):
    worker_ref: str = Field(..., min_length=1)
    platform_code: str = Field(..., min_length=1)
    session_ref: Optional[str] = None
    accepted_at: Optional[datetime] = None
    completed_at: datetime
    pickup_zone_code: Optional[str] = None
    drop_zone_code: Optional[str] = None
    payout_paise: int = Field(default=0, ge=0)
    incentive_paise: int = Field(default=0, ge=0)
    tip_paise: int = Field(default=0, ge=0)
    distance_m: Optional[int] = Field(default=None, ge=0)
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    status: DeliveryStatus = DeliveryStatus.COMPLETED
    target_quality: TargetQuality = TargetQuality.USER_REPORTED
    source_type: SourceType = SourceType.MANUAL


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    worker_ref: str
    platform_code: str
    session_ref: Optional[str]
    accepted_at: Optional[datetime]
    completed_at: datetime
    pickup_zone_code: Optional[str]
    drop_zone_code: Optional[str]
    payout_paise: int
    incentive_paise: int
    tip_paise: int
    gross_payout_paise: int = 0
    distance_m: Optional[int]
    duration_seconds: Optional[int]
    status: str
    target_quality: str
    source_type: str
    import_batch_id: Optional[str]
    created_at: datetime


class DeliveryListResponse(BaseModel):
    items: List[DeliveryResponse]
    meta: PaginationMeta


# --- Expenses ---
class ExpenseCreate(BaseModel):
    worker_ref: str = Field(..., min_length=1)
    session_ref: Optional[str] = None
    occurred_at: datetime
    category: ExpenseCategory = ExpenseCategory.OTHER
    amount_paise: int = Field(..., ge=0)
    source_type: SourceType = SourceType.MANUAL
    notes: Optional[str] = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    worker_ref: str
    session_ref: Optional[str]
    occurred_at: datetime
    category: str
    amount_paise: int
    source_type: str
    notes: Optional[str]
    import_batch_id: Optional[str]
    created_at: datetime


class ExpenseListResponse(BaseModel):
    items: List[ExpenseResponse]
    meta: PaginationMeta


# --- Zone Demand ---
class ZoneDemandCreate(BaseModel):
    zone_code: str = Field(..., min_length=1)
    interval_start: datetime
    interval_minutes: int = Field(default=30, gt=0)
    orders_requested: Optional[int] = Field(default=None, ge=0)
    orders_completed: Optional[int] = Field(default=None, ge=0)
    deliveries_observed: Optional[int] = Field(default=None, ge=0)
    demand_proxy_value: Optional[float] = Field(default=None, ge=0.0)
    target_type: TargetType = TargetType.DEMAND_PROXY
    coverage_fraction: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    target_quality: TargetQuality = TargetQuality.PROXY
    source_type: SourceType = SourceType.CSV_IMPORT


class ZoneDemandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zone_code: str
    interval_start: datetime
    interval_minutes: int
    orders_requested: Optional[int]
    orders_completed: Optional[int]
    deliveries_observed: Optional[int]
    demand_proxy_value: Optional[float]
    target_type: str
    coverage_fraction: Optional[float]
    target_quality: str
    source_type: str
    import_batch_id: Optional[str]
    created_at: datetime


class ZoneDemandListResponse(BaseModel):
    items: List[ZoneDemandResponse]
    meta: PaginationMeta
