# relation.py
from datetime import datetime, timedelta
from .context import RelationContext

class Predicate:
    """Represents a type of relation (like IS, HAS, TAKES_TO)."""
    def __init__(self, name: str):
        self.name = name.upper()

class Relation:
    """
    Represents a logical relation between entities.

    Supports n-ary roles, optional context, and permanent/temporary status.
    """

    def __init__(self, predicate, roles: dict, relation_type="GENERAL", context=None, active=True):
        """
        Args:
            predicate (Predicate): Type of relation (e.g., IS, HAS).
            roles (dict[str, Entity]): Mapping role names to entities, e.g., {"subject": FIDO, "object": DOG}.
            relation_type (str): Logical type: GENERAL, PERMANENT, etc.
            context (any): Optional context that governs the validity of the relation.
            active (bool): Whether active at creation.
        """
        self.predicate = predicate
        self.predicate_name = predicate.name.upper()
        self.roles = roles
        self.relation_type = relation_type.upper()
        self.context = context
        self.active = active
        self.manual_override = None
        self.dependents = set()

    def is_active(self) -> bool:
        """Check if relation is currently active based on context and manual override."""
        if not self.active:
            return False

        if isinstance(self.context, Relation):
            return self.context.is_active()
        elif isinstance(self.context, RelationContext):
            return self.context.evaluate()
        elif callable(self.context):
            return bool(self.context())
        elif self.context is not None:
            return bool(self.context)

        return self.active

    def activate(self):
        """Mark relation as active and notify dependents."""
        self.active = True
        self.manual_override = True
        for dep in self.dependents:
            dep.update_from_context(force=True)

    def deactivate(self):
        """Mark relation as inactive and notify dependents."""
        self.active = False
        self.manual_override = False
        for dep in self.dependents:
            dep.update_from_context(force=True)

    def update_from_context(self, force=False):
        """Update active state based on context."""
        new_state = self.is_active()
        if self.active != new_state or force:
            self.active = new_state
            for dep in self.dependents:
                dep.update_from_context(force=force)

    def __repr__(self):
        roles_str = ", ".join([f"{k}={v.name}" for k, v in self.roles.items()])
        ctx = f", context={self.context}" if self.context else ""
        if self.active:
            return f"Relation({self.predicate_name}: {roles_str}, type={self.relation_type}{ctx})"
        return "Inactive Relation"
