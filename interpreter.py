from .logical_ops import *

class Interpreter:
    def __init__(self):
        self.kb = {}

    # ----------------------
    # Core evaluation
    # ----------------------
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

        # Store statement node as key in KB
        self.kb[stmt] = value_node
        return value_node

    # ----------------------
    # Query
    # ----------------------
    def eval_Query(self, node: Query):
        """Queries are simple: evaluate the underlying statement."""
        stmt = node.stmt
        if stmt in self.kb:
            return self.evaluate(self.kb[stmt])
        return self.infer(stmt)

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

    # ----------------------
    # Inference dispatcher
    # ----------------------
    def infer(self, node):
        method_name = f"infer_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_infer)
        return method(node)

    def generic_infer(self, node):
        # Default fallback: unknown
        return TruthValue("UNKNOWN")

    # ----------------------
    # Predicate inference
    # ----------------------
    def infer_Predicate(self, node: Predicate):
        # 1. Direct assignment
        if node in self.kb:
            value = self.evaluate(self.kb[node])
            if isinstance(value, TruthValue):
                return value

        # 2. Look for logical operators in KB
        for stmt, val in self.kb.items():
            stmt_val = self.evaluate(val)
            
            if not isinstance(stmt, LogicalOp):
                continue

            if stmt.op == "NOT":
                if stmt.left == node:
                    if stmt_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")
                    elif stmt_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")

            if node == stmt.left:
                other = stmt.right
            elif node == stmt.right:
                other = stmt.left
            
            other_val = self.evaluate(other)

            if stmt.op == "AND":
                if node == stmt.left or node == stmt.right:
                    if stmt_val == TruthValue("TRUE"):
                        return TruthValue("TRUE")
                    elif stmt_val == TruthValue("FALSE") and other_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")

            if stmt.op == "OR":
                if node == stmt.left or node == stmt.right:
                    if stmt_val == TruthValue("FALSE"):
                        return TruthValue("FALSE")
                    elif stmt_val == TruthValue("TRUE") and other_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")
                    
            if stmt.op == "NAND":
                if node == stmt.left or node == stmt.right:
                    if stmt_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")
                    elif stmt_val == TruthValue("FALSE") and other_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")

            if stmt.op == "NOR":
                if node == stmt.left or node == stmt.right:
                    if stmt_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")
                    elif stmt_val == TruthValue("FALSE") and other_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")

            if stmt.op == "XOR":
                if node == stmt.left or node == stmt.right:
                    if stmt_val == TruthValue("TRUE"):
                        return logical_not(other_val)
                    elif stmt_val == TruthValue("FALSE"):
                        return other_val
            
            if stmt.op == "XNOR":
                if node == stmt.left or node == stmt.right:
                    if stmt_val == TruthValue("TRUE"):
                        return other_val
                    elif stmt_val == TruthValue("FALSE"):
                        return logical_not(other_val)
                    
        # 3. Nothing can be inferred
        return TruthValue("UNKNOWN")


    # ----------------------
    # LogicalOp inference
    # ----------------------
    def infer_LogicalOp(self, node: LogicalOp):
        # Try to evaluate using known values of its parts
        left_val = self.evaluate(node.left) if node.left else None
        right_val = self.evaluate(node.right) if node.right else None

        if node.op == "NOT":
            return logical_not(left_val)

        if node.op == "AND":
            return logical_and(left_val, right_val)

        if node.op == "OR":
            return logical_or(left_val, right_val)

        if node.op == "NAND":
            return logical_nand(left_val, right_val)

        if node.op == "NOR":
            return logical_nor(left_val, right_val)
        
        if node.op == "XOR":
            return logical_xor(left_val, right_val)

        if node.op == "XNOR":
            return logical_xnor(left_val, right_val)

        return TruthValue("UNKNOWN")

    # ----------------------
    # Helper
    # ----------------------
    def contains_predicate(self, expr, target: Predicate):
        """
        Recursively check if a predicate is inside a logical expression.
        """
        if isinstance(expr, Predicate):
            return expr == target
        if isinstance(expr, LogicalOp):
            return (
                self.contains_predicate(expr.left, target) or
                (expr.right and self.contains_predicate(expr.right, target))
            )
        return False