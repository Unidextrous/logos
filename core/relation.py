# relation.py
from datetime import datetime, timedelta

class Relation:
    """
    Represents a logical relation between entities.

    Supports n-ary roles, optional context, duration, and permanent vs temporary status.
    """
    def __init__(self, predicate, roles: dict, relation_type="GENERAL", context=None, duration=None, active=True):
        """
        Args:
            predicate (Predicate): Type of relation (e.g., IS, HAS).
            roles (dict[str, Entity]): Mapping role names to entities, e.g., {"subject": FIDO, "object": DOG}.
            relation_type (str): Logical type: GENERAL, PERMANENT, etc.
            context (any): Optional context that governs the validity of the relation.
            duration (timedelta | None): How long a temporary relation remains valid.
        """
        self.predicate = predicate
        self.predicate_name = predicate.name.upper()
        self.roles = roles  # e.g. {"subject": FIDO, "object": DOG}
        self.relation_type = relation_type.upper()
        self.context = context
        self.dependents = set()
        self.created_at = datetime.now()
        self.duration = duration  # timedelta or None
        self.active = active
        self.manual_override = None

    def is_active(self):
        if self.manual_override is True:
            return True
        if self.manual_override is False:
            return False

        # Check expiration
        if self.duration:
            return datetime.now() < self.created_at + self.duration
        # Context
        if isinstance(self.context, Relation):
            return self.context.is_active()
        elif callable(self.context):
            return bool(self.context())
        elif self.context is not None:
            return bool(self.context)
        return True

    def activate(self):
        """Mark this relation as active and update dependents recursively."""
        self.manual_override = True
        self.active = True
        for dep in getattr(self, "dependents", []):
            dep.update_from_context(force=True)

    def deactivate(self):
        """Mark this relation as inactive and update dependents recursively."""
        self.manual_override = False
        self.active = False
        for dep in getattr(self, "dependents", []):
            dep.update_from_context(force=True)

    def update_from_context(self, force=False):
        """Update this relation's active state based on its context."""
        new_state = self.is_active()
        if self.active != new_state or force:
            self.active = new_state
            for dep in self.dependents:
                dep.update_from_context(force=force)

    def __repr__(self):
        """
        Return a string representation of the relation.

        Active relations show predicate, roles, type, and context.
        Inactive relations are clearly labeled.
        """
        roles_str = ", ".join([f"{k}={v.name}" for k, v in self.roles.items()])
        ctx = f", context={self.context}" if self.context else ""
        if self.active:
            return f"Relation({self.predicate_name}: {roles_str}, type={self.relation_type}{ctx})"
        return "Inactive Relation"

class Predicate:
    """
    Represents a type of relation (like IS, HAS, TAKES_TO).
    """
    def __init__(self, name: str):
        self.name = name.upper()
