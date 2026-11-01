"""Data governance, export, and account deletion endpoints."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.errors import AppException
from api.schemas.governance import (
    AccountDeletionResponse,
    DataExportResponse,
)
from gigpulse_core.db.repository import (
    list_deliveries,
    list_expenses,
    list_work_sessions,
)
from gigpulse_core.db.schema import (
    DeliveryModel,
    ExpenseModel,
    WorkSessionModel,
    WorkerProfileModel,
)

router = APIRouter(tags=["Data Governance & Privacy"])


@router.post("/data/export", response_model=DataExportResponse)
def export_worker_data(
    worker_ref: str = Query(default="worker_w01", description="Worker reference identifier"),
    db: Session = Depends(get_db),
):
    """Export all operational records owned by the worker in structured format."""
    sessions = list_work_sessions(db, worker_ref=worker_ref, limit=10000)
    deliveries = list_deliveries(db, worker_ref=worker_ref, limit=50000)
    expenses = list_expenses(db, worker_ref=worker_ref, limit=10000)

    return DataExportResponse(
        worker_ref=worker_ref,
        exported_at=datetime.now(timezone.utc).isoformat(),
        counts={
            "work_sessions": len(sessions),
            "deliveries": len(deliveries),
            "expenses": len(expenses),
        },
        work_sessions=[
            {
                "id": s.id,
                "platform_code": s.platform_code,
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat(),
                "status": s.status,
            }
            for s in sessions
        ],
        deliveries=[
            {
                "id": d.id,
                "platform_code": d.platform_code,
                "completed_at": d.completed_at.isoformat(),
                "pickup_zone_code": d.pickup_zone_code,
                "drop_zone_code": d.drop_zone_code,
                "payout_paise": d.payout_paise,
                "incentive_paise": d.incentive_paise,
                "tip_paise": d.tip_paise,
                "status": d.status,
            }
            for d in deliveries
        ],
        expenses=[
            {
                "id": e.id,
                "occurred_at": e.occurred_at.isoformat(),
                "category": e.category,
                "amount_paise": e.amount_paise,
                "notes": e.notes,
            }
            for e in expenses
        ],
    )


@router.delete("/account/data", response_model=AccountDeletionResponse)
def delete_worker_data(
    worker_ref: str = Query(..., description="Worker identifier to delete"),
    confirm: bool = Query(default=False, description="Explicit confirmation flag"),
    db: Session = Depends(get_db),
):
    """Safely delete all operational records for a given worker under explicit confirmation."""
    from api.config import settings
    if settings.DEMO_MODE:
        raise AppException(
            code="DEMO_MODE_FORBIDDEN",
            message="Data deletion is disabled in public demo mode to preserve study data integrity.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if not confirm:
        raise AppException(
            code="CONFIRMATION_REQUIRED",
            message="Data deletion requires explicit confirm=true query parameter.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Count records before deletion
    n_deliv = db.execute(select(DeliveryModel).where(DeliveryModel.worker_ref == worker_ref)).scalars().all()
    n_sess = db.execute(select(WorkSessionModel).where(WorkSessionModel.worker_ref == worker_ref)).scalars().all()
    n_exp = db.execute(select(ExpenseModel).where(ExpenseModel.worker_ref == worker_ref)).scalars().all()

    # Execute deletions
    db.execute(delete(DeliveryModel).where(DeliveryModel.worker_ref == worker_ref))
    db.execute(delete(WorkSessionModel).where(WorkSessionModel.worker_ref == worker_ref))
    db.execute(delete(ExpenseModel).where(ExpenseModel.worker_ref == worker_ref))
    db.commit()

    return AccountDeletionResponse(
        worker_ref=worker_ref,
        deleted=True,
        deleted_counts={
            "deliveries": len(n_deliv),
            "work_sessions": len(n_sess),
            "expenses": len(n_exp),
        },
        message=f"Successfully purged all operational records for worker '{worker_ref}'.",
    )

