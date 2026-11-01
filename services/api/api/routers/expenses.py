"""Worker expense tracking endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import DateFilterParams, PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.records import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
)
from gigpulse_core.db.repository import (
    get_or_create_worker_profile,
    list_expenses,
)
from gigpulse_core.db.schema import ExpenseModel

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=ExpenseListResponse)
def get_expenses(
    worker_ref: Optional[str] = Query(default=None, description="Filter by worker identifier"),
    category: Optional[str] = Query(default=None, description="Filter by expense category"),
    date_filter: DateFilterParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    base_query = select(ExpenseModel)
    if worker_ref:
        base_query = base_query.where(ExpenseModel.worker_ref == worker_ref)
    if category:
        base_query = base_query.where(ExpenseModel.category == category)
    if date_filter.start_date:
        base_query = base_query.where(ExpenseModel.occurred_at >= date_filter.start_date)
    if date_filter.end_date:
        base_query = base_query.where(ExpenseModel.occurred_at <= date_filter.end_date)

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    items = list_expenses(
        db,
        worker_ref=worker_ref,
        start_date=date_filter.start_date,
        end_date=date_filter.end_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return ExpenseListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
):
    if payload.amount_paise < 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_AMOUNT",
            message="Expense amount_paise must be non-negative.",
        )

    get_or_create_worker_profile(db, payload.worker_ref)

    expense = ExpenseModel(
        worker_ref=payload.worker_ref,
        session_ref=payload.session_ref,
        occurred_at=payload.occurred_at,
        category=payload.category.value,
        amount_paise=payload.amount_paise,
        source_type=payload.source_type.value,
        notes=payload.notes,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

