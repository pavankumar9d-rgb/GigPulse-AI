"""Pydantic schemas for machine learning predictions and demand forecasts."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EarningsForecastRequest(BaseModel):
    worker_ref: str = Field(..., description="Worker identifier")
    platform_code: str = Field(..., description="Platform code (e.g. zomato, swiggy, zepto, blinkit)")
    zone_code: str = Field(..., description="Operating zone identifier")
    start_at: datetime = Field(..., description="Planned shift start time (ISO-8601)")
    end_at: datetime = Field(..., description="Planned shift end time (ISO-8601)")
    prediction_unit: str = Field(default="INR_PER_ONLINE_HOUR", description="Forecast unit")
    include_interval: bool = Field(default=True, description="Whether to include Q10 and Q90 confidence intervals")


class EarningsForecastResponse(BaseModel):
    target: str = "net_earnings_paise_per_online_hour"
    unit: str = "INR/hour"
    worker_ref: str
    platform_code: str
    zone_code: str
    duration_hours: float
    q10_paise_per_hour: int
    q50_paise_per_hour: int
    q90_paise_per_hour: int
    q10_inr_per_hour: float
    q50_inr_per_hour: float
    q90_inr_per_hour: float
    expected_gross_paise: int
    expected_expenses_paise: int
    expected_net_paise: int
    expected_gross_inr: str
    expected_expenses_inr: str
    expected_net_inr: str
    horizon_start: str
    horizon_end: str
    model_version: str
    source_class: str = "synthetic_model"
    coverage_level: str = "high"


class DemandForecastRequest(BaseModel):
    zone_codes: List[str] = Field(..., description="List of spatial zone identifiers")
    forecast_from: datetime = Field(..., description="Starting timestamp for forecast (ISO-8601)")
    steps: int = Field(default=8, ge=1, le=48, description="Number of future intervals")
    interval_minutes: int = Field(default=30, ge=15, le=120, description="Minutes per forecast interval")
    target_type: str = Field(default="observed_deliveries", description="Target type definition")
    include_interval: bool = Field(default=True, description="Whether to include lower and upper prediction intervals")


class DemandStepForecast(BaseModel):
    zone_code: str
    interval_start: str
    interval_end: str
    interval_minutes: int
    step: int
    target_type: str
    target_quality: str
    point_prediction: float
    lower_prediction: float
    upper_prediction: float
    unit: str
    model_version: str
    coverage_fraction: float


class DemandForecastResponse(BaseModel):
    project: str = "GigPulse AI"
    target_type: str
    interval_minutes: int
    total_steps: int
    generated_at: str
    forecasts: List[DemandStepForecast]

