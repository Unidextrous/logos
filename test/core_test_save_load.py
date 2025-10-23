# core_test_save_load.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from core.ontology import Ontology
from core.temporal import TimeInterval, TemporalRelation
from core.quantifier import Quantifier
from core.truth import TruthValue, TruthState
from core.save_load import save_ontology, load_ontology

def test_save_load():
    ontology = Ontology()

    # --- Create entities ---
    DEX = ontology.add_entity("DEX", "NOUN")
    FOOD = ontology.add_entity("FOOD", "NOUN")

    # --- Create predicates ---
    EATS = ontology.add_predicate("EATS")
    IS_HUNGRY = ontology.add_predicate("IS_HUNGRY")

    # --- Create relations ---
    DEX_EATS_FOOD = ontology.add_relation(
        predicate=EATS,
        roles={"subject": DEX, "object": FOOD},
        truth_value=TruthValue(TruthState.TRUE)
    )

    # --- Create quantified relations using templates ---
    DEX_EATS_EVERYTHING = ontology.add_quantified_relation(
        quantifier=Quantifier.FORALL,
        variables=["X"],
        relation_template={
            "predicate": "EATS",
            "roles": {
                "subject": "DEX",
                "object": "$X"
            }
        },
        truth_value=TruthValue(TruthState.FALSE)
    )

    DEX_EATS_SOMETHING = ontology.add_quantified_relation(
        quantifier=Quantifier.EXISTS,
        variables=["Y"],
        relation_template={
            "predicate": "EATS",
            "roles": {
                "subject": "DEX",
                "object": "$Y"
            }
        },
        truth_value=TruthValue(TruthState.TRUE)
    )

    # --- Create temporal relation ---
    tr = TemporalRelation(predicate=EATS, roles={"subject": DEX, "object": FOOD})
    
    now = datetime.now()
    interval1 = TimeInterval(start_time=now, end_time=now + timedelta(hours=1))
    interval2 = TimeInterval(start_time=now + timedelta(hours=1), end_time=now + timedelta(hours=2))

    tr.add_interval(interval1, TruthValue(TruthState.TRUE))
    tr.add_interval(interval2, TruthValue(TruthState.FALSE))

    ontology.relations.append(tr)

    # --- Save ontology ---
    save_ontology(ontology, "ontology_test.json")

    # --- Load ontology ---
    new_ontology = load_ontology("ontology_test.json")

    # --- Checks ---
    assert "DEX" in [e.name for e in new_ontology.entities.values()]
    assert "FOOD" in [e.name for e in new_ontology.entities.values()]
    assert any(r.predicate.name == "EATS" for r in new_ontology.relations)
    assert any(qr.quantifier == Quantifier.FORALL for qr in new_ontology.quantified_relations)
    assert any(qr.quantifier == Quantifier.EXISTS for qr in new_ontology.quantified_relations)

    print("Save/load test passed!")

if __name__ == "__main__":
    test_save_load()
