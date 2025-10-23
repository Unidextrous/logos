import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology

# Initialize ontology
onto = Ontology()

# Create entities
CATEGORY = onto.add_entity("CATEGORY", word_type="NOUN", description="A general category of things")
INSTANCE = onto.add_entity("INSTANCE", word_type="NOUN", description="An individual instance of an entity type")
LIVING_THING = onto.add_entity("LIVING_THING", word_type="NOUN", parents=[CATEGORY], description="Multicellular organisms that move")
ANIMAL = onto.add_entity("ANIMAL", word_type="NOUN", parents=[LIVING_THING], description="Warm-blooded vertebrates")
MAMMAL = onto.add_entity("MAMMAL", word_type="NOUN", parents=[ANIMAL], description="Mammals")
SPECIES = onto.add_entity("SPECIES", word_type="NOUN", parents=[LIVING_THING], description="Taxonomic species")
DOG = onto.add_entity("DOG", word_type="NOUN", parents=[MAMMAL, SPECIES], description="Canis lupus familiaris")
A_DOG = onto.add_entity("A_DOG", word_type="NOUN", parents=[DOG, INSTANCE], description="An instance of a dog")
A_PET = onto.add_entity("A_PET", word_type="NOUN", parents=[INSTANCE], description="An instance of a pet")
TAIL = onto.add_entity("TAIL", word_type="NOUN", description="A tail of an animal")
FIDO = onto.add_entity("FIDO", word_type="PROPER_NOUN", parents=[A_DOG, A_PET], description="My pet dog")

# Test printing the hierarchy
print("Hierarchy for DOG:")
onto.describe_hierarchy(DOG, show_description=True)

print("\nHierarchy for FIDO:")
onto.describe_hierarchy(FIDO, show_description=True)
