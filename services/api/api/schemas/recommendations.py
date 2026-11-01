"""Pydantic schemas for intelligent opportunity recommendations."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationPreferences(BaseModel):
    min_net_earnings_paise_per_hour: int = Field(default=0, ge=0)
    max_travel_distance_m: int = Field(default=15000, ge=500, le=50000)
    risk_tolerance: str = Field(default="balanced", description="risk_averse | balanced | risk_tolerant")
    exclude_platform_ids: List[str] = Field(default_factory=list)
    exclude_zone_ids: List[str] = Field(default_factory=list)
    current_zone_code: str = Field(default="zone_koramangala")


class RecommendationTimeWindow(BaseModel):
    start_at: datetime
    end_at: datetime


class RecommendationPreviewRequest(BaseModel):
    worker_ref: str = Field(default="worker_w01")
    candidate_zone_ids: List[str] = Field(default_factory=list)
    candidate_platform_ids: List[str] = Field(default_factory=list)
    time_window: RecommendationTimeWindow
    preferences: Optional[RecommendationPreferences] = None


class CandidateOption(BaseModel):
    candidate_id: str
    platform_code: str
    zone_code: str
    start_at: str
    end_at: str
    duration_hours: float
    composite_score: int
    expected_net_paise_per_hour: int
    expected_net_inr_per_hour: float
    q10_inr_per_hour: float
    q90_inr_per_hour: float
    expected_session_net_paise: int
    expected_session_net_inr: str
    expected_session_gross_paise: int
    expected_session_gross_inr: str
    travel_distance_m: int
    travel_cost_paise: int
    travel_cost_inr: float
    uncertainty_penalty_paise: int
    uncertainty_penalty_inr: float
    demand_estimate: float
    demand_tier: str
    reasons: List[str]
    data_quality: str


class ExcludedCandidateOption(BaseModel):
    candidate_id: str
    platform_code: str
    zone_code: str
    reason: str


class RecommendationPreviewResponse(BaseModel):
    worker_ref: str
    scoring_version: str
    generated_at: str
    time_window: Dict[str, Any]
    recommendation_run_id: str
    total_evaluated: int
    viable_count: int
    top_candidate: Optional[CandidateOption]
    ranked_candidates: List[CandidateOption]
    excluded_candidates: List[ExcludedCandidateOption]
    disclaimer: str

