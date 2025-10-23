# core/save_load.py
import json
from .ontology import Ontology
from .entity import Entity
from .relation import Predicate, Relation
from .quantifier import QuantifiedProposition

def save_ontology(ontology: Ontology, filepath: str):
    """
    Save the ontology to a JSON file.
    """
    data = {
        "entities": [e.to_dict() for e in ontology.entities.values()],
        "predicates": [p.to_dict() for p in ontology.predicates.values()],
        "relations": [r.to_dict() for r in ontology.relations],
        "quantified_propositions": [qp.to_dict() for qp in getattr(ontology, "quantified_propositions", [])],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_ontology(filepath: str) -> Ontology:
    """
    Load an ontology from a JSON file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    ontology = Ontology()

    # Reconstruct entities
    for e_dict in data.get("entities", []):
        e = Entity.from_dict(e_dict)
        ontology.entities[e.id] = e

    # Reconstruct predicates
    for p_dict in data.get("predicates", []):
        p = Predicate.from_dict(p_dict)
        ontology.predicates[p.name] = p

    # Reconstruct relations
    for r_dict in data.get("relations", []):
        r = Relation.from_dict(r_dict, ontology)
        ontology.relations.append(r)
        for e in r.roles.values():
            e.relations.append(r)

    # Reconstruct quantified propositions
    ontology.quantified_propositions = []
    for qp_dict in data.get("quantified_propositions", []):
        qp = QuantifiedProposition.from_dict(qp_dict, ontology)
        ontology.quantified_propositions.append(qp)

    return ontology
