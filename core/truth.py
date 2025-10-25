# trith.py
from enum import Enum, auto
import random

class TruthState(Enum):
    TRUE = auto()
    FALSE = auto()
    UNKNOWN = auto()

class TruthValue:
    """
    Represents a truth.
    Supports TRUE, FALSE, UNKNOWN with optional certainty metadata.
    """

    def __init__(
        self,
        value: TruthState = TruthState.UNKNOWN,
        certainty: float | None = None 
    ):
        self.value = value
        self.certainty = certainty

    def to_dict(self):
        return {"value": self.value.value, "certainty": getattr(self, "certainty", None)}

    @classmethod
    def from_dict(cls, data):
        return cls(value=TruthState(data["value"]))
    
    def __repr__(self):
        prob_str = f", certainty={self.certainty}" if self.certainty is not None else ""
        return f"{self.value.name}{prob_str}"
