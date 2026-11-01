"""Delivery event tracking endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import DateFilterParams, PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.records import (
    DeliveryCreate,
    DeliveryListResponse,
    DeliveryResponse,
)
from gigpulse_core.db.repository import (
    get_or_create_platform,
    get_or_create_worker_profile,
    get_or_create_zone,
    list_deliveries,
)
from gigpulse_core.db.schema import DeliveryModel

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.get("", response_model=DeliveryListResponse)
def get_deliveries(
    worker_ref: Optional[str] = Query(default=None, description="Filter by worker identifier"),
    platform_code: Optional[str] = Query(default=None, description="Filter by platform code"),
    date_filter: DateFilterParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    base_query = select(DeliveryModel)
    if worker_ref:
        base_query = base_query.where(DeliveryModel.worker_ref == worker_ref)
    if platform_code:
        base_query = base_query.where(DeliveryModel.platform_code == platform_code)
    if date_filter.start_date:
        base_query = base_query.where(DeliveryModel.completed_at >= date_filter.start_date)
    if date_filter.end_date:
        base_query = base_query.where(DeliveryModel.completed_at <= date_filter.end_date)

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    models = list_deliveries(
        db,
        worker_ref=worker_ref,
        platform_code=platform_code,
        start_date=date_filter.start_date,
        end_date=date_filter.end_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    items = []
    for d in models:
        resp = DeliveryResponse.model_validate(d)
        resp.gross_payout_paise = d.payout_paise + d.incentive_paise + d.tip_paise
        items.append(resp)

    return DeliveryListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
):
    if payload.accepted_at and payload.completed_at < payload.accepted_at:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_COMPLETION_TIME",
            message="Delivery completed_at cannot precede accepted_at.",
        )

    get_or_create_worker_profile(db, payload.worker_ref)
    get_or_create_platform(db, payload.platform_code)
    if payload.pickup_zone_code:
        get_or_create_zone(db, payload.pickup_zone_code)
    if payload.drop_zone_code:
        get_or_create_zone(db, payload.drop_zone_code)

    delivery = DeliveryModel(
        worker_ref=payload.worker_ref,
        platform_code=payload.platform_code,
        session_ref=payload.session_ref,
        accepted_at=payload.accepted_at,
        completed_at=payload.completed_at,
        pickup_zone_code=payload.pickup_zone_code,
        drop_zone_code=payload.drop_zone_code,
        payout_paise=payload.payout_paise,
        incentive_paise=payload.incentive_paise,
        tip_paise=payload.tip_paise,
        distance_m=payload.distance_m,
        duration_seconds=payload.duration_seconds,
        status=payload.status.value,
        target_quality=payload.target_quality.value,
        source_type=payload.source_type.value,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    resp = DeliveryResponse.model_validate(delivery)
    resp.gross_payout_paise = delivery.payout_paise + delivery.incentive_paise + delivery.tip_paise
    return resp

