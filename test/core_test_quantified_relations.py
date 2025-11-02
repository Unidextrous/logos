import sys
import os
from datetime import timedelta, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ontology import Ontology
from core.entity import Entity
from core.relation import Relation, Predicate
from core.quantifier import Quantifier, QuantifiedRelation
from core.truth import TruthValue, TruthState

# Initialize ontology
ontology = Ontology()

# Define entities and predicates
DEX = ontology.add_entity("DEX", "NOUN")

EATS = ontology.add_predicate("EATS")
IS_HUNGRY = ontology.add_predicate("IS_HUNGRY")

# Define quantified relations using the new dict-style template
DEX_DOES_EATS_EVERYTHING = ontology.add_quantified_relation(
    quantifier=Quantifier.FORALL,
    variables=["X"],
    relation_template=Relation(Predicate("EATS"), {"subject": "DEX", "object": "$X"}),
    truth_value=TruthValue(TruthState.FALSE)
)

DEX_EATS_SOMETHING = ontology.add_quantified_relation(
    quantifier=Quantifier.EXISTS,
    variables=["Y"],
    relation_template=Relation(Predicate("EATS"), {"subject": "DEX", "object": "$Y"}),
    truth_value=TruthValue(TruthState.TRUE)
)

# Print out to confirm creation and template structure
for qr in ontology.quantified_relations:
    print(qr)
    # Test instantiation
    instantiated = qr.instantiate(X="APPLE", Y="PIZZA")  # Flexible based on variable names
    print("→ Instantiated Relation:", instantiated)
