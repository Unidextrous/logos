from .logical_ops import *

# ----------------------
# Interpreter class
# ----------------------
class Interpreter:
    def __init__(self):
        # Knowledge base: maps statements (Predicates, LogicalOps, etc.)
        # to their assigned values (TruthValue or other expressions).
        self.kb = {}

    # ----------------------
    # Core evaluation
    # ----------------------
    def evaluate(self, node):
        """Dynamically dispatch evaluation based on node type."""
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_eval)
        return method(node)

    def generic_eval(self, node):
        """Fallback if no eval method is defined for a node type."""
        raise NotImplementedError(f"No eval method for {type(node).__name__}")

    # ----------------------
    # Truth values
    # ----------------------
    def eval_TruthValue(self, node: TruthValue):
        """Truth values evaluate to themselves."""
        return node

    # ----------------------
    # Assignment
    # ----------------------
    def eval_Assignment(self, node: Assignment):
        """
        Assign a truth value to a statement and store it in the KB.
        Example: P(X) = TRUE
        """
        stmt = node.stmt
        value_node = node.value

        # Store statement node as key in KB
        self.kb[stmt] = value_node
        return value_node

    # ----------------------
    # Query
    # ----------------------
    def eval_Query(self, node: Query):
        """
        Evaluate a query (e.g. `P(X)?`).
        1. If it's a Predicate or LogicalOp → evaluate directly.
        2. Otherwise, try inference.
        3. If unknown, return UNKNOWN.
        """
        stmt = node.stmt

        if isinstance(stmt, Predicate):
            result = self.eval_Predicate(stmt)
        elif isinstance(stmt, LogicalOp):
            result = self.eval_LogicalOp(stmt)
        else:
            result = TruthValue("UNKNOWN")
            inferred = self.infer(stmt, set())
            if inferred is not None:
                return inferred

        return result

    # ----------------------
    # Predicates
    # ----------------------
    def eval_Predicate(self, node: Predicate):
        """
        Evaluate a predicate.
        - If found in KB → return stored value.
        - Otherwise, attempt inference.
        - If not inferable → UNKNOWN.
        """
        if node in self.kb:
            return self.evaluate(self.kb[node])

        inferred = self.infer(node, set())
        return inferred if inferred is not None else TruthValue("UNKNOWN")

    # ----------------------
    # Logical operations
    # ----------------------
    def eval_LogicalOp(self, node: LogicalOp):
        """
        Evaluate logical operators directly.
        Handles NOT (unary) and all binary ops (AND, OR, etc.).
        """
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
    def infer(self, target, visited=None):
        """
        Attempt to infer the truth value of a target node
        from the knowledge base.
        - Uses visited set to prevent infinite recursion.
        - Dispatches to `infer_from_*` methods depending on stmt type.
        """
        if visited == None:
            visited = set()

        if target in visited:
            return None
        visited.add(target)

        for stmt, val in self.kb.items():
            # Dispatch based on *stmt* not target
            method_name = f"infer_from_{type(stmt).__name__}"
            method = getattr(self, method_name, self.generic_infer_from)
            result = method(stmt, val, target, visited)
            if result is not None:
                visited.remove(target)
                return result
        
        visited.remove(target)
        return None

    def generic_infer_from(self, node):
        return None

    # ----------------------
    # Predicate inference
    # ----------------------
    def infer_from_Predicate(self, stmt, val, target, visited):
        """
        If the target is exactly the predicate in the KB,
        return its assigned value.
        """
        if stmt == target:
            return self.evaluate(val)
        return None


    # ----------------------
    # LogicalOp inference
    # ----------------------
    def infer_from_LogicalOp(self, stmt, val, target, visited):
        """
        Try to infer the truth value of `target` using logical operator
        statements stored in the KB.
        - Handles cases where target is part of a logical expression.
        - Uses decomposition and recursive inference when needed.
        """
        if stmt == target:
            return self.evaluate(val)
        
        op = stmt.op
        
        # Skip if target isn't part of this expression
        if not self.contains_target(stmt, target):
            return None
        
        # Directly check if target is one side of the expression
        if target in [stmt.left, stmt.right]:
            other = stmt.right if target == stmt.left else stmt.left
            stmt_val = self.evaluate(val)

            other_val = self.infer(other, visited)

            # Handle each logical operator
            if op == "NOT":
                return logical_not(stmt_val)
            if op == "AND":
                if stmt_val == TruthValue("TRUE"):
                    return TruthValue("TRUE")
                elif stmt_val == TruthValue("FALSE") and other_val == TruthValue("TRUE"):
                    return TruthValue("FALSE")
            if op == "OR":
                if stmt_val == TruthValue("FALSE"):
                    return TruthValue("FALSE")
                elif stmt_val == TruthValue("TRUE") and other_val == TruthValue("FALSE"):
                    return TruthValue("TRUE")
            if op == "NAND":
                if stmt_val == TruthValue("TRUE"):
                    return TruthValue("FALSE")
                elif stmt_val == TruthValue("FALSE") and other_val == TruthValue("FALSE"):
                    return TruthValue("TRUE")
            if op == "NOR":
                if stmt_val == TruthValue("TRUE"):
                    return TruthValue("FALSE")
                elif stmt_val == TruthValue("FALSE") and other_val == TruthValue("TRUE"):
                    return TruthValue("TRUE")
            if op == "XOR":
                if other_val is not None:
                    return logical_xor(stmt_val, other_val)
                return None
            if op == "XNOR":
                if other_val is not None:
                    return logical_xnor(stmt_val, other_val)
                return None
        
        # Try recursive inference on sub-expressions
        left_val = self.infer(stmt.left, visited) if not isinstance(stmt.left, TruthValue) else None
        right_val = self.infer(stmt.right, visited) if not isinstance(stmt.right, TruthValue) else None

        stmt_val = self.evaluate(val)
        
        if isinstance(stmt.left, LogicalOp):
            result = self.infer_from_LogicalOp(
                stmt.left, left_val if left_val is not None else TruthValue("UNKNOWN"), target, visited
            )
            if result is not None:
                return result
        if isinstance(stmt.right, LogicalOp):
            result = self.infer_from_LogicalOp(
                stmt.right, right_val if right_val is not None else TruthValue("UNKNOWN"), target, visited
            )
            if result is not None:
                return result
        
        return None

    # ----------------------
    # Helper Methods
    # ----------------------
    def decompose(self, expr, val, target):
        """
        Try to deduce the truth value of a target inside an expression
        based on the overall expression value.
        (Used as a fallback when direct inference fails.)
        """
        if expr == target:
            return val

        if isinstance(expr, LogicalOp):
            op = expr.op
            left = expr.left
            right = expr.right

            # Determine which side is "other"
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

            # Recursive decomposition for nested logical ops
            if self.contains_target(left, target) and val == TruthValue("TRUE"):
                left_val = self.evaluate(left)
                return self.decompose(left, left_val, target)
            if self.contains_target(right, target) and val == TruthValue("TRUE"):
                right_val = self.evaluate(right)
                return self.decompose(right, right_val, target)

        return TruthValue("UNKNOWN")

    def contains_target(self, expr, target: Node):
        """
        Recursively check whether a target node is part of a larger expression.
        Used to avoid exploring irrelevant branches during inference.
        """
        if expr == target:
            return True
        
        if isinstance(expr, LogicalOp):
            return (
                (self.contains_target(expr.left, target)) or
                (expr.right and self.contains_target(expr.right, target))
            )
        return False