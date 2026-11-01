"""FastAPI dependency injection for database sessions and request filters."""

from datetime import datetime
from typing import Generator, Optional
from fastapi import Query
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from gigpulse_core.db.database import get_engine, get_session_factory, init_db
from api.config import settings

# Global engine cache
_active_engine: Optional[Engine] = None


def get_active_engine() -> Engine:
    """Retrieve or initialize the active SQLAlchemy Engine."""
    global _active_engine
    if _active_engine is None:
        _active_engine = get_engine(settings.DATABASE_PATH)
        init_db(_active_engine)
    return _active_engine


def set_active_engine(engine: Engine) -> None:
    """Explicitly set active engine (used in tests for in-memory SQLite)."""
    global _active_engine
    _active_engine = engine


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a SQLAlchemy Session with automatic commit/rollback."""
    engine = get_active_engine()
    session_factory = get_session_factory(engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


class PaginationParams:
    """Common pagination query parameters."""
    def __init__(
        self,
        limit: int = Query(default=50, ge=1, le=200, description="Maximum number of items to return"),
        offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    ):
        self.limit = limit
        self.offset = offset


class DateFilterParams:
    """Common date range query filters."""
    def __init__(
        self,
        start_date: Optional[datetime] = Query(default=None, description="Start date filter (UTC or with timezone)"),
        end_date: Optional[datetime] = Query(default=None, description="End date filter (UTC or with timezone)"),
    ):
        self.start_date = start_date
        self.end_date = end_date

