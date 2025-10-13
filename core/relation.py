class Relation:
    """
    Represents a logical relationship between entities.

    Attributes:
        predicate: str — the type of relation, e.g., "IS", "HAS", "IS_AT"
        subject: Entity — the entity this relation originates from
        object: Entity — the entity this relation points to
        relation_type: str — optional tag indicating the logical nature of the relation
            Examples:
                - "PERMANENT"  (e.g., IS_A, PART_OF)
                - "TEMPORARY"  (e.g., IS_AT, IS_COLORED)
                - "INVERSE"    (e.g., OWNS / OWNED_BY)
                - "META"       (e.g., CONTRADICTS, ANALOGOUS_TO)
    """

    def __init__(self, predicate: str, subject, object_, relation_type: str = "GENERAL"):
        self.predicate = predicate.upper()
        self.subject = subject
        self.object = object_
        self.relation_type = relation_type.upper()

    def __repr__(self):
        return (f"Relation(predicate={self.predicate}, "
                f"subject={self.subject.name}, "
                f"object={self.object.name}, "
                f"type={self.relation_type})")
