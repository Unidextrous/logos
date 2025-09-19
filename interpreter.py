from .logical_ops import *
from itertools import product

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
        elif isinstance(stmt, Conditional):
            result = self.eval_Conditional(stmt)
        elif isinstance(stmt, Quantifier):
            result = self.eval_Quantifier(stmt)
        
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
        # Check if the exact expression is stored in the KB
        if node in self.kb:
            return self.evaluate(self.kb[node])
        
        left_val = self.evaluate(node.left)
        
        # Lookup the operator in the dictionary
        if node.op not in LOGICAL_OPERATORS:
            return TruthValue("UNKNOWN")

        func, arity = LOGICAL_OPERATORS[node.op]

        if arity == 1:  # unary operator (NOT)
            return func(left_val)

        right_val = self.evaluate(node.right)
        return func(left_val, right_val)

    # ----------------------
    # Conditionals
    # ----------------------
    def eval_Conditional(self, node: Conditional):
        """
        Evaluate a conditional IF antecedent THEN consequent.
        Only returns TRUE/FALSE if the conditional exists in the KB.
        Otherwise, returns UNKNOWN.
        """
        # Check if the exact conditional is in the KB
        if node in self.kb:
            return self.evaluate(self.kb[node])
        
        # Otherwise, attempt to infer its value
        inferred = self.infer(node, set())
        if inferred is not None:
            return inferred

        # Conditional isn't known → UNKNOWN
        return TruthValue("UNKNOWN")

    # ----------------------
    # Quantifiers
    # ----------------------
    def eval_Quantifier(self, node: Quantifier):
        """
        Evaluate quantifiers (multi-variable + nested) strictly via KB.
        TRUE/FALSE only if explicitly stated in KB or inferable.
        """
        # Check for explicit KB assignment
        if node in self.kb:
            return self.evaluate(self.kb[node])
        
        # Try inferrence
        inferred = self.infer(node, set())
        if inferred is not None:
            return inferred

        # Collect constants from KB
        constants = set()
        for stmt in self.kb:
            constants.update(self._extract_terms(stmt))
        if not constants:
            return TruthValue("UNKNOWN")

        from itertools import product
        var_names = [v.name for v in node.vars]
        all_combinations = product(constants, repeat=len(var_names))

        for combination in all_combinations:
            subst = dict(zip(var_names, combination))
            body_instance = node.body.substitute(subst)
            val = self.evaluate(body_instance)

            # Short-circuit only for explicit TRUE/FALSE
            if node.quantifier == "FORALL" and val == TruthValue("FALSE"):
                return TruthValue("FALSE")
            if node.quantifier == "EXISTS" and val == TruthValue("TRUE"):
                return TruthValue("TRUE")

        # Nothing decisive in KB → return UNKNOWN
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

    def generic_infer_from(self, stmt, val=None, target=None, visited=None):
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
    # Conditional inference
    # ----------------------
    def infer_from_Conditional(self, stmt, val, target, visited):
        """
        stmt: Conditional node (IF antecedent THEN consequent)
        val: TruthValue of the conditional itself (TRUE/FALSE)
        target: The node we are trying to infer
        visited: Set of already visited nodes to avoid cycles
        """
        antecedent = stmt.antecedent
        consequent = stmt.consequent

        # Case 1: target is the conditional itself
        if stmt == target:
            return self.evaluate(val)

        # Case 2: target is the consequent
        if target == consequent:
            # If conditional is TRUE and antecedent is TRUE → consequent must be TRUE
            antecedent_val = self.infer(antecedent, visited)
            if val == TruthValue("TRUE") and antecedent_val == TruthValue("TRUE"):
                return TruthValue("TRUE")
            # If conditional is FALSE and antecedent is TRUE → consequent must be FALSE
            if val == TruthValue("FALSE") and antecedent_val == TruthValue("TRUE"):
                return TruthValue("FALSE")
        
        # Case 3: target is the antecedent
        if target == antecedent:
            consequent_val = self.infer(consequent, visited)
            # Modus tollens: IF A THEN B = TRUE, B = FALSE → A = FALSE
            if val == TruthValue("TRUE") and consequent_val == TruthValue("FALSE"):
                return TruthValue("FALSE")
            # Rare case: IF A THEN B = FALSE, B = TRUE → A = TRUE (less common)
            if val == TruthValue("FALSE") and consequent_val == TruthValue("TRUE"):
                return TruthValue("TRUE")
        
        # Recursively try to infer inside nested expressions
        if isinstance(antecedent, LogicalOp) or isinstance(antecedent, Conditional):
            result = self.infer(antecedent, visited)
            if result is not None:
                return result
        if isinstance(consequent, LogicalOp) or isinstance(consequent, Conditional):
            result = self.infer(consequent, visited)
            if result is not None:
                return result

        return None

    def infer_from_Quantifier(self, stmt: Quantifier, val, target, visited):
        """
        Attempt to infer the truth value of a quantifier.
        Only returns TRUE/FALSE if all (FORALL) or some (EXISTS) instantiations are TRUE/FALSE in KB.
        """
        if stmt == target:
            return self.evaluate(val)

        # Collect constants from KB
        constants = set()
        for s in self.kb:
            constants.update(self._extract_terms(s))
        if not constants:
            return None

        from itertools import product
        var_names = [v.name for v in stmt.vars]
        all_combinations = product(constants, repeat=len(var_names))

        # Evaluate each instantiation
        for combination in all_combinations:
            subst = dict(zip(var_names, combination))
            body_instance = stmt.body.substitute(subst)
            body_val = self.infer(body_instance, visited)
            if stmt.quantifier == "FORALL" and body_val == TruthValue("FALSE"):
                return TruthValue("FALSE")
            if stmt.quantifier == "EXISTS" and body_val == TruthValue("TRUE"):
                return TruthValue("TRUE")

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

    def _extract_terms(self, node):
        """Recursively collect Term objects from any node."""
        terms = set()
        if isinstance(node, Predicate):
            for arg in node.args:
                if isinstance(arg, Term):
                    terms.add(arg)
        elif isinstance(node, LogicalOp):
            terms.update(self._extract_terms(node.left))
            if node.right:
                terms.update(self._extract_terms(node.right))
        elif isinstance(node, Conditional):
            terms.update(self._extract_terms(node.antecedent))
            terms.update(self._extract_terms(node.consequent))
        return terms
