# context.py
from __future__ import annotations
from typing import Union, Callable

class RelationContext:
    """
    Represents a logical condition built from one or more Relations.
    Supports logical NOT (~), AND (&), OR (|), XOR (^), NAND, NOR, and XNOR.
    """

    def __init__(self, condition: Union[Callable[[], bool], tuple, "Relation"]):    # type: ignore
        """
        condition can be:
          - a callable returning a bool
          - a (operator, operands) tuple representing a logical tree
          - a Relation or RelationContext object
        """
        self.condition = condition

    def evaluate(self) -> bool:
        """Recursively evaluate the logical condition."""
        # 1. Callable case
        if callable(self.condition):
            return bool(self.condition())

        # 2. Single Relation or RelationContext
        if not isinstance(self.condition, tuple):
            if hasattr(self.condition, "is_active"):
                return self.condition.is_active()
            elif hasattr(self.condition, "evaluate"):
                return self.condition.evaluate()
            return bool(self.condition)

        # 3. Logical tree (operator, operands)
        op, *args = self.condition
        vals = [RelationContext.ensure(a).evaluate() for a in args]

        if op == "NOT":
            return not vals[0]
        elif op == "AND":
            return all(vals)
        elif op == "OR":
            return any(vals)
        elif op == "XOR":
            return vals[0] ^ vals[1]
        elif op == "NAND":
            return not all(vals)
        elif op == "NOR":
            return not any(vals)
        elif op == "XNOR":
            return not (vals[0] ^ vals[1])
        else:
            raise ValueError(f"Unknown logical operator: {op}")

    # --- Operator overloads for symbolic logic ---

    def __invert__(self):
        """~A → NOT A"""
        return RelationContext(("NOT", self))

    def __and__(self, other: Union["RelationContext", "Relation"]): # type: ignore
        """A & B → A AND B"""
        return RelationContext(("AND", self, RelationContext.ensure(other)))

    def __or__(self, other: Union["RelationContext", "Relation"]):  # type: ignore
        """A | B → A OR B"""
        return RelationContext(("OR", self, RelationContext.ensure(other)))

    def __xor__(self, other: Union["RelationContext", "Relation"]): # type: ignore
        """A ^ B → A XOR B"""
        return RelationContext(("XOR", self, RelationContext.ensure(other)))

    # --- Convenience for NAND, NOR, XNOR ---

    def nand(self, other: Union["RelationContext", "Relation"]):    # type: ignore
        """A.nand(B) → NOT (A AND B)"""
        return RelationContext(("NAND", self, RelationContext.ensure(other)))

    def nor(self, other: Union["RelationContext", "Relation"]):   # type: ignore
        """A.nor(B) → NOT (A OR B)"""
        return RelationContext(("NOR", self, RelationContext.ensure(other)))

    def xnor(self, other: Union["RelationContext", "Relation"]):    # type: ignore
        """A.xnor(B) → NOT (A XOR B)"""
        return RelationContext(("XNOR", self, RelationContext.ensure(other)))

    @staticmethod
    def ensure(value: Union["RelationContext", "Relation"]) -> "RelationContext":   # type: ignore
        """Wrap non-context objects into a RelationContext."""
        if isinstance(value, RelationContext):
            return value
        from logos.core.relation import Relation  # Lazy import to avoid circularity
        if isinstance(value, Relation):
            return RelationContext(value)
        raise TypeError(f"Cannot wrap {value} into RelationContext")

    def __repr__(self):
        if callable(self.condition):
            return f"<RelationContext(callable)>"
        if not isinstance(self.condition, tuple):
            return f"<RelationContext({self.condition})>"
        op, *args = self.condition
        return f"<RelationContext({op}, {args})>"