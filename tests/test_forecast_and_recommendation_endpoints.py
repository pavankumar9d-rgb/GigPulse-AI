"""Integration tests for forecasting, recommendation, model registry, and governance endpoints."""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest

from api.main import app

client = TestClient(app)


def test_earnings_forecast_endpoint():
    """Test POST /api/v1/forecasts/earnings."""
    start_at = datetime.now(timezone.utc) + timedelta(days=1)
    end_at = start_at + timedelta(hours=3)

    payload = {
        "worker_ref": "worker_w01",
        "platform_code": "flash_drop",
        "zone_code": "zone_koramangala",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "prediction_unit": "INR_PER_ONLINE_HOUR",
        "include_interval": True,
    }

    res = client.post("/api/v1/forecasts/earnings", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["target"] == "net_earnings_paise_per_online_hour"
    assert data["worker_ref"] == "worker_w01"
    assert data["q10_paise_per_hour"] <= data["q50_paise_per_hour"] <= data["q90_paise_per_hour"]
    assert "expected_net_inr" in data
    assert "expected_gross_inr" in data


def test_earnings_forecast_invalid_time_range():
    """Test POST /api/v1/forecasts/earnings with invalid time range."""
    start_at = datetime.now(timezone.utc) + timedelta(days=1)
    end_at = start_at - timedelta(hours=1)

    payload = {
        "worker_ref": "worker_w01",
        "platform_code": "flash_drop",
        "zone_code": "zone_koramangala",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
    }

    res = client.post("/api/v1/forecasts/earnings", json=payload)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INVALID_TIME_RANGE"


def test_demand_forecast_endpoint():
    """Test POST /api/v1/forecasts/demand."""
    forecast_from = datetime.now(timezone.utc) + timedelta(days=1)
    payload = {
        "zone_codes": ["HYD_ZONE_01", "HYD_ZONE_02"],
        "forecast_from": forecast_from.isoformat(),
        "steps": 4,
        "interval_minutes": 30,
        "target_type": "observed_deliveries",
        "include_interval": True,
    }

    res = client.post("/api/v1/forecasts/demand", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["target_type"] == "observed_deliveries"
    assert len(data["forecasts"]) == 8  # 2 zones * 4 steps
    for item in data["forecasts"]:
        assert item["lower_prediction"] <= item["point_prediction"] <= item["upper_prediction"]


def test_demand_forecast_empty_zones_rejection():
    """Test POST /api/v1/forecasts/demand with empty zone list."""
    payload = {
        "zone_codes": [],
        "forecast_from": datetime.now(timezone.utc).isoformat(),
        "steps": 4,
    }
    res = client.post("/api/v1/forecasts/demand", json=payload)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "EMPTY_ZONE_LIST"


def test_recommendation_preview_endpoint():
    """Test POST /api/v1/recommendations/preview."""
    start_at = datetime.now(timezone.utc) + timedelta(days=1)
    end_at = start_at + timedelta(hours=4)

    payload = {
        "worker_ref": "worker_w01",
        "candidate_zone_ids": ["zone_koramangala", "zone_indiranagar", "zone_hsr"],
        "candidate_platform_ids": ["flash_drop", "swift_bite"],
        "time_window": {
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        },
        "preferences": {
            "min_net_earnings_paise_per_hour": 10000,
            "max_travel_distance_m": 8000,
            "risk_tolerance": "balanced",
            "exclude_platform_ids": [],
            "exclude_zone_ids": [],
            "current_zone_code": "zone_koramangala",
        },
    }

    res = client.post("/api/v1/recommendations/preview", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["viable_count"] >= 1
    assert data["top_candidate"] is not None
    top = data["top_candidate"]
    assert "composite_score" in top
    assert "reasons" in top
    assert len(top["reasons"]) >= 1


def test_model_registry_endpoints():
    """Test GET /api/v1/models and GET /api/v1/models/{id}."""
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) >= 2

    first_model = data["models"][0]
    model_id = first_model["id"]

    res_detail = client.get(f"/api/v1/models/{model_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == model_id


def test_data_export_and_deletion_governance():
    """Test POST /api/v1/data/export and DELETE /api/v1/account/data."""
    # Seed worker, session, delivery, expense in active database
    client.post("/api/v1/workers", json={"worker_ref": "worker_w01", "display_name": "Rider W01"})
    client.post("/api/v1/platforms", json={"code": "flash_drop", "display_name": "FlashDrop"})
    client.post(
        "/api/v1/deliveries",
        json={
            "worker_ref": "worker_w01",
            "platform_code": "flash_drop",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "payout_paise": 12000,
            "incentive_paise": 1500,
            "tip_paise": 500,
            "status": "completed",
        },
    )

    # 1. Export data
    res_export = client.post("/api/v1/data/export?worker_ref=worker_w01")
    assert res_export.status_code == 200
    exp_data = res_export.json()
    assert exp_data["worker_ref"] == "worker_w01"
    assert "counts" in exp_data
    assert exp_data["counts"]["deliveries"] >= 1

    # 2. Rejection of deletion without confirmation
    res_del_fail = client.delete("/api/v1/account/data?worker_ref=test_delete_worker")
    assert res_del_fail.status_code == 400
    assert res_del_fail.json()["error"]["code"] == "CONFIRMATION_REQUIRED"

    # 3. Successful deletion with confirmation
    res_del_ok = client.delete("/api/v1/account/data?worker_ref=test_delete_worker&confirm=true")
    assert res_del_ok.status_code == 200
    assert res_del_ok.json()["deleted"] is True
