from .ast_nodes import *

class Interpreter:
    def __init__(self):
        self.kb = {}

    def evaluate(self, node):
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_eval)
        return method(node)

    def generic_eval(self, node):
        raise NotImplementedError(f"No eval method for {type(node).__name__}")
    
    # === Evaluation Methods for Each AST Node Type === #

    def eval_Assignment(self, node):
        statement = node.statement
        if isinstance(statement, (Predicate, Conditional, Quantifier, LogicalOp)):
            evaluated_value = TruthValue(node.value)
            self.kb[statement] = evaluated_value

            if isinstance(node.statement, LogicalOp) and node.statement.op.upper() == "NOT":
                transformed = apply_demorgan(node.statement)
                if transformed != node.statement:
                    self.kb[transformed] = node.value

            return evaluated_value
        else:
            raise TypeError("Only predicate, conditional, and quantifier assignments are supported.")
    
    def eval_Query(self, node):
        # Try direct match first
        result = self.evaluate(node.expr)
        if result != TruthValue("UNKNOWN") and result is not None:
            return result

        # Try reverse inference from known logical expressions
        for key, value in self.kb.items():
            if isinstance(key, LogicalOp) and value == TruthValue("TRUE"):
                # AND Case: If (A AND B) == TRUE, then A == TRUE and B == TRUE
                if key.op.upper() == "AND":
                    # If (NOT A AND NOT B) == TRUE, then both NOT A == TRUE and NOT B == TRUE -> A and B must be FALSE
                    for sub in [key.left, key.right]:
                        if isinstance(sub, LogicalOp) and sub.op.upper() == "NOT":
                            if sub.left == node.expr:
                                return TruthValue("FALSE")
                            
                    if self.expression_contains(key, node.expr):
                        return TruthValue("TRUE")

                # OR: if A OR B == TRUE, and other side is FALSE, then this side is TRUE
                elif key.op.upper() == "OR":
                    if node.expr == key.left:
                        other = key.right
                    elif node.expr == key.right:
                        other = key.left
                    else:
                        continue

                    other_val = self.evaluate(other)
                    if other_val == TruthValue("FALSE"):
                        return TruthValue("TRUE")

                # NOT: if NOT A == TRUE, then A == FALSE
                elif key.op.upper() == "NOT":
                    if node.expr == key.left:
                        return TruthValue("FALSE")

            if isinstance(key, LogicalOp) and value == TruthValue("FALSE"):
                # AND Case: If (A AND B) == FALSE, then A == FALSE or B == FALSE
                if key.op.upper() == "AND":
                    if node.expr == key.left:
                        other = key.right
                    elif node.expr == key.right:
                        other = key.left
                    else:
                        continue

                    other_val = self.evaluate(other)
                    if other_val == TruthValue("TRUE"):
                        return TruthValue("FALSE")

                # OR: if A OR B == FALSE, and other side is TRUE, then this side is FALSE
                elif key.op.upper() == "OR":
                    # If (NOT A OR NOT B) == FALSE, then both NOT A == FALSE and NOT B == FALSE -> A and B must be TRUE
                    for sub in [key.left, key.right]:
                        if isinstance(sub, LogicalOp) and sub.op.upper() == "NOT":
                            if sub.left == node.expr:
                                return TruthValue("TRUE")
                            
                    if self.expression_contains(key, node.expr):
                        return TruthValue("FALSE")

                # NOT: if NOT A == TRUE, then A == FALSE
                elif key.op.upper() == "NOT":
                    if node.expr == key.left:
                        return TruthValue("TRUE")

        # Try Modus Ponens inference
        for key in self.kb:
            if isinstance(key, Conditional):
                antecedent = key.antecedent
                consequent = key.consequent
                if consequent == node.expr:
                    antecedent_value = self.kb.get(antecedent)
                    conditional_value = self.kb.get(key)
                    if conditional_value == TruthValue("TRUE") and antecedent_value == TruthValue("TRUE"):
                        return TruthValue("TRUE")

        # Handle double negation: if NOT NOT A = TRUE, then A = TRUE
        for expr, value in self.kb.items():
            if (
                isinstance(expr, LogicalOp) and 
                expr.op.upper() == "NOT" and 
                isinstance(expr.left, LogicalOp) and 
                expr.left.op.upper() == "NOT"
            ):
                inner = expr.left.left
                if inner == node.expr:
                    return value  # pass along the truth of the double negation

        return TruthValue("UNKNOWN")

    def eval_TruthValue(self, node):
        return node
    
    def eval_Predicate(self, node):
        # Direct fact
        if node in self.kb:
            return self.kb[node]

        # Inferred from conditionals
        for kb_key, value in self.kb.items():
            if isinstance(kb_key, Conditional) and value == TruthValue("TRUE"):               
                antecedent = kb_key.antecedent
                consequent = kb_key.consequent

                # If this predicate matches the consequent,
                # and the antecedent is known to be true, infer it
                if consequent == node:
                    antecedent_value = self.evaluate(antecedent)
                    if antecedent_value == TruthValue("TRUE"):
                        return TruthValue("TRUE")

        # Inferred from universal quantifiers
        for kb_key, value in self.kb.items():
            if isinstance(kb_key, Quantifier) and kb_key.quantifier == "FORALL" and value == "TRUE":
                if self._predicate_matches_quantified_statement(node, kb_key):
                    return TruthValue("TRUE")

        return TruthValue("UNKNOWN")
    
    def eval_LogicalOp(self, node):
        op = node.op.upper()
        
        if op == "NOT":
            if node in self.kb:
                return self.kb[node]
            left = self.evaluate(node.left)
            return self.logical_not(left)

        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if op == "AND":
            if node in self.kb:
                return self.kb[node]    
            return self.logical_and(left, right)
        elif op == "OR":
            if node in self.kb:
                return self.kb[node] 
            return self.logical_or(left, right)
        else:
            raise ValueError(f"Unknown logical operator: {op}")

    def logical_not(self, value):
        if value == TruthValue("TRUE"):
            return TruthValue("FALSE")
        elif value == TruthValue("FALSE"):
            return TruthValue("TRUE")
        else:
            return TruthValue("UNKNOWN")

    def logical_and(self, a, b):
        if a == TruthValue("TRUE") and b == TruthValue("TRUE"):
            return TruthValue("TRUE")
        if a == TruthValue("FALSE") or b == TruthValue("FALSE"):
            return TruthValue("FALSE")
        return TruthValue("UNKNOWN")

    def logical_or(self, a, b):
        if a == TruthValue("TRUE") or b == TruthValue("TRUE"):
            return TruthValue("TRUE")
        if a == TruthValue("FALSE") and b == TruthValue("FALSE"):
            return TruthValue("FALSE")
        return TruthValue("UNKNOWN")
    
    def eval_Conditional(self, node):
        if node in self.kb:
            return self.kb[node]
        else:
            return TruthValue("UNKNOWN")
    
    def eval_Quantifier(self, node):
        if node in self.kb:
            return self.kb[node]
        else:
            return TruthValue("UNKNOWN")
    
    def expression_contains(self, expr, subexpr):
        # Check if subexpr is exactly expr
        if expr == subexpr:
            return True

        # If expr is LogicalOp, check recursively
        if isinstance(expr, LogicalOp):
            if self.expression_contains(expr.left, subexpr):
                return True
            # For NOT, right may not exist, so be safe:
            if hasattr(expr, 'right') and expr.right:
                if self.expression_contains(expr.right, subexpr):
                    return True
        return False

def apply_demorgan(expr):
    """
    Applies DeMorgan's law to NOT expressions with AND/OR inside.
    NOT (A AND B) => (NOT A OR NOT B)
    NOT (A OR B)  => (NOT A AND NOT B)
    """
    if not (isinstance(expr, LogicalOp) and expr.op.upper() == "NOT"):
        return expr  # Not a NOT expression, return as-is

    inner = expr.left
    if not isinstance(inner, LogicalOp):
        return expr  # Nothing to transform

    if inner.op.upper() == "AND":
        return LogicalOp("OR", LogicalOp("NOT", inner.left), LogicalOp("NOT", inner.right))
    elif inner.op.upper() == "OR":
        return LogicalOp("AND", LogicalOp("NOT", inner.left), LogicalOp("NOT", inner.right))
    else:
        return expr  # Not a DeMorgan target