"""Safe CSV data importer for GigPulse AI.

Uses Phase 1 validation engine to validate CSV content, tracks import batches,
safely handles duplicates and malformed records, and guarantees idempotent imports.
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from gigpulse_core.models import (
    DeliveryRecord,
    ExpenseRecord,
    WorkSessionRecord,
    ZoneDemandRecord,
)
from gigpulse_core.validator import (
    RowError,
    ValidationReport,
    compute_row_hash,
    validate_csv_content,
)
from gigpulse_core.db.repository import (
    get_or_create_platform,
    get_or_create_worker_profile,
    get_or_create_zone,
)
from gigpulse_core.db.schema import (
    DeliveryModel,
    ExpenseModel,
    ImportBatchModel,
    WorkSessionModel,
    ZoneDemandObservationModel,
)


@dataclass
class ImportBatchResult:
    batch_id: str
    file_hash: str
    template_type: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    already_imported: bool = False
    errors: List[Dict[str, Any]] = field(default_factory=list)


def import_csv_content(
    session: Session,
    csv_content: str,
    template_type: str,
    filename: str = "upload.csv",
    owner_user_id: Optional[str] = None,
) -> ImportBatchResult:
    """Validate and safely persist records from raw CSV text into SQLite."""
    file_hash = hashlib.sha256(csv_content.encode("utf-8")).hexdigest()

    # 1. Idempotency check: Has this exact file already been committed?
    existing_batch_stmt = select(ImportBatchModel).where(
        ImportBatchModel.file_hash == file_hash,
        ImportBatchModel.status == "committed",
    )
    existing_batch = session.execute(existing_batch_stmt).scalar_one_or_none()
    if existing_batch:
        return ImportBatchResult(
            batch_id=existing_batch.id,
            file_hash=file_hash,
            template_type=template_type,
            status="committed",
            total_rows=existing_batch.row_count,
            accepted_rows=existing_batch.accepted_count,
            rejected_rows=existing_batch.rejected_count,
            duplicate_rows=existing_batch.duplicate_count,
            already_imported=True,
        )

    # 2. Validate CSV content using Phase 1 contract validator
    report: ValidationReport = validate_csv_content(csv_content, template_type)

    batch_model = ImportBatchModel(
        owner_user_id=owner_user_id,
        filename_safe=Path(filename).name,
        file_hash=file_hash,
        detected_format="csv",
        status="committed" if report.accepted_rows > 0 else "rejected",
        row_count=report.total_rows,
        accepted_count=report.accepted_rows,
        rejected_count=report.rejected_rows,
        duplicate_count=report.duplicate_rows,
        validation_report_json=json.dumps([{"row": e.row_number, "field": e.field, "error": e.error_message} for e in report.errors]),
    )
    session.add(batch_model)
    session.flush()

    if report.accepted_rows == 0:
        session.commit()
        return ImportBatchResult(
            batch_id=batch_model.id,
            file_hash=file_hash,
            template_type=template_type,
            status="rejected",
            total_rows=report.total_rows,
            accepted_rows=0,
            rejected_rows=report.rejected_rows,
            duplicate_rows=report.duplicate_rows,
            errors=[{"row": e.row_number, "field": e.field, "error": e.error_message} for e in report.errors],
        )

    # 3. Safe insertion of validated records
    if template_type == "work_sessions":
        for rec in report.valid_records:
            assert isinstance(rec, WorkSessionRecord)
            get_or_create_worker_profile(session, rec.worker_ref)
            get_or_create_platform(session, rec.platform_code)

            r_hash = compute_row_hash(rec.model_dump())
            session_model = WorkSessionModel(
                worker_ref=rec.worker_ref,
                platform_code=rec.platform_code,
                started_at=rec.started_at,
                ended_at=rec.ended_at,
                status=rec.status.value,
                source_type=rec.source_type.value,
                timezone=rec.timezone,
                import_batch_id=batch_model.id,
                row_hash=r_hash,
            )
            session.add(session_model)

    elif template_type == "deliveries":
        for rec in report.valid_records:
            assert isinstance(rec, DeliveryRecord)
            get_or_create_worker_profile(session, rec.worker_ref)
            get_or_create_platform(session, rec.platform_code)
            if rec.pickup_zone_code:
                get_or_create_zone(session, rec.pickup_zone_code)
            if rec.drop_zone_code:
                get_or_create_zone(session, rec.drop_zone_code)

            r_hash = compute_row_hash(rec.model_dump())
            delivery_model = DeliveryModel(
                worker_ref=rec.worker_ref,
                platform_code=rec.platform_code,
                session_ref=rec.session_ref,
                external_ref_hash=rec.session_ref,
                accepted_at=rec.accepted_at,
                completed_at=rec.completed_at,
                pickup_zone_code=rec.pickup_zone_code,
                drop_zone_code=rec.drop_zone_code,
                payout_paise=rec.payout_paise,
                incentive_paise=rec.incentive_paise,
                tip_paise=rec.tip_paise,
                distance_m=rec.distance_m,
                duration_seconds=rec.duration_seconds,
                status=rec.status.value,
                target_quality=rec.target_quality.value,
                source_type=rec.source_type.value,
                import_batch_id=batch_model.id,
                row_hash=r_hash,
            )
            session.add(delivery_model)

    elif template_type == "expenses":
        for rec in report.valid_records:
            assert isinstance(rec, ExpenseRecord)
            get_or_create_worker_profile(session, rec.worker_ref)

            r_hash = compute_row_hash(rec.model_dump())
            expense_model = ExpenseModel(
                worker_ref=rec.worker_ref,
                session_ref=rec.session_ref,
                occurred_at=rec.occurred_at,
                category=rec.category.value,
                amount_paise=rec.amount_paise,
                source_type=rec.source_type.value,
                notes=rec.notes,
                import_batch_id=batch_model.id,
                row_hash=r_hash,
            )
            session.add(expense_model)

    elif template_type == "zone_demand":
        for rec in report.valid_records:
            assert isinstance(rec, ZoneDemandRecord)
            get_or_create_zone(session, rec.zone_code)

            r_hash = compute_row_hash(rec.model_dump())
            # Duplicate check for unique interval
            dup_check = select(ZoneDemandObservationModel).where(
                ZoneDemandObservationModel.zone_code == rec.zone_code,
                ZoneDemandObservationModel.interval_start == rec.interval_start,
                ZoneDemandObservationModel.interval_minutes == rec.interval_minutes,
                ZoneDemandObservationModel.target_type == rec.target_type.value,
            )
            if session.execute(dup_check).scalar_one_or_none():
                # Skip duplicate interval safely
                continue

            demand_model = ZoneDemandObservationModel(
                zone_code=rec.zone_code,
                interval_start=rec.interval_start,
                interval_minutes=rec.interval_minutes,
                orders_requested=rec.orders_requested,
                orders_completed=rec.orders_completed,
                deliveries_observed=rec.deliveries_observed,
                demand_proxy_value=rec.demand_proxy_value,
                target_type=rec.target_type.value,
                coverage_fraction=rec.coverage_fraction,
                target_quality=rec.target_quality.value,
                source_type=rec.source_type.value,
                import_batch_id=batch_model.id,
                row_hash=r_hash,
            )
            session.add(demand_model)

    session.commit()
    return ImportBatchResult(
        batch_id=batch_model.id,
        file_hash=file_hash,
        template_type=template_type,
        status="committed",
        total_rows=report.total_rows,
        accepted_rows=report.accepted_rows,
        rejected_rows=report.rejected_rows,
        duplicate_rows=report.duplicate_rows,
        errors=[{"row": e.row_number, "field": e.field, "error": e.error_message} for e in report.errors],
    )


def import_csv_file(session: Session, file_path: Path, template_type: str) -> ImportBatchResult:
    """Convenience helper to import a CSV file by path."""
    content = Path(file_path).read_text(encoding="utf-8")
    return import_csv_content(session, content, template_type, filename=Path(file_path).name)

