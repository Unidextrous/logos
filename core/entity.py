# entity.py
import uuid

class Entity:
    def __init__(self, name, word_type, entity_types=None, description=None):
        self.name = name.upper()
        self.word_type = word_type.upper()
        self.entity_types = entity_types or []
        self.description = description
        self.id = f"{self.name}_{uuid.uuid4().hex[:8]}"
        self.relations = []  # direct + inherited via propagation

    def get_all_ancestors(self, seen=None):
        """Return all ancestor entity types recursively."""
        if seen is None:
            seen = set()
        for et in self.entity_types:
            if et not in seen:
                seen.add(et)
                et.get_all_ancestors(seen)
        return seen

    def all_relations(self):
        """Return all relations this entity participates in, including inherited ones."""
        active_rels = [r for r in self.relations if r.is_active()]
        return list(dict.fromkeys(active_rels))  # remove duplicates, preserve order

    def __repr__(self):
        return f"Entity({self.name})"
