# temporal.py
from datetime import datetime
from typing import Optional, List
from .relation import Relation
from .truth import TruthState, TruthValue

class TimeInterval:
    """
    Represents a period of time with an optional start and end.
    """
    def __init__(self, start_time: Optional[datetime], end_time: Optional[datetime] = None):
        self.start_time = start_time
        self.end_time = end_time

    def contains(self, moment: datetime) -> bool:
        if self.start_time is not None and moment < self.start_time:
            return False
        if self.end_time is not None and moment >= self.end_time:
            return False
        return True

    def overlaps(self, other: "TimeInterval") -> bool:
        start_a = self.start_time or datetime.min
        end_a = self.end_time or datetime.max
        start_b = other.start_time or datetime.min
        end_b = other.end_time or datetime.max
        return start_a < end_b and start_b < end_a

    def modify(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        if start_time is not None and end_time is not None and start_time >= end_time:
            raise ValueError("start_time must be earlier than end_time")
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time

    def to_dict(self):
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

    @classmethod
    def from_dict(cls, data):
        start = datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None
        end = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        return cls(start, end)
    
    def __repr__(self):
        return f"<TimeInterval {self.start_time} → {self.end_time}>"

    def __lt__(self, other: "TimeInterval"):
        return (self.start_time or datetime.min) < (other.start_time or datetime.min)


class TemporalRelation(Relation):
    """
    Represents a relation whose truth varies over time.
    Extends the standard Relation class with a dictionary mapping intervals to TruthValues.
    """

    def __init__(
        self,
        predicate,
        roles: dict,
        *,
        relation_type: str = "GENERAL",
        context=None,
        default_truth: TruthValue | None = None
    ):
        super().__init__(predicate, roles, relation_type=relation_type, context=context)
        self.interval_truths: dict[TimeInterval, TruthValue] = {}
        self.default_truth = default_truth or TruthValue(TruthState.UNKNOWN)

    # ──────────────────────────────────────────────
    # Interval Management
    # ──────────────────────────────────────────────

    def add_interval(self, interval: TimeInterval, truth_value: TruthValue | None = None):
        """
        Add a new interval with a TruthValue.
        Raises ValueError if the interval overlaps any existing interval.
        """
        for existing in self.interval_truths:
            if interval.overlaps(existing):
                raise ValueError(f"New interval {interval} overlaps existing {existing}")
        self.interval_truths[interval] = truth_value or TruthValue()

    def remove_interval(self, interval: TimeInterval):
        """Remove a specific interval if it exists."""
        if interval in self.interval_truths:
            del self.interval_truths[interval]

    def clear_intervals(self):
        """Remove all intervals."""
        self.interval_truths.clear()

    # ──────────────────────────────────────────────
    # Temporal Logic
    # ──────────────────────────────────────────────

    def truth_value_at(self, moment: datetime | None = None) -> TruthState:
        if moment is None:
            moment = datetime.now()
        interval = next((i for i in self.interval_truths if i.contains(moment)), None)
        if interval is None:
            return self.default_truth.evaluate()
        return self.interval_truths[interval].evaluate()

    def get_current_interval(self) -> tuple[TimeInterval, TruthValue] | None:
        """Return the current interval and its TruthValue, if any."""
        now = datetime.now()
        for interval, tv in self.interval_truths.items():
            if interval.contains(now):
                return (interval, tv)
        return None

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "default_truth": self.default_truth.to_dict() if self.default_truth else None,
            "interval_truths": [
                {
                    "start_time": i.start_time.isoformat() if i.start_time else None,
                    "end_time": i.end_time.isoformat() if i.end_time else None,
                    "truth_value": tv.to_dict() if tv else None
                }
                for i, tv in self.interval_truths.items()
            ]
        })
        return base

    @classmethod
    def from_dict(cls, data, ontology):
        # Reconstruct the base Relation
        predicate = ontology.predicates[data["predicate"]]
        roles = {role_name: ontology.entities[ent_id] for role_name, ent_id in data["roles"].items()}
        context = data.get("context")
        default_truth = TruthValue.from_dict(data["default_truth"]) if data.get("default_truth") else None

        r = cls(predicate, roles, relation_type=data.get("relation_type", "GENERAL"),
                context=context, default_truth=default_truth)

        # Reconstruct interval_truths
        for interval_dict in data.get("interval_truths", []):
            start = datetime.fromisoformat(interval_dict["start_time"]) if interval_dict.get("start_time") else None
            end = datetime.fromisoformat(interval_dict["end_time"]) if interval_dict.get("end_time") else None
            interval = TimeInterval(start, end)
            tv = TruthValue.from_dict(interval_dict["truth_value"]) if interval_dict.get("truth_value") else TruthValue()
            r.interval_truths[interval] = tv

        return r

    # ──────────────────────────────────────────────
    # Representation
    # ──────────────────────────────────────────────

    def __repr__(self):
        return f"<TemporalRelation type={self.relation_type} intervals={list(self.interval_truths.items())}>"
