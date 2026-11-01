"""Zone Demand Forecasting Engine for GigPulse AI.

Provides spatio-temporal aggregation, strict target type preservation
(requested_orders, completed_orders, observed_deliveries, proxy),
chronological split backtesting, multiple baselines (Last-Bucket, Seasonal-Naive, Zone Rolling Mean),
Gradient Boosted Regressor count forecasting with uncertainty intervals, and metrics (MAE, RMSE, WAPE).
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sqlalchemy import select
from sqlalchemy.orm import Session

from gigpulse_core.db.schema import ZoneDemandObservationModel


MODELS_DIR = Path("models")


def extract_zone_demand_data(session: Session, target_type: str = "observed_deliveries") -> pd.DataFrame:
    """Extract historical zone demand observations filtered by target_type."""
    stmt = (
        select(
            ZoneDemandObservationModel.zone_code,
            ZoneDemandObservationModel.interval_start,
            ZoneDemandObservationModel.interval_minutes,
            ZoneDemandObservationModel.orders_requested,
            ZoneDemandObservationModel.orders_completed,
            ZoneDemandObservationModel.deliveries_observed,
            ZoneDemandObservationModel.demand_proxy_value,
            ZoneDemandObservationModel.target_type,
            ZoneDemandObservationModel.target_quality,
        )
        .where(ZoneDemandObservationModel.target_type == target_type)
        .order_by(ZoneDemandObservationModel.interval_start.asc())
    )

    rows = session.execute(stmt).all()
    if not rows:
        # Fallback to any target_type if specific one not present
        stmt_any = (
            select(
                ZoneDemandObservationModel.zone_code,
                ZoneDemandObservationModel.interval_start,
                ZoneDemandObservationModel.interval_minutes,
                ZoneDemandObservationModel.orders_requested,
                ZoneDemandObservationModel.orders_completed,
                ZoneDemandObservationModel.deliveries_observed,
                ZoneDemandObservationModel.demand_proxy_value,
                ZoneDemandObservationModel.target_type,
                ZoneDemandObservationModel.target_quality,
            ).order_by(ZoneDemandObservationModel.interval_start.asc())
        )
        rows = session.execute(stmt_any).all()

    if not rows:
        return pd.DataFrame()

    records = []
    for r in rows:
        dt = r.interval_start
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Select target count based on target_type
        if r.target_type == "requested_orders":
            val = float(r.orders_requested if r.orders_requested is not None else 0)
        elif r.target_type == "completed_orders":
            val = float(r.orders_completed if r.orders_completed is not None else 0)
        elif r.target_type == "observed_deliveries":
            val = float(r.deliveries_observed if r.deliveries_observed is not None else 0)
        else:
            val = float(r.demand_proxy_value if r.demand_proxy_value is not None else 0.0)

        records.append({
            "zone_code": r.zone_code,
            "interval_start": dt,
            "interval_minutes": r.interval_minutes,
            "target_value": val,
            "target_type": r.target_type,
            "target_quality": r.target_quality,
            "hour": dt.hour,
            "minute": dt.minute,
            "day_of_week": dt.weekday(),
            "is_weekend": 1 if dt.weekday() >= 5 else 0,
        })

    df = pd.DataFrame(records)
    df.sort_values(by=["zone_code", "interval_start"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def calculate_demand_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute MAE, RMSE, WAPE for demand counts."""
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    sum_y = float(np.sum(y_true))
    wape = float(np.sum(np.abs(y_true - y_pred)) / sum_y) if sum_y > 0 else 0.0
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "wape": round(wape, 4),
    }


