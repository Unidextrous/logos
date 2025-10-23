# ontology.py
from .entity import *
from .relation import *
from .temporal import *
from .quantifier import *

class Ontology:
    """
    Central knowledge base storing all entities, predicates, and relations.
    Handles inheritance, propagation of relations, and expiration of temporary facts.
    """
    def __init__(self):
        self.entities = {}    # dict[str, Entity]: key = entity.id
        self.alias_map = {}  # dict[str, Entity]: key = alias name
        self.predicates = {}  # dict[str, Predicate]
        self.relations = []   # list[Relation]
        self.quantified_propositions = []   # list[QuantifiedProposition]

    def add_entity(self, name, word_type, parents=None, description=None):
        """
        Create and register a new entity.

        Returns:
            Entity: The newly created entity.
        """
        e = Entity(name, word_type, parents, description)
        if e.id in self.entities:
            raise ValueError(f"Entity '{e.id}' already exists.")
        self.entities[e.id] = e
        return e

    def add_alias(self, alias_name: str, target_entity: Entity):
        """Register an alias purely for query purposes, supporting homonyms."""
        alias_name = alias_name.upper()
        if alias_name not in self.alias_map:
            self.alias_map[alias_name] = []

        # Avoid duplicates
        if target_entity not in self.alias_map[alias_name]:
            self.alias_map[alias_name].append(target_entity)

        # Ensure the target entity also stores the alias
        if alias_name not in target_entity.aliases:
            target_entity.aliases.append(alias_name)

    def resolve_entity(self, name: str):
        """
        Return all entities whose name or alias matches the query.
        Homonyms are handled by returning multiple entities.
        """
        name = name.upper()
        # Entities whose canonical name or alias matches
        matches = [e for e in self.entities.values() if name in e.all_names()]

        # Include any entities listed in alias_map
        alias_matches = self.alias_map.get(name, [])
        all_matches = list({*matches, *alias_matches})  # remove duplicates

        return all_matches

    def get_entity(self, name: str):
        """
        Retrieve an entity (or entities) by name or alias.

        If multiple entities match (homonyms), returns the full list
        so the parser or user can decide which one was intended.

        Args:
            name (str): The canonical name or alias to search for.

        Returns:
            Entity | list[Entity] | None:
                - A single Entity if exactly one match is found.
                - A list of Entities if multiple matches exist.
                - None if no matches exist.
        """
        matches = self.resolve_entity(name)

        if not matches:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            return matches

    def add_predicate(self, name: str):
        """Create and register a new predicate."""
        name = name.upper()  # standardize

        if name in self.predicates:
            raise ValueError(f"Predicate '{name}' already exists.")

        p = Predicate(name)
        self.predicates[name] = p
        return p

    def add_inverse_predicate(
        self,
        original_predicate: Predicate,
        inverse_name: str,
        role_mapping: dict[str, str]
    ):
        """
        Add an inverse Predicate for the original predicate.

        Args:
            original_predicate: The Predicate to invert.
            inverse_name: Name of the inverse predicate.
            role_mapping: Dict mapping original roles -> inverse roles.
        """
        # Create the inverse Predicate
        inverse_pred = Predicate(inverse_name, roles=list(role_mapping.values()))
        inverse_pred.inverse_of = original_predicate
        inverse_pred.role_mapping = role_mapping

        # Register the inverse
        original_predicate.inverses.append(inverse_pred)
        self.predicates[inverse_pred.name] = inverse_pred

        # Optionally: generate inverse Relations for existing Relations
        for rel in self.relations:
            if rel.predicate == original_predicate:
                self._create_inverse_relation(rel, inverse_pred)

        return inverse_pred
    
    def add_relation(
        self,
        predicate,
        roles: dict,
        relation_type="GENERAL",
        context=None,
        truth_value=None,
    ):
        """
        Add a new relation between entities (n-ary).

        Prevents duplicates and propagates to descendant entities.

        Args:
            predicate (Predicate): Type of relation.
            roles (dict[str, Entity]): Role-to-entity mapping.
            relation_type (str): Logical type.
            context (any): Optional context dependency.
            truth_value (TruthValue | None): Optional explicit truth value.

        Returns:
            Relation: The newly created or existing relation.
        """
        # Prevent duplicates
        for existing in self.relations:
            if (
                existing.predicate == predicate
                and existing.roles == roles
                and existing.context == context
            ):
                return existing

        # Create relation with truth_value if provided
        r = Relation(
            predicate,
            roles,
            relation_type,
            context,
            truth_value=truth_value,
        )

        # Register dependency if context is another relation
        if isinstance(context, Relation):
            context.dependents.add(r)

        self.relations.append(r)

        # Attach to entities
        for e in roles.values():
            e.relations.append(r)

        # Propagate to descendants
        self.propagate_relation_to_descendants(r)

        return r

    def add_temporal_relation(
        self,
        predicate,
        roles: dict,
        *,
        relation_type: str = "GENERAL",
        context=None,
        default_truth=None
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
            truth_value (TruthValue | None): optional explicit truth value.
            active (bool): whether the relation starts active
        """
        for existing in self.relations:
            if (
                isinstance(existing, TemporalRelation)
                and existing.predicate == predicate
                and existing.roles == roles
                and existing.context == context
                and getattr(existing, "relation_type", None) == relation_type.upper()
            ):
                return existing

        # Create TemporalRelation with optional truth_value
        r = TemporalRelation(
            predicate=predicate,
            roles=roles,
            context=context,
            relation_type=relation_type,
            default_truth=default_truth
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
        print(f"{indent}{entity.name} ({', '.join([p.name for p in entity.parents])}){desc_str}")
        seen.add(entity.id)
        for p in entity.parents:
            if p.id not in seen:
                self.describe_hierarchy(p, level=level+1, seen=seen, show_description=show_description)

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

    def add_quantified_proposition(self, quantifier, variables, relation_template, truth_value=None):
        """
        relation_template: dict, e.g.
        {
            "predicate": "EATS",
            "roles": {
                "subject": "DEX",
                "object": "$X"
            }
        }
        """
        qp = QuantifiedProposition(
            quantifier=quantifier,
            variables=variables,
            relation_template=relation_template,
            truth_value=truth_value
        )
        self.quantified_propositions.append(qp)
        return qp
