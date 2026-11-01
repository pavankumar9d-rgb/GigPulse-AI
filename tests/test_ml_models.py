"""Automated regression and verification tests for GigPulse AI ML pipelines."""

from datetime import datetime, timedelta, timezone
import pytest
from gigpulse_core.db.database import get_engine, get_session_factory, init_db
from gigpulse_core.ml.demand import (
    DemandForecastPipeline,
    extract_zone_demand_data,
    forecast_zone_demand,
)
from gigpulse_core.ml.earnings import (
    EarningsModelPipeline,
    extract_earnings_training_data,
    predict_worker_earnings,
)
from gigpulse_core.ml.optimizer import (
    RecommendationEngine,
    generate_recommendations,
)


@pytest.fixture(scope="module")
def seeded_db():
    engine = get_engine("gigpulse.db")
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        yield session


def test_earnings_training_and_chronological_evaluation(seeded_db):
    """Verify earnings pipeline trains with zero time-leakage and outperforms baseline."""
    df = extract_earnings_training_data(seeded_db)
    assert len(df) >= 100, f"Expected at least 100 sessions, got {len(df)}"

    pipeline = EarningsModelPipeline(model_version="test_v1")
    eval_res = pipeline.train_and_evaluate(df)

    assert eval_res["model_version"] == "test_v1"
    assert "models_comparison" in eval_res

    comparisons = eval_res["models_comparison"]
    b1_mae = comparisons["baseline_global_median"]["mae_inr"]
    linear_mae = comparisons["linear_ridge_regression"]["mae_inr"]
    gbt_mae = comparisons["gradient_boosted_trees_q50"]["mae_inr"]

    # Linear and GBT models must have lower error than naive global median
    assert linear_mae < b1_mae
    assert gbt_mae < b1_mae

    # Verify uncertainty interval coverage
    unc = eval_res["uncertainty_evaluation"]
    assert "empirical_coverage_pct" in unc
    assert unc["empirical_coverage_pct"] > 40.0


def test_earnings_prediction_contract(seeded_db):
    """Verify earnings prediction schema and integer paise integrity."""
    start_at = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
    end_at = start_at + timedelta(hours=4)

    pred = predict_worker_earnings(
        session=seeded_db,
        worker_ref="worker_w01",
        platform_code="flash_drop",
        zone_code="zone_koramangala",
        start_at=start_at,
        end_at=end_at,
    )

    assert pred["target"] == "net_earnings_paise_per_online_hour"
    assert pred["unit"] == "INR/hour"
    assert pred["q10_paise_per_hour"] <= pred["q50_paise_per_hour"]
    assert pred["q50_paise_per_hour"] <= pred["q90_paise_per_hour"]
    assert pred["expected_gross_paise"] >= pred["expected_net_paise"]
    assert pred["expected_net_paise"] > 0
    assert pred["duration_hours"] == 4.0


def test_demand_training_and_baselines(seeded_db):
    """Verify demand forecasting pipeline trains and beats last-bucket and zone-median baselines."""
    df = extract_zone_demand_data(seeded_db, target_type="observed_deliveries")
    assert len(df) >= 1000

    pipeline = DemandForecastPipeline(model_version="test_d1", target_type="observed_deliveries")
    eval_res = pipeline.train_and_evaluate(df)

    comparisons = eval_res["models_comparison"]
    naive_mae = comparisons["baseline_last_bucket_naive"]["mae"]
    median_mae = comparisons["baseline_zone_median"]["mae"]
    gbt_mae = comparisons["gradient_boosted_regressor"]["mae"]

    assert gbt_mae < naive_mae
    assert gbt_mae < median_mae
    assert eval_res["uncertainty_evaluation"]["empirical_coverage_pct"] > 60.0


def test_demand_multi_step_forecast(seeded_db):
    """Verify multi-step multi-zone demand forecast output."""
    forecast_from = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
    zones = ["HYD_ZONE_01", "HYD_ZONE_02"]

    res = forecast_zone_demand(
        session=seeded_db,
        zone_codes=zones,
        forecast_from=forecast_from,
        steps=4,
        interval_minutes=30,
    )

    assert len(res) == len(zones) * 4
    for item in res:
        assert item["target_type"] == "observed_deliveries"
        assert item["point_prediction"] >= 0.0
        assert item["lower_prediction"] <= item["point_prediction"]
        assert item["upper_prediction"] >= item["point_prediction"]


def test_opportunity_recommendation_ranking(seeded_db):
    """Verify recommendation engine hard constraints, scoring, and explainability."""
    start_at = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    end_at = start_at + timedelta(hours=3)

    rec = generate_recommendations(
        session=seeded_db,
        worker_ref="worker_w01",
        candidate_platforms=["flash_drop", "swift_bite"],
        candidate_zones=["zone_koramangala", "zone_indiranagar", "zone_whitefield"],
        start_at=start_at,
        end_at=end_at,
        current_zone_code="zone_koramangala",
        max_travel_distance_m=12000,
        risk_tolerance="balanced",
    )

    assert rec["total_evaluated"] > 0
    assert rec["viable_count"] > 0
    assert rec["top_candidate"] is not None

    top = rec["top_candidate"]
    assert "composite_score" in top
    assert "expected_net_inr_per_hour" in top
    assert len(top["reasons"]) >= 3

    # Whitefield is > 14km away from Koramangala; with max_travel_distance_m=12000 it must be excluded
    excluded_zones = [e["zone_code"] for e in rec["excluded_candidates"]]
    assert "zone_whitefield" in excluded_zones

