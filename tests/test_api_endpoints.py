"""Comprehensive integration tests for GigPulse AI FastAPI backend service."""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_active_engine, set_active_engine
from api.main import app
from gigpulse_core.db.database import get_engine, init_db


@pytest.fixture(autouse=True)
def setup_test_db():
    """Run every test against a pristine in-memory SQLite database."""
    engine = get_engine(":memory:")
    init_db(engine)
    set_active_engine(engine)
    yield engine


@pytest.fixture
def client():
    return TestClient(app)


def test_api_root_and_docs(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["project"] == "GigPulse AI"
    assert data["status"] == "online"
    assert data["docs"] == "/docs"

    # Swagger OpenAPI json
    openapi_res = client.get("/openapi.json")
    assert openapi_res.status_code == 200
    assert openapi_res.json()["info"]["title"] == "GigPulse AI"


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database_status"] == "connected"
    assert data["synthetic_mode"] is True
    assert "server_time" in data


def test_workers_crud_and_missing_record(client):
    # 1. Create worker
    create_res = client.post(
        "/api/v1/workers",
        json={"worker_ref": "worker_w01", "display_name": "Rider W01", "preferred_currency": "INR"},
    )
    assert create_res.status_code == 201
    w_data = create_res.json()
    assert w_data["worker_ref"] == "worker_w01"
    assert w_data["display_name"] == "Rider W01"

    # 2. Duplicate worker returns 409
    dup_res = client.post(
        "/api/v1/workers",
        json={"worker_ref": "worker_w01", "display_name": "Duplicate"},
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "CONFLICT"

    # 3. Retrieve worker
    get_res = client.get("/api/v1/workers/worker_w01")
    assert get_res.status_code == 200
    assert get_res.json()["worker_ref"] == "worker_w01"

    # 4. Missing worker returns 404
    missing_res = client.get("/api/v1/workers/non_existent_worker")
    assert missing_res.status_code == 404
    assert missing_res.json()["error"]["code"] == "NOT_FOUND"

    # 5. List workers
    list_res = client.get("/api/v1/workers?limit=10&offset=0")
    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) == 1
    assert list_res.json()["meta"]["total"] == 1


def test_platforms_and_zones_crud(client):
    # Platform
    p_res = client.post(
        "/api/v1/platforms",
        json={"code": "flash_drop", "display_name": "FlashDrop Demo", "active": True},
    )
    assert p_res.status_code == 201
    assert p_res.json()["code"] == "flash_drop"

    p_list = client.get("/api/v1/platforms")
    assert p_list.status_code == 200
    assert len(p_list.json()["items"]) == 1

    # Zone
    z_res = client.post(
        "/api/v1/zones",
        json={"zone_code": "HYD_ZONE_01", "zone_system": "study_area", "display_name": "HITEC City"},
    )
    assert z_res.status_code == 201
    assert z_res.json()["zone_code"] == "HYD_ZONE_01"

    z_list = client.get("/api/v1/zones?zone_system=study_area")
    assert z_list.status_code == 200
    assert len(z_list.json()["items"]) == 1


def test_work_sessions_crud_and_invalid_duration(client):
    # Valid session
    res = client.post(
        "/api/v1/sessions",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "started_at": "2026-10-01T10:00:00Z",
            "ended_at": "2026-10-01T14:00:00Z",
            "status": "completed",
            "source_type": "synthetic",
        },
    )
    assert res.status_code == 201
    assert res.json()["worker_ref"] == "worker_w01"

    # Invalid session where ended_at < started_at
    bad_res = client.post(
        "/api/v1/sessions",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "started_at": "2026-10-01T14:00:00Z",
            "ended_at": "2026-10-01T10:00:00Z",
            "status": "completed",
        },
    )
    assert bad_res.status_code == 400
    assert bad_res.json()["error"]["code"] == "INVALID_DURATION"

    # Query with date filter
    list_res = client.get("/api/v1/sessions?worker_ref=worker_w01&start_date=2026-10-01T00:00:00Z")
    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) == 1


