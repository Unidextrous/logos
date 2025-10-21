# context.py
from __future__ import annotations
from typing import Union, Callable
from .truth import TruthState, TruthValue, Modality  # Make sure Modality is imported


class RelationContext:
    """
    Represents a logical condition built from one or more Relations or RelationContexts.
    Supports logical NOT (~), AND (&), OR (|), XOR (^), NAND, NOR, and XNOR.
    """

    def __init__(self, condition: Union[Callable[[], TruthValue], tuple, "Relation", "RelationContext"]):  # type: ignore
        """
        condition can be:
          - a callable returning a TruthValue
          - a (operator, operands) tuple representing a logical tree
          - a Relation or RelationContext object
        """
        self.condition = condition

    def evaluate(self, sample_probability: bool = False) -> TruthValue:
        """Recursively evaluate the logical condition and return a TruthValue."""
        # --- Callable case ---
        if callable(self.condition):
            result = self.condition()
            if isinstance(result, TruthValue):
                return result
            return TruthValue(value=TruthState.TRUE if bool(result) else TruthState.FALSE)

        # --- Single Relation or RelationContext ---
        if not isinstance(self.condition, tuple):
            # Avoid top-level import to prevent circular import
            from .relation import Relation  # local import
            if isinstance(self.condition, Relation):
                tv = self.condition.evaluate_truth()
                return tv if isinstance(tv, TruthValue) else TruthValue(tv)
            elif isinstance(self.condition, RelationContext):
                return self.condition.evaluate(sample_probability=sample_probability)
            return TruthValue(value=TruthState.TRUE if bool(self.condition) else TruthState.FALSE)

        # --- Logical tree (operator, operands) ---
        op, *args = self.condition
        vals = [RelationContext.ensure(a).evaluate(sample_probability=sample_probability) for a in args]

        # --- Logic operations ---
        if op == "NOT":
            tv = vals[0]
            if tv.value == TruthState.TRUE:
                return TruthValue(TruthState.FALSE, modality=tv.modality)
            if tv.value == TruthState.FALSE:
                return TruthValue(TruthState.TRUE, modality=tv.modality)
            # UNKNOWN passes through
            return tv

        elif op == "AND":
            if any(v.value == TruthState.FALSE for v in vals):
                return TruthValue(TruthState.FALSE)
            if all(v.value == TruthState.TRUE for v in vals):
                return TruthValue(TruthState.TRUE)
            return TruthValue(TruthState.UNKNOWN)

        elif op == "OR":
            if any(v.value == TruthState.TRUE for v in vals):
                return TruthValue(TruthState.TRUE)
            if all(v.value == TruthState.FALSE for v in vals):
                return TruthValue(TruthState.FALSE)
            return TruthValue(TruthState.UNKNOWN)

        elif op == "XOR":
            true_count = sum(v.value == TruthState.TRUE for v in vals)
            return TruthValue(TruthState.TRUE if true_count % 2 == 1 else TruthState.FALSE)

        elif op == "NAND":
            return RelationContext(("NOT", ("AND", *args))).evaluate(sample_probability=sample_probability)

        elif op == "NOR":
            return RelationContext(("NOT", ("OR", *args))).evaluate(sample_probability=sample_probability)

        elif op == "XNOR":
            return RelationContext(("NOT", ("XOR", *args))).evaluate(sample_probability=sample_probability)

        else:
            raise ValueError(f"Unknown logical operator: {op}")

    # --- Operator overloads ---
    def __invert__(self):
        return RelationContext(("NOT", self))

    def __and__(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        return RelationContext(("AND", self, RelationContext.ensure(other)))

    def __or__(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        return RelationContext(("OR", self, RelationContext.ensure(other)))

    def __xor__(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        return RelationContext(("XOR", self, RelationContext.ensure(other)))

    # Convenience for NAND, NOR, XNOR
    def nand(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        return RelationContext(("NAND", self, RelationContext.ensure(other)))

    def nor(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        return RelationContext(("NOR", self, RelationContext.ensure(other)))

    def xnor(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        return RelationContext(("XNOR", self, RelationContext.ensure(other)))

    @staticmethod
    def ensure(value: Union["RelationContext", "Relation"]) -> "RelationContext":  # type: ignore
        """Wrap non-context objects into a RelationContext."""
        from .relation import Relation  # local import to avoid circular dependency
        if isinstance(value, RelationContext):
            return value
        if isinstance(value, Relation):
            return RelationContext(value)
        raise TypeError(f"Cannot wrap {value} into RelationContext")

    def __repr__(self):
        if callable(self.condition):
            return "<RelationContext(callable)>"
        if not isinstance(self.condition, tuple):
            return f"<RelationContext({self.condition})>"
        op, *args = self.condition
        return f"<RelationContext({op}, {args})>"
