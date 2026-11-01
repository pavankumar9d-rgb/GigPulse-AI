"""Worker profile endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.workers import (
    WorkerProfileCreate,
    WorkerProfileListResponse,
    WorkerProfileResponse,
)
from gigpulse_core.db.schema import WorkerProfileModel

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("", response_model=WorkerProfileListResponse)
def list_workers(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count(WorkerProfileModel.id))) or 0
    stmt = (
        select(WorkerProfileModel)
        .order_by(WorkerProfileModel.worker_ref.asc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    items = list(db.scalars(stmt).all())
    return WorkerProfileListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.get("/{worker_ref}", response_model=WorkerProfileResponse)
def get_worker(
    worker_ref: str,
    db: Session = Depends(get_db),
):
    stmt = select(WorkerProfileModel).where(WorkerProfileModel.worker_ref == worker_ref)
    worker = db.scalar(stmt)
    if not worker:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"Worker profile '{worker_ref}' was not found.",
        )
    return worker


@router.post("", response_model=WorkerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_worker(
    payload: WorkerProfileCreate,
    db: Session = Depends(get_db),
):
    existing = db.scalar(select(WorkerProfileModel).where(WorkerProfileModel.worker_ref == payload.worker_ref))
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=f"Worker profile '{payload.worker_ref}' already exists.",
        )

    worker = WorkerProfileModel(
        worker_ref=payload.worker_ref,
        display_name=payload.display_name,
        home_zone_code=payload.home_zone_code,
        preferred_currency=payload.preferred_currency,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker

