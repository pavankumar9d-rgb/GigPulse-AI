"""Intelligent opportunity recommendation endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.errors import AppException
from api.schemas.recommendations import (
    CandidateOption,
    ExcludedCandidateOption,
    RecommendationPreviewRequest,
    RecommendationPreviewResponse,
)
from gigpulse_core.ml.optimizer import generate_recommendations

router = APIRouter(prefix="/recommendations", tags=["Intelligent Recommendations"])


@router.post("/preview", response_model=RecommendationPreviewResponse)
def get_recommendations_preview(
    payload: RecommendationPreviewRequest,
    db: Session = Depends(get_db),
):
    """Rank multi-platform candidate opportunities under worker constraints and risk preferences."""
    if payload.time_window.end_at <= payload.time_window.start_at:
        raise AppException(
            code="INVALID_TIME_RANGE",
            message="Time window end_at must be strictly greater than start_at.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    prefs = payload.preferences
    min_rate = prefs.min_net_earnings_paise_per_hour if prefs else 0
    max_dist = prefs.max_travel_distance_m if prefs else 15000
    risk = prefs.risk_tolerance if prefs else "balanced"
    curr_zone = prefs.current_zone_code if prefs else "zone_koramangala"
    ex_plats = prefs.exclude_platform_ids if prefs else []
    ex_zones = prefs.exclude_zone_ids if prefs else []

    try:
        results = generate_recommendations(
            session=db,
            worker_ref=payload.worker_ref,
            candidate_platforms=payload.candidate_platform_ids,
            candidate_zones=payload.candidate_zone_ids,
            start_at=payload.time_window.start_at,
            end_at=payload.time_window.end_at,
            current_zone_code=curr_zone,
            min_net_earnings_paise_per_hour=min_rate,
            max_travel_distance_m=max_dist,
            risk_tolerance=risk,
            excluded_platforms=ex_plats,
            excluded_zones=ex_zones,
        )

        ranked = [CandidateOption(**c) for c in results["ranked_candidates"]]
        excluded = [ExcludedCandidateOption(**e) for e in results["excluded_candidates"]]
        top = CandidateOption(**results["top_candidate"]) if results["top_candidate"] else None

        return RecommendationPreviewResponse(
            worker_ref=results["worker_ref"],
            scoring_version=results["scoring_version"],
            generated_at=results["generated_at"],
            time_window=results["time_window"],
            recommendation_run_id=results["recommendation_run_id"],
            total_evaluated=results["total_evaluated"],
            viable_count=results["viable_count"],
            top_candidate=top,
            ranked_candidates=ranked,
            excluded_candidates=excluded,
            disclaimer=results["disclaimer"],
        )
    except Exception as e:
        raise AppException(
            code="RECOMMENDATION_ERROR",
            message=f"Failed to generate recommendations: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

