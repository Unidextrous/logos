# core/save_load.py
import json
from .ontology import Ontology
from .entity import Entity
from .relation import Predicate, Relation
from .temporal import TemporalRelation
from .quantifier import QuantifiedRelation

def save_ontology(ontology: Ontology, filepath: str):
    """
    Save the ontology to a JSON file.
    """
    data = {
        "entities": [e.to_dict() for e in ontology.entities.values()],
        "predicates": [p.to_dict() for p in ontology.predicates.values()],
        "relations": [r.to_dict() for r in ontology.relations],
        "quantified_relations": [qr.to_dict() for qr in getattr(ontology, "quantified_relations", [])],
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
        if r_dict.get("relation_type") == "TEMPORAL":
            r = TemporalRelation.from_dict(r_dict, ontology)
        else:
            r = Relation.from_dict(r_dict, ontology)
        ontology.relations.append(r)
        for e in r.roles.values():
            e.relations.append(r)

    # Reconstruct quantified relations
    ontology.quantified_relations = []
    for qr_dict in data.get("quantified_relations", []):
        qr = QuantifiedRelation.from_dict(qr_dict, ontology)
        ontology.quantified_relations.append(qr)

    return ontology
