import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology

# Initialize ontology
onto = Ontology()

# Create entities
LIVING_THING = onto.add_entity("LIVING_THING", word_type="NOUN", description="Multicellular organisms that move")
ANIMAL = onto.add_entity("ANIMAL", word_type="NOUN", entity_types=[LIVING_THING], description="Warm-blooded vertebrates")
MAMMAL = onto.add_entity("MAMMAL", word_type="NOUN", entity_types=[ANIMAL], description="Mammals")
SPECIES = onto.add_entity("SPECIES", word_type="NOUN", entity_types=[LIVING_THING], description="Taxonomic species")
HUMAN = onto.add_entity("HUMAN", word_type="NOUN", entity_types=[MAMMAL, SPECIES], description="Homo sapiens")
JOHN = onto.add_entity("JOHN", word_type="PROPER_NOUN", entity_types=[HUMAN], description="Person named John")
LETTER = onto.add_entity("LETTER", word_type="NOUN", description="A written letter")
POST_OFFICE = onto.add_entity("POST_OFFICE", word_type="NOUN", description="Place to send letters")

# Create predicates
TAKES_TO = onto.add_predicate("TAKES_TO")

# Add relations
# Temporary: JOHN TAKES LETTER TO POST_OFFICE for 10 seconds
JOHN_TAKES_LETTER = onto.add_relation(
    TAKES_TO,
    roles={"actor": JOHN, "item": LETTER, "destination": POST_OFFICE},
    relation_type="TEMPORARY",
    duration=timedelta(seconds=5)
)

# Print all relations
print("\nAll relations:")
for r in onto.relations:
    print(r)

# --- Test expiration ---
import time
print("\nWaiting 5 seconds to expire temporary relations...")
time.sleep(5)
onto.expire_temporary_relations()

print("\nRelations after expiration:")
for r in onto.relations:
    print(r)
