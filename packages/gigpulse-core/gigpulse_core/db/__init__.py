"""Database package for GigPulse AI.

Provides SQLite initialization, SQLAlchemy ORM schema, repositories,
safe CSV batch importing, and synthetic fixture seeding.
"""

from gigpulse_core.db.database import (
    Base,
    get_engine,
    get_session_factory,
    init_db,
)
from gigpulse_core.db.importer import (
    ImportBatchResult,
    import_csv_content,
    import_csv_file,
)
from gigpulse_core.db.repository import (
    get_or_create_platform,
    get_or_create_worker_profile,
    get_or_create_zone,
    get_worker_analytics_summary,
    list_deliveries,
    list_expenses,
    list_work_sessions,
    list_zone_demand,
)
from gigpulse_core.db.schema import (
    ContextObservationModel,
    DeliveryModel,
    ExpenseModel,
    ForecastRunModel,
    ImportBatchModel,
    ModelVersionModel,
    PlatformModel,
    RecommendationRunModel,
    WorkSessionModel,
    WorkerProfileModel,
    ZoneDemandObservationModel,
    ZoneModel,
)
from gigpulse_core.db.seed import seed_synthetic_fixtures

__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "init_db",
    "WorkerProfileModel",
    "PlatformModel",
    "ZoneModel",
    "WorkSessionModel",
    "DeliveryModel",
    "ExpenseModel",
    "ZoneDemandObservationModel",
    "ImportBatchModel",
    "ModelVersionModel",
    "ForecastRunModel",
    "RecommendationRunModel",
    "ContextObservationModel",
    "get_or_create_worker_profile",
    "get_or_create_platform",
    "get_or_create_zone",
    "list_work_sessions",
    "list_deliveries",
    "list_expenses",
    "list_zone_demand",
    "get_worker_analytics_summary",
    "ImportBatchResult",
    "import_csv_content",
    "import_csv_file",
    "seed_synthetic_fixtures",
]

