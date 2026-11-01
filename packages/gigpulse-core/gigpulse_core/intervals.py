"""Time interval mathematics and union algorithms for multi-platform sessions.

Gig workers often run multiple apps simultaneously (e.g., waiting on Platform A
and Platform B). Simple summation double-counts hours. This module merges
overlapping and contiguous intervals to compute true worker online time.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List


@dataclass(frozen=True)
class TimeInterval:
    """Represents a bounded half-open time interval [start, end)."""
    start: datetime
    end: datetime

    def __post_init__(self):
        # Normalize timezone to UTC if offset-aware, otherwise treat as UTC
        if self.start.tzinfo is None:
            object.__setattr__(self, "start", self.start.replace(tzinfo=timezone.utc))
        if self.end.tzinfo is None:
            object.__setattr__(self, "end", self.end.replace(tzinfo=timezone.utc))
        
        if self.end < self.start:
            raise ValueError(f"Interval end ({self.end}) cannot be before start ({self.start})")

    @property
    def duration_seconds(self) -> int:
        return int((self.end - self.start).total_seconds())


def union_intervals(intervals: Iterable[TimeInterval]) -> List[TimeInterval]:
    """Compute the union of an arbitrary collection of time intervals.
    
    Merges overlapping and touching intervals. Returns sorted, non-overlapping intervals.
    """
    sorted_intervals = sorted(intervals, key=lambda iv: iv.start)
    if not sorted_intervals:
        return []

    merged: List[TimeInterval] = []
    current_start = sorted_intervals[0].start
    current_end = sorted_intervals[0].end

    for iv in sorted_intervals[1:]:
        if iv.start <= current_end:
            # Overlapping or contiguous; extend current interval if needed
            if iv.end > current_end:
                current_end = iv.end
        else:
            # Disjoint interval found; commit current and advance
            merged.append(TimeInterval(current_start, current_end))
            current_start = iv.start
            current_end = iv.end

    merged.append(TimeInterval(current_start, current_end))
    return merged


def calculate_unioned_duration_seconds(intervals: Iterable[TimeInterval]) -> int:
    """Calculate total online seconds across intervals without double-counting overlap."""
    unioned = union_intervals(intervals)
    return sum(iv.duration_seconds for iv in unioned)

