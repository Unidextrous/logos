# core_test_quantified_propositions.py
import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from core.ontology import Ontology
from core.entity import Entity
from core.relation import Relation, Predicate
from core.quantifier import Quantifier, QuantifiedProposition
from core.truth import TruthValue, TruthState

ontology = Ontology()

DEX = ontology.add_entity("DEX", "NOUN")

EATS = ontology.add_predicate("EATS")
IS_HUNGRY = ontology.add_predicate("IS_HUNGRY")


DEX_DOES_NOT_EAT_EVERYTHING = ontology.add_quantified_proposition(
    quantifier=Quantifier.FORALL,
    variables=["X"],
    proposition=lambda X: Relation(EATS, roles={"subject": DEX, "object": X}),
    truth_value=TruthValue(TruthState.FALSE)
)

DEX_EATS_SOMETHING = ontology.add_quantified_proposition(
    quantifier=Quantifier.EXISTS,
    variables=["Y"],
    proposition=lambda Y: Relation(EATS, roles={"subject": DEX, "object": Y}),
    truth_value=TruthValue(TruthState.TRUE)
)

print(ontology.quantified_propositions)