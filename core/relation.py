# relation.py
from .truth import TruthState, TruthValue
from .context import RelationContext

class Predicate:
    """Represents a type of relation (like IS, HAS, TAKES_TO)."""
    def __init__(self, name: str, roles: list[str] | None = None):
        self.name = name.upper()
        self.roles = roles or []

class Relation:
    """
    Represents a logical relation between entities.

    Supports n-ary roles, optional context, and truth evaluation via TruthValue.
    """

    def __init__(
        self,
        predicate: Predicate,
        roles: dict,
        relation_type: str = "GENERAL",
        context=None,
        truth_value: TruthValue | None = None
    ):
        """
        Args:
            predicate (Predicate): Type of relation (e.g., IS, HAS).
            roles (dict[str, Entity]): Mapping role names to entities, e.g., {"subject": FIDO, "object": DOG}.
            relation_type (str): Logical type: GENERAL, PERMANENT, etc.
            context (RelationContext | callable | Relation | None): governs validity.
            truth_value (TruthValue | None): initial truth state (defaults to UNKNOWN)
        """
        self.predicate = predicate
        self.predicate_name = predicate.name.upper()
        self.roles = roles
        self.relation_type = relation_type.upper()
        self.context = context
        self.truth_value = truth_value or TruthValue(value=TruthState.UNKNOWN)
        self.dependents = set()

    def evaluate_truth(self) -> TruthState:
        """Evaluate the current truth of this relation based on context."""
        # Context can override the base truth_value
        if isinstance(self.context, Relation):
            return self.context.evaluate_truth()
        elif isinstance(self.context, RelationContext):
            return self.context.evaluate_truth()
        elif callable(self.context):
            # Callables should return a TruthState
            return self.context()
        elif self.context is not None:
            # Wrap raw values into a TruthValue
            return TruthValue(self.context).value

        return self.truth_value.value

    def update_from_context(self):
        """Re-evaluate truth_value based on context and propagate to dependents."""
        new_truth = self.evaluate_truth()
        if new_truth != self.truth_value.value:
            self.truth_value.value = new_truth
            for dep in self.dependents:
                dep.update_from_context()

    def set_truth_value(self, new_value: TruthValue):
        """Directly set a TruthValue and propagate changes."""
        if new_value.value != self.truth_value.value:
            self.truth_value = new_value
            for dep in self.dependents:
                dep.update_from_context()

    def __repr__(self):
        roles_str = ", ".join([f"{k}={v.name}" for k, v in self.roles.items()])
        ctx = f", context={self.context}" if self.context else ""
        return f"Relation({self.predicate_name}: {roles_str}, type={self.relation_type}{ctx}, truth={self.truth_value})"
