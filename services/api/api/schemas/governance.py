"""Pydantic schemas for model registry and governance."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ModelVersionResponse(BaseModel):
    id: str
    model_name: str
    version: str
    target_definition: str
    training_data_ref: str
    feature_schema_version: str
    evaluation: Optional[Dict[str, Any]]
    limitations: str
    status: str
    created_at: datetime


class ModelListResponse(BaseModel):
    project: str = "GigPulse AI"
    models: List[ModelVersionResponse]


class DataExportResponse(BaseModel):
    worker_ref: str
    exported_at: str
    counts: Dict[str, int]
    work_sessions: List[Dict[str, Any]]
    deliveries: List[Dict[str, Any]]
    expenses: List[Dict[str, Any]]


class AccountDeletionResponse(BaseModel):
    worker_ref: str
    deleted: bool
    deleted_counts: Dict[str, int]
    message: str

