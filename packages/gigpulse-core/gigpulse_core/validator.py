"""CSV validation engine for GigPulse AI data templates.

Provides strict header verification, type coercion, formula injection checks,
row deduplication, and detailed validation reports without destructive database actions.
"""

import csv
import hashlib
import io
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type
from pydantic import BaseModel, ValidationError

from gigpulse_core.models import (
    DeliveryRecord,
    ExpenseRecord,
    WorkSessionRecord,
    ZoneDemandRecord,
)

# Template header contracts
TEMPLATE_HEADERS = {
    "deliveries": [
        "worker_ref", "platform_code", "session_ref", "accepted_at", "completed_at",
        "pickup_zone_code", "drop_zone_code", "payout_paise", "incentive_paise",
        "tip_paise", "distance_m", "duration_seconds", "status", "target_quality", "source_type"
    ],
    "work_sessions": [
        "worker_ref", "platform_code", "started_at", "ended_at", "status",
        "source_type", "timezone"
    ],
    "expenses": [
        "worker_ref", "session_ref", "occurred_at", "category", "amount_paise",
        "source_type", "notes"
    ],
    "zone_demand": [
        "zone_code", "interval_start", "interval_minutes", "orders_requested",
        "orders_completed", "deliveries_observed", "demand_proxy_value",
        "target_type", "coverage_fraction", "target_quality", "source_type"
    ],
}

MODEL_MAPPING: Dict[str, Type[BaseModel]] = {
    "deliveries": DeliveryRecord,
    "work_sessions": WorkSessionRecord,
    "expenses": ExpenseRecord,
    "zone_demand": ZoneDemandRecord,
}


@dataclass
class RowError:
    row_number: int
    field: Optional[str]
    error_message: str


@dataclass
class ValidationReport:
    template_type: str
    total_rows: int = 0
    accepted_rows: int = 0
    rejected_rows: int = 0
    duplicate_rows: int = 0
    errors: List[RowError] = field(default_factory=list)
    valid_records: List[BaseModel] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.rejected_rows == 0 and self.total_rows > 0


def sanitize_csv_cell(value: Any) -> Any:
    """Check for and neutralize CSV formula injection risks."""
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
        # Strip or escape formula prefixes
        return "'" + value
    return value


def compute_row_hash(row: Dict[str, str]) -> str:
    """Compute a deterministic hash of sorted row key-values for idempotency check."""
    normalized = "|".join(f"{k}:{str(v).strip()}" for k, v in sorted(row.items()))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_csv_content(csv_content: str, template_type: str) -> ValidationReport:
    """Validate raw CSV text against the specified template contract."""
    if template_type not in TEMPLATE_HEADERS:
        raise ValueError(f"Unknown template type '{template_type}'. Expected one of {list(TEMPLATE_HEADERS.keys())}")

    expected_headers = TEMPLATE_HEADERS[template_type]
    model_cls = MODEL_MAPPING[template_type]
    report = ValidationReport(template_type=template_type)

    reader = csv.reader(io.StringIO(csv_content))
    try:
        actual_headers = next(reader)
    except StopIteration:
        report.errors.append(RowError(0, None, "Empty CSV content"))
        return report

    # Clean BOM and spaces
    actual_headers = [h.strip().lstrip("\ufeff") for h in actual_headers]

    # Verify exact header presence
    if actual_headers != expected_headers:
        missing = set(expected_headers) - set(actual_headers)
        unexpected = set(actual_headers) - set(expected_headers)
        msg = f"Header mismatch. Expected {expected_headers}."
        if missing:
            msg += f" Missing: {list(missing)}."
        if unexpected:
            msg += f" Unexpected: {list(unexpected)}."
        report.errors.append(RowError(1, "headers", msg))
        return report

    seen_hashes = set()

    for row_idx, row in enumerate(reader, start=2):
        report.total_rows += 1
        if len(row) != len(expected_headers):
            report.rejected_rows += 1
            report.errors.append(RowError(row_idx, None, f"Expected {len(expected_headers)} columns, got {len(row)}"))
            continue

        raw_dict = {expected_headers[i]: sanitize_csv_cell(row[i].strip()) for i in range(len(expected_headers))}

        # Deduplication check
        row_hash = compute_row_hash(raw_dict)
        if row_hash in seen_hashes:
            report.duplicate_rows += 1
            report.rejected_rows += 1
            report.errors.append(RowError(row_idx, None, "Duplicate row detected"))
            continue
        seen_hashes.add(row_hash)

        # Convert empty strings to None for optional fields
        cleaned_dict = {k: (None if v == "" else v) for k, v in raw_dict.items()}

        try:
            record = model_cls.model_validate(cleaned_dict)
            report.valid_records.append(record)
            report.accepted_rows += 1
        except ValidationError as e:
            report.rejected_rows += 1
            for err in e.errors():
                loc = ".".join(str(l) for l in err["loc"])
                report.errors.append(RowError(row_idx, loc, err["msg"]))

    return report

