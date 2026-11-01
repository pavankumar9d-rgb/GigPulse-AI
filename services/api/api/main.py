"""FastAPI application factory and server entrypoint for GigPulse AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.dependencies import get_active_engine
from api.errors import register_error_handlers
from api.routers import (
    analytics_router,
    deliveries_router,
    demand_router,
    expenses_router,
    forecasts_router,
    governance_router,
    health_router,
    imports_router,
    models_router,
    platforms_router,
    recommendations_router,
    sessions_router,
    workers_router,
    zones_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure SQLite database schema is initialized on startup
    get_active_engine()
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Middleware (restricted to local origins for zero-cost local dev)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Register standard error handlers (no secrets or stack traces leaked)
    register_error_handlers(app)

    # 3. Register API v1 Routers
    api_v1_prefix = settings.API_V1_STR

    app.include_router(health_router, prefix=api_v1_prefix)
    app.include_router(workers_router, prefix=api_v1_prefix)
    app.include_router(platforms_router, prefix=api_v1_prefix)
    app.include_router(zones_router, prefix=api_v1_prefix)
    app.include_router(sessions_router, prefix=api_v1_prefix)
    app.include_router(deliveries_router, prefix=api_v1_prefix)
    app.include_router(expenses_router, prefix=api_v1_prefix)
    app.include_router(demand_router, prefix=api_v1_prefix)
    app.include_router(analytics_router, prefix=api_v1_prefix)
    app.include_router(imports_router, prefix=api_v1_prefix)
    app.include_router(forecasts_router, prefix=api_v1_prefix)
    app.include_router(recommendations_router, prefix=api_v1_prefix)
    app.include_router(models_router, prefix=api_v1_prefix)
    app.include_router(governance_router, prefix=api_v1_prefix)

    @app.get("/", tags=["Root"], summary="API Root Status")
    def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "api_v1": api_v1_prefix,
            "status": "online",
        }

    return app


# Module-level application instance
app = create_app()
