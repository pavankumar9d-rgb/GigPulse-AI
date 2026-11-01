"""Work session tracking endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import DateFilterParams, PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.records import (
    WorkSessionCreate,
    WorkSessionListResponse,
    WorkSessionResponse,
)
from gigpulse_core.db.repository import (
    get_or_create_platform,
    get_or_create_worker_profile,
    list_work_sessions,
)
from gigpulse_core.db.schema import WorkSessionModel

router = APIRouter(prefix="/sessions", tags=["Work Sessions"])


@router.get("", response_model=WorkSessionListResponse)
def get_work_sessions(
    worker_ref: Optional[str] = Query(default=None, description="Filter by worker identifier"),
    platform_code: Optional[str] = Query(default=None, description="Filter by platform code"),
    date_filter: DateFilterParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    base_query = select(WorkSessionModel)
    if worker_ref:
        base_query = base_query.where(WorkSessionModel.worker_ref == worker_ref)
    if platform_code:
        base_query = base_query.where(WorkSessionModel.platform_code == platform_code)
    if date_filter.start_date:
        base_query = base_query.where(WorkSessionModel.started_at >= date_filter.start_date)
    if date_filter.end_date:
        base_query = base_query.where(WorkSessionModel.ended_at <= date_filter.end_date)

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    items = list_work_sessions(
        db,
        worker_ref=worker_ref,
        platform_code=platform_code,
        start_date=date_filter.start_date,
        end_date=date_filter.end_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return WorkSessionListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.post("", response_model=WorkSessionResponse, status_code=status.HTTP_201_CREATED)
def create_work_session(
    payload: WorkSessionCreate,
    db: Session = Depends(get_db),
):
    if payload.ended_at < payload.started_at:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_DURATION",
            message="Session ended_at cannot precede started_at.",
        )

    get_or_create_worker_profile(db, payload.worker_ref)
    get_or_create_platform(db, payload.platform_code)

    session_model = WorkSessionModel(
        worker_ref=payload.worker_ref,
        platform_code=payload.platform_code,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        status=payload.status.value,
        source_type=payload.source_type.value,
        timezone=payload.timezone,
    )
    db.add(session_model)
    db.commit()
    db.refresh(session_model)
    return session_model

