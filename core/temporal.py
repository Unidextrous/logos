# temoral.py
from datetime import datetime, timedelta
from typing import Optional, List
from .relation import Relation


class TimeInterval:
    """
    Represents a period of time with an optional start and end.

    - If start_time is None, the interval is considered to begin indefinitely in the past.
    - If end_time is None, the interval continues indefinitely into the future.
    """

    def __init__(self, start_time: Optional[datetime], end_time: Optional[datetime] = None):
        self.start_time = start_time
        self.end_time = end_time

    # ────────────────────────────────────────────────────────────────
    # Fundamental Behaviors
    # ────────────────────────────────────────────────────────────────

    def contains(self, moment: datetime) -> bool:
        """
        Return True if the given datetime 'moment' falls within this interval.

        Open-ended intervals (with None for start or end) are treated as infinite.
        """
        if self.start_time is not None and moment < self.start_time:
            return False
        if self.end_time is not None and moment >= self.end_time:
            return False
        return True

    def overlaps(self, other: "TimeInterval") -> bool:
        """
        Check whether this interval overlaps another.

        Open-ended sides are treated as infinitely far in that direction.
        """
        start_a = self.start_time or datetime.min
        end_a = self.end_time or datetime.max
        start_b = other.start_time or datetime.min
        end_b = other.end_time or datetime.max
        return start_a < end_b and start_b < end_a

    # ────────────────────────────────────────────────────────────────
    # Editing & Management
    # ────────────────────────────────────────────────────────────────

    def modify(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        """
        Safely modify this interval's start and/or end time.
        Ensures start_time < end_time if both are defined.
        """
        if start_time is not None and end_time is not None and start_time >= end_time:
            raise ValueError("start_time must be earlier than end_time")

        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time

    # ────────────────────────────────────────────────────────────────
    # Representations
    # ────────────────────────────────────────────────────────────────

    def __repr__(self):
        return f"<TimeInterval {self.start_time} → {self.end_time}>"

    def __lt__(self, other: "TimeInterval"):
        """Allow sorting intervals chronologically (None treated as earliest start)."""
        return (self.start_time or datetime.min) < (other.start_time or datetime.min)


class TemporalRelation(Relation):
    """
    Represents a relation whose truth varies over time.
    Extends the standard Relation class with a set of TimeIntervals.
    """

    def __init__(
        self,
        predicate,
        roles: dict,
        *,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        relation_type: str = "TEMPORAL",
        context=None,
        active: bool = True,
    ):
        # Initialize base relation
        super().__init__(predicate, roles, relation_type=relation_type, context=context)

        # Store active intervals
        self.active_intervals: List[TimeInterval] = []

        # If an interval is specified, add it immediately
        if active:
            self.add_interval(start_time, end_time)

    # ────────────────────────────────────────────────────────────────
    # Interval Management
    # ────────────────────────────────────────────────────────────────

    def add_interval(self, start_time: Optional[datetime], end_time: Optional[datetime] = None):
        """
        Add a new interval, ensuring no overlaps occur.
        Intervals are automatically sorted chronologically.
        """
        new_interval = TimeInterval(start_time, end_time)

        # Check for overlap with existing intervals
        for existing in self.active_intervals:
            if new_interval.overlaps(existing):
                raise ValueError(f"New interval {new_interval} overlaps existing {existing}")

        self.active_intervals.append(new_interval)
        self.active_intervals.sort()

    def remove_interval(self, interval: TimeInterval):
        """Remove a specific interval, if it exists."""
        if interval in self.active_intervals:
            self.active_intervals.remove(interval)

    def clear(self):
        """Remove all intervals entirely."""
        self.active_intervals.clear()

    # ────────────────────────────────────────────────────────────────
    # Temporal Logic
    # ────────────────────────────────────────────────────────────────

    def is_active_at(self, moment: datetime) -> bool:
        """Return True if any interval contains the given time."""
        return any(interval.contains(moment) for interval in self.active_intervals)

    def get_current_interval(self) -> Optional[TimeInterval]:
        """Return the interval that contains the current time, if any."""
        now = datetime.now()
        for interval in self.active_intervals:
            if interval.contains(now):
                return interval
        return None

    # ────────────────────────────────────────────────────────────────
    # Representation
    # ────────────────────────────────────────────────────────────────

    def __repr__(self):
        return f"<TemporalRelation type={self.relation_type} intervals={self.active_intervals}>"
