import sys
import os
from datetime import timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.relation import Relation, Predicate
from core.context import RelationContext

def test_context_evaluation():
    print("\n=== Context Logic Tests ===")

    # Predicates
    IS_TRUE = Predicate("IS_TRUE")
    IS_FALSE = Predicate("IS_FALSE")

    # Mock relations
    A = Relation(IS_TRUE, {"subject": None})
    B = Relation(IS_TRUE, {"subject": None})
    C = Relation(IS_FALSE, {"subject": None}, active=False)

    # Logical combinations
    ctx_and = RelationContext(A) & RelationContext(B)
    ctx_or = RelationContext(A) | RelationContext(C)
    ctx_not = ~RelationContext(C)
    ctx_xor = RelationContext(A) ^ RelationContext(C)
    ctx_nand = ~(RelationContext(A) & RelationContext(B))
    ctx_nor = ~(RelationContext(A) | RelationContext(B))
    ctx_xnor = ~(RelationContext(A) ^ RelationContext(C))

    ctx_complex = (RelationContext(A) & (~RelationContext(C) | RelationContext(B)))

    print("\n--- Initial States ---")
    print(f"A.active={A.active}, B.active={B.active}, C.active={C.active}\n")

    print("--- Evaluations ---")
    print("A AND B:", ctx_and.evaluate())
    print("A OR C:", ctx_or.evaluate())
    print("NOT C:", ctx_not.evaluate())
    print("A XOR C:", ctx_xor.evaluate())
    print("A NAND B:", ctx_nand.evaluate())
    print("A NOR B:", ctx_nor.evaluate())
    print("A XNOR C:", ctx_xnor.evaluate())
    print("A AND (NOT C OR B):", ctx_complex.evaluate())

    # Assertions (initial truth table)
    assert ctx_and.evaluate() is True
    assert ctx_or.evaluate() is True
    assert ctx_not.evaluate() is True
    assert ctx_xor.evaluate() is True
    assert ctx_nand.evaluate() is False
    assert ctx_nor.evaluate() is False
    assert ctx_xnor.evaluate() is False
    assert ctx_complex.evaluate() is True

    # Flip A and B off
    A.deactivate()
    B.deactivate()

    print("\nAfter deactivating A and B:")
    print(f"A.active={A.active}, B.active={B.active}, C.active={C.active}\n")

    print("--- Evaluations (After Deactivation) ---")
    print("A AND B:", ctx_and.evaluate())
    print("A OR C:", ctx_or.evaluate())
    print("NOT C:", ctx_not.evaluate())
    print("A XOR C:", ctx_xor.evaluate())
    print("A NAND B:", ctx_nand.evaluate())
    print("A NOR B:", ctx_nor.evaluate())
    print("A XNOR C:", ctx_xnor.evaluate())
    print("Complex:", ctx_complex.evaluate())

    # Assertions (after deactivation)
    assert ctx_and.evaluate() is False
    assert ctx_or.evaluate() is False
    assert ctx_not.evaluate() is True
    assert ctx_xor.evaluate() is False
    assert ctx_nand.evaluate() is True
    assert ctx_nor.evaluate() is True
    assert ctx_xnor.evaluate() is True
    assert ctx_complex.evaluate() is False

    print("\n✅ All context logic tests passed!\n")


if __name__ == "__main__":
    test_context_evaluation()
