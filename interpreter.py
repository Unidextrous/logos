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
        """Evaluate quantifier with inference."""
        # Explicit assignment
        if node in self.kb:
            return self.evaluate(self.kb[node])

        # Collect all constants known in KB for the variables
        constants = set()
        for stmt in self.kb:
            if isinstance(stmt, Predicate):
                for arg in stmt.args:
                    if isinstance(arg, Term):
                        constants.add(arg)

        if not constants:
            return TruthValue("UNKNOWN")

        # Track results
        any_true = False
        any_false = False

        for const in constants:
            # Generate substitution dict for the variable(s)
            subst = {v.name: const for v in node.vars}
            body_instance = node.body.substitute(subst)
            val = self.evaluate(body_instance)

            if val == TruthValue("TRUE"):
                any_true = True
            elif val == TruthValue("FALSE"):
                any_false = True

            if node.quantifier == "FORALL" and val == TruthValue("FALSE"):
                return TruthValue("FALSE")
            if node.quantifier == "EXISTS" and val == TruthValue("TRUE"):
                return TruthValue("TRUE")

        # Decide UNKNOWN/TRUE/FALSE
        if node.quantifier == "FORALL":
            return TruthValue("TRUE") if any_false == False else TruthValue("UNKNOWN")
        elif node.quantifier == "EXISTS":
            return TruthValue("FALSE") if any_true == False else TruthValue("UNKNOWN")

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

    def matches_quantifier(self, quant_body, kb_stmt, vars, subst=None):
        """
        Check whether kb_stmt can be obtained from quant_body by substituting
        the quantified variables (vars). Returns a substitution dict on match,
        or None if no match.

        vars: tuple/list of Variable nodes (e.g. (Variable('X'), ...))
        subst: carry-through substitution dict used during recursion
        """
        if subst is None:
            subst = {}

        # variable name set for quick checks (vars may be Variable objects)
        var_names = {v.name if hasattr(v, "name") else v for v in vars}

        # ---- Predicates ----
        if isinstance(quant_body, Predicate) and isinstance(kb_stmt, Predicate):
            if quant_body.name != kb_stmt.name or len(quant_body.args) != len(kb_stmt.args):
                return None

            local = subst.copy()

            for q_arg, kb_arg in zip(quant_body.args, kb_stmt.args):
                # If q_arg is itself a complex node, recurse
                if not isinstance(q_arg, Term):
                    sub_res = self.matches_quantifier(q_arg, kb_arg, vars, local)
                    if sub_res is None:
                        return None
                    # merge substitutions (check consistency)
                    for k, v in sub_res.items():
                        if k in local and local[k] != v:
                            return None
                        local[k] = v
                    continue

                # q_arg is a Term (identifier). If its name is a quantified var,
                # treat it as variable to be bound; otherwise it must match exactly.
                q_name = q_arg.name
                if q_name in var_names:
                    existing = local.get(q_name)
                    if existing is None:
                        local[q_name] = kb_arg
                    else:
                        if existing != kb_arg:
                            return None  # conflicting mapping
                else:
                    # non-variable term: must match exactly
                    if not isinstance(kb_arg, Term) or q_name != kb_arg.name:
                        return None

            return local

        # ---- LogicalOp ----
        if isinstance(quant_body, LogicalOp) and isinstance(kb_stmt, LogicalOp):
            if quant_body.op != kb_stmt.op:
                return None

            # Unary (NOT)
            if quant_body.right is None:
                return self.matches_quantifier(quant_body.left, kb_stmt.left, vars, subst)

            # Binary ops
            commutative_ops = {"AND", "OR", "XOR", "XNOR"}
            if quant_body.op in commutative_ops:
                # Try (left→left, right→right)
                left_first = self.matches_quantifier(quant_body.left, kb_stmt.left, vars, subst)
                if left_first is not None:
                    right_first = self.matches_quantifier(quant_body.right, kb_stmt.right, vars, left_first)
                    if right_first is not None:
                        return right_first

                # Try swapped (left→right, right→left)
                left_swapped = self.matches_quantifier(quant_body.left, kb_stmt.right, vars, subst)
                if left_swapped is not None:
                    right_swapped = self.matches_quantifier(quant_body.right, kb_stmt.left, vars, left_swapped)
                    if right_swapped is not None:
                        return right_swapped

                return None
            else:
                # Non-commutative: must match in order
                left_subst = self.matches_quantifier(quant_body.left, kb_stmt.left, vars, subst)
                if left_subst is None:
                    return None
                return self.matches_quantifier(quant_body.right, kb_stmt.right, vars, left_subst)

        # Not supported yet (Conditionals, Quantifiers nested, etc.)
        return None
