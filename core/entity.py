# entity.py
import uuid

class Entity:
    """
    Represents a concept or object in the Logos ontology.

    Attributes:
        name (str): Lexical form of the entity, e.g., "DOG".
        word_type (str): Part of speech or type, e.g., "NOUN".
        parents (list[Entity]): Parent types (for inheritance hierarchy).
        aliases list[str]: Alternative names for the entity.
        description (str | None): Optional human-readable description.
        id (str): Unique identifier (UUID-based) for the entity.
        relations (list[Relation]): Relations this entity directly participates in (propagated relations included).
    """
    def __init__(self, name, word_type, parents=None, aliases=None, description=None):
        self.name = name.upper()
        self.word_type = word_type.upper()
        self.parents = parents or []
        self.aliases = [a.upper() for a in (aliases or [])]
        self.description = description
        self.id = f"{self.name}_{uuid.uuid4().hex[:8]}" # unique entity ID
        self.relations = []  # direct and propagated relations

    def get_all_ancestors(self, seen=None):
        """
        Recursively return all ancestor entities in the hierarchy.

        Args:
            seen (set[Entity], optional): Entities already visited to prevent cycles.

        Returns:
            set[Entity]: All ancestors of this entity.
        """
        if seen is None:
            seen = set()
        for p in self.parents:
            if p not in seen:
                seen.add(p)
                p.get_all_ancestors(seen)
        return seen

    def all_relations(self):
        """
        Return all active relations involving this entity, including inherited ones.

        Returns:
            list[Relation]: Active relations without duplicates.
        """
        active_rels = [r for r in self.relations if r.is_active()]
        return list(dict.fromkeys(active_rels))  # remove duplicates, preserve order

    def all_names(self):
        """Return the entity’s canonical name plus any aliases."""
        return {self.name, *self.aliases}

    def __repr__(self):
        return f"Entity({self.name})"
