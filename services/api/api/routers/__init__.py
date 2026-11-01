"""API Routers for GigPulse AI backend."""

from api.routers.analytics import router as analytics_router
from api.routers.deliveries import router as deliveries_router
from api.routers.demand import router as demand_router
from api.routers.expenses import router as expenses_router
from api.routers.forecasts import router as forecasts_router
from api.routers.governance import router as governance_router
from api.routers.health import router as health_router
from api.routers.imports import router as imports_router
from api.routers.models import router as models_router
from api.routers.platforms import router as platforms_router
from api.routers.recommendations import router as recommendations_router
from api.routers.sessions import router as sessions_router
from api.routers.workers import router as workers_router
from api.routers.zones import router as zones_router

__all__ = [
    "analytics_router",
    "deliveries_router",
    "demand_router",
    "expenses_router",
    "forecasts_router",
    "governance_router",
    "health_router",
    "imports_router",
    "models_router",
    "platforms_router",
    "recommendations_router",
    "sessions_router",
    "workers_router",
    "zones_router",
]