def test_deliveries_crud_and_validation(client):
    # Valid delivery
    res = client.post(
        "/api/v1/deliveries",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "completed_at": "2026-10-01T12:00:00Z",
            "payout_paise": 5500,
            "incentive_paise": 1000,
            "tip_paise": 500,
            "duration_seconds": 1800,
            "distance_m": 4200,
            "status": "completed",
            "target_quality": "synthetic",
            "source_type": "synthetic",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["payout_paise"] == 5500
    assert data["gross_payout_paise"] == 7000  # 5500 + 1000 + 500

    # Negative payout should fail Pydantic validation (422)
    bad_res = client.post(
        "/api/v1/deliveries",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "completed_at": "2026-10-01T12:00:00Z",
            "payout_paise": -500,
        },
    )
    assert bad_res.status_code == 422
    assert bad_res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_expenses_crud_and_validation(client):
    # Valid expense
    res = client.post(
        "/api/v1/expenses",
        json={
            "worker_ref": "worker_w01",
            "occurred_at": "2026-10-01T10:30:00Z",
            "category": "fuel",
            "amount_paise": 18000,
            "source_type": "synthetic",
            "notes": "Daily petrol",
        },
    )
    assert res.status_code == 201
    assert res.json()["amount_paise"] == 18000
    assert res.json()["category"] == "fuel"

    # Query expenses
    list_res = client.get("/api/v1/expenses?worker_ref=worker_w01&category=fuel")
    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) == 1


def test_zone_demand_target_integrity(client):
    # Invalid: target_type=requested_orders but orders_requested is null
    bad_res = client.post(
        "/api/v1/demand",
        json={
            "zone_code": "HYD_ZONE_01",
            "interval_start": "2026-10-01T12:00:00Z",
            "interval_minutes": 30,
            "target_type": "requested_orders",
            "target_quality": "synthetic",
        },
    )
    assert bad_res.status_code == 400
    assert bad_res.json()["error"]["code"] == "INVALID_TARGET_DATA"

    # Valid synthetic demand
    good_res = client.post(
        "/api/v1/demand",
        json={
            "zone_code": "HYD_ZONE_01",
            "interval_start": "2026-10-01T12:00:00Z",
            "interval_minutes": 30,
            "orders_requested": 35,
            "orders_completed": 30,
            "deliveries_observed": 4,
            "target_type": "requested_orders",
            "target_quality": "synthetic",
            "source_type": "synthetic",
        },
    )
    assert good_res.status_code == 201
    assert good_res.json()["orders_requested"] == 35


