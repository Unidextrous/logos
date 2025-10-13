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

# Optional: add some relations
FIDO_HAS_DOG = onto.add_relation("HAS", FIDO, DOG)  # Example, could be something like HAS_SPECIES
DOG_IS_A_MAMMAL = onto.add_relation("IS_A", DOG, MAMMAL)  # Example redundancy

# Test printing the hierarchy
print("Hierarchy for DOG:")
onto.describe_hierarchy(DOG, show_description=True)

print("\nHierarchy for FIDO:")
onto.describe_hierarchy(FIDO, show_description=True)
