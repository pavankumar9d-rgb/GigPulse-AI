"""Model registry, diagnostic evaluations, and training endpoints."""

import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.errors import AppException
from api.schemas.governance import (
    ModelListResponse,
    ModelVersionResponse,
)
from gigpulse_core.db.schema import ModelVersionModel
from gigpulse_core.ml.training import train_all_models

router = APIRouter(prefix="/models", tags=["Model Registry & Evaluation"])
MODELS_DIR = Path("models")


def _sync_models_from_disk_if_needed(db: Session):
    """Ensure database has model records if artifact metadata exists on disk."""
    earnings_meta = MODELS_DIR / "earnings_metadata_v1.json"
    demand_meta = MODELS_DIR / "demand_metadata_v1.json"

    if earnings_meta.exists():
        exist_e = db.scalar(select(ModelVersionModel).where(ModelVersionModel.model_name == "earnings_predictor"))
        if not exist_e:
            with open(earnings_meta, "r", encoding="utf-8") as f:
                data_e = json.load(f)
            m_e = ModelVersionModel(
                model_name="earnings_predictor",
                version=data_e.get("model_version", "v1.0.0"),
                target_definition="net_earnings_paise_per_online_hour",
                training_data_ref="db://work_sessions+deliveries+expenses",
                feature_schema_version="v1",
                evaluation_json=json.dumps(data_e),
                limitations=(
                    "Trained on synthetic Bangalore multi-platform delivery dataset. "
                    "Predictions are decision-support estimates, not guaranteed earnings."
                ),
                status="approved",
            )
            db.add(m_e)

    if demand_meta.exists():
        exist_d = db.scalar(select(ModelVersionModel).where(ModelVersionModel.model_name == "demand_forecaster"))
        if not exist_d:
            with open(demand_meta, "r", encoding="utf-8") as f:
                data_d = json.load(f)
            m_d = ModelVersionModel(
                model_name="demand_forecaster",
                version=data_d.get("model_version", "v1.0.0"),
                target_definition="observed_deliveries_per_30min",
                training_data_ref="db://zone_demand_observations",
                feature_schema_version="v1",
                evaluation_json=json.dumps(data_d),
                limitations=(
                    "Forecast represents observed synthetic deliveries in spatial study zones. "
                    "Individual observations are strictly distinguished from market demand."
                ),
                status="approved",
            )
            db.add(m_d)

    db.commit()


@router.get("", response_model=ModelListResponse)
def list_models(db: Session = Depends(get_db)):
    """List all registered models with their evaluation summaries and status."""
    _sync_models_from_disk_if_needed(db)

    stmt = select(ModelVersionModel).order_by(ModelVersionModel.created_at.desc())
    models = db.execute(stmt).scalars().all()

    items = []
    for m in models:
        eval_data = None
        if m.evaluation_json:
            try:
                eval_data = json.loads(m.evaluation_json)
            except Exception:
                eval_data = None

        items.append(ModelVersionResponse(
            id=m.id,
            model_name=m.model_name,
            version=m.version,
            target_definition=m.target_definition,
            training_data_ref=m.training_data_ref,
            feature_schema_version=m.feature_schema_version,
            evaluation=eval_data,
            limitations=m.limitations,
            status=m.status,
            created_at=m.created_at,
        ))

    return ModelListResponse(project="GigPulse AI", models=items)


@router.get("/{model_id}", response_model=ModelVersionResponse)
def get_model_details(model_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed metadata, backtest metrics, and limitations for a specific model."""
    _sync_models_from_disk_if_needed(db)

    stmt = select(ModelVersionModel).where(ModelVersionModel.id == model_id)
    m = db.execute(stmt).scalar_one_or_none()
    if not m:
        # Also allow querying by model_name
        stmt_name = select(ModelVersionModel).where(ModelVersionModel.model_name == model_id)
        m = db.execute(stmt_name).scalar_one_or_none()

    if not m:
        raise AppException(
            code="MODEL_NOT_FOUND",
            message=f"Model version '{model_id}' was not found in registry.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    eval_data = None
    if m.evaluation_json:
        try:
            eval_data = json.loads(m.evaluation_json)
        except Exception:
            eval_data = None

    return ModelVersionResponse(
        id=m.id,
        model_name=m.model_name,
        version=m.version,
        target_definition=m.target_definition,
        training_data_ref=m.training_data_ref,
        feature_schema_version=m.feature_schema_version,
        evaluation=eval_data,
        limitations=m.limitations,
        status=m.status,
        created_at=m.created_at,
    )


@router.post("/train", response_model=ModelListResponse)
def trigger_model_training(db: Session = Depends(get_db)):
    """Trigger full retraining of earnings and demand forecasting pipelines."""
    from api.config import settings
    if settings.DEMO_MODE:
        raise AppException(
            code="DEMO_MODE_FORBIDDEN",
            message="Model retraining is disabled in public demo mode to conserve cloud resources.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    try:
        train_all_models()
        return list_models(db)
    except Exception as e:
        raise AppException(
            code="TRAINING_ERROR",
            message=f"Model retraining failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