def test_worker_analytics_and_interval_union(client):
    # Create 2 overlapping work sessions: 10:00-13:00 (3h) and 12:00-15:00 (3h)
    # Union online time = 5 hours (18000s)
    client.post(
        "/api/v1/sessions",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "started_at": "2026-10-01T10:00:00Z",
            "ended_at": "2026-10-01T13:00:00Z",
            "status": "completed",
        },
    )
    client.post(
        "/api/v1/sessions",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "swift_bite",
            "started_at": "2026-10-01T12:00:00Z",
            "ended_at": "2026-10-01T15:00:00Z",
            "status": "completed",
        },
    )

    # Deliveries: ₹60 on flash_drop + ₹40 on swift_bite = ₹100 gross (10000 paise)
    client.post(
        "/api/v1/deliveries",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "completed_at": "2026-10-01T11:00:00Z",
            "payout_paise": 6000,
            "duration_seconds": 1800,
        },
    )
    client.post(
        "/api/v1/deliveries",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "swift_bite",
            "completed_at": "2026-10-01T14:00:00Z",
            "payout_paise": 4000,
            "duration_seconds": 2400,
        },
    )

    # Expense: ₹25 fuel (2500 paise)
    client.post(
        "/api/v1/expenses",
        json={
            "worker_ref": "worker_w01",
            "occurred_at": "2026-10-01T10:30:00Z",
            "category": "fuel",
            "amount_paise": 2500,
        },
    )

    # Fetch Worker Analytics
    res = client.get("/api/v1/workers/worker_w01/analytics")
    assert res.status_code == 200
    data = res.json()

    # Gross = ₹100.00 (10000 paise)
    assert data["earnings"]["gross_paise"] == 10000
    assert data["earnings"]["gross_formatted"] == "₹100.00"

    # Net = ₹100 - ₹25 = ₹75.00 (7500 paise)
    assert data["earnings"]["net_paise"] == 7500
    assert data["earnings"]["net_formatted"] == "₹75.00"

    # Online time: union = 5.0 hours (18000s), NOT 6.0 hours
    assert data["time"]["online_seconds"] == 18000
    assert data["time"]["online_hours"] == 5.0

    # Hourly rate: 7500 paise / 5 hrs = 1500 paise/hr (₹15.00/hr)
    assert data["rates"]["net_earnings_per_online_hour_paise"] == 1500.0
    assert data["rates"]["net_earnings_per_online_hour_formatted"] == "₹15.00"

    # Platform shares: 60% flash_drop, 40% swift_bite
    assert data["platform_gross_shares"]["flash_drop"] == 0.6
    assert data["platform_gross_shares"]["swift_bite"] == 0.4

    # Dashboard Summary endpoint
    dash_res = client.get("/api/v1/dashboard/summary?worker_ref=worker_w01")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["worker_ref"] == "worker_w01"
    assert dash_data["synthetic_mode"] is True
    assert dash_data["analytics"]["earnings"]["net_formatted"] == "₹75.00"


def test_earnings_history_endpoint(client):
    # Add delivery & expense
    client.post(
        "/api/v1/deliveries",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "completed_at": "2026-10-01T12:00:00Z",
            "payout_paise": 8000,
        },
    )
    client.post(
        "/api/v1/expenses",
        json={
            "worker_ref": "worker_w01",
            "occurred_at": "2026-10-01T10:00:00Z",
            "category": "fuel",
            "amount_paise": 2000,
        },
    )

    res = client.get("/api/v1/earnings/history?worker_ref=worker_w01")
    assert res.status_code == 200
    data = res.json()
    assert data["days_count"] == 1
    day = data["timeline"][0]
    assert day["date"] == "2026-10-01"
    assert day["gross_paise"] == 8000
    assert day["expenses_paise"] == 2000
    assert day["net_paise"] == 6000


def test_csv_import_validate_and_commit(client):
    csv_text = (
        "worker_ref,platform_code,started_at,ended_at,status,source_type,timezone\n"
        "worker_w01,flash_drop,2026-10-01T10:00:00Z,2026-10-01T14:00:00Z,completed,synthetic,Asia/Kolkata\n"
    )

    # 1. Validate only
    v_res = client.post(
        "/api/v1/imports/validate",
        json={"template_type": "work_sessions", "csv_content": csv_text, "filename": "sessions.csv"},
    )
    assert v_res.status_code == 200
    assert v_res.json()["is_valid"] is True
    assert v_res.json()["accepted_rows"] == 1

    # 2. Commit
    c_res = client.post(
        "/api/v1/imports/commit",
        json={"template_type": "work_sessions", "csv_content": csv_text, "filename": "sessions.csv"},
    )
    assert c_res.status_code == 201
    c_data = c_res.json()
    assert c_data["status"] == "committed"
    assert c_data["accepted_rows"] == 1
    batch_id = c_data["batch_id"]

    # 3. Retrieve batch report
    r_res = client.get(f"/api/v1/imports/{batch_id}/report")
    assert r_res.status_code == 200
    assert r_res.json()["batch_id"] == batch_id
    assert r_res.json()["accepted_count"] == 1

    # 4. Idempotent re-commit of identical file
    c_res2 = client.post(
        "/api/v1/imports/commit",
        json={"template_type": "work_sessions", "csv_content": csv_text, "filename": "sessions.csv"},
    )
    assert c_res2.status_code == 201
    assert c_res2.json()["already_imported"] is True

