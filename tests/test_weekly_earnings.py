"""Unit tests for rolling 7-completed-calendar-day weekly earnings logic.

Tests fixed dates across midnight, Sundays, Mondays, month boundaries, and year boundaries,
verifying that today's earnings are strictly excluded from completed weekly totals.
"""

from datetime import datetime, timezone
import pytest
from zoneinfo import ZoneInfo

from gigpulse_core.domain.weekly_earnings import (
    compute_rolling_weekly_earnings,
    get_calendar_day_in_timezone,
)


def test_sunday_reference_date_excludes_today_and_covers_previous_7_days():
    """If today is Sunday, Nov 1, 2026:

    Completed window is Sun Oct 25 - Sat Oct 31 (7 days).
    Sunday Nov 1 is in-progress and excluded from completed totals.
    """
    ref_dt = datetime(2026, 11, 1, 18, 30, tzinfo=ZoneInfo("Asia/Kolkata"))

    deliveries = [
        # In completed window: Saturday Oct 31
        {
            "completed_at": "2026-10-31T20:00:00+05:30",
            "payout_paise": 25000,
            "incentive_paise": 5000,
            "tip_paise": 2000,
        },
        # In completed window: Sunday Oct 25
        {
            "completed_at": "2026-10-25T14:00:00+05:30",
            "payout_paise": 15000,
            "incentive_paise": 0,
            "tip_paise": 1000,
        },
        # TODAY (Sunday Nov 1) - Must be in-progress, NOT in completed total
        {
            "completed_at": "2026-11-01T12:00:00+05:30",
            "payout_paise": 18000,
            "incentive_paise": 2000,
            "tip_paise": 1000,
        },
        # Outside window: Saturday Oct 24 (8 days ago)
        {
            "completed_at": "2026-10-24T19:00:00+05:30",
            "payout_paise": 30000,
            "incentive_paise": 0,
            "tip_paise": 0,
        },
    ]

    expenses = [
        # In completed window
        {"occurred_at": "2026-10-31T10:00:00+05:30", "amount_paise": 5000},
        # Today's expense
        {"occurred_at": "2026-11-01T09:00:00+05:30", "amount_paise": 3000},
    ]

    summary = compute_rolling_weekly_earnings(deliveries, expenses, ref_dt, "Asia/Kolkata")

    assert len(summary.completed_days) == 7
    assert summary.completed_days[0].date_str == "2026-10-25"
    assert summary.completed_days[-1].date_str == "2026-10-31"

    # Completed gross: 32000 (Oct 31) + 16000 (Oct 25) = 48000
    assert summary.total_completed_gross_paise == 48000
    assert summary.total_completed_expenses_paise == 5000
    assert summary.total_completed_net_paise == 43000
    assert summary.total_completed_deliveries == 2

    # Verify sum of days equals totals
    sum_days_gross = sum(d.gross_paise for d in summary.completed_days)
    sum_days_exp = sum(d.expenses_paise for d in summary.completed_days)
    sum_days_net = sum(d.net_paise for d in summary.completed_days)
    assert sum_days_gross == summary.total_completed_gross_paise
    assert sum_days_exp == summary.total_completed_expenses_paise
    assert sum_days_net == summary.total_completed_net_paise

    # Today's in-progress
    assert summary.today_in_progress.date_str == "2026-11-01"
    assert summary.today_in_progress.is_in_progress is True
    assert summary.today_in_progress.gross_paise == 21000
    assert summary.today_in_progress.expenses_paise == 3000
    assert summary.today_in_progress.net_paise == 18000
    assert summary.today_in_progress.delivery_count == 1


def test_monday_progression_advances_completed_window():
    """On Monday, Nov 2, 2026:

    Sunday Nov 1 is now a finalized completed day in the 7-day window.
    Monday Nov 2 becomes the new in-progress day.
    """
    ref_dt = datetime(2026, 11, 2, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    deliveries = [
        # Sunday Nov 1 now completed
        {
            "completed_at": "2026-11-01T15:00:00+05:30",
            "payout_paise": 20000,
            "incentive_paise": 0,
            "tip_paise": 0,
        },
        # Monday Nov 2 in progress
        {
            "completed_at": "2026-11-02T09:30:00+05:30",
            "payout_paise": 10000,
            "incentive_paise": 0,
            "tip_paise": 0,
        },
    ]

    summary = compute_rolling_weekly_earnings(deliveries, [], ref_dt, "Asia/Kolkata")

    assert summary.completed_days[0].date_str == "2026-10-26"
    assert summary.completed_days[-1].date_str == "2026-11-01"
    assert summary.completed_days[-1].gross_paise == 20000
    assert summary.total_completed_gross_paise == 20000

    assert summary.today_in_progress.date_str == "2026-11-02"
    assert summary.today_in_progress.gross_paise == 10000


def test_month_and_year_boundary_crossing():
    """At Jan 3, 2027:

    Completed window spans Dec 27, 2026 to Jan 2, 2027.
    Crossing year and month boundaries without index or date arithmetic errors.
    """
    ref_dt = datetime(2027, 1, 3, 14, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    deliveries = [
        {"completed_at": "2026-12-31T23:30:00+05:30", "payout_paise": 40000, "incentive_paise": 0, "tip_paise": 0},
        {"completed_at": "2027-01-01T00:30:00+05:30", "payout_paise": 50000, "incentive_paise": 0, "tip_paise": 0},
    ]

    summary = compute_rolling_weekly_earnings(deliveries, [], ref_dt, "Asia/Kolkata")

    assert summary.completed_days[0].date_str == "2026-12-27"
    assert summary.completed_days[-1].date_str == "2027-01-02"
    assert summary.total_completed_gross_paise == 90000


def test_midnight_timezone_conversion():
    """A delivery completed at 2026-10-31 18:45 UTC is 2026-11-01 00:15 in Asia/Kolkata (+05:30).

    It belongs to Nov 1 in Kolkata, not Oct 31!
    """
    utc_dt = datetime(2026, 10, 31, 18, 45, tzinfo=timezone.utc)
    kolkata_date = get_calendar_day_in_timezone(utc_dt, "Asia/Kolkata")
    assert kolkata_date.isoformat() == "2026-11-01"
