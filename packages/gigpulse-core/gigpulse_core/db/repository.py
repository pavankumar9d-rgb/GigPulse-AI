"""Data access and repository operations for GigPulse AI.

Provides safe persistence, querying, and domain metrics integration
using Phase 1 mathematical modules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gigpulse_core.enums import DeliveryStatus
from gigpulse_core.metrics import (
    calculate_active_time_seconds,
    calculate_earnings_per_online_hour_paise,
    calculate_gross_earnings_paise,
    calculate_net_earnings_paise,
    calculate_online_time_seconds,
    calculate_platform_gross_shares,
    calculate_total_expenses_paise,
)
from gigpulse_core.models import (
    DeliveryRecord,
    ExpenseRecord,
    WorkSessionRecord,
)
from gigpulse_core.money import paise_to_rupees_str
from gigpulse_core.db.schema import (
    DeliveryModel,
    ExpenseModel,
    PlatformModel,
    WorkSessionModel,
    WorkerProfileModel,
    ZoneDemandObservationModel,
    ZoneModel,
)


def get_or_create_worker_profile(session: Session, worker_ref: str, display_name: Optional[str] = None) -> WorkerProfileModel:
    stmt = select(WorkerProfileModel).where(WorkerProfileModel.worker_ref == worker_ref)
    worker = session.execute(stmt).scalar_one_or_none()
    if not worker:
        worker = WorkerProfileModel(worker_ref=worker_ref, display_name=display_name or worker_ref)
        session.add(worker)
        session.flush()
    return worker


def get_or_create_platform(session: Session, code: str, display_name: Optional[str] = None) -> PlatformModel:
    stmt = select(PlatformModel).where(PlatformModel.code == code)
    platform = session.execute(stmt).scalar_one_or_none()
    if not platform:
        platform = PlatformModel(code=code, display_name=display_name or code)
        session.add(platform)
        session.flush()
    return platform


def get_or_create_zone(session: Session, zone_code: str, zone_system: str = "study_area", display_name: Optional[str] = None) -> ZoneModel:
    stmt = select(ZoneModel).where(ZoneModel.zone_code == zone_code, ZoneModel.zone_system == zone_system)
    zone = session.execute(stmt).scalar_one_or_none()
    if not zone:
        zone = ZoneModel(zone_code=zone_code, zone_system=zone_system, display_name=display_name or zone_code)
        session.add(zone)
        session.flush()
    return zone


def list_work_sessions(
    session: Session,
    worker_ref: Optional[str] = None,
    platform_code: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[WorkSessionModel]:
    stmt = select(WorkSessionModel)
    if worker_ref:
        stmt = stmt.where(WorkSessionModel.worker_ref == worker_ref)
    if platform_code:
        stmt = stmt.where(WorkSessionModel.platform_code == platform_code)
    if start_date:
        stmt = stmt.where(WorkSessionModel.started_at >= start_date)
    if end_date:
        stmt = stmt.where(WorkSessionModel.ended_at <= end_date)
    stmt = stmt.order_by(WorkSessionModel.started_at.desc()).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def list_deliveries(
    session: Session,
    worker_ref: Optional[str] = None,
    platform_code: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[DeliveryModel]:
    stmt = select(DeliveryModel)
    if worker_ref:
        stmt = stmt.where(DeliveryModel.worker_ref == worker_ref)
    if platform_code:
        stmt = stmt.where(DeliveryModel.platform_code == platform_code)
    if start_date:
        stmt = stmt.where(DeliveryModel.completed_at >= start_date)
    if end_date:
        stmt = stmt.where(DeliveryModel.completed_at <= end_date)
    stmt = stmt.order_by(DeliveryModel.completed_at.desc()).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def list_expenses(
    session: Session,
    worker_ref: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[ExpenseModel]:
    stmt = select(ExpenseModel)
    if worker_ref:
        stmt = stmt.where(ExpenseModel.worker_ref == worker_ref)
    if start_date:
        stmt = stmt.where(ExpenseModel.occurred_at >= start_date)
    if end_date:
        stmt = stmt.where(ExpenseModel.occurred_at <= end_date)
    stmt = stmt.order_by(ExpenseModel.occurred_at.desc()).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def list_zone_demand(
    session: Session,
    zone_code: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[ZoneDemandObservationModel]:
    stmt = select(ZoneDemandObservationModel)
    if zone_code:
        stmt = stmt.where(ZoneDemandObservationModel.zone_code == zone_code)
    if target_type:
        stmt = stmt.where(ZoneDemandObservationModel.target_type == target_type)
    if start_date:
        stmt = stmt.where(ZoneDemandObservationModel.interval_start >= start_date)
    if end_date:
        stmt = stmt.where(ZoneDemandObservationModel.interval_start <= end_date)
    stmt = stmt.order_by(ZoneDemandObservationModel.interval_start.desc()).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def get_worker_analytics_summary(
    session: Session,
    worker_ref: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Compute holistic worker analytics using Phase 1 domain math and interval union.
    
    Unions overlapping sessions across platforms to ensure true online duration.
    """
    # 1. Fetch sessions
    session_models = list_work_sessions(session, worker_ref=worker_ref, start_date=start_date, end_date=end_date, limit=10000)
    session_records = [
        WorkSessionRecord(
            worker_ref=s.worker_ref,
            platform_code=s.platform_code,
            started_at=s.started_at,
            ended_at=s.ended_at,
            status=s.status,
            source_type=s.source_type,
            timezone=s.timezone,
        ) for s in session_models
    ]

    # 2. Fetch deliveries
    delivery_models = list_deliveries(session, worker_ref=worker_ref, start_date=start_date, end_date=end_date, limit=50000)
    delivery_records = [
        DeliveryRecord(
            worker_ref=d.worker_ref,
            platform_code=d.platform_code,
            session_ref=d.session_ref,
            accepted_at=d.accepted_at,
            completed_at=d.completed_at,
            pickup_zone_code=d.pickup_zone_code,
            drop_zone_code=d.drop_zone_code,
            payout_paise=d.payout_paise,
            incentive_paise=d.incentive_paise,
            tip_paise=d.tip_paise,
            distance_m=d.distance_m,
            duration_seconds=d.duration_seconds,
            status=d.status,
            target_quality=d.target_quality,
            source_type=d.source_type,
        ) for d in delivery_models
    ]

    # 3. Fetch expenses
    expense_models = list_expenses(session, worker_ref=worker_ref, start_date=start_date, end_date=end_date, limit=10000)
    expense_records = [
        ExpenseRecord(
            worker_ref=e.worker_ref,
            session_ref=e.session_ref,
            occurred_at=e.occurred_at,
            category=e.category,
            amount_paise=e.amount_paise,
            source_type=e.source_type,
            notes=e.notes,
        ) for e in expense_models
    ]

    # 4. Compute metrics using Phase 1 domain math
    gross_paise = calculate_gross_earnings_paise(delivery_records)
    total_expenses_paise = calculate_total_expenses_paise(expense_records)
    net_paise = calculate_net_earnings_paise(gross_paise, expense_records)
    online_seconds = calculate_online_time_seconds(session_records)
    active_seconds = calculate_active_time_seconds(delivery_records)
    rate_paise_hr = calculate_earnings_per_online_hour_paise(net_paise, online_seconds)
    platform_shares = calculate_platform_gross_shares(delivery_records)

    return {
        "worker_ref": worker_ref,
        "counts": {
            "sessions": len(session_records),
            "deliveries": len(delivery_records),
            "expenses": len(expense_records),
        },
        "earnings": {
            "gross_paise": gross_paise,
            "gross_formatted": paise_to_rupees_str(gross_paise),
            "total_expenses_paise": total_expenses_paise,
            "total_expenses_formatted": paise_to_rupees_str(total_expenses_paise),
            "net_paise": net_paise,
            "net_formatted": paise_to_rupees_str(net_paise),
        },
        "time": {
            "online_seconds": online_seconds,
            "online_hours": round(online_seconds / 3600.0, 2),
            "active_seconds": active_seconds,
            "active_hours": round(active_seconds / 3600.0, 2),
            "idle_seconds": max(0, online_seconds - active_seconds),
        },
        "rates": {
            "net_earnings_per_online_hour_paise": rate_paise_hr,
            "net_earnings_per_online_hour_formatted": paise_to_rupees_str(int(rate_paise_hr)) if rate_paise_hr is not None else None,
        },
        "platform_gross_shares": platform_shares,
    }

