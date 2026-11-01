"""Machine learning, forecasting, and optimization package for GigPulse AI."""

from gigpulse_core.ml.earnings import (
    EarningsModelPipeline,
    predict_worker_earnings,
)
from gigpulse_core.ml.demand import (
    DemandForecastPipeline,
    forecast_zone_demand,
)
from gigpulse_core.ml.optimizer import (
    RecommendationEngine,
    generate_recommendations,
)

__all__ = [
    "EarningsModelPipeline",
    "predict_worker_earnings",
    "DemandForecastPipeline",
    "forecast_zone_demand",
    "RecommendationEngine",
    "generate_recommendations",
]

