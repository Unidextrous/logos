# ontology.py
from .entity import *
from .relation import *
from .temporal import *

class Ontology:
    """
    Central knowledge base storing all entities, predicates, and relations.
    Handles inheritance, propagation of relations, and expiration of temporary facts.
    """
    def __init__(self):
        self.entities = {}    # dict[str, Entity]: key = entity.id
        self.predicates = {}  # dict[str, Predicate]
        self.relations = []   # list[Relation]

    def add_entity(self, name, word_type, entity_types=None, description=None):
        """
        Create and register a new entity.

        Returns:
            Entity: The newly created entity.
        """
        e = Entity(name, word_type, entity_types, description)
        if e.id in self.entities:
            raise ValueError(f"Entity '{e.id}' already exists.")
        self.entities[e.id] = e
        return e

    def add_predicate(self, name: str):
        """Create and register a new predicate."""
        p = Predicate(name)
        self.predicates[p.name] = p
        return p

    def add_relation(self, predicate, roles: dict, relation_type="GENERAL", context=None):
        """
        Add a new relation between entities (n-ary).

        Prevents duplicates and propagates to descendant entities.

        Args:
            predicate (Predicate): Type of relation.
            roles (dict[str, Entity]): Role-to-entity mapping.
            relation_type (str): Logical type.
            context (any): Optional context dependency.
            duration (timedelta | None): Optional lifespan of relation.

        Returns:
            Relation: The newly created or existing relation.
        """
        # Prevent duplicates
        for existing in self.relations:
            if (existing.predicate == predicate and
                existing.roles == roles and
                existing.context == context):
                return existing

        r = Relation(predicate, roles, relation_type, context)

        # If this relation has a context that is another relation, register as dependent
        if isinstance(context, Relation):
            context.dependents.add(r)
        self.relations.append(r)

        # Attach relation to each involved entity
        for e in roles.values():
            e.relations.append(r)

        # Propagate to descendants dynamically
        self.propagate_relation_to_descendants(r)
        return r

    def add_temporal_relation(
        self,
        predicate,
        roles: dict,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        relation_type: str = "GENERAL",
        context=None,
        active: bool = True,
    ):
        """
        Create and register a TemporalRelation.

        Args:
            predicate (Predicate): relation type (e.g., ATTENDS)
            roles (dict): role->Entity mapping
            start_time (datetime|None): when relation begins (may be None)
            end_time (datetime|None): when relation ends (may be None)
            relation_type (str): logical subtype (e.g., CONTEXTUAL, PERMANENT...)
            context (any): optional context (Relation, RelationContext, or callable)
            active (bool): whether the relation starts active
        """
        for existing in self.relations:
            if (isinstance(existing, TemporalRelation) and
                existing.predicate == predicate and
                existing.roles == roles and
                existing.context == context and
                getattr(existing, "relation_type", None) == relation_type.upper()):
                return existing

        r = TemporalRelation(
            predicate=predicate,
            roles=roles,
            start_time=start_time,
            end_time=end_time,
            context=context,
            relation_type=relation_type,
            active=active,
        )

        self.relations.append(r)

        for e in roles.values():
            e.relations.append(r)

        self.propagate_relation_to_descendants(r)

        if isinstance(context, Relation):
            context.dependents.add(r)

        return r
    
    def propagate_relation_to_descendants(self, relation):
        """
        Ensure descendants of any involved entities inherit this relation.
        """
        involved = set(relation.roles.values())
        for e in self.entities.values():
            if any(ancestor in e.get_all_ancestors() for ancestor in involved):
                if relation not in e.relations:
                    e.relations.append(relation)

    def describe_hierarchy(self, entity, level=0, seen=None, show_description=False):
        """
        Print entity hierarchy recursively with optional descriptions.
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

    def refresh_context_relations(self):
        """
        Re-evaluate all contextual relations recursively based on their dependencies.
        """
        visited = set()

        def update_relation(relation):
            if relation in visited:
                return
            visited.add(relation)
            if isinstance(relation.context, Relation):
                update_relation(relation.context)
            relation.update_from_context()

        for r in self.relations:
            if r.context:
                update_relation(r)

        # Update all contextual relations
        for r in self.relations:
            if getattr(r, "relation_type", None) == "CONTEXTUAL":
                update_relation(r)
