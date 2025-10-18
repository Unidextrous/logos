import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.relation import Relation, Predicate
from core.context import RelationContext
from core.truth import TruthValue, TruthState, Modality

def test_context_evaluation():
    print("\n=== Context Logic Tests ===")

    # Neutral predicate
    IS = Predicate("IS")

    # Mock relations with explicit truth states
    A = Relation(IS, {"subject": None}, truth_value=TruthValue(TruthState.TRUE))
    B = Relation(IS, {"subject": None}, truth_value=TruthValue(TruthState.TRUE))
    C = Relation(IS, {"subject": None}, truth_value=TruthValue(TruthState.FALSE))

    UNKNOWN_REL = Relation(IS, {"subject": None}, truth_value=TruthValue(TruthState.UNKNOWN))
    SUPER_REL = Relation(IS, {"subject": None}, truth_value=TruthValue(TruthState.SUPERPOSITION, probability=0.7))

    # Logical combinations
    ctx_and = RelationContext(A) & RelationContext(B)
    ctx_or = RelationContext(A) | RelationContext(C)
    ctx_not = ~RelationContext(C)
    ctx_xor = RelationContext(A) ^ RelationContext(C)
    ctx_nand = ~(RelationContext(A) & RelationContext(B))
    ctx_nor = ~(RelationContext(A) | RelationContext(B))
    ctx_xnor = ~(RelationContext(A) ^ RelationContext(C))
    ctx_complex = (RelationContext(A) & (~RelationContext(C) | RelationContext(B)))

    # Additional tests with UNKNOWN and SUPERPOSITION
    ctx_unknown_and_true = RelationContext(UNKNOWN_REL) & RelationContext(A)
    ctx_super_or_false = RelationContext(SUPER_REL) | RelationContext(C)
    ctx_unknown_and_super = RelationContext(UNKNOWN_REL) & RelationContext(SUPER_REL)
    ctx_unknown_or_super = RelationContext(UNKNOWN_REL) | RelationContext(SUPER_REL)

    # --- Assertions for initial state ---
    assert ctx_and.evaluate().value == TruthState.TRUE
    assert ctx_or.evaluate().value == TruthState.TRUE
    assert ctx_not.evaluate().value == TruthState.TRUE
    assert ctx_xor.evaluate().value == TruthState.TRUE
    assert ctx_nand.evaluate().value == TruthState.FALSE
    assert ctx_nor.evaluate().value == TruthState.FALSE
    assert ctx_xnor.evaluate().value == TruthState.FALSE
    assert ctx_complex.evaluate().value == TruthState.TRUE

    # Assertions for UNKNOWN/SUPERPOSITION combinations
    assert ctx_unknown_and_true.evaluate().value == TruthState.UNKNOWN
    assert ctx_super_or_false.evaluate().value == TruthState.SUPERPOSITION
    assert ctx_unknown_and_super.evaluate().value == TruthState.SUPERPOSITION
    assert ctx_unknown_or_super.evaluate().value == TruthState.SUPERPOSITION

    # Flip A and B to FALSE
    A.truth_value = TruthValue(TruthState.FALSE)
    B.truth_value = TruthValue(TruthState.FALSE)

    # Assertions after changing A and B
    assert ctx_and.evaluate().value == TruthState.FALSE
    assert ctx_or.evaluate().value == TruthState.FALSE
    assert ctx_not.evaluate().value == TruthState.TRUE
    assert ctx_xor.evaluate().value == TruthState.FALSE
    assert ctx_nand.evaluate().value == TruthState.TRUE
    assert ctx_nor.evaluate().value == TruthState.TRUE
    assert ctx_xnor.evaluate().value == TruthState.TRUE
    assert ctx_complex.evaluate().value == TruthState.FALSE

    # Assertions for UNKNOWN/SUPERPOSITION with A FALSE
    assert ctx_unknown_and_true.evaluate().value == TruthState.FALSE
    assert ctx_super_or_false.evaluate().value == TruthState.SUPERPOSITION
    assert ctx_unknown_and_super.evaluate().value == TruthState.SUPERPOSITION
    assert ctx_unknown_or_super.evaluate().value == TruthState.SUPERPOSITION

    print("\n✅ All context logic tests passed!\n")

if __name__ == "__main__":
    test_context_evaluation()
