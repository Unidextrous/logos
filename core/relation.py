# relation.py
from datetime import datetime, timedelta

class Relation:
    """
    Represents a logical relation between entities.

    Supports n-ary roles, optional context, duration, and permanent vs temporary status.
    """
    def __init__(self, predicate, roles: dict, relation_type="GENERAL", context=None, duration=None):
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
        self.created_at = datetime.now()
        self.duration = duration  # timedelta or None

    def is_active(self):
        """
        Determine if this relation is currently valid.

        Returns:
            bool: True if PERMANENT or temporary but not expired.
        """
        if self.relation_type == "PERMANENT":
            return True
        if self.duration:
            return datetime.now() < self.created_at + self.duration
        return True

    def __repr__(self):
        roles_str = ", ".join([f"{k}={v.name}" for k, v in self.roles.items()])
        ctx = f", context={self.context}" if self.context else ""
        return f"Relation({self.predicate_name}: {roles_str}, type={self.relation_type}{ctx})"


class Predicate:
    """
    Represents a type of relation (like IS, HAS, TAKES_TO).
    """
    def __init__(self, name: str):
        self.name = name.upper()
