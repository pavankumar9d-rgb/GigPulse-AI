"""Unit tests for derived metrics calculations (gross, net, hours, shares)."""

from datetime import datetime, timezone
from gigpulse_core.enums import DeliveryStatus, ExpenseCategory, SessionStatus, SourceType, TargetQuality
from gigpulse_core.metrics import (
    calculate_active_time_seconds,
    calculate_earnings_per_online_hour_paise,
    calculate_gross_earnings_paise,
    calculate_net_earnings_paise,
    calculate_online_time_seconds,
    calculate_platform_gross_shares,
    calculate_total_expenses_paise,
)
from gigpulse_core.models import DeliveryRecord, ExpenseRecord, WorkSessionRecord


def test_gross_and_net_earnings():
    d1 = DeliveryRecord(
        worker_ref="w1",
        platform_code="flash_drop",
        completed_at=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        payout_paise=5000,
        incentive_paise=1000,
        tip_paise=500,
        status=DeliveryStatus.COMPLETED,
    )
    d2 = DeliveryRecord(
        worker_ref="w1",
        platform_code="swift_bite",
        completed_at=datetime(2026, 10, 1, 13, 0, tzinfo=timezone.utc),
        payout_paise=6000,
        incentive_paise=0,
        tip_paise=1000,
        status=DeliveryStatus.COMPLETED,
    )
    # Cancelled delivery should not contribute to gross earnings
    d3 = DeliveryRecord(
        worker_ref="w1",
        platform_code="swift_bite",
        completed_at=datetime(2026, 10, 1, 14, 0, tzinfo=timezone.utc),
        payout_paise=2000,
        incentive_paise=0,
        tip_paise=0,
        status=DeliveryStatus.CANCELLED,
    )

    gross = calculate_gross_earnings_paise([d1, d2, d3])
    # (5000 + 1000 + 500) + (6000 + 0 + 1000) = 6500 + 7000 = 13500 paise
    assert gross == 13500

    e1 = ExpenseRecord(
        worker_ref="w1",
        occurred_at=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
        category=ExpenseCategory.FUEL,
        amount_paise=2500,
    )
    e2 = ExpenseRecord(
        worker_ref="w1",
        occurred_at=datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc),
        category=ExpenseCategory.PARKING,
        amount_paise=500,
    )

    assert calculate_total_expenses_paise([e1, e2]) == 3000
    net = calculate_net_earnings_paise(gross, [e1, e2])
    assert net == 10500


def test_online_and_active_time():
    # Multi-app session with 1 hour overlap
    s1 = WorkSessionRecord(
        worker_ref="w1",
        platform_code="flash_drop",
        started_at=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 10, 1, 13, 0, tzinfo=timezone.utc),  # 3 hrs
    )
    s2 = WorkSessionRecord(
        worker_ref="w1",
        platform_code="swift_bite",
        started_at=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 10, 1, 15, 0, tzinfo=timezone.utc),  # 3 hrs (1 hr overlap)
    )

    online_sec = calculate_online_time_seconds([s1, s2])
    # Union of 10:00-13:00 and 12:00-15:00 is 10:00-15:00 = 5 hours = 18000s
    assert online_sec == 18000

    # Deliveries active time
    d1 = DeliveryRecord(
        worker_ref="w1",
        platform_code="flash_drop",
        completed_at=datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc),
        duration_seconds=1800,  # 30 mins
        status=DeliveryStatus.COMPLETED,
    )
    d2 = DeliveryRecord(
        worker_ref="w1",
        platform_code="swift_bite",
        completed_at=datetime(2026, 10, 1, 14, 0, tzinfo=timezone.utc),
        duration_seconds=2400,  # 40 mins
        status=DeliveryStatus.COMPLETED,
    )
    assert calculate_active_time_seconds([d1, d2]) == 4200


def test_earnings_per_online_hour():
    net_paise = 10000  # ₹100
    online_seconds = 7200  # 2 hours
    rate = calculate_earnings_per_online_hour_paise(net_paise, online_seconds)
    assert rate == 5000.0  # ₹50/hr = 5000 paise/hr

    # Non-positive hours returns None
    assert calculate_earnings_per_online_hour_paise(net_paise, 0) is None
    assert calculate_earnings_per_online_hour_paise(net_paise, -3600) is None


def test_platform_gross_shares():
    d1 = DeliveryRecord(
        worker_ref="w1",
        platform_code="p1",
        completed_at=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        payout_paise=6000,
        status=DeliveryStatus.COMPLETED,
    )
    d2 = DeliveryRecord(
        worker_ref="w1",
        platform_code="p2",
        completed_at=datetime(2026, 10, 1, 13, 0, tzinfo=timezone.utc),
        payout_paise=4000,
        status=DeliveryStatus.COMPLETED,
    )
    shares = calculate_platform_gross_shares([d1, d2])
    assert shares["p1"] == 0.6
    assert shares["p2"] == 0.4

