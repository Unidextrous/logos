# relation.py
import uuid
from typing import Dict, List
from .truth import TruthState, TruthValue
from .context import RelationContext

class Predicate:
    """Represents a type of relation (like IS, HAS, TAKES_TO)."""
    def __init__(self, name: str, roles: list[str] | None = None):
        self.name = name.upper()
        self.roles = roles or []
        self.inverses = []

    def to_dict(self) -> dict:
        """Serialize the Predicate for saving."""
        return {
            "name": self.name,
            "roles": self.roles,
            "inverses": [inv.name for inv in self.inverses],  # just store names
        }

    @classmethod
    def from_dict(cls, data: dict, ontology=None) -> "Predicate":
        """Deserialize a Predicate from a dictionary. Resolves inverses if ontology is provided."""
        p = cls(name=data["name"], roles=data.get("roles", []))
        p.inverses = []
        if ontology and "inverses" in data:
            for inv_name in data["inverses"]:
                if inv_name in ontology.predicates:
                    p.inverses.append(ontology.predicates[inv_name])
        return p

class PredicateInverse(Predicate):
    def __init__(self, name, roles, inverse_of, role_mapping):
        super().__init__(name, roles)
        self.inverse_of = inverse_of       # original Predicate
        self.role_mapping = role_mapping   # dict: original_role -> inverse_role

    def to_dict(self):
        return {
            "name": self.name,
            "roles": self.roles,
            "inverse_of": self.inverse_of.name if self.inverse_of else None,
            "role_mapping": self.role_mapping,
            "inverses": [inv.name for inv in self.inverses],
        }

    @classmethod
    def from_dict(cls, data, ontology=None):
        inverse_of = ontology.predicates.get(data["inverse_of"]) if ontology else None
        p_inv = cls(
            name=data["name"],
            roles=data.get("roles", []),
            inverse_of=inverse_of,
            role_mapping=data.get("role_mapping", {})
        )
        p_inv.inverses = []
        if ontology and "inverses" in data:
            for inv_name in data["inverses"]:
                if inv_name in ontology.predicates:
                    p_inv.inverses.append(ontology.predicates[inv_name])
        return p_inv

class Relation:
    """
    Represents a logical relation between entities.

    Supports n-ary roles, optional context, and truth evaluation via TruthValue.
    """

    def __init__(
        self,
        predicate: Predicate,
        roles: dict,
        relation_type: str = "GENERAL",
        context=None,
        truth_value: TruthValue | None = None
    ):
        """
        Args:
            predicate (Predicate): Type of relation (e.g., IS, HAS).
            roles (dict[str, Entity]): Mapping role names to entities, e.g., {"subject": FIDO, "object": DOG}.
            relation_type (str): Logical type: GENERAL, PERMANENT, etc.
            context (RelationContext | callable | Relation | None): governs validity.
            truth_value (TruthValue | None): initial truth state (defaults to UNKNOWN)
        """
        self.id = f"REL_{uuid.uuid4().hex[:8]}"
        self.predicate = predicate
        self.predicate_name = predicate.name.upper()
        self.roles = roles
        self.relation_type = relation_type.upper()
        self.context = context
        self.truth_value = truth_value or TruthValue(value=TruthState.UNKNOWN)
        self.dependents = set()

    def evaluate_truth(self) -> TruthState:
        """Evaluate the current truth of this relation based on context."""
        # Context can override the base truth_value
        if isinstance(self.context, Relation):
            return self.context.evaluate_truth()
        elif isinstance(self.context, RelationContext):
            return self.context.evaluate_truth()
        elif callable(self.context):
            # Callables should return a TruthState
            return self.context()
        elif self.context is not None:
            # Wrap raw values into a TruthValue
            return TruthValue(self.context).value

        return self.truth_value.value

    def update_from_context(self):
        """Re-evaluate truth_value based on context and propagate to dependents."""
        new_truth = self.evaluate_truth()
        if new_truth != self.truth_value.value:
            self.truth_value.value = new_truth
            for dep in self.dependents:
                dep.update_from_context()

    def set_truth_value(self, new_value: TruthValue):
        """Directly set a TruthValue and propagate changes."""
        if new_value.value != self.truth_value.value:
            self.truth_value = new_value
            for dep in self.dependents:
                dep.update_from_context()

    def to_dict(self):
        return {
            "id": getattr(self, "id", None),
            "predicate": self.predicate.name,
            "roles": {role: entity.id for role, entity in self.roles.items()},
            "relation_type": self.relation_type,
            "context": getattr(self.context, "id", None) if self.context else None,
            "truth_value": self.truth_value.to_dict() if self.truth_value else None,
        }

    @classmethod
    def from_dict(cls, data, ontology):
        predicate = ontology.predicates.get(data["predicate"])
        if not predicate:
            raise ValueError(f"Predicate {data['predicate']} not found in ontology.")

        roles = {role: ontology.entities[entity_id] for role, entity_id in data["roles"].items()}

        context = None
        if data.get("context"):
            context = next((r for r in ontology.relations if getattr(r, "id", None) == data["context"]), None)

        truth_value = TruthValue.from_dict(data["truth_value"]) if data.get("truth_value") else None

        r = cls(predicate, roles, relation_type=data.get("relation_type", "GENERAL"), context=context, truth_value=truth_value)
        r.id = data.get("id")
        return r
    
    def __repr__(self):
        roles_str = ", ".join([f"{k}={v.name}" for k, v in self.roles.items()])
        ctx = f", context={self.context}" if self.context else ""
        return f"Relation({self.predicate_name}: {roles_str}, type={self.relation_type}{ctx}, truth={self.truth_value})"
