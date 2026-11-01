"""Schemas for earnings, expenses, and worker analytics summaries."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EarningsBreakdown(BaseModel):
    gross_paise: int
    gross_formatted: str
    total_expenses_paise: int
    total_expenses_formatted: str
    net_paise: int
    net_formatted: str


class TimeBreakdown(BaseModel):
    online_seconds: int
    online_hours: float
    active_seconds: int
    active_hours: float
    idle_seconds: int


class RateBreakdown(BaseModel):
    net_earnings_per_online_hour_paise: Optional[float]
    net_earnings_per_online_hour_formatted: Optional[str]


class WorkerAnalyticsResponse(BaseModel):
    worker_ref: str
    counts: Dict[str, int]
    earnings: EarningsBreakdown
    time: TimeBreakdown
    rates: RateBreakdown
    platform_gross_shares: Dict[str, float]


class DashboardSummaryResponse(BaseModel):
    project: str = "GigPulse AI"
    synthetic_mode: bool = True
    worker_ref: str
    analytics: WorkerAnalyticsResponse

