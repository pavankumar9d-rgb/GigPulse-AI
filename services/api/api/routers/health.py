"""Health and application status endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.config import settings
from api.dependencies import get_db
from api.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check & database readiness",
)
def get_health_status(db: Session = Depends(get_db)):
    """Check backend operational status and SQLite database connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1;"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        version=settings.VERSION,
        project=settings.PROJECT_NAME,
        database_status=db_status,
        synthetic_mode=True,
        server_time=datetime.now(timezone.utc),
    )

