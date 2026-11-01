"""Unified model training, backtesting, and registry pipeline for GigPulse AI.

Trains earnings prediction and demand forecasting models on chronological splits,
computes comparative metrics against baselines, persists artifacts to models/,
and records versions in the SQLite database model_versions table.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.orm import Session

from gigpulse_core.db.database import get_engine, get_session_factory, init_db
from gigpulse_core.db.schema import ModelVersionModel
from gigpulse_core.ml.demand import (
    DemandForecastPipeline,
    extract_zone_demand_data,
)
from gigpulse_core.ml.earnings import (
    EarningsModelPipeline,
    extract_earnings_training_data,
)


def train_all_models(db_path: str = "gigpulse.db", artifacts_dir: Path = Path("models")) -> Dict[str, Any]:
    """Train both earnings and demand models, evaluate backtests, and save to registry."""
    print(f"Connecting to database: {db_path}")
    engine = get_engine(db_path=db_path)
    init_db(engine)
    session_factory = get_session_factory(engine)

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    with session_factory() as session:
        # 1. Train & Evaluate Earnings Prediction Pipeline
        print("\n--- Training Earnings Prediction Models ---")
        earnings_df = extract_earnings_training_data(session)
        print(f"Extracted {len(earnings_df)} historical work sessions for training.")

        earnings_pipeline = EarningsModelPipeline(model_version="v1.0.0")
        earnings_eval = earnings_pipeline.train_and_evaluate(earnings_df)
        earnings_pipeline.save(target_dir=artifacts_dir)
        results["earnings"] = earnings_eval

        # Save to SQLite model_versions table
        existing_e = session.scalar(
            select(ModelVersionModel).where(
                ModelVersionModel.model_name == "earnings_predictor",
                ModelVersionModel.version == "v1.0.0",
            )
        )
        if not existing_e:
            m_earnings = ModelVersionModel(
                model_name="earnings_predictor",
                version="v1.0.0",
                target_definition="net_earnings_paise_per_online_hour",
                training_data_ref=f"db://work_sessions+deliveries+expenses ({len(earnings_df)} rows)",
                feature_schema_version="v1",
                evaluation_json=json.dumps(earnings_eval),
                limitations=earnings_pipeline.limitations,
                status="approved",
            )
            session.add(m_earnings)
        else:
            existing_e.evaluation_json = json.dumps(earnings_eval)
            existing_e.status = "approved"

        # 2. Train & Evaluate Zone Demand Forecasting Pipeline
        print("\n--- Training Zone Demand Forecasting Models ---")
        demand_df = extract_zone_demand_data(session, target_type="observed_deliveries")
        print(f"Extracted {len(demand_df)} zone demand intervals for training.")

        demand_pipeline = DemandForecastPipeline(model_version="v1.0.0", target_type="observed_deliveries")
        demand_eval = demand_pipeline.train_and_evaluate(demand_df)
        demand_pipeline.save(target_dir=artifacts_dir)
        results["demand"] = demand_eval

        existing_d = session.scalar(
            select(ModelVersionModel).where(
                ModelVersionModel.model_name == "demand_forecaster",
                ModelVersionModel.version == "v1.0.0",
            )
        )
        if not existing_d:
            m_demand = ModelVersionModel(
                model_name="demand_forecaster",
                version="v1.0.0",
                target_definition="observed_deliveries_per_30min",
                training_data_ref=f"db://zone_demand_observations ({len(demand_df)} rows)",
                feature_schema_version="v1",
                evaluation_json=json.dumps(demand_eval),
                limitations=demand_pipeline.limitations,
                status="approved",
            )
            session.add(m_demand)
        else:
            existing_d.evaluation_json = json.dumps(demand_eval)
            existing_d.status = "approved"

        session.commit()

    return results


def print_evaluation_summary(results: Dict[str, Any]) -> None:
    """Print readable academic evaluation table."""
    print("\n" + "=" * 80)
    print("           GIGPULSE AI — MODEL BACKTEST EVALUATION SUMMARY")
    print("=" * 80)

    # Earnings Summary
    e_res = results.get("earnings", {})
    e_models = e_res.get("models_comparison", {})
    print("\n[Target: Net Earnings (INR / Online Hour)]")
    print(f"{'Model / Baseline':<40} | {'MAE (INR)':<10} | {'RMSE (INR)':<10} | {'WAPE':<8} | {'R²':<8}")
    print("-" * 80)
    for name, m in e_models.items():
        print(f"{name:<40} | {m['mae_inr']:<10.2f} | {m['rmse_inr']:<10.2f} | {m['wape']:<8.4f} | {m['r2']:<8.4f}")

    e_unc = e_res.get("uncertainty_evaluation", {})
    print(f"\nUncertainty Calibration (80% Nominal Interval):")
    print(f"  Empirical Coverage: {e_unc.get('empirical_coverage_pct')}%")
    print(f"  Pinball Loss Q10 / Q50 / Q90: {e_unc.get('pinball_loss_q10')} / {e_unc.get('pinball_loss_q50')} / {e_unc.get('pinball_loss_q90')}")

    # Demand Summary
    d_res = results.get("demand", {})
    d_models = d_res.get("models_comparison", {})
    print("\n[Target: Zone Demand (Deliveries / 30-min bucket)]")
    print(f"{'Model / Baseline':<40} | {'MAE (count)':<12} | {'RMSE (count)':<12} | {'WAPE':<8}")
    print("-" * 80)
    for name, m in d_models.items():
        print(f"{name:<40} | {m['mae']:<12.2f} | {m['rmse']:<12.2f} | {m['wape']:<8.4f}")

    d_unc = d_res.get("uncertainty_evaluation", {})
    print(f"\nDemand Interval Calibration:")
    print(f"  Empirical Coverage: {d_unc.get('empirical_coverage_pct')}%")
    print("=" * 80 + "\n")


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else "gigpulse.db"
    res = train_all_models(db_path=db_path)
    print_evaluation_summary(res)


if __name__ == "__main__":
    main()

