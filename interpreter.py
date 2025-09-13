from .logical_ops import *

class Interpreter:
    def __init__(self):
        self.kb = {}

    def evaluate(self, node):
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_eval)
        return method(node)

    def generic_eval(self, node):
        raise NotImplementedError(f"No eval method for {type(node).__name__}")

    # ----------------------
    # Truth values
    # ----------------------
    def eval_TruthValue(self, node: TruthValue):
        return node

    # ----------------------
    # Assignment
    # ----------------------
    def eval_Assignment(self, node: Assignment):
        stmt = node.stmt
        value_node = node.value

        if not isinstance(value_node, TruthValue):
            raise TypeError("Assignment value must be a TruthValue node")

        # Store statement node as key in KB
        self.kb[stmt] = value_node
        return value_node

    # ----------------------
    # Query
    # ----------------------
    def eval_Query(self, node: Query):
        """Queries are simple: evaluate the underlying statement."""
        stmt = node.stmt
        return self.evaluate(stmt)

    # ----------------------
    # Predicates
    # ----------------------
    def eval_Predicate(self, node: Predicate):
        # Direct lookup
        if node in self.kb:
            return self.kb[node]

        # Inference rules will go here
        # e.g., check conditionals, universal quantifiers, etc.

        return TruthValue("UNKNOWN")

    # ----------------------
    # Logical operations
    # ----------------------
    def eval_LogicalOp(self, node: LogicalOp):
        left_val = self.evaluate(node.left)
        if node.op == "NOT":
            return logical_not(left_val)

        right_val = self.evaluate(node.right)

        if node.op == "AND":
            return logical_and(left_val, right_val)
        elif node.op == "OR":
            return logical_or(left_val, right_val)
        if node.op == "NAND":
            return logical_nand(left_val, right_val)
        elif node.op == "NOR":
            return logical_nor(left_val, right_val)
        if node.op == "XOR":
            return logical_xor(left_val, right_val)
        elif node.op == "XNOR":
            return logical_xnor(left_val, right_val)
        else:
            return TruthValue("UNKNOWN")