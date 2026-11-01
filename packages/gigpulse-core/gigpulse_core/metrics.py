"""Derived earnings, time, and performance metrics computation.

Defines mathematically sound aggregations for multi-platform delivery data.
"""

from typing import Dict, Iterable, List, Optional

from gigpulse_core.enums import DeliveryStatus
from gigpulse_core.intervals import TimeInterval, calculate_unioned_duration_seconds
from gigpulse_core.models import DeliveryRecord, ExpenseRecord, WorkSessionRecord


def calculate_gross_earnings_paise(deliveries: Iterable[DeliveryRecord]) -> int:
    """Compute total gross delivery earnings in paise.
    
    Includes base payout + incentives + tips for completed deliveries.
    """
    total = 0
    for d in deliveries:
        if d.status == DeliveryStatus.COMPLETED:
            total += d.gross_payout_paise
    return total


def calculate_total_expenses_paise(expenses: Iterable[ExpenseRecord]) -> int:
    """Compute sum of all recorded expenses in paise."""
    return sum(e.amount_paise for e in expenses)


def calculate_net_earnings_paise(gross_paise: int, expenses: Iterable[ExpenseRecord]) -> int:
    """Compute net earnings in paise: Gross Earnings minus Total Expenses."""
    return gross_paise - calculate_total_expenses_paise(expenses)


def calculate_online_time_seconds(sessions: Iterable[WorkSessionRecord]) -> int:
    """Compute total worker online time across all platforms using interval union.
    
    Prevents double-counting hours when a worker is logged into multiple platforms simultaneously.
    """
    intervals = [TimeInterval(s.started_at, s.ended_at) for s in sessions]
    return calculate_unioned_duration_seconds(intervals)


def calculate_active_time_seconds(deliveries: Iterable[DeliveryRecord]) -> int:
    """Compute total active time spent fulfilling completed deliveries."""
    total = 0
    for d in deliveries:
        if d.status == DeliveryStatus.COMPLETED and d.duration_seconds is not None:
            total += d.duration_seconds
    return total


def calculate_earnings_per_online_hour_paise(net_paise: int, online_seconds: int) -> Optional[float]:
    """Calculate net earnings per online hour in paise.
    
    Returns None if online_seconds <= 0 to avoid division by zero or fabricated rates.
    """
    if online_seconds <= 0:
        return None
    hours = online_seconds / 3600.0
    return net_paise / hours


def calculate_platform_gross_shares(deliveries: Iterable[DeliveryRecord]) -> Dict[str, float]:
    """Compute observed payout shares by platform (0.0 to 1.0).
    
    Note: Represents sample activity share, NOT total city market share.
    """
    platform_totals: Dict[str, int] = {}
    grand_total = 0

    for d in deliveries:
        if d.status == DeliveryStatus.COMPLETED:
            payout = d.gross_payout_paise
            platform_totals[d.platform_code] = platform_totals.get(d.platform_code, 0) + payout
            grand_total += payout

    if grand_total == 0:
        return {p: 0.0 for p in platform_totals}

    return {p: amt / grand_total for p, amt in platform_totals.items()}

