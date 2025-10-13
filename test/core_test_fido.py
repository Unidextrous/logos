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
DOG = onto.add_entity("DOG", word_type="NOUN", entity_types=[MAMMAL, SPECIES], description="Canis lupus familiaris")
TAIL = onto.add_entity("TAIL", word_type="NOUN", description="A tail of an animal")
FIDO = onto.add_entity("FIDO", word_type="PROPER_NOUN", entity_types=[DOG], description="My pet dog")

# Create predicates
IS = onto.add_predicate("IS")
HAS = onto.add_predicate("HAS")

# Test printing the hierarchy
print("Hierarchy for DOG:")
onto.describe_hierarchy(DOG, show_description=True)

print("\nHierarchy for FIDO:")
onto.describe_hierarchy(FIDO, show_description=True)

# Add relations
# Permanent: FIDO IS A DOG
FIDO_IS_A_DOG = onto.add_relation(IS, roles={"subject": FIDO, "object": DOG}, relation_type="PERMANENT")

# Permanent: DOG IS A MAMMAL
DOG_IS_A_MAMMAL = onto.add_relation(IS, roles={"subject": DOG, "object": MAMMAL}, relation_type="PERMANENT")

# Permanent: DOG HAS TAIL
DOG_HAS_TAIL = onto.add_relation(HAS, roles={"owner": DOG, "part": TAIL}, relation_type="PERMANENT")

# Print all relations
print("\nAll relations:")
for r in onto.relations:
    print(r)

# Print relations for FIDO
print("\nRelations for FIDO:")
for r in FIDO.relations:
    print(r)

# Print relations for DOG
print("\nRelations for DOG:")
for r in DOG.relations:
    print(r)
