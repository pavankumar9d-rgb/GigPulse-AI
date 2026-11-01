"""CSV data import validation and commit endpoints."""

import json
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.errors import AppException
from api.schemas.imports import (
    ImportCommitRequest,
    ImportCommitResponse,
    ImportValidateRequest,
    ImportValidateResponse,
)
from gigpulse_core.db.importer import import_csv_content
from gigpulse_core.db.schema import ImportBatchModel
from gigpulse_core.validator import validate_csv_content

router = APIRouter(prefix="/imports", tags=["CSV Imports"])


@router.post("/validate", response_model=ImportValidateResponse)
def validate_import(payload: ImportValidateRequest):
    """Validate CSV content against template schema without committing any data."""
    try:
        report = validate_csv_content(payload.csv_content, payload.template_type)
    except ValueError as e:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_TEMPLATE_TYPE",
            message=str(e),
        )

    error_list = [{"row": e.row_number, "field": e.field, "error": e.error_message} for e in report.errors]

    return ImportValidateResponse(
        template_type=payload.template_type,
        total_rows=report.total_rows,
        accepted_rows=report.accepted_rows,
        rejected_rows=report.rejected_rows,
        duplicate_rows=report.duplicate_rows,
        is_valid=report.is_valid,
        errors=error_list,
        message="Validation complete. No rows committed to database.",
    )


@router.post("/commit", response_model=ImportCommitResponse, status_code=status.HTTP_201_CREATED)
def commit_import(
    payload: ImportCommitRequest,
    db: Session = Depends(get_db),
):
    """Validate and commit CSV records into the SQLite database with duplicate protection."""
    from api.config import settings
    if settings.DEMO_MODE:
        raise AppException(
            code="DEMO_MODE_FORBIDDEN",
            message="Import commits are disabled in public demo mode to preserve study data integrity.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    try:
        result = import_csv_content(
            session=db,
            csv_content=payload.csv_content,
            template_type=payload.template_type,
            filename=payload.filename or "upload.csv",
        )
    except ValueError as e:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_TEMPLATE_TYPE",
            message=str(e),
        )

    return ImportCommitResponse(
        batch_id=result.batch_id,
        file_hash=result.file_hash,
        template_type=result.template_type,
        status=result.status,
        total_rows=result.total_rows,
        accepted_rows=result.accepted_rows,
        rejected_rows=result.rejected_rows,
        duplicate_rows=result.duplicate_rows,
        already_imported=result.already_imported,
        errors=result.errors,
    )


@router.get("/{batch_id}/report")
def get_import_report(
    batch_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed validation and commit report for a previously uploaded batch."""
    batch = db.scalar(select(ImportBatchModel).where(ImportBatchModel.id == batch_id))
    if not batch:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"Import batch '{batch_id}' was not found.",
        )

    report_details = []
    if batch.validation_report_json:
        try:
            report_details = json.loads(batch.validation_report_json)
        except Exception:
            pass

    return {
        "batch_id": batch.id,
        "filename": batch.filename_safe,
        "file_hash": batch.file_hash,
        "status": batch.status,
        "row_count": batch.row_count,
        "accepted_count": batch.accepted_count,
        "rejected_count": batch.rejected_count,
        "duplicate_count": batch.duplicate_count,
        "created_at": batch.created_at,
        "errors": report_details,
    }

