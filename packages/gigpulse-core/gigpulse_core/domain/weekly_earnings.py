"""Rolling 7-Completed-Calendar-Day Weekly Earnings Domain Logic.

Business Rule:
Today's earnings are in-progress and must be excluded from the finalized completed-week total.
The rolling completed window consists of the 7 consecutive completed calendar days
immediately preceding the reference date in the configured timezone (default Asia/Kolkata).
Today's earnings appear strictly as 'today_in_progress'.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from gigpulse_core.money import paise_to_rupees_str, validate_non_negative_paise

DEFAULT_TIMEZONE = "Asia/Kolkata"


@dataclass(frozen=True)
class DailyEarningsBucket:
    """Financial aggregation for a single calendar day."""

    date_str: str  # YYYY-MM-DD
    day_name: str  # Mon, Tue, etc.
    day_letter: str  # M, T, W, T, F, S, S
    gross_paise: int
    expenses_paise: int
    net_paise: int
    delivery_count: int
    is_in_progress: bool = False

    @property
    def gross_inr(self) -> str:
        return paise_to_rupees_str(self.gross_paise)

    @property
    def expenses_inr(self) -> str:
        return paise_to_rupees_str(self.expenses_paise)

    @property
    def net_inr(self) -> str:
        return paise_to_rupees_str(self.net_paise)


@dataclass
class WeeklyEarningsSummary:
    """Rolling 7-completed-day earnings summary with separate today's in-progress block."""

    timezone: str
    reference_date_str: str  # 'today' in the specified timezone
    completed_days: List[DailyEarningsBucket]
    today_in_progress: DailyEarningsBucket
    total_completed_gross_paise: int
    total_completed_expenses_paise: int
    total_completed_net_paise: int
    total_completed_deliveries: int

    @property
    def total_completed_gross_inr(self) -> str:
        return paise_to_rupees_str(self.total_completed_gross_paise)

    @property
    def total_completed_net_inr(self) -> str:
        return paise_to_rupees_str(self.total_completed_net_paise)

    @property
    def total_completed_expenses_inr(self) -> str:
        return paise_to_rupees_str(self.total_completed_expenses_paise)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timezone": self.timezone,
            "reference_date": self.reference_date_str,
            "completed_window": {
                "start_date": self.completed_days[0].date_str if self.completed_days else None,
                "end_date": self.completed_days[-1].date_str if self.completed_days else None,
            },
            "completed_days": [
                {
                    "date": d.date_str,
                    "day_name": d.day_name,
                    "day_letter": d.day_letter,
                    "gross_paise": d.gross_paise,
                    "expenses_paise": d.expenses_paise,
                    "net_paise": d.net_paise,
                    "gross_inr": d.gross_inr,
                    "expenses_inr": d.expenses_inr,
                    "net_inr": d.net_inr,
                    "delivery_count": d.delivery_count,
                    "is_in_progress": False,
                }
                for d in self.completed_days
            ],
            "today_in_progress": {
                "date": self.today_in_progress.date_str,
                "day_name": self.today_in_progress.day_name,
                "day_letter": self.today_in_progress.day_letter,
                "gross_paise": self.today_in_progress.gross_paise,
                "expenses_paise": self.today_in_progress.expenses_paise,
                "net_paise": self.today_in_progress.net_paise,
                "gross_inr": self.today_in_progress.gross_inr,
                "expenses_inr": self.today_in_progress.expenses_inr,
                "net_inr": self.today_in_progress.net_inr,
                "delivery_count": self.today_in_progress.delivery_count,
                "is_in_progress": True,
            },
            "totals": {
                "completed_gross_paise": self.total_completed_gross_paise,
                "completed_expenses_paise": self.total_completed_expenses_paise,
                "completed_net_paise": self.total_completed_net_paise,
                "completed_gross_inr": self.total_completed_gross_inr,
                "completed_expenses_inr": self.total_completed_expenses_inr,
                "completed_net_inr": self.total_completed_net_inr,
                "completed_deliveries": self.total_completed_deliveries,
            },
        }


def get_calendar_day_in_timezone(dt: datetime, tz_name: str = DEFAULT_TIMEZONE) -> date:
    """Convert any UTC or naive datetime to calendar date in the target timezone."""
    tz = ZoneInfo(tz_name)
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt_aware = dt.replace(tzinfo=ZoneInfo("UTC"))
    else:
        dt_aware = dt
    return dt_aware.astimezone(tz).date()


