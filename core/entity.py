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
        self.id = f"ENT_{uuid.uuid4().hex[:8]}" # unique entity ID
        self.name = name.upper()
        self.word_type = word_type.upper()
        self.parents = parents or []
        self.aliases = [a.upper() for a in (aliases or [])]
        self.description = description
        self.relations = []  # direct and propagated relations

    def matches_name(self, query_name: str) -> bool:
        """Check if the query_name matches the primary name or any alias."""
        query_upper = query_name.upper()
        return query_upper == self.name or query_upper in self.aliases
    
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

    def to_dict(self) -> dict:
        """
        Serialize the entity to a dictionary for saving.
        """
        return {
            "id": self.id,
            "name": self.name,
            "word_type": self.word_type,
            "parents": [p.id for p in self.parents],  # store parent IDs
            "aliases": self.aliases,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict, ontology=None) -> "Entity":
        """
        Reconstruct an Entity from a dictionary.
        If ontology is provided, resolve parent references to Entity objects.
        """
        e = cls(
            name=data["name"],
            word_type=data["word_type"],
            parents=[],  # will attach parents below if ontology is provided
            aliases=data.get("aliases", []),
            description=data.get("description")
        )
        e.id = data["id"]  # restore original ID

        if ontology and "parents" in data:
            e.parents = [ontology.entities[parent_id] for parent_id in data["parents"] if parent_id in ontology.entities]

        return e
        
    def __repr__(self):
        return f"Entity({self.name})"
