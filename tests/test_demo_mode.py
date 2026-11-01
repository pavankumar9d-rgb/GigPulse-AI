"""Unit tests for Public DEMO_MODE protections."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.config import settings

client = TestClient(app)


def test_demo_mode_blocks_destructive_endpoints():
    """Verify that enabling DEMO_MODE protects sensitive write operations with 403."""
    original_demo_mode = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True

        # 1. Test CSV Import Commit
        res_import = client.post(
            "/api/v1/imports/commit",
            json={
                "template_type": "work_sessions",
                "csv_content": "worker_ref,platform_code,started_at,ended_at,status\nw01,flash_drop,2026-09-01T10:00:00Z,2026-09-01T14:00:00Z,completed\n",
                "filename": "test.csv",
            },
        )
        assert res_import.status_code == 403
        data_import = res_import.json()
        assert data_import["error"]["code"] == "DEMO_MODE_FORBIDDEN"

        # 2. Test Account Data Deletion
        res_delete = client.delete("/api/v1/account/data?worker_ref=worker_w01&confirm=true")
        assert res_delete.status_code == 403
        data_delete = res_delete.json()
        assert data_delete["error"]["code"] == "DEMO_MODE_FORBIDDEN"

        # 3. Test Model Retraining
        res_train = client.post("/api/v1/models/train")
        assert res_train.status_code == 403
        data_train = res_train.json()
        assert data_train["error"]["code"] == "DEMO_MODE_FORBIDDEN"

    finally:
        settings.DEMO_MODE = original_demo_mode


def test_demo_mode_allows_read_endpoints():
    """Verify read-only endpoints remain fully accessible under DEMO_MODE."""
    original_demo_mode = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True
        res_health = client.get("/api/v1/health")
        assert res_health.status_code == 200

        res_summary = client.get("/api/v1/dashboard/summary?worker_ref=worker_w01")
        assert res_summary.status_code == 200

        res_models = client.get("/api/v1/models")
        assert res_models.status_code == 200
    finally:
        settings.DEMO_MODE = original_demo_mode

