import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology
from core.truth import TruthState, TruthValue

onto = Ontology()

# Entities
A = onto.add_entity("A", word_type="NOUN")
B = onto.add_entity("B", word_type="NOUN")
C = onto.add_entity("C", word_type="NOUN")

# Predicate
REL = onto.add_predicate("REL")

# Relation examples with different TruthValues
# TRUE
r_true = onto.add_relation(
    REL, 
    roles={"subject": A, "object": B}, 
    truth_value=TruthValue(value=TruthState.TRUE)
)

# FALSE
r_false = onto.add_relation(
    REL,
    roles={"subject": B, "object": C},
    truth_value=TruthValue(value=TruthState.FALSE)
)

# UNKNOWN
r_unknown = onto.add_relation(
    REL,
    roles={"subject": A, "object": C},
    truth_value=TruthValue(value=TruthState.UNKNOWN)
)

# Print all relations
for r in onto.relations:
    print(r)
