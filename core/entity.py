# entity.py
class Entity:
    """
    Represents an entity in the Logos ontology.

    Attributes:
        name: str — lexical form of the entity, e.g., "LIGHT"
        word_type: str — part of speech, e.g., "NOUN", "ADJECTIVE", "VERB"
        entity_types: list[Entity] — parent types/entities for hierarchy
        description: str, optional — human-readable description
        relations: list[Relation] — relations where this entity is the subject
    """

    def __init__(self, name: str, word_type: str, entity_types=None, description: str = None):
        self.name = name.upper()
        self.word_type = word_type.upper()
        self.entity_types = entity_types if entity_types else []  # list of Entity objects
        self.description = description
        self.relations = []  # filled via Ontology.add_relation()

    @property
    def id(self):
        """Unique identifier used in Ontology dictionary."""
        type_ids = tuple(et.name for et in self.entity_types)
        return (self.name, self.word_type, type_ids)

    def __repr__(self):
        types_str = [et.name for et in self.entity_types]
        return f"Entity(name={self.name}, word_type={self.word_type}, entity_types={types_str})"
