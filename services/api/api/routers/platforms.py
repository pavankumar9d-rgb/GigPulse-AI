"""Platform configuration endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import PaginationParams, get_db
from api.errors import AppException
from api.schemas.common import PaginationMeta
from api.schemas.platforms import (
    PlatformCreate,
    PlatformListResponse,
    PlatformResponse,
)
from gigpulse_core.db.schema import PlatformModel

router = APIRouter(prefix="/platforms", tags=["Platforms"])


@router.get("", response_model=PlatformListResponse)
def list_platforms(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count(PlatformModel.id))) or 0
    stmt = (
        select(PlatformModel)
        .order_by(PlatformModel.code.asc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    items = list(db.scalars(stmt).all())
    return PlatformListResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            count=len(items),
        ),
    )


@router.post("", response_model=PlatformResponse, status_code=status.HTTP_201_CREATED)
def create_platform(
    payload: PlatformCreate,
    db: Session = Depends(get_db),
):
    existing = db.scalar(select(PlatformModel).where(PlatformModel.code == payload.code))
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=f"Platform code '{payload.code}' already exists.",
        )

    platform = PlatformModel(
        code=payload.code,
        display_name=payload.display_name,
        active=payload.active,
    )
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return platform

