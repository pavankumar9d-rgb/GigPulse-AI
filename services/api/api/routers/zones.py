"""Geographic zone endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.zones import (
    ZoneCreate,
    ZoneListResponse,
    ZoneResponse,
)
from gigpulse_core.db.schema import ZoneModel

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get("", response_model=ZoneListResponse)
def list_zones(
    zone_system: Optional[str] = Query(default=None, description="Filter by zone system (e.g. 'study_area', 'h3')"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    base_query = select(ZoneModel)
    if zone_system:
        base_query = base_query.where(ZoneModel.zone_system == zone_system)

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    stmt = (
        base_query
        .order_by(ZoneModel.zone_code.asc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    items = list(db.scalars(stmt).all())
    return ZoneListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    payload: ZoneCreate,
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(ZoneModel).where(
            ZoneModel.zone_system == payload.zone_system,
            ZoneModel.zone_code == payload.zone_code,
        )
    )
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=f"Zone '{payload.zone_code}' already exists in system '{payload.zone_system}'.",
        )

    zone = ZoneModel(
        zone_system=payload.zone_system,
        zone_code=payload.zone_code,
        resolution=payload.resolution,
        display_name=payload.display_name,
        centroid_lat=payload.centroid_lat,
        centroid_lon=payload.centroid_lon,
        boundary_ref=payload.boundary_ref,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

