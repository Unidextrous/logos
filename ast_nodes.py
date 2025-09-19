# ----------------------
# Abstract Syntax Tree (AST) Nodes
# ----------------------
class Node:
    """
    Base class for all AST nodes.
    Provides a common type for isinstance checks.
    """
    pass

# ----------------------
# Truth Values
# ----------------------
class TruthValue(Node):
    """
    Represents a logical truth value.
    Allowed values: TRUE, FALSE, UNKNOWN.
    """
    def __init__(self, value):
        # If another TruthValue is passed, unwrap it
        if isinstance(value, TruthValue):
            self.value = value.value
        else:
            self.value = value

    def __repr__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return isinstance(other, TruthValue) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

# ----------------------
# Assignments
# ----------------------
class Assignment(Node):
    """
    Represents an assignment of a value to a statement.
    Example: P(X) = TRUE
    """
    def __init__(self, stmt, value):
        self.stmt = stmt    # The left-hand side statement (Predicate, LogicalOp, etc.)
        self.value = value  # The right-hand side (TruthValue or expression)

    def __repr__(self):
        return f"{self.stmt} = {self.value}"

# ----------------------
# Queries
# ----------------------
class Query(Node):
    """
    Represents a query asking for the truth of a statement.
    Example: P(X)?
    """
    def __init__(self, stmt):
        self.stmt = stmt

    def __repr__(self):
        return f"{self.stmt}?"

# ----------------------
# Terms (variables or constants)
# ----------------------
class Term(Node):
    """
    Represents a simple term, which can be:
      - a variable (x, y, etc.)
      - a constant (Fido, Alice, etc.)
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, Term) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

# ----------------------
# Predicates
# ----------------------
class Predicate(Node):
    """
    Represents an atomic logical predicate with arguments.
    Example: Likes(Alice, IceCream)
    """
    def __init__(self, name, args):
        self.name = name        # Predicate name
        self.args = args        # List of Term or Variable nodes

    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"
    
    def __eq__(self, other):
        return (isinstance(other, Predicate) and
            self.name == other.name and
            self.args == other.args)
    
    def __hash__(self):
        return hash((self.name, tuple(self.args)))

# ----------------------
# Logical Operations
# ----------------------
class LogicalOp(Node):
    """
    Represents a logical operation such as:
      - Unary: NOT A
      - Binary: A AND B, A OR B, etc.
    """
    def __init__(self, op, left, right=None):
        self.op = op        # Operator keyword (AND, OR, NOT, etc.)
        self.left = left    # Left operand (Node)
        self.right = right  # Right operand (Node) or None for unary ops

    def __repr__(self):
        if self.right:
            return f"({self.left} {self.op} {self.right})"
        else:
            return f"{self.op} {self.left}"
    
    def __eq__(self, other):
        return (isinstance(other, LogicalOp) and
                self.op == other.op and
                self.left == other.left and
                self.right == other.right)
    
    def __hash__(self):
        return hash((self.op, self.left, self.right))

# ----------------------
# Conditionals
# ----------------------
class Conditional(Node):
    """
    Represents a conditional statement.
    Example: IF A THEN B
    """
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent  # Left side (condition)
        self.consequent = consequent  # Right side (result)

    def __repr__(self):
        return f"IF {self.antecedent} THEN {self.consequent}"
    
    def __eq__(self, other):
        return (isinstance(other, Conditional) and
                self.antecedent == other.antecedent and
                self.consequent == other.consequent)
    
    def __hash__(self):
        return hash((self.antecedent, self.consequent))

# ----------------------
# Quantifiers
# ----------------------
class Quantifier(Node):
    """
    Represents a quantified expression.
    Example: FORALL(x, y): Likes(x, y)
    """
    def __init__(self, quantifier, vars, body):
        self.quantifier = quantifier  # "FORALL" or "EXISTS"
        self.vars = vars              # Tuple of Variable nodes
        self.body = body              # Expression inside quantifier

    def __repr__(self):
        vars_str = ", ".join(str(v) for v in self.vars)
        return f"{self.quantifier}({vars_str}): {self.body}"
    
    def __eq__(self, other):
        if not isinstance(other, Quantifier):
            return False
        if self.quantifier != other.quantifier:
            return False
        if len(self.vars) != len(other.vars):
            return False

        # Map self.vars → other.vars
        var_map = dict(zip(self.vars, other.vars))
        
        # Recursively check if bodies are equivalent under this mapping
        return self.alpha_eq(self.body, other.body, var_map)

    def alpha_eq(self, node1, node2, var_map):
        """
        Check if two nodes are equivalent under a variable mapping.
        """
        # If they are the exact same object
        if node1 == node2:
            return True

        # If both are predicates
        if isinstance(node1, Predicate) and isinstance(node2, Predicate):
            if node1.name != node2.name or len(node1.args) != len(node2.args):
                return False
            # Check if each argument maps correctly
            for arg1, arg2 in zip(node1.args, node2.args):
                if arg1 in var_map:
                    if var_map[arg1] != arg2:
                        return False
                else:
                    if arg1 != arg2:
                        return False
            return True

        # If both are logical operators
        if isinstance(node1, LogicalOp) and isinstance(node2, LogicalOp):
            if node1.op != node2.op:
                return False
            return (self.alpha_eq(node1.left, node2.left, var_map) and
                    self.alpha_eq(node1.right, node2.right, var_map))

        # If both are conditionals
        if isinstance(node1, Conditional) and isinstance(node2, Conditional):
            return (self.alpha_eq(node1.antecedent, node2.antecedent, var_map) and
                    self.alpha_eq(node1.consequent, node2.consequent, var_map))

        # Otherwise, not equivalent
        return False

    
    def __hash__(self):
        return hash((self.quantifier, tuple(self.vars), self.body))

# ----------------------
# Variables (distinct from Terms for quantifiers)
# ----------------------
class Variable(Node):
    """
    Represents a variable (used in quantifiers and predicates).
    Example: x, y
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name  # or f"?{self.name}" for clarity

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self):
        return hash(self.name)