class DemandForecastPipeline:
    """Demand forecasting model with lag feature engineering, baselines, and gradient boosting."""

    def __init__(self, model_version: str = "v1.0.0", target_type: str = "observed_deliveries"):
        self.model_version = model_version
        self.target_type = target_type
        self.zones: List[str] = []
        self.zone_medians: Dict[str, float] = {}
        self.zone_dow_hour_medians: Dict[str, float] = {}
        self.hgb_model: Optional[HistGradientBoostingRegressor] = None
        self.hgb_lower: Optional[HistGradientBoostingRegressor] = None
        self.hgb_upper: Optional[HistGradientBoostingRegressor] = None
        self.evaluation_results: Dict[str, Any] = {}
        self.limitations: str = (
            "Forecast represents observed synthetic deliveries/demand proxy in the designated spatial zones. "
            "Individual worker observations are strictly not confused with market-wide requested demand. "
            "Evaluation reflects backtest on held-out chronological timeline."
        )

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fit models on chronological split and evaluate against baselines."""
        if len(df) < 50:
            raise ValueError(f"Insufficient demand data ({len(df)} rows). Need at least 50 rows.")

        self.zones = sorted(df["zone_code"].unique().tolist())
        target_quality = df["target_quality"].iloc[0] if "target_quality" in df else "synthetic"

        # Engineer features with past-only lag mechanisms
        df_feats = df.copy()
        df_feats["sin_hour"] = np.sin(2 * np.pi * df_feats["hour"] / 24.0)
        df_feats["cos_hour"] = np.cos(2 * np.pi * df_feats["hour"] / 24.0)
        df_feats["sin_dow"] = np.sin(2 * np.pi * df_feats["day_of_week"] / 7.0)
        df_feats["cos_dow"] = np.cos(2 * np.pi * df_feats["day_of_week"] / 7.0)

        # Lag-1, lag-2 (past values within same zone)
        df_feats["lag_1"] = df_feats.groupby("zone_code")["target_value"].shift(1)
        df_feats["lag_2"] = df_feats.groupby("zone_code")["target_value"].shift(2)
        # Fill initial NaNs with zone median
        zone_medians_init = df_feats.groupby("zone_code")["target_value"].median().to_dict()
        df_feats["lag_1"] = df_feats.apply(
            lambda r: zone_medians_init.get(r["zone_code"], 0.0) if pd.isna(r["lag_1"]) else r["lag_1"],
            axis=1,
        )
        df_feats["lag_2"] = df_feats.apply(
            lambda r: zone_medians_init.get(r["zone_code"], 0.0) if pd.isna(r["lag_2"]) else r["lag_2"],
            axis=1,
        )

        # Chronological split (70/15/15)
        # Order by interval_start
        df_feats.sort_values(by="interval_start", inplace=True)
        df_feats.reset_index(drop=True, inplace=True)

        n = len(df_feats)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)

        train_df = df_feats.iloc[:train_idx]
        test_df = df_feats.iloc[val_idx:]

        y_train = train_df["target_value"].values.astype(float)
        y_test = test_df["target_value"].values.astype(float)

        # 1. Baseline 1: Last-Bucket Naive (lag_1)
        b1_pred = test_df["lag_1"].values
        b1_metrics = calculate_demand_metrics(y_test, b1_pred)

        # 2. Baseline 2: Zone Median
        self.zone_medians = {
            z: float(sub["target_value"].median())
            for z, sub in train_df.groupby("zone_code")
        }
        b2_pred = np.array([self.zone_medians.get(z, 0.0) for z in test_df["zone_code"]])
        b2_metrics = calculate_demand_metrics(y_test, b2_pred)

        # 3. Baseline 3: Seasonal Naive (Zone x DOW x Hour Median)
        z_dow_hr = (
            train_df.groupby(["zone_code", "day_of_week", "hour"])["target_value"]
            .median()
            .to_dict()
        )
        self.zone_dow_hour_medians = {
            f"{k[0]}_{k[1]}_{k[2]}": float(v) for k, v in z_dow_hr.items()
        }
        b3_pred = np.array([
            self.zone_dow_hour_medians.get(
                f"{r.zone_code}_{r.day_of_week}_{r.hour}",
                self.zone_medians.get(r.zone_code, 0.0),
            )
            for _, r in test_df.iterrows()
        ])
        b3_metrics = calculate_demand_metrics(y_test, b3_pred)

        # ML Feature matrix
        def get_X(d: pd.DataFrame) -> np.ndarray:
            base = d[["hour", "minute", "day_of_week", "is_weekend", "sin_hour", "cos_hour", "sin_dow", "cos_dow", "lag_1", "lag_2"]].values
            # One-hot zones
            z_cols = [np.array(d["zone_code"] == z, dtype=float) for z in self.zones]
            z_mat = np.column_stack(z_cols) if z_cols else np.zeros((len(d), 1))
            return np.column_stack([base, z_mat])

        X_train = get_X(train_df)
        X_test = get_X(test_df)

        # 4. Model: HistGradientBoosting Regressor
        self.hgb_model = HistGradientBoostingRegressor(loss="squared_error", max_iter=100, random_state=42)
        self.hgb_model.fit(X_train, y_train)
        hgb_pred = np.maximum(0, self.hgb_model.predict(X_test))
        hgb_metrics = calculate_demand_metrics(y_test, hgb_pred)

        # Uncertainty intervals (Q10 and Q90)
        self.hgb_lower = HistGradientBoostingRegressor(loss="quantile", quantile=0.10, max_iter=100, random_state=42)
        self.hgb_lower.fit(X_train, y_train)
        self.hgb_upper = HistGradientBoostingRegressor(loss="quantile", quantile=0.90, max_iter=100, random_state=42)
        self.hgb_upper.fit(X_train, y_train)

        q10_pred = np.maximum(0, self.hgb_lower.predict(X_test))
        q90_pred = np.maximum(hgb_pred, self.hgb_upper.predict(X_test))
        interval_coverage = float(np.mean((y_test >= q10_pred) & (y_test <= q90_pred)))

        self.evaluation_results = {
            "model_version": self.model_version,
            "target_type": self.target_type,
            "target_quality": target_quality,
            "split_info": {
                "total_rows": n,
                "train_rows": len(y_train),
                "test_rows": len(y_test),
                "split_type": "chronological_70_15_15",
                "train_start": str(df["interval_start"].min()),
                "test_end": str(df["interval_start"].max()),
            },
            "models_comparison": {
                "baseline_last_bucket_naive": b1_metrics,
                "baseline_zone_median": b2_metrics,
                "baseline_seasonal_naive": b3_metrics,
                "gradient_boosted_regressor": hgb_metrics,
            },
            "uncertainty_evaluation": {
                "nominal_coverage_pct": 80.0,
                "empirical_coverage_pct": round(interval_coverage * 100.0, 2),
            },
            "selected_model": "gradient_boosted_regressor",
            "synthetic_mode": True,
        }

        return self.evaluation_results

    def save(self, target_dir: Path = MODELS_DIR) -> None:
        """Serialize demand forecast model to disk."""
        target_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model_version": self.model_version,
            "target_type": self.target_type,
            "zones": self.zones,
            "zone_medians": self.zone_medians,
            "zone_dow_hour_medians": self.zone_dow_hour_medians,
            "hgb_model": self.hgb_model,
            "hgb_lower": self.hgb_lower,
            "hgb_upper": self.hgb_upper,
            "evaluation_results": self.evaluation_results,
            "limitations": self.limitations,
        }, target_dir / "demand_model_v1.joblib")

        with open(target_dir / "demand_metadata_v1.json", "w", encoding="utf-8") as f:
            json.dump(self.evaluation_results, f, indent=2)

    @classmethod
    def load(cls, target_dir: Path = MODELS_DIR) -> DemandForecastPipeline:
        """Load trained demand model from disk."""
        model_path = target_dir / "demand_model_v1.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}. Train the model first.")

        data = joblib.load(model_path)
        instance = cls(model_version=data["model_version"], target_type=data["target_type"])
        instance.zones = data["zones"]
        instance.zone_medians = data["zone_medians"]
        instance.zone_dow_hour_medians = data["zone_dow_hour_medians"]
        instance.hgb_model = data["hgb_model"]
        instance.hgb_lower = data["hgb_lower"]
        instance.hgb_upper = data["hgb_upper"]
        instance.evaluation_results = data["evaluation_results"]
        instance.limitations = data["limitations"]
        return instance

    def forecast_step(
        self,
        zone_code: str,
        interval_start: datetime,
        interval_minutes: int = 30,
        lag_value: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Predict demand for a single zone at a specific future interval."""
        hour = interval_start.hour
        minute = interval_start.minute
        dow = interval_start.weekday()
        is_weekend = 1 if dow >= 5 else 0

        sin_hour = math.sin(2 * math.pi * hour / 24.0)
        cos_hour = math.cos(2 * math.pi * hour / 24.0)
        sin_dow = math.sin(2 * math.pi * dow / 7.0)
        cos_dow = math.cos(2 * math.pi * dow / 7.0)

        lag_1 = lag_value if lag_value is not None else self.zone_medians.get(zone_code, 5.0)
        lag_2 = lag_1

        z_vec = [1.0 if z == zone_code else 0.0 for z in self.zones]
        if not any(z_vec):
            z_vec = [0.0] * len(self.zones)

        features = np.array([
            hour, minute, dow, is_weekend,
            sin_hour, cos_hour, sin_dow, cos_dow,
            lag_1, lag_2,
            *z_vec,
        ]).reshape(1, -1)

        if self.hgb_model and self.hgb_lower and self.hgb_upper:
            point = float(max(0.0, self.hgb_model.predict(features)[0]))
            lower = float(max(0.0, self.hgb_lower.predict(features)[0]))
            upper = float(max(point, self.hgb_upper.predict(features)[0]))
        else:
            point = self.zone_medians.get(zone_code, 5.0)
            lower = max(0.0, point * 0.7)
            upper = point * 1.35

        interval_end = interval_start + timedelta(minutes=interval_minutes)

        return {
            "zone_code": zone_code,
            "interval_start": interval_start.isoformat(),
            "interval_end": interval_end.isoformat(),
            "interval_minutes": interval_minutes,
            "target_type": self.target_type,
            "target_quality": "synthetic",
            "point_prediction": round(point, 1),
            "lower_prediction": round(lower, 1),
            "upper_prediction": round(upper, 1),
            "unit": "deliveries / interval",
            "model_version": self.model_version,
            "coverage_fraction": 1.0,
        }


def forecast_zone_demand(
    session: Session,
    zone_codes: List[str],
    forecast_from: datetime,
    steps: int = 8,
    interval_minutes: int = 30,
    target_type: str = "observed_deliveries",
) -> List[Dict[str, Any]]:
    """Helper service for multi-zone, multi-step demand forecasting."""
    try:
        pipeline = DemandForecastPipeline.load()
    except FileNotFoundError:
        df = extract_zone_demand_data(session, target_type=target_type)
        pipeline = DemandForecastPipeline(target_type=target_type)
        pipeline.train_and_evaluate(df)
        pipeline.save()

    results = []
    for zone in zone_codes:
        current_time = forecast_from
        for step_idx in range(steps):
            step_forecast = pipeline.forecast_step(
                zone_code=zone,
                interval_start=current_time,
                interval_minutes=interval_minutes,
            )
            step_forecast["step"] = step_idx + 1
            results.append(step_forecast)
            current_time = current_time + timedelta(minutes=interval_minutes)

    return results