def compute_rolling_weekly_earnings(
    deliveries: List[Dict[str, Any]],
    expenses: List[Dict[str, Any]],
    reference_datetime: Optional[datetime] = None,
    tz_name: str = DEFAULT_TIMEZONE,
) -> WeeklyEarningsSummary:
    """Compute rolling 7-completed-calendar-day earnings excluding today's in-progress data.

    Parameters:
    - deliveries: list of dicts with 'completed_at', 'payout_paise', 'incentive_paise', 'tip_paise'
    - expenses: list of dicts with 'occurred_at', 'amount_paise'
    - reference_datetime: the current moment or fixed test datetime (defaults to now in tz)
    - tz_name: timezone name (e.g. 'Asia/Kolkata')
    """
    tz = ZoneInfo(tz_name)
    if reference_datetime is None:
        ref_dt = datetime.now(tz)
    else:
        if reference_datetime.tzinfo is None:
            ref_dt = reference_datetime.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
        else:
            ref_dt = reference_datetime.astimezone(tz)

    today_date = ref_dt.date()

    # The 7 completed days are today_date - 7 through today_date - 1
    completed_dates = [today_date - timedelta(days=offset) for offset in range(7, 0, -1)]

    # Aggregate buckets
    # Key: date -> {gross, expenses, count}
    aggregates: Dict[date, Dict[str, int]] = {
        d: {"gross": 0, "expenses": 0, "count": 0} for d in completed_dates + [today_date]
    }

    # Process deliveries
    for d in deliveries:
        completed_at = d.get("completed_at")
        if not completed_at:
            continue
        if isinstance(completed_at, str):
            dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        else:
            dt = completed_at

        cal_date = get_calendar_day_in_timezone(dt, tz_name)
        if cal_date in aggregates:
            payout = int(d.get("payout_paise", 0) or 0)
            incentive = int(d.get("incentive_paise", 0) or 0)
            tip = int(d.get("tip_paise", 0) or 0)
            aggregates[cal_date]["gross"] += payout + incentive + tip
            aggregates[cal_date]["count"] += 1

    # Process expenses
    for e in expenses:
        occurred_at = e.get("occurred_at")
        if not occurred_at:
            continue
        if isinstance(occurred_at, str):
            dt = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
        else:
            dt = occurred_at

        cal_date = get_calendar_day_in_timezone(dt, tz_name)
        if cal_date in aggregates:
            amount = int(e.get("amount_paise", 0) or 0)
            aggregates[cal_date]["expenses"] += amount

    # Format daily buckets
    day_letters = ["M", "T", "W", "T", "F", "S", "S"]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    completed_buckets: List[DailyEarningsBucket] = []
    tot_gross = 0
    tot_exp = 0
    tot_net = 0
    tot_count = 0

    for d in completed_dates:
        agg = aggregates[d]
        gross = agg["gross"]
        exp = agg["expenses"]
        net = gross - exp
        count = agg["count"]

        weekday_idx = d.weekday()  # 0=Monday, 6=Sunday
        bucket = DailyEarningsBucket(
            date_str=d.isoformat(),
            day_name=day_names[weekday_idx],
            day_letter=day_letters[weekday_idx],
            gross_paise=gross,
            expenses_paise=exp,
            net_paise=net,
            delivery_count=count,
            is_in_progress=False,
        )
        completed_buckets.append(bucket)
        tot_gross += gross
        tot_exp += exp
        tot_net += net
        tot_count += count

    # Today's in-progress bucket
    today_agg = aggregates[today_date]
    today_gross = today_agg["gross"]
    today_exp = today_agg["expenses"]
    today_net = today_gross - today_exp
    today_count = today_agg["count"]
    today_weekday_idx = today_date.weekday()

    today_bucket = DailyEarningsBucket(
        date_str=today_date.isoformat(),
        day_name=day_names[today_weekday_idx],
        day_letter=day_letters[today_weekday_idx],
        gross_paise=today_gross,
        expenses_paise=today_exp,
        net_paise=today_net,
        delivery_count=today_count,
        is_in_progress=True,
    )

    return WeeklyEarningsSummary(
        timezone=tz_name,
        reference_date_str=today_date.isoformat(),
        completed_days=completed_buckets,
        today_in_progress=today_bucket,
        total_completed_gross_paise=tot_gross,
        total_completed_expenses_paise=tot_exp,
        total_completed_net_paise=tot_net,
        total_completed_deliveries=tot_count,
    )
