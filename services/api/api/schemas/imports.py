"""Schemas for CSV Import validation and commitment."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ImportValidateRequest(BaseModel):
    template_type: str = Field(..., description="One of 'deliveries', 'work_sessions', 'expenses', 'zone_demand'")
    csv_content: str = Field(..., min_length=1, description="Raw CSV string content")
    filename: Optional[str] = "upload.csv"


class ImportValidateResponse(BaseModel):
    template_type: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    is_valid: bool
    errors: List[Dict[str, Any]]
    message: str = "Validation complete. No rows committed."


class ImportCommitRequest(BaseModel):
    template_type: str = Field(..., description="One of 'deliveries', 'work_sessions', 'expenses', 'zone_demand'")
    csv_content: str = Field(..., min_length=1, description="Raw CSV string content")
    filename: Optional[str] = "upload.csv"


class ImportCommitResponse(BaseModel):
    batch_id: str
    file_hash: str
    template_type: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    already_imported: bool
    errors: List[Dict[str, Any]]

