import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology
from core.truth import TruthState, TruthValue

# Initialize ontology
onto = Ontology()

# GENERAL: HUMAN HAS PARTS including HEAD, ARMS, LEGS
CATEGORY = onto.add_entity("CATEGORY", word_type="NOUN", description="A general category or class")
LIVING_THING = onto.add_entity("LIVING_THING", word_type="NOUN", parents=[CATEGORY], description="A living organism")
BODY_PART = onto.add_entity("BODY_PART", word_type="NOUN", parents=[CATEGORY], description="A part of a body")
HUMAN = onto.add_entity("HUMAN", word_type="NOUN", parents=[LIVING_THING], description="A human being")
HEAD = onto.add_entity("HEAD", word_type="NOUN", parents=[BODY_PART], description="Human head")
ARMS = onto.add_entity("ARMS", word_type="NOUN", parents=[BODY_PART], description="Human arms")
LEGS = onto.add_entity("LEGS", word_type="NOUN", parents=[BODY_PART], description="Human legs")

# Relation type GENERAL, with explicit TruthValue
HUMAN_HAS_BODY_PARTS = onto.add_relation(
    predicate=onto.add_predicate("HAS_PARTS"),
    roles={
        "whole": HUMAN,
        "part1": HEAD,
        "part2": ARMS,
        "part3": LEGS
    },
    relation_type="GENERAL",
    truth_value=TruthValue(value=TruthState.TRUE)  # Alethic TRUE
)

# Print all relations
print("\nAll relations:")
for r in onto.relations:
    print(r)
