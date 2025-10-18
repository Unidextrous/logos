import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology
from core.truth import Modality, TruthState, TruthValue

onto = Ontology()

# Entities
A = onto.add_entity("A", word_type="NOUN")
B = onto.add_entity("B", word_type="NOUN")
C = onto.add_entity("C", word_type="NOUN")

# Predicate
REL = onto.add_predicate("REL")

# Relation examples with different TruthValues
# TRUE (Alethic, default)
r_true = onto.add_relation(
    REL, 
    roles={"subject": A, "object": B}, 
    relation_type="PERMANENT",
    truth_value=TruthValue(value=TruthState.TRUE)
)

# FALSE (Alethic)
r_false = onto.add_relation(
    REL,
    roles={"subject": B, "object": C},
    relation_type="PERMANENT",
    truth_value=TruthValue(value=TruthState.FALSE)
)

# UNKNOWN (Alethic)
r_unknown = onto.add_relation(
    REL,
    roles={"subject": A, "object": C},
    relation_type="PERMANENT",
    truth_value=TruthValue(value=TruthState.UNKNOWN)
)

# SUPERPOSITION with probability
r_superposition = onto.add_relation(
    REL,
    roles={"subject": C, "object": A},
    relation_type="PERMANENT",
    truth_value=TruthValue(value=TruthState.SUPERPOSITION, probability=0.7)
)

# Relation with a different modality (e.g., Epistemic)
r_epistemic = onto.add_relation(
    REL,
    roles={"subject": B, "object": A},
    relation_type="PERMANENT",
    truth_value=TruthValue(value=TruthState.TRUE, modality=Modality.EPISTEMIC)
)

# Print all relations
for r in onto.relations:
    print(r, "->", r.evaluate_truth())
