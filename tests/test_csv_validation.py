"""Unit tests for CSV schema validation, sanitization, and deduplication."""

import pytest
from gigpulse_core.validator import (
    TEMPLATE_HEADERS,
    compute_row_hash,
    sanitize_csv_cell,
    validate_csv_content,
)


def test_sanitize_csv_cell():
    assert sanitize_csv_cell("normal_text") == "normal_text"
    assert sanitize_csv_cell("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"


def test_validate_header_mismatch():
    invalid_csv = "col1,col2,col3\n1,2,3\n"
    report = validate_csv_content(invalid_csv, "deliveries")
    assert not report.is_valid
    assert len(report.errors) == 1
    assert "Header mismatch" in report.errors[0].error_message


def test_validate_empty_content():
    report = validate_csv_content("", "work_sessions")
    assert not report.is_valid
    assert "Empty CSV content" in report.errors[0].error_message


def test_validate_valid_work_session_csv():
    headers = ",".join(TEMPLATE_HEADERS["work_sessions"])
    csv_data = f"{headers}\nw1,flash_drop,2026-10-01T10:00:00Z,2026-10-01T14:00:00Z,completed,synthetic,Asia/Kolkata\n"
    report = validate_csv_content(csv_data, "work_sessions")
    assert report.is_valid
    assert report.total_rows == 1
    assert report.accepted_rows == 1
    assert report.rejected_rows == 0
    record = report.valid_records[0]
    assert record.worker_ref == "w1"
    assert record.platform_code == "flash_drop"


def test_validate_invalid_time_range():
    headers = ",".join(TEMPLATE_HEADERS["work_sessions"])
    # ended_at is before started_at
    csv_data = f"{headers}\nw1,flash_drop,2026-10-01T14:00:00Z,2026-10-01T10:00:00Z,completed,synthetic,Asia/Kolkata\n"
    report = validate_csv_content(csv_data, "work_sessions")
    assert not report.is_valid
    assert report.rejected_rows == 1
    assert any("ended_at" in err.error_message for err in report.errors)


def test_validate_duplicate_rows():
    headers = ",".join(TEMPLATE_HEADERS["expenses"])
    row = "w1,sess_1,2026-10-01T10:00:00Z,fuel,15000,synthetic,petrol"
    csv_data = f"{headers}\n{row}\n{row}\n"
    report = validate_csv_content(csv_data, "expenses")
    assert not report.is_valid
    assert report.total_rows == 2
    assert report.accepted_rows == 1
    assert report.rejected_rows == 1
    assert report.duplicate_rows == 1


def test_validate_zone_demand_target_integrity():
    headers = ",".join(TEMPLATE_HEADERS["zone_demand"])
    # target_type is requested_orders, but target_quality is proxy -> should fail
    bad_row = "HYD_Z01,2026-10-01T10:00:00Z,30,25,20,5,22.5,requested_orders,0.85,proxy,synthetic"
    report = validate_csv_content(f"{headers}\n{bad_row}\n", "zone_demand")
    assert not report.is_valid
    assert any("requested_orders target must have verified_aggregate or synthetic quality" in err.error_message for err in report.errors)

    # Valid row with synthetic quality
    good_row = "HYD_Z01,2026-10-01T10:00:00Z,30,25,20,5,22.5,requested_orders,0.85,synthetic,synthetic"
    report_good = validate_csv_content(f"{headers}\n{good_row}\n", "zone_demand")
    assert report_good.is_valid
    assert report_good.accepted_rows == 1

