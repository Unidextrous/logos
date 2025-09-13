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

        if stmt in self.kb:
            return self.kb[stmt]