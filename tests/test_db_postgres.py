"""Unit tests for Database URL normalization and PostgreSQL engine compatibility."""

from gigpulse_core.db.database import normalize_database_url, get_engine


def test_normalize_database_url_converts_legacy_postgres_prefix():
    """Verify postgres:// is rewritten to postgresql:// for SQLAlchemy 2.0+."""
    legacy = "postgres://usr:pwd@ep-dry-lake.neon.tech/neondb?sslmode=require"
    expected = "postgresql://usr:pwd@ep-dry-lake.neon.tech/neondb?sslmode=require"
    assert normalize_database_url(legacy) == expected


def test_normalize_database_url_preserves_postgresql_and_sqlite():
    """Verify modern postgresql:// and sqlite:/// URLs remain untouched."""
    pg = "postgresql://usr:pwd@localhost:5432/gigpulse"
    assert normalize_database_url(pg) == pg

    sqlite = "sqlite:///gigpulse.db"
    assert normalize_database_url(sqlite) == sqlite


def test_in_memory_sqlite_engine():
    """Verify :memory: engine creation with StaticPool."""
    engine = get_engine(":memory:")
    assert str(engine.url) == "sqlite:///:memory:"

