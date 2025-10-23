# quantifier.py
from enum import Enum
from .truth import TruthValue, TruthState

class Quantifier(Enum):
    FORALL = "FORALL"
    EXISTS = "EXISTS"

class QuantifiedProposition:
    """
    Represents a quantified logical proposition, e.g.,
    FORALL X: LOVES(X, TONYA)
    EXISTS Y: OWNS(DEX, Y)
    """

    def __init__(self, quantifier: Quantifier, variables: list[str], proposition, truth_value: TruthValue | None = None):
        """
        Args:
            quantifier (Quantifier): FORALL or EXISTS
            variables (list[str]): Variable names used in the proposition, e.g., ["X"]
            proposition (Relation | callable): The logical proposition or Relation template
            truth_value (TruthValue | None): Optional initial truth value (defaults to UNKNOWN)
        """
        self.quantifier = quantifier
        self.variables = [v.upper() for v in variables]  # standardize
        self.proposition = proposition
        self.truth_value = truth_value or TruthValue(value=TruthState.UNKNOWN)

    def __repr__(self):
        vars_str = ", ".join(self.variables)
        return f"{self.quantifier}({vars_str}): {self.proposition} [{self.truth_value}]"

    def __eq__(self, other):
        if not isinstance(other, QuantifiedProposition):
            return NotImplemented

        # Check quantifier and variable names
        if self.quantifier != other.quantifier:
            return False
        if len(self.variables) != len(other.variables):
            return False

        # Check proposition identity (or string representation if callable)
        if callable(self.proposition) and callable(other.proposition):
            # Compare string representations for simplicity
            return self.proposition.__code__.co_code == other.proposition.__code__.co_code
        else:
            return self.proposition == other.proposition

    def __hash__(self):
        # Make hash compatible with __eq__
        prop_hash = None
        if callable(self.proposition):
            prop_hash = hash(self.proposition.__code__.co_code)
        else:
            prop_hash = hash(self.proposition)
        return hash((self.quantifier, tuple(self.variables), prop_hash))
    