"""Tests for SQLite database layer, schema, repository, and safe CSV import."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from gigpulse_core.db.database import get_engine, get_session_factory, init_db
from gigpulse_core.db.importer import import_csv_content, import_csv_file
from gigpulse_core.db.repository import (
    get_or_create_platform,
    get_or_create_worker_profile,
    get_or_create_zone,
    get_worker_analytics_summary,
    list_deliveries,
    list_expenses,
    list_work_sessions,
    list_zone_demand,
)
from gigpulse_core.db.schema import (
    DeliveryModel,
    ExpenseModel,
    ImportBatchModel,
    PlatformModel,
    WorkSessionModel,
    WorkerProfileModel,
    ZoneDemandObservationModel,
    ZoneModel,
)
from gigpulse_core.db.seed import seed_synthetic_fixtures


@pytest.fixture
def db_session():
    """Create a fresh in-memory SQLite database session for each test."""
    engine = get_engine(":memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    session = session_factory()
    try:
        yield session, engine
    finally:
        session.close()


def test_database_schema_initialization(db_session):
    session, engine = db_session
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = {
        "worker_profiles",
        "platforms",
        "zones",
        "work_sessions",
        "deliveries",
        "expenses",
        "zone_demand_observations",
        "import_batches",
        "model_versions",
        "forecast_runs",
        "recommendation_runs",
        "context_observations",
    }
    for t in expected_tables:
        assert t in tables, f"Expected table '{t}' not found in SQLite schema"


def test_worker_profile_and_platform_crud(db_session):
    session, _ = db_session
    worker = get_or_create_worker_profile(session, worker_ref="worker_w01", display_name="Rider One")
    assert worker.worker_ref == "worker_w01"
    assert worker.preferred_currency == "INR"

    platform = get_or_create_platform(session, code="flash_drop", display_name="FlashDrop Demo")
    assert platform.code == "flash_drop"
    assert platform.active is True

    zone = get_or_create_zone(session, zone_code="HYD_ZONE_01", display_name="HITEC City")
    assert zone.zone_code == "HYD_ZONE_01"


def test_delivery_paise_check_constraints(db_session):
    session, _ = db_session
    # Valid delivery with integer paise
    d = DeliveryModel(
        worker_ref="w1",
        platform_code="p1",
        completed_at=datetime.now(timezone.utc),
        payout_paise=5000,
        incentive_paise=1000,
        tip_paise=500,
    )
    session.add(d)
    session.commit()
    assert d.id is not None

    # Negative paise should trigger database CheckConstraint
    d_bad = DeliveryModel(
        worker_ref="w1",
        platform_code="p1",
        completed_at=datetime.now(timezone.utc),
        payout_paise=-100,
    )
    session.add(d_bad)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_work_session_duration_constraint(db_session):
    session, _ = db_session
    t_start = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    t_end = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)  # ended before started

    bad_session = WorkSessionModel(
        worker_ref="w1",
        platform_code="p1",
        started_at=t_start,
        ended_at=t_end,
    )
    session.add(bad_session)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_safe_csv_import_and_retrieval(db_session):
    session, _ = db_session
    csv_text = (
        "worker_ref,platform_code,started_at,ended_at,status,source_type,timezone\n"
        "worker_w01,flash_drop,2026-10-01T10:00:00Z,2026-10-01T14:00:00Z,completed,synthetic,Asia/Kolkata\n"
        "worker_w01,swift_bite,2026-10-01T13:00:00Z,2026-10-01T16:00:00Z,completed,synthetic,Asia/Kolkata\n"
    )

    result = import_csv_content(session, csv_text, "work_sessions", filename="test_sessions.csv")
    assert result.status == "committed"
    assert result.total_rows == 2
    assert result.accepted_rows == 2
    assert result.rejected_rows == 0
    assert not result.already_imported

    # Query sessions back
    stored = list_work_sessions(session, worker_ref="worker_w01")
    assert len(stored) == 2


def test_import_idempotency_and_duplicate_handling(db_session):
    session, _ = db_session
    csv_text = (
        "worker_ref,session_ref,occurred_at,category,amount_paise,source_type,notes\n"
        "worker_w01,s1,2026-10-01T10:00:00Z,fuel,15000,synthetic,fuel topup\n"
    )

    # 1. First import
    res1 = import_csv_content(session, csv_text, "expenses", filename="expenses.csv")
    assert res1.status == "committed"
    assert res1.accepted_rows == 1
    assert not res1.already_imported

    # 2. Second import of exact identical file (idempotency guard)
    res2 = import_csv_content(session, csv_text, "expenses", filename="expenses.csv")
    assert res2.already_imported is True
    assert res2.batch_id == res1.batch_id

    # Verify no duplicate row in DB
    expenses = list_expenses(session, worker_ref="worker_w01")
    assert len(expenses) == 1


def test_import_invalid_record_rejection(db_session):
    session, _ = db_session
    # Missing required columns / malformed header
    bad_csv = "col_a,col_b\nval1,val2\n"
    res = import_csv_content(session, bad_csv, "deliveries")
    assert res.status == "rejected"
    assert res.accepted_rows == 0
    assert len(res.errors) > 0


def test_worker_analytics_summary_with_interval_union(db_session):
    session, _ = db_session

    # 2 overlapping shifts: 10:00-13:00 (3h) and 12:00-15:00 (3h) -> Union is 5 hours (18000s)
    s1 = WorkSessionModel(
        worker_ref="w1",
        platform_code="p1",
        started_at=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 10, 1, 13, 0, tzinfo=timezone.utc),
    )
    s2 = WorkSessionModel(
        worker_ref="w1",
        platform_code="p2",
        started_at=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 10, 1, 15, 0, tzinfo=timezone.utc),
    )
    session.add_all([s1, s2])

    # 2 deliveries: ₹50 + ₹70 gross = ₹120 (12000 paise)
    d1 = DeliveryModel(
        worker_ref="w1",
        platform_code="p1",
        completed_at=datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc),
        payout_paise=4000,
        incentive_paise=1000,
        tip_paise=0,
        duration_seconds=1800,
    )
    d2 = DeliveryModel(
        worker_ref="w1",
        platform_code="p2",
        completed_at=datetime(2026, 10, 1, 14, 0, tzinfo=timezone.utc),
        payout_paise=6000,
        incentive_paise=500,
        tip_paise=500,
        duration_seconds=2400,
    )
    session.add_all([d1, d2])

    # 1 expense: ₹20 (2000 paise)
    e1 = ExpenseModel(
        worker_ref="w1",
        occurred_at=datetime(2026, 10, 1, 10, 30, tzinfo=timezone.utc),
        category="fuel",
        amount_paise=2000,
    )
    session.add(e1)
    session.commit()

    summary = get_worker_analytics_summary(session, "w1")

    # Gross = 5000 + 7000 = 12000 paise (₹120.00)
    assert summary["earnings"]["gross_paise"] == 12000
    assert summary["earnings"]["gross_formatted"] == "₹120.00"

    # Net = 12000 - 2000 = 10000 paise (₹100.00)
    assert summary["earnings"]["net_paise"] == 10000
    assert summary["earnings"]["net_formatted"] == "₹100.00"

    # Online time: union of 10:00-13:00 and 12:00-15:00 = 5 hours (18000 seconds)
    assert summary["time"]["online_seconds"] == 18000
    assert summary["time"]["online_hours"] == 5.0

    # Rate: 10000 paise / 5 hours = 2000 paise/hour (₹20.00/hr)
    assert summary["rates"]["net_earnings_per_online_hour_paise"] == 2000.0
    assert summary["rates"]["net_earnings_per_online_hour_formatted"] == "₹20.00"


def test_seed_synthetic_fixtures_integration(db_session):
    _, engine = db_session
    synthetic_dir = Path("data/synthetic")
    assert synthetic_dir.exists()

    results = seed_synthetic_fixtures(engine, synthetic_dir)

    assert results["work_sessions"]["accepted_rows"] == 338
    assert results["deliveries"]["accepted_rows"] == 1472
    assert results["expenses"]["accepted_rows"] == 171
    assert results["zone_demand"]["accepted_rows"] == 10080

    # Verify counts directly via repository queries
    session_factory = get_session_factory(engine)
    with session_factory() as s:
        sessions = list_work_sessions(s, limit=10000)
        assert len(sessions) == 338

        deliveries = list_deliveries(s, limit=2000)
        assert len(deliveries) == 1472

        expenses = list_expenses(s, limit=1000)
        assert len(expenses) == 171

        demand = list_zone_demand(s, limit=20000)
        assert len(demand) == 10080

