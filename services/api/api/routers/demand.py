"""Zone demand observations endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import DateFilterParams, PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.records import (
    ZoneDemandCreate,
    ZoneDemandListResponse,
    ZoneDemandResponse,
)
from gigpulse_core.enums import TargetQuality, TargetType
from gigpulse_core.db.repository import get_or_create_zone, list_zone_demand
from gigpulse_core.db.schema import ZoneDemandObservationModel

router = APIRouter(prefix="/demand", tags=["Zone Demand"])


@router.get("", response_model=ZoneDemandListResponse)
def get_zone_demand_observations(
    zone_code: Optional[str] = Query(default=None, description="Filter by zone identifier"),
    target_type: Optional[str] = Query(default=None, description="Filter by target type (e.g. requested_orders, observed_deliveries)"),
    date_filter: DateFilterParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    base_query = select(ZoneDemandObservationModel)
    if zone_code:
        base_query = base_query.where(ZoneDemandObservationModel.zone_code == zone_code)
    if target_type:
        base_query = base_query.where(ZoneDemandObservationModel.target_type == target_type)
    if date_filter.start_date:
        base_query = base_query.where(ZoneDemandObservationModel.interval_start >= date_filter.start_date)
    if date_filter.end_date:
        base_query = base_query.where(ZoneDemandObservationModel.interval_start <= date_filter.end_date)

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    items = list_zone_demand(
        db,
        zone_code=zone_code,
        target_type=target_type,
        start_date=date_filter.start_date,
        end_date=date_filter.end_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return ZoneDemandListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.post("", response_model=ZoneDemandResponse, status_code=status.HTTP_201_CREATED)
def create_zone_demand_observation(
    payload: ZoneDemandCreate,
    db: Session = Depends(get_db),
):
    # Non-negotiable target integrity check
    if payload.target_type == TargetType.REQUESTED_ORDERS:
        if payload.orders_requested is None:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="INVALID_TARGET_DATA",
                message="orders_requested cannot be null when target_type is requested_orders.",
            )
        if payload.target_quality not in (TargetQuality.VERIFIED_AGGREGATE, TargetQuality.SYNTHETIC):
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="INVALID_TARGET_QUALITY",
                message="requested_orders target must have verified_aggregate or synthetic quality.",
            )

    get_or_create_zone(db, payload.zone_code)

    demand = ZoneDemandObservationModel(
        zone_code=payload.zone_code,
        interval_start=payload.interval_start,
        interval_minutes=payload.interval_minutes,
        orders_requested=payload.orders_requested,
        orders_completed=payload.orders_completed,
        deliveries_observed=payload.deliveries_observed,
        demand_proxy_value=payload.demand_proxy_value,
        target_type=payload.target_type.value,
        coverage_fraction=payload.coverage_fraction,
        target_quality=payload.target_quality.value,
        source_type=payload.source_type.value,
    )
    db.add(demand)
    db.commit()
    db.refresh(demand)
    return demand

