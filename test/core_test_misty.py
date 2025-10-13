import sys
import os
import time
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
CAT = onto.add_entity("CAT", word_type="NOUN", entity_types=[MAMMAL, SPECIES], description="Felis catus")
MISTY = onto.add_entity("MISTY", word_type="PROPER NOUN", entity_types=[CAT], description="My pet cat")
CONTAINER = onto.add_entity("CONTAINER", word_type="NOUN", description="A receptable where material is held or carried")
BOX = onto.add_entity("BOX", word_type="NOUN", entity_types=[CONTAINER])

# Create predicates
IS_IN_A = onto.add_predicate("IS_IN_A")
IS_HAPPY = onto.add_predicate("IS_HAPPY")
IS_PURRING = onto.add_predicate("IS_PURRING")

# Add relations
MISTY_IS_IN_A_BOX = onto.add_relation(
    IS_IN_A,
    roles={"subject": MISTY, "object": BOX},
    relation_type="TEMPORARY",
    duration=timedelta(seconds=5)
)

MISTY_IS_HAPPY = onto.add_relation(
    IS_HAPPY,
    roles={"subject": MISTY},
    relation_type="CONTEXTUAL",
    context=MISTY_IS_IN_A_BOX
)

MISTY_IS_PURRING = onto.add_relation(
    IS_PURRING,
    roles={"subject": MISTY},
    relation_type="CONTEXTUAL",
    context=MISTY_IS_HAPPY
)

# Print all relations
print("\nAll relations:")
for r in onto.relations:
    print(r)

# Print relations for MISTY
print("\nRelations for MISTY:")
for r in MISTY.relations:
    print(r)

# Show initial active states
print("\nInitially:")
for r in [MISTY_IS_IN_A_BOX, MISTY_IS_HAPPY, MISTY_IS_PURRING]:
    print(f"{r} active={r.active}")

# Simulate expiration of MISTY_IN_BOX
time.sleep(3)

print("\nJust before MISTY leaves BOX:")
for r in [MISTY_IS_IN_A_BOX, MISTY_IS_HAPPY, MISTY_IS_PURRING]:
    print(f"{r} active={r.active}")

time.sleep(2)

print("\nAfter MISTY is no longer in BOX:")
for r in [MISTY_IS_IN_A_BOX, MISTY_IS_HAPPY, MISTY_IS_PURRING]:
    print(f"{r} active={r.active}")

# Manually activate MISTY_IN_BOX again
MISTY_IS_IN_A_BOX.activate()

print("\nAfter manually activating MISTY_IN_BOX again:")
for r in [MISTY_IS_IN_A_BOX, MISTY_IS_HAPPY, MISTY_IS_PURRING]:
    print(f"{r} active={r.active}")
