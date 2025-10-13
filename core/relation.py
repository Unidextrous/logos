# relation.py
from datetime import datetime, timedelta

class Relation:
    def __init__(self, predicate, roles: dict, relation_type="GENERAL", context=None, duration=None):
        self.predicate = predicate
        self.predicate_name = predicate.name.upper()
        self.roles = roles  # e.g. {"subject": FIDO, "object": DOG}
        self.relation_type = relation_type.upper()
        self.context = context
        self.created_at = datetime.now()
        self.duration = duration  # timedelta or None

    def is_active(self):
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
    def __init__(self, name: str):
        self.name = name.upper()
