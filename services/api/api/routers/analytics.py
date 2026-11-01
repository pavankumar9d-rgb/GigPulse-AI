"""Analytics, earnings summaries, and worker intelligence endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import DateFilterParams, get_db
from api.errors import AppException
from api.schemas.analytics import (
    DashboardSummaryResponse,
    WorkerAnalyticsResponse,
)
from gigpulse_core.db.repository import get_worker_analytics_summary
from gigpulse_core.db.schema import DeliveryModel, ExpenseModel, WorkerProfileModel
from gigpulse_core.domain.weekly_earnings import compute_rolling_weekly_earnings
from gigpulse_core.money import paise_to_rupees_str

router = APIRouter(tags=["Analytics & Summaries"])


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    worker_ref: Optional[str] = Query(default=None, description="Worker identifier (defaults to first available worker)"),
    date_filter: DateFilterParams = Depends(),
    db: Session = Depends(get_db),
):
    """Holistic dashboard summary integrating multi-platform interval union and net earnings."""
    if not worker_ref:
        # Default to first worker profile or fallback
        first_worker = db.scalar(select(WorkerProfileModel.worker_ref).order_by(WorkerProfileModel.worker_ref.asc()))
        worker_ref = first_worker or "worker_w01"

    summary = get_worker_analytics_summary(
        db,
        worker_ref=worker_ref,
        start_date=date_filter.start_date,
        end_date=date_filter.end_date,
    )

    return DashboardSummaryResponse(
        project="GigPulse AI",
        synthetic_mode=True,
        worker_ref=worker_ref,
        analytics=WorkerAnalyticsResponse(**summary),
    )


@router.get("/workers/{worker_ref}/analytics", response_model=WorkerAnalyticsResponse)
def get_worker_analytics(
    worker_ref: str,
    date_filter: DateFilterParams = Depends(),
    db: Session = Depends(get_db),
):
    """Detailed worker intelligence metrics with multi-platform interval-union online hours."""
    # Check if worker exists
    exists = db.scalar(select(WorkerProfileModel).where(WorkerProfileModel.worker_ref == worker_ref))
    if not exists:
        # Check if deliveries exist for this worker
        deliv_exists = db.scalar(select(DeliveryModel).where(DeliveryModel.worker_ref == worker_ref))
        if not deliv_exists:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                code="NOT_FOUND",
                message=f"No records found for worker '{worker_ref}'.",
            )

    summary = get_worker_analytics_summary(
        db,
        worker_ref=worker_ref,
        start_date=date_filter.start_date,
        end_date=date_filter.end_date,
    )
    return WorkerAnalyticsResponse(**summary)


@router.get("/earnings/history")
def get_earnings_history(
    worker_ref: Optional[str] = Query(default=None, description="Filter by worker identifier"),
    date_filter: DateFilterParams = Depends(),
    db: Session = Depends(get_db),
):
    """Historical deliveries and expenses aggregated by date."""
    stmt_deliv = select(DeliveryModel)
    stmt_exp = select(ExpenseModel)
    if worker_ref:
        stmt_deliv = stmt_deliv.where(DeliveryModel.worker_ref == worker_ref)
        stmt_exp = stmt_exp.where(ExpenseModel.worker_ref == worker_ref)
    if date_filter.start_date:
        stmt_deliv = stmt_deliv.where(DeliveryModel.completed_at >= date_filter.start_date)
        stmt_exp = stmt_exp.where(ExpenseModel.occurred_at >= date_filter.start_date)
    if date_filter.end_date:
        stmt_deliv = stmt_deliv.where(DeliveryModel.completed_at <= date_filter.end_date)
        stmt_exp = stmt_exp.where(ExpenseModel.occurred_at <= date_filter.end_date)

    deliveries = list(db.scalars(stmt_deliv.order_by(DeliveryModel.completed_at.asc())).all())
    expenses = list(db.scalars(stmt_exp.order_by(ExpenseModel.occurred_at.asc())).all())

    # Daily aggregation
    daily_map: Dict[str, Dict[str, Any]] = {}

    for d in deliveries:
        if d.status == "completed":
            day_str = d.completed_at.strftime("%Y-%m-%d")
            if day_str not in daily_map:
                daily_map[day_str] = {"date": day_str, "gross_paise": 0, "expenses_paise": 0, "delivery_count": 0}
            gross = d.payout_paise + d.incentive_paise + d.tip_paise
            daily_map[day_str]["gross_paise"] += gross
            daily_map[day_str]["delivery_count"] += 1

    for e in expenses:
        day_str = e.occurred_at.strftime("%Y-%m-%d")
        if day_str not in daily_map:
            daily_map[day_str] = {"date": day_str, "gross_paise": 0, "expenses_paise": 0, "delivery_count": 0}
        daily_map[day_str]["expenses_paise"] += e.amount_paise

    timeline = []
    for day in sorted(daily_map.keys()):
        item = daily_map[day]
        net_paise = item["gross_paise"] - item["expenses_paise"]
        timeline.append({
            "date": day,
            "gross_paise": item["gross_paise"],
            "gross_formatted": paise_to_rupees_str(item["gross_paise"]),
            "expenses_paise": item["expenses_paise"],
            "expenses_formatted": paise_to_rupees_str(item["expenses_paise"]),
            "net_paise": net_paise,
            "net_formatted": paise_to_rupees_str(net_paise),
            "deliveries": item["delivery_count"],
        })

    return {
        "worker_ref": worker_ref,
        "days_count": len(timeline),
        "timeline": timeline,
    }


@router.get("/earnings/weekly-summary")
def get_weekly_earnings_summary(
    worker_ref: Optional[str] = Query(default=None, description="Worker identifier"),
    reference_date: Optional[str] = Query(default=None, description="ISO datetime for evaluation window"),
    tz_name: str = Query(default="Asia/Kolkata", description="Configured timezone"),
    db: Session = Depends(get_db),
):
    """Rolling 7-completed-calendar-day weekly earnings strictly excluding today's in-progress data."""
    if not worker_ref:
        first_worker = db.scalar(select(WorkerProfileModel.worker_ref).order_by(WorkerProfileModel.worker_ref.asc()))
        worker_ref = first_worker or "worker_w01"

    stmt_deliv = select(DeliveryModel).where(
        DeliveryModel.worker_ref == worker_ref,
        DeliveryModel.status == "completed",
    )
    stmt_exp = select(ExpenseModel).where(ExpenseModel.worker_ref == worker_ref)

    deliveries = list(db.scalars(stmt_deliv).all())
    expenses = list(db.scalars(stmt_exp).all())

    deliv_dicts = [
        {
            "completed_at": d.completed_at,
            "payout_paise": d.payout_paise,
            "incentive_paise": d.incentive_paise,
            "tip_paise": d.tip_paise,
        }
        for d in deliveries
    ]
    exp_dicts = [
        {
            "occurred_at": e.occurred_at,
            "amount_paise": e.amount_paise,
        }
        for e in expenses
    ]

    ref_dt = None
    if reference_date:
        try:
            from datetime import datetime
            ref_dt = datetime.fromisoformat(reference_date)
        except Exception:
            ref_dt = None
    elif deliv_dicts:
        # If no reference_date is provided and dataset is in the past, anchor reference to day after latest delivery
        latest_deliv_dt = max(d["completed_at"] for d in deliv_dicts)
        from datetime import datetime, timezone, timedelta
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        if (now_utc - latest_deliv_dt).days > 7:
            ref_dt = latest_deliv_dt + timedelta(days=1)

    summary = compute_rolling_weekly_earnings(
        deliveries=deliv_dicts,
        expenses=exp_dicts,
        reference_datetime=ref_dt,
        tz_name=tz_name,
    )
    payload = summary.to_dict()
    payload["worker_ref"] = worker_ref
    return payload


