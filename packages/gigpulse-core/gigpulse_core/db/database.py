"""Database engine, connection lifecycle, and initialization.

Supports dual SQLite (local-first storage with WAL mode) and PostgreSQL (cloud e.g. Neon Free / Render).
"""

import os
from pathlib import Path
from typing import Generator, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Base class for SQLAlchemy ORM models
Base = declarative_base()


def normalize_database_url(raw_url: str) -> str:
    """Normalize database connection string for SQLAlchemy 2.0+ compatibility."""
    if not raw_url:
        return raw_url
    url = raw_url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign keys and pragmas for SQLite connections only."""
    # Only execute SQLite pragmas if the DBAPI is sqlite3
    mod = getattr(dbapi_connection.__class__, "__module__", "")
    if "sqlite" in mod:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()


def get_engine(db_path_or_url: Optional[str] = None, echo: bool = False) -> Engine:
    """Create a database Engine for SQLite or PostgreSQL.
    
    Supports:
    - PostgreSQL connection URLs (e.g. postgresql://user:pass@host/db or postgres://...)
    - Local SQLite file paths (e.g. gigpulse.db)
    - In-memory SQLite (':memory:') with StaticPool for test isolation.
    """
    raw_target = db_path_or_url or os.getenv("DATABASE_URL") or os.getenv("DATABASE_PATH") or "gigpulse.db"
    target = normalize_database_url(raw_target)

    if target.startswith("postgresql://") or target.startswith("postgres://"):
        return create_engine(
            target,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    elif target == ":memory:":
        return create_engine(
            "sqlite:///:memory:",
            echo=echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # SQLite file path
        clean_path = target.replace("sqlite:///", "")
        parent = Path(clean_path).parent
        if parent and str(parent) != "." and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        return create_engine(
            f"sqlite:///{clean_path}",
            echo=echo,
            connect_args={"check_same_thread": False},
        )


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a scoped sessionmaker bound to engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(engine: Engine) -> None:
    """Create all schema tables in the database."""
    Base.metadata.create_all(bind=engine)
