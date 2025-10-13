import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology

# Initialize ontology
onto = Ontology()

# Define the hierarchy
LIVING_THING = onto.add_entity("LIVING_THING", word_type="NOUN", description="Multicellular organisms that move")
ANIMAL = onto.add_entity("ANIMAL", word_type="NOUN", entity_types=[LIVING_THING], description="Warm-blooded vertebrates")
MAMMAL = onto.add_entity("MAMMAL", word_type="NOUN", entity_types=[ANIMAL], description="Mammals")
SPECIES = onto.add_entity("SPECIES", word_type="NOUN", entity_types=[LIVING_THING], description="Taxonomic species")
DOG = onto.add_entity("DOG", word_type="NOUN", entity_types=[MAMMAL, SPECIES], description="Canis lupus familiaris")
FIDO = onto.add_entity("FIDO", word_type="NOUN", entity_types=[DOG], description="My pet dog")

# Define predicates
IS = onto.predicates.get("IS") or onto.add_predicate("IS", "PERMANENT")
HAS = onto.add_predicate("HAS", "GENERAL")

# Add explicit relations
FIDO_HAS_DOG = onto.add_relation(HAS, FIDO, DOG)
DOG_IS_A_MAMMAL = onto.add_relation(IS, DOG, MAMMAL)  # redundancy, but okay for testing

# Test printing the hierarchy
print("Hierarchy for DOG:")
onto.describe_hierarchy(DOG, show_description=True)

print("\nHierarchy for FIDO:")
onto.describe_hierarchy(FIDO, show_description=True)

# Print relations for FIDO
print("\nRelations for FIDO:")
for r in FIDO.relations:
    print(r)

# Print relations for DOG
print("\nRelations for DOG:")
for r in DOG.relations:
    print(r)