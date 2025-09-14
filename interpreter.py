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
        
        # 1. Direct KB lookup
        stmt = node.stmt
        if stmt in self.kb:
            return self.evaluate(self.kb[stmt])

        # 2. Evaluate LogicalOp
        if isinstance(stmt, LogicalOp):
            return self.eval_LogicalOp(stmt)
        
        # 3. Try inference
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
    def infer(self, target):
        """Infer the truth value of the target from the knowledge base."""
        for stmt, val in self.kb.items():
            # Dispatch based on *stmt* not target
            method_name = f"infer_from_{type(stmt).__name__}"
            method = getattr(self, method_name, self.generic_infer)
            result = method(stmt, val, target)
            if result is not None:
                return result
        return "UNKNOWN"

    def generic_infer(self, node):
        # Default fallback: unknown
        return TruthValue("UNKNOWN")

    # ----------------------
    # Predicate inference
    # ----------------------
    def infer_from_Predicate(self, stmt, val, target):
        if stmt == target:
            return val
        return None


    # ----------------------
    # LogicalOp inference
    # ----------------------
    def infer_from_LogicalOp(self, stmt, val, target: Node):
        """
        Try to infer the truth value of `target` using logical operator
        statements stored in the KB.
        """
        for stmt, val in self.kb.items():
            if not isinstance(stmt, LogicalOp):
                continue

            # First, try a direct decomposition
            inferred = self.decompose(stmt, val, target)
            if inferred is not None:
                return inferred

            # --- Recursive path: maybe stmt implies some sub-target ---
            # For example, if stmt = (A AND B) AND C = TRUE
            # and target = A, decompose() might not return directly,
            # but we know (A AND B) must be TRUE.
            if stmt.op in {"AND", "OR", "NAND", "NOR", "XOR", "XNOR"}:
                sub_left = stmt.left
                sub_right = stmt.right

                # Check left sub-expression
                if self.contains_target(sub_left, target):
                    sub_val = self.infer(sub_left)
                    if sub_val != TruthValue("UNKNOWN"):
                        return self.decompose(stmt, sub_val, target)

                # Check right sub-expression
                if self.contains_target(sub_right, target):
                    sub_val = self.infer(sub_right)
                    if sub_val != TruthValue("UNKNOWN"):
                        return self.decompose(stmt, sub_val, target)

            elif stmt.op == "NOT":
                if self.contains_target(stmt.left, target):
                    sub_val = self.infer(stmt.left)
                    if sub_val != TruthValue("UNKNOWN"):
                        return self.decompose(stmt, sub_val, target)

        return TruthValue("UNKNOWN")

    # ----------------------
    # Helper Methods
    # ----------------------
    def decompose(self, expr, val, target):
        if expr == target:
            return val

        if isinstance(expr, LogicalOp):
            op = expr.op
            left = expr.left
            right = expr.right

            # Determine the other side
            other = None
            if target == left:
                other = right
            elif target == right:
                other = left

            other_val = self.evaluate(other) if other else TruthValue("UNKNOWN")

            # ---- NOT ----
            if op == "NOT":
                if target == left:
                    return logical_not(val)

            # ---- AND ----
            elif op == "AND":
                if val == TruthValue("TRUE"):
                    # Both must be TRUE
                    return TruthValue("TRUE")
                elif val == TruthValue("FALSE"):
                    # Only if the other is TRUE can we be sure this target is FALSE
                    if other_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")
                    else:
                        return TruthValue("UNKNOWN")

            # ---- OR ----
            elif op == "OR":
                if val == TruthValue("FALSE"):
                    # Both must be FALSE
                    return TruthValue("FALSE")
                elif val == TruthValue("TRUE"):
                    # Only if the other is FALSE can we be sure this target is TRUE
                    if other_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")
                    else:
                        return TruthValue("UNKNOWN")

            # ---- NAND ----
            elif op == "NAND":
                if val == TruthValue("FALSE"):
                    if other_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")
                    else:
                        return TruthValue("UNKNOWN")
                elif val == TruthValue("TRUE"):
                    return TruthValue("FALSE")
                    
            # ---- NOR ----
            elif op == "NOR":
                if val == TruthValue("FALSE"):
                    if other_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")
                    else:
                        return TruthValue("UNKNOWN")
                elif val == TruthValue("TRUE"):
                    return TruthValue("FALSE")

            # ---- XOR ----
            elif op == "XOR":
                if val == TruthValue("TRUE") and other_val != TruthValue("UNKNOWN"):
                    return logical_not(other_val)
                elif val == TruthValue("FALSE") and other_val != TruthValue("UNKNOWN"):
                    return other_val
                else:
                    return TruthValue("UNKNOWN")

            # ---- XNOR ----
            elif op == "XNOR":
                if val == TruthValue("TRUE") and other_val != TruthValue("UNKNOWN"):
                    return other_val
                elif val == TruthValue("FALSE") and other_val != TruthValue("UNKNOWN"):
                    return logical_not(other_val)
                else:
                    return TruthValue("UNKNOWN")

            # ---- Recursive decomposition for subexpressions ----
            if self.contains_target(left, target) and val == TruthValue("TRUE"):
                left_val = self.evaluate(left)
                return self.decompose(left, left_val, target)
            if self.contains_target(right, target) and val == TruthValue("TRUE"):
                right_val = self.evaluate(right)
                return self.decompose(right, right_val, target)

        return TruthValue("UNKNOWN")

    def contains_target(self, expr, target: Node):
        """
        Recursively check if a predicate is inside a logical expression.
        """
        if expr == target:
            return TruthValue("TRUE")
        
        if isinstance(expr, LogicalOp):
            if (
                self.contains_target(expr.left, target) or
                (expr.right and self.contains_target(expr.right, target))
            ):
                return TruthValue("TRUE")
        return False