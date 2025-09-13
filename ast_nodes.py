# ast_nodes.py

class Node:
    pass

class TruthValue(Node):
    def __init__(self, value):
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

class Assignment(Node):
    def __init__(self, stmt, value):
        self.stmt = stmt
        self.value = value  # True or False

    def __repr__(self):
        return f"{self.stmt} = {self.value}"

class Query(Node):
    def __init__(self, stmt):
        self.stmt = stmt

    def __repr__(self):
        return f"{self.stmt}?"

class Term(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, Term) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

class Predicate(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"
    
    def __eq__(self, other):
        return (isinstance(other, Predicate) and
            self.name == other.name and
            self.args == other.args)
    
    def __hash__(self):
        return hash((self.name, tuple(self.args)))
    
class LogicalOp(Node):
    def __init__(self, op, left, right=None):
        self.op = op
        self.left = left
        self.right = right

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

class Conditional(Node):
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent

    def __repr__(self):
        return f"IF {self.antecedent} THEN {self.consequent}"
    
    def __eq__(self, other):
        return (isinstance(other, Conditional) and
                self.antecedent == other.antecedent and
                self.consequent == other.consequent)
    
    def __hash__(self):
        return hash((self.antecedent, self.consequent))

class Quantifier(Node):
    def __init__(self, quantifier, vars, body):
        self.quantifier = quantifier
        self.vars = vars
        self.body = body

    def __repr__(self):
        vars_str = ", ".join(str(v) for v in self.vars)
        return f"{self.quantifier}({vars_str}): {self.expr}"
    
    def __eq__(self, other):
        return (isinstance(other, Quantifier) and
                self.quantifier == other.quantifier and
                self.vars == other.vars and
                self.body == other.body)
    
    def __hash__(self):
        return hash((self.quantifier, tuple(self.vars), self.body))

class Variable(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name  # or f"?{self.name}" for clarity

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self):
        return hash(self.name)