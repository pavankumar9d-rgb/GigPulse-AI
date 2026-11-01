"""Pydantic domain models for GigPulse AI records and templates."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from gigpulse_core.enums import (
    DeliveryStatus,
    ExpenseCategory,
    SessionStatus,
    SourceType,
    TargetQuality,
    TargetType,
)
from gigpulse_core.money import validate_non_negative_paise


class WorkSessionRecord(BaseModel):
    """Corresponds to data/templates/work_sessions_template.csv."""
    worker_ref: str = Field(..., min_length=1)
    platform_code: str = Field(..., min_length=1)
    started_at: datetime
    ended_at: datetime
    status: SessionStatus = SessionStatus.COMPLETED
    source_type: SourceType = SourceType.MANUAL
    timezone: str = "Asia/Kolkata"

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.ended_at < self.started_at:
            raise ValueError(f"ended_at ({self.ended_at}) must be >= started_at ({self.started_at})")
        return self


class DeliveryRecord(BaseModel):
    """Corresponds to data/templates/deliveries_template.csv."""
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

    @model_validator(mode="after")
    def validate_accepted_before_completed(self):
        if self.accepted_at and self.completed_at and self.completed_at < self.accepted_at:
            raise ValueError(f"completed_at ({self.completed_at}) cannot precede accepted_at ({self.accepted_at})")
        return self

    @property
    def gross_payout_paise(self) -> int:
        return self.payout_paise + self.incentive_paise + self.tip_paise


class ExpenseRecord(BaseModel):
    """Corresponds to data/templates/expenses_template.csv."""
    worker_ref: str = Field(..., min_length=1)
    session_ref: Optional[str] = None
    occurred_at: datetime
    category: ExpenseCategory = ExpenseCategory.OTHER
    amount_paise: int = Field(..., ge=0)
    source_type: SourceType = SourceType.MANUAL
    notes: Optional[str] = None


class ZoneDemandRecord(BaseModel):
    """Corresponds to data/templates/zone_demand_template.csv.
    
    CRITICAL: Preserves strict distinction between true requested orders,
    fulfilled orders, and observed sample deliveries.
    """
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

    @model_validator(mode="after")
    def validate_target_type_integrity(self):
        # A single worker's sample cannot claim to be true requested orders
        if self.target_type == TargetType.REQUESTED_ORDERS:
            if self.orders_requested is None:
                raise ValueError("orders_requested cannot be null when target_type is requested_orders")
            if self.target_quality not in (TargetQuality.VERIFIED_AGGREGATE, TargetQuality.SYNTHETIC):
                raise ValueError("requested_orders target must have verified_aggregate or synthetic quality")
        return self

