# quantifier.py
import uuid
from enum import Enum
from .truth import TruthValue, TruthState
from .relation import Relation

class Quantifier(Enum):
    FORALL = "FORALL"
    EXISTS = "EXISTS"

class QuantifiedRelation:
    """
    Represents a quantified logical relation, e.g.,
    FORALL X: LOVES(X, TONYA)
    EXISTS Y: OWNS(DEX, Y)
    """
    def __init__(self, quantifier: Quantifier, variables: list[str], relation_template, truth_value: TruthValue | None):
        """
        Args:
            quantifier (Quantifier): FORALL or EXISTS
            variables (list[str]): Variable names used in the relation, e.g., ["X"]
            relation_template: {
                "predicate": str,
                "roles": dict where some values can be "$variable"
            }
            truth_value (TruthValue | None): Optional initial truth value (defaults to UNKNOWN)
        """
        self.quantifier = quantifier
        self.variables = [v.upper() for v in variables]
        self.relation_template = relation_template
        self.truth_value = truth_value or TruthValue(value=TruthState.UNKNOWN)

    def instantiate(self, **kwargs):
        """Generate a Relation from the template with variables substituted"""
        predicate_name = self.relation_template.predicate
        roles_template = self.relation_template.roles

        roles_instantiated = {}
        for role, val in roles_template.items():
            if isinstance(val, str) and val.startswith("$"):
                var_name = val[1:]
                if var_name not in kwargs:
                    raise ValueError(f"Missing variable {var_name}")
                roles_instantiated[role] = kwargs[var_name]
            else:
                roles_instantiated[role] = val

        return Relation(predicate_name, roles=roles_instantiated)

    def to_dict(self):
        return {
            "quantifier": self.quantifier.name,
            "variables": self.variables,
            "relation_template": self.relation_template,
            "truth_value": self.truth_value.to_dict(),
        }

    @classmethod
    def from_dict(cls, data, ontology):
        from .truth import TruthValue
        return cls(
            quantifier=Quantifier[data["quantifier"]],
            variables=data["variables"],
            relation_template=data["relation_template"],
            truth_value=TruthValue.from_dict(data["truth_value"])
        )
    
    def __eq__(self, other):
        if not isinstance(other, QuantifiedRelation):
            return False
        return (
            self.quantifier == other.quantifier and
            self.variables == other.variables and
            self.relation_template == other.relation_template
        )

    def __hash__(self):
        return hash((
            self.quantifier,
            tuple(self.variables),
            frozenset(self._flatten_template(self.relation_template))
        ))

    @staticmethod
    def _flatten_template(template):
        """
        Flatten the template dict into key-value tuples for hashing.
        Recursively converts dicts into tuples of key-value pairs.
        """
        if isinstance(template, dict):
            return tuple((k, QuantifiedRelation._flatten_template(v)) for k, v in template.items())
        elif isinstance(template, list):
            return tuple(QuantifiedRelation._flatten_template(x) for x in template)
        else:
            return template
        
    def __repr__(self):
        vars_str = ", ".join(var for var in self.variables)
        role_values_str = ", ".join(f"{rv}" for rv in self.relation_template.roles.values())
        return f"{self.quantifier.name}({vars_str}): {self.relation_template.predicate.name}({role_values_str}): {self.truth_value}"