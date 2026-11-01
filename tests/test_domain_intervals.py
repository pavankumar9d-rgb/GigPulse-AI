"""Unit tests for time interval mathematics and session union algorithms."""

from datetime import datetime, timezone
import pytest
from gigpulse_core.intervals import (
    TimeInterval,
    calculate_unioned_duration_seconds,
    union_intervals,
)


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, 1, hour, minute, tzinfo=timezone.utc)


def test_time_interval_validation():
    iv = TimeInterval(dt(10), dt(11))
    assert iv.duration_seconds == 3600

    with pytest.raises(ValueError, match="cannot be before start"):
        TimeInterval(dt(12), dt(11))


def test_union_empty_and_single():
    assert union_intervals([]) == []

    single = [TimeInterval(dt(10), dt(11))]
    unioned = union_intervals(single)
    assert len(unioned) == 1
    assert unioned[0].duration_seconds == 3600


def test_union_disjoint_intervals():
    intervals = [
        TimeInterval(dt(10), dt(11)),
        TimeInterval(dt(13), dt(15)),
    ]
    unioned = union_intervals(intervals)
    assert len(unioned) == 2
    assert calculate_unioned_duration_seconds(intervals) == 3600 + 7200


def test_union_overlapping_intervals():
    # Session A: 10:00 - 12:00 (2 hrs)
    # Session B: 11:00 - 13:00 (2 hrs)
    # Total combined without double count should be 10:00 - 13:00 (3 hrs = 10800s)
    intervals = [
        TimeInterval(dt(10), dt(12)),
        TimeInterval(dt(11), dt(13)),
    ]
    unioned = union_intervals(intervals)
    assert len(unioned) == 1
    assert unioned[0].start == dt(10)
    assert unioned[0].end == dt(13)
    assert calculate_unioned_duration_seconds(intervals) == 10800


def test_union_nested_and_touching_intervals():
    intervals = [
        TimeInterval(dt(10), dt(14)),  # outer
        TimeInterval(dt(11), dt(12)),  # nested
        TimeInterval(dt(14), dt(15)),  # touching at 14:00
    ]
    unioned = union_intervals(intervals)
    assert len(unioned) == 1
    assert unioned[0].start == dt(10)
    assert unioned[0].end == dt(15)
    assert calculate_unioned_duration_seconds(intervals) == 5 * 3600

