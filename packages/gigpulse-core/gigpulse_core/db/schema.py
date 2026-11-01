"""SQLAlchemy schema models for GigPulse AI.

Implements all 12 domain entities from docs/05_DATA_DICTIONARY_SCHEMA.md.
Enforces non-negative monetary values in integer paise, UTC timestamps,
and composite indexing for fast spatio-temporal queries.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from gigpulse_core.db.database import Base


def generate_uuid() -> str:
    return uuid.uuid4().hex


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkerProfileModel(Base):
    """Corresponds to worker_profiles."""
    __tablename__ = "worker_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_ref = Column(String(64), unique=True, nullable=False, index=True)
    owner_user_id = Column(String(36), nullable=True)
    display_name = Column(String(128), nullable=True)
    home_zone_code = Column(String(64), nullable=True)
    preferred_currency = Column(String(3), nullable=False, default="INR")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class PlatformModel(Base):
    """Corresponds to platforms."""
    __tablename__ = "platforms"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class ZoneModel(Base):
    """Corresponds to zones."""
    __tablename__ = "zones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    zone_system = Column(String(32), nullable=False, default="study_area")
    zone_code = Column(String(64), nullable=False, index=True)
    resolution = Column(Integer, nullable=True)
    display_name = Column(String(128), nullable=True)
    centroid_lat = Column(Float, nullable=True)
    centroid_lon = Column(Float, nullable=True)
    boundary_ref = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("zone_system", "zone_code", name="uq_zone_system_code"),
    )


class WorkSessionModel(Base):
    """Corresponds to work_sessions."""
    __tablename__ = "work_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_ref = Column(String(64), nullable=False, index=True)
    platform_code = Column(String(64), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="completed")
    source_type = Column(String(32), nullable=False, default="manual")
    timezone = Column(String(64), nullable=False, default="Asia/Kolkata")
    import_batch_id = Column(String(36), nullable=True, index=True)
    row_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        Index("ix_work_sessions_worker_started", "worker_ref", "started_at"),
        CheckConstraint("ended_at >= started_at", name="ck_work_sessions_valid_duration"),
    )


class DeliveryModel(Base):
    """Corresponds to deliveries.
    
    All monetary fields stored in authoritative integer paise (INR).
    """
    __tablename__ = "deliveries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_ref = Column(String(64), nullable=False, index=True)
    platform_code = Column(String(64), nullable=False, index=True)
    session_ref = Column(String(64), nullable=True, index=True)
    external_ref_hash = Column(String(64), nullable=True, index=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    pickup_zone_code = Column(String(64), nullable=True, index=True)
    drop_zone_code = Column(String(64), nullable=True)
    payout_paise = Column(BigInteger, nullable=False, default=0)
    incentive_paise = Column(BigInteger, nullable=False, default=0)
    tip_paise = Column(BigInteger, nullable=False, default=0)
    distance_m = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(32), nullable=False, default="completed")
    target_quality = Column(String(32), nullable=False, default="user_reported")
    source_type = Column(String(32), nullable=False, default="manual")
    import_batch_id = Column(String(36), nullable=True, index=True)
    row_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        Index("ix_deliveries_worker_completed", "worker_ref", "completed_at"),
        Index("ix_deliveries_platform_completed", "platform_code", "completed_at"),
        CheckConstraint("payout_paise >= 0", name="ck_deliveries_payout_paise_non_negative"),
        CheckConstraint("incentive_paise >= 0", name="ck_deliveries_incentive_paise_non_negative"),
        CheckConstraint("tip_paise >= 0", name="ck_deliveries_tip_paise_non_negative"),
    )


class ExpenseModel(Base):
    """Corresponds to expenses."""
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_ref = Column(String(64), nullable=False, index=True)
    session_ref = Column(String(64), nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    category = Column(String(32), nullable=False, default="other")
    amount_paise = Column(BigInteger, nullable=False)
    source_type = Column(String(32), nullable=False, default="manual")
    notes = Column(Text, nullable=True)
    import_batch_id = Column(String(36), nullable=True, index=True)
    row_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        Index("ix_expenses_worker_occurred", "worker_ref", "occurred_at"),
        CheckConstraint("amount_paise >= 0", name="ck_expenses_amount_non_negative"),
    )


class ZoneDemandObservationModel(Base):
    """Corresponds to zone_demand_observations.
    
    Critical: strictly preserves target_type separation (requested, completed, observed, proxy).
    """
    __tablename__ = "zone_demand_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    zone_code = Column(String(64), nullable=False, index=True)
    interval_start = Column(DateTime(timezone=True), nullable=False, index=True)
    interval_minutes = Column(Integer, nullable=False, default=30)
    orders_requested = Column(Integer, nullable=True)
    orders_completed = Column(Integer, nullable=True)
    deliveries_observed = Column(Integer, nullable=True)
    demand_proxy_value = Column(Float, nullable=True)
    target_type = Column(String(32), nullable=False, default="proxy")
    coverage_fraction = Column(Float, nullable=True)
    target_quality = Column(String(32), nullable=False, default="proxy")
    source_type = Column(String(32), nullable=False, default="csv_import")
    import_batch_id = Column(String(36), nullable=True, index=True)
    row_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        Index("ix_demand_zone_interval", "zone_code", "interval_start"),
        UniqueConstraint("zone_code", "interval_start", "interval_minutes", "target_type", name="uq_zone_demand_observation"),
    )


class ImportBatchModel(Base):
    """Corresponds to import_batches."""
    __tablename__ = "import_batches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_user_id = Column(String(36), nullable=True)
    filename_safe = Column(String(256), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    detected_format = Column(String(32), nullable=False, default="csv")
    status = Column(String(32), nullable=False, default="uploaded")
    row_count = Column(Integer, nullable=False, default=0)
    accepted_count = Column(Integer, nullable=False, default=0)
    rejected_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    validation_report_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class ModelVersionModel(Base):
    """Corresponds to model_versions."""
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    target_definition = Column(String(128), nullable=False)
    training_data_ref = Column(String(256), nullable=False)
    feature_schema_version = Column(String(32), nullable=False)
    evaluation_json = Column(Text, nullable=True)
    limitations = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="experimental")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("model_name", "version", name="uq_model_name_version"),
    )


class ForecastRunModel(Base):
    """Corresponds to forecast_runs."""
    __tablename__ = "forecast_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_version_id = Column(String(36), ForeignKey("model_versions.id"), nullable=False, index=True)
    target_type = Column(String(32), nullable=False)
    zone_code = Column(String(64), nullable=True, index=True)
    worker_ref = Column(String(64), nullable=True, index=True)
    horizon_start = Column(DateTime(timezone=True), nullable=False)
    horizon_end = Column(DateTime(timezone=True), nullable=False)
    point_prediction = Column(Float, nullable=True)
    lower_prediction = Column(Float, nullable=True)
    upper_prediction = Column(Float, nullable=True)
    unit = Column(String(32), nullable=False)
    input_snapshot_ref = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class RecommendationRunModel(Base):
    """Corresponds to recommendation_runs."""
    __tablename__ = "recommendation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_ref = Column(String(64), nullable=True, index=True)
    constraints_json = Column(Text, nullable=False)
    scoring_version = Column(String(32), nullable=False)
    candidates_json = Column(Text, nullable=False)
    selected_candidate_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class ContextObservationModel(Base):
    """Corresponds to context_observations."""
    __tablename__ = "context_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    zone_code = Column(String(64), nullable=True, index=True)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_to = Column(DateTime(timezone=True), nullable=True)
    weather_code = Column(String(32), nullable=True)
    temperature_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    event_type = Column(String(64), nullable=True)
    source_name = Column(String(128), nullable=False)
    source_version = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

