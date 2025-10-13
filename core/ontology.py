# ontology.py
from .entity import Entity
from .relation import Relation

class Ontology:
    """
    Stores all entities and relations. Handles disambiguation of homonyms
    and multi-inheritance hierarchy.
    """

    def __init__(self):
        self.entities = {}   # key: Entity.id -> Entity
        self.relations = []  # list of all Relation objects

    def add_entity(self, name: str, word_type: str, entity_types=None, description: str = None):
        """Add a new Entity to the ontology."""
        e = Entity(name, word_type, entity_types, description)
        if e.id in self.entities:
            raise ValueError(f"Entity '{e.id}' already exists.")
        self.entities[e.id] = e
        return e

    def get_entity(self, name: str, word_type: str = None, entity_type_names=None):
        """
        Return a list of entities matching this name.
        Optionally filter by word_type or a list of parent entity names.
        """
        results = []
        for e in self.entities.values():
            if e.name != name.upper():
                continue
            if word_type and e.word_type != word_type.upper():
                continue
            if entity_type_names:
                parent_names = [et.name for et in e.entity_types]
                if not all(n.upper() in parent_names for n in entity_type_names):
                    continue
            results.append(e)
        return results

    def add_relation(self, predicate: str, subject: Entity, object_: Entity, relation_type: str = "GENERAL"):
        r = Relation(predicate, subject, object_, relation_type)
        self.relations.append(r)
        subject.relations.append(r)
        return r

    def describe_entity(self, name: str):
        """Return all possible meanings for a name."""
        matches = self.get_entity(name)
        if not matches:
            return f"No entity named '{name}' found."
        if len(matches) == 1:
            e = matches[0]
            types_str = ", ".join([et.name for et in e.entity_types])
            return f"{e.name} ({types_str}) — {e.description or 'No description'}"
        result = []
        for i, e in enumerate(matches):
            types_str = ", ".join([et.name for et in e.entity_types])
            result.append(f"{i+1}. {e.name} ({types_str}) — {e.description or 'No description'}")
        return f"Multiple meanings found for '{name}':\n" + "\n".join(result)

    def describe_hierarchy(self, entity, level=0, seen=None, show_description=False):
        """
        Recursively prints the hierarchy of entity_types for a given Entity.
        Avoids duplicate display for multi-inheritance.
        
        Parameters:
        - entity: Entity to describe
        - level: current indentation level (for recursion)
        - seen: set of already printed entity IDs
        - show_description: if True, display entity.description next to the name
        """
        if seen is None:
            seen = set()

        indent = "    " * level + "└─" if level > 0 else ""
        desc_str = f" — {entity.description}" if show_description and entity.description else ""
        print(f"{indent}{entity.name} ({', '.join([et.name for et in entity.entity_types])}){desc_str}")
        seen.add(entity.id)

        for et in entity.entity_types:
            if et.id not in seen:
                self.describe_hierarchy(et, level=level+1, seen=seen, show_description=show_description)
