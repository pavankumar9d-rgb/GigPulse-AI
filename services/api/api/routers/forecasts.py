"""Forecast endpoints for worker earnings and zone demand."""

from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.errors import AppException
from api.schemas.forecasts import (
    DemandForecastRequest,
    DemandForecastResponse,
    DemandStepForecast,
    EarningsForecastRequest,
    EarningsForecastResponse,
)
from gigpulse_core.ml.demand import forecast_zone_demand
from gigpulse_core.ml.earnings import predict_worker_earnings

router = APIRouter(prefix="/forecasts", tags=["Machine Learning Forecasts"])


@router.post("/earnings", response_model=EarningsForecastResponse)
def get_earnings_forecast(
    payload: EarningsForecastRequest,
    db: Session = Depends(get_db),
):
    """Predict worker net earnings per online hour and shift gross/net totals using ML."""
    if payload.end_at <= payload.start_at:
        raise AppException(
            code="INVALID_TIME_RANGE",
            message="end_at must be strictly greater than start_at.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        prediction = predict_worker_earnings(
            session=db,
            worker_ref=payload.worker_ref,
            platform_code=payload.platform_code,
            zone_code=payload.zone_code,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
        return EarningsForecastResponse(**prediction)
    except Exception as e:
        raise AppException(
            code="EARNINGS_PREDICTION_ERROR",
            message=f"Failed to compute earnings forecast: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/demand", response_model=DemandForecastResponse)
def get_demand_forecast(
    payload: DemandForecastRequest,
    db: Session = Depends(get_db),
):
    """Spatio-temporal zone demand forecast preserving target separation."""
    if not payload.zone_codes:
        raise AppException(
            code="EMPTY_ZONE_LIST",
            message="At least one zone_code must be provided for demand forecasting.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        forecast_items = forecast_zone_demand(
            session=db,
            zone_codes=payload.zone_codes,
            forecast_from=payload.forecast_from,
            steps=payload.steps,
            interval_minutes=payload.interval_minutes,
            target_type=payload.target_type,
        )

        steps_typed = [DemandStepForecast(**item) for item in forecast_items]
        return DemandForecastResponse(
            project="GigPulse AI",
            target_type=payload.target_type,
            interval_minutes=payload.interval_minutes,
            total_steps=payload.steps,
            generated_at=datetime.now(timezone.utc).isoformat(),
            forecasts=steps_typed,
        )
    except Exception as e:
        raise AppException(
            code="DEMAND_FORECAST_ERROR",
            message=f"Failed to generate demand forecast: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

