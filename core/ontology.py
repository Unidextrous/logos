# ontology.py
from .entity import *
from .relation import *

class Ontology:
    def __init__(self):
        self.entities = {}
        self.predicates = {}
        self.relations = []

    def add_entity(self, name, word_type, entity_types=None, description=None):
        e = Entity(name, word_type, entity_types, description)
        if e.id in self.entities:
            raise ValueError(f"Entity '{e.id}' already exists.")
        self.entities[e.id] = e
        return e

    def add_predicate(self, name: str):
        p = Predicate(name)
        self.predicates[p.name] = p
        return p

    def add_relation(self, predicate, roles: dict, relation_type="GENERAL", context=None, duration=None):
        """Add a new relation (n-ary)."""
        # Prevent duplicates
        for existing in self.relations:
            if (existing.predicate == predicate and
                existing.roles == roles and
                existing.context == context):
                return existing

        r = Relation(predicate, roles, relation_type, context, duration)
        self.relations.append(r)

        # Attach relation to each involved entity
        for e in roles.values():
            e.relations.append(r)

        # Propagate to descendants dynamically
        self.propagate_relation_to_descendants(r)
        return r

    def propagate_relation_to_descendants(self, relation):
        """Ensure descendants of any involved entities inherit this relation."""
        involved = set(relation.roles.values())
        for e in self.entities.values():
            if any(ancestor in e.get_all_ancestors() for ancestor in involved):
                if relation not in e.relations:
                    e.relations.append(relation)

    def describe_hierarchy(self, entity, level=0, seen=None, show_description=False):
        if seen is None:
            seen = set()
        indent = "    " * level + "└─" if level > 0 else ""
        desc_str = f" — {entity.description}" if show_description and entity.description else ""
        print(f"{indent}{entity.name} ({', '.join([et.name for et in entity.entity_types])}){desc_str}")
        seen.add(entity.id)
        for et in entity.entity_types:
            if et.id not in seen:
                self.describe_hierarchy(et, level=level+1, seen=seen, show_description=show_description)

    def expire_temporary_relations(self, context=None):
        new_relations = []
        for r in self.relations:
            if r.is_active():
                new_relations.append(r)
            else:
                for ent in r.roles.values():
                    if r in ent.relations:
                        ent.relations.remove(r)
        self.relations = new_relations
