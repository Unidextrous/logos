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

    def eval_Assignment(self, node: Assignment):
        """
        Handles an assignment of the form `statement = value`.
        Stores the statement node as the key in the KB.
        """
        # The left side is a statement node
        stmt = node.stmt
        value_node = node.value

        # Ensure the value is a TruthValue node
        if not isinstance(value_node, TruthValue):
            raise TypeError("Assignment value must be a TruthValue node")

        # Store the direct assignment in the KB
        self.kb[stmt] = value_node

        # Return the assigned value
        return value_node

    def eval_Query(self, node: Query):
        """
        Evaluate a query statement. Returns a TruthValue.
        Checks direct KB assignments first, then attempts simple inference.
        """
        stmt = node.stmt

        # 1. Direct match in KB
        if stmt in self.kb:
            return self.kb[stmt]
        
        # 2. Logical operator
        if isinstance(stmt, LogicalOp):
            if stmt.op == "NOT":
                return logical_not(self.evaluate(stmt.left))
            elif stmt.op == "AND":
                return self.infer_from_and(stmt)
            elif stmt.op == "OR":
                return self.infer_from_or(stmt)

        # 3. Predicate (single expression)
        if isinstance(stmt, Predicate):
            if stmt in self.kb:
                return self.kb[stmt]
            return TruthValue("UNKNOWN")
        
        # 4. Fallback: unknown
        return TruthValue("UNKNOWN")

    def eval_Predicate(self, node: Predicate):
        # Direct match in KB
        if node in self.kb:
            return self.kb[node]
        # Fallback if no known value
        return TruthValue("UNKNOWN")
    
    def infer_from_and(self, stmt: LogicalOp):
        left_val = self.evaluate(stmt.left)
        right_val = self.evaluate(stmt.right)
        return logical_and(left_val, right_val)

    def infer_from_or(self, stmt: LogicalOp):
        left_val = self.evaluate(stmt.left)
        right_val = self.evaluate(stmt.right)
        return logical_or(left_val, right_val)