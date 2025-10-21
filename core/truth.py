# trith.py
from enum import Enum, auto
import random

class Modality(Enum):
    ALETHIC = auto()
    DEONTIC = auto()
    EPISTEMIC = auto()
    PROBABILISTIC = auto()

class TruthState(Enum):
    TRUE = auto()
    FALSE = auto()
    UNKNOWN = auto()

class TruthValue:
    """
    Represents a truth under a modality.
    Supports TRUE, FALSE, UNKNOWN with optional probability metadata.
    """

    def __init__(
        self,
        value: TruthState = TruthState.UNKNOWN,
        modality: Modality = Modality.ALETHIC,
        probability: float | None = None 
    ):
        self.value = value
        self.modality = modality
        self.probability = probability

    def evaluate(self, sample_probability: bool = False) -> TruthState:
        """
        Return the current TruthState.
        - If sample_probability=True, collapse probabilistically.
        - UNKNOWN remains as UNKNOWN.
        """
        if sample_probability:
            if self.probability is not None:
                return TruthState.TRUE if random.random() <= self.probability else TruthState.FALSE
        return self.value

    def __repr__(self):
        prob_str = f", probability={self.probability}" if self.probability is not None else ""
        return f"<TruthValue(modality={self.modality}, value={self.value.name}{prob_str})>"
