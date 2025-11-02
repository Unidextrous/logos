# relation.py
import uuid
from typing import Dict, List
from .truth import TruthState, TruthValue

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

    Supports n-ary roles and truth evaluation via TruthValue.
    """

    def __init__(
        self,
        predicate: Predicate,
        roles: dict,
        relation_type: str = "GENERAL",
        truth_value: TruthValue | None = None
    ):
        """
        Args:
            predicate (Predicate): Type of relation (e.g., IS, HAS).
            roles (dict[str, Entity]): Mapping role names to entities, e.g., {"subject": FIDO, "object": DOG}.
            relation_type (str): Logical type: GENERAL, PERMANENT, etc.
            truth_value (TruthValue | None): initial truth state (defaults to UNKNOWN)
        """
        self.id = f"REL_{uuid.uuid4().hex[:8]}"
        self.predicate = predicate
        self.predicate_name = predicate.name.upper()
        self.roles = roles
        self.truth_value = truth_value or TruthValue(value=TruthState.UNKNOWN)
        self.dependents = set()

    def to_dict(self):
        return {
            "id": getattr(self, "id", None),
            "predicate": self.predicate.name,
            "roles": {role: entity.id for role, entity in self.roles.items()},
            "truth_value": self.truth_value.to_dict() if self.truth_value else None,
        }

    @classmethod
    def from_dict(cls, data, ontology):
        predicate = ontology.predicates.get(data["predicate"])
        if not predicate:
            raise ValueError(f"Predicate {data['predicate']} not found in ontology.")
        roles = {role: ontology.entities[entity_id] for role, entity_id in data["roles"].items()}
        truth_value = TruthValue.from_dict(data["truth_value"]) if data.get("truth_value") else None
        r = cls(predicate, roles, truth_value=truth_value)
        r.id = data.get("id")
        return r
    
    def __repr__(self):
        role_values_str = ", ".join([f"{rv}" for rv in self.roles.values()])
        return f"Relation({self.predicate_name}({role_values_str})): {self.truth_value}"
