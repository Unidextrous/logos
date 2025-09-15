from .lexer import *
from .ast_nodes import *

# ----------------------
# Parser class
# ----------------------
class Parser:
    """
    Converts a list of tokens into an Abstract Syntax Tree (AST).
    Supports:
      - Quantifiers (FORALL, EXISTS)
      - Conditionals (IF ... THEN ...)
      - Logical operations (AND, OR, NOT, NAND, NOR, XOR, XNOR)
      - Assignments and queries
      - Predicates and terms
    """
    def __init__(self):
        self.tokens = []            # List of tokens to parse
        self.pos = -1               # Current token index
        self.current_tok = None     # Current token object

    # ----------------------
    # Token navigation
    # ----------------------
    def advance(self):
        """Move to the next token in the list, updating current_tok."""
        self.pos += 1
        self.current_tok = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # ----------------------
    # Entry point
    # ----------------------
    def parse(self, tokens):
        """
        Main parsing function.
        - Resets internal state.
        - Starts parsing a single statement.
        Returns the root AST node for that statement.
        """
        self.tokens = tokens
        self.pos = -1
        self.current_tok = None
        self.advance()

        try:
            if self.current_tok is None:
                return None
            result = self.statement()
            return result
        except Exception as e:
            print(f"Parser error: {e}")
            return None

    # ----------------------
    # Statement parsing
    # ----------------------
    def statement(self, partial=False):
        """
        Parse a "statement", which could be:
          - a quantified expression (FORALL/EXISTS)
          - a conditional (IF ... THEN ...)
          - a logical expression
        Also handles:
          - Assignments (expr = value)
          - Queries (expr ?)
        partial=True is used when parsing inside parentheses to avoid expecting '=' or '?'.
        """
        # Quantifier
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value in ("FORALL", "EXISTS"):
            expr_node = self.quantified()
        # Conditional
        elif self.current_tok.type == TT_KEYWORD and self.current_tok.value == "IF":
            expr_node = self.conditional()
        # General logical expression
        else:
            expr_node = self.expr()

        # If partial, do not expect assignment or query
        if partial:
            return expr_node
        
        # Assignment
        if self.current_tok and self.current_tok.type == TT_EQ:
            self.advance()
            value = self.truth_value() if self.current_tok.type == TT_TRUTH_VALUE else self.expr()
            return Assignment(expr_node, value)

        # Query
        if self.current_tok and self.current_tok.type == TT_QMARK:
            self.advance()
            return Query(expr_node)

        # Unexpected token if neither '=' nor '?'
        raise Exception("Expected '=' or '?' after expression")
    
    # ----------------------
    # Expression parsing hierarchy
    # ----------------------
    def expr(self):
        """Top-level expression parser entry point: XNOR is lowest precedence."""
        return self.parse_xnor()

    # Each of the following parse_* methods implements precedence climbing.
    # Higher-precedence operations are parsed first.
    # NOT > AND > OR > NAND > NOR > XOR > XNOR
    def parse_xnor(self):
        left = self.parse_xor()
        while self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "XNOR":
            op = self.current_tok.value
            self.advance()
            right = self.parse_xor()
            left = LogicalOp(op, left, right)
        return left

    def parse_xor(self):
        left = self.parse_nor()
        while self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "XOR":
            op = self.current_tok.value
            self.advance()
            right = self.parse_nor()
            left = LogicalOp(op, left, right)
        return left

    def parse_nor(self):
        left = self.parse_nand()
        while self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "NOR":
            op = self.current_tok.value
            self.advance()
            right = self.parse_nand()
            left = LogicalOp(op, left, right)
        return left

    def parse_nand(self):
        left = self.parse_or()
        while self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "NAND":
            op = self.current_tok.value
            self.advance()
            right = self.parse_or()
            left = LogicalOp(op, left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "OR":
            op = self.current_tok.value
            self.advance()
            right = self.parse_and()
            left = LogicalOp(op, left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "AND":
            op = self.current_tok.value
            self.advance()
            right = self.parse_not()
            left = LogicalOp(op, left, right)
        return left

    # ----------------------
    # Unary NOT and parentheses
    # ----------------------
    def parse_not(self):
        """
        Parse unary NOT or parenthesized expressions.
        NOT has the highest precedence.
        """
        # Unary NOT
        if self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "NOT":
            op = self.current_tok.value
            self.advance()
            operand = self.parse_not()
            return LogicalOp(op, operand)
        # Parentheses
        elif self.current_tok and self.current_tok.type == TT_LPAREN:
            self.advance()
            expr = self.statement(True)
            if self.current_tok.type != TT_RPAREN:
                raise Exception("Expected ')' after expression")
            self.advance()
            return expr
        # Base case: atomic value
        else:
            return self.atom()

    # ----------------------
    # Atoms (predicates, terms, truth values)
    # ----------------------
    def atom(self):
        """
        Parse:
          - A predicate (with parentheses and arguments)
          - A single variable/term
          - A truth value (TRUE, FALSE, UNKNOWN)
        """
        if self.current_tok.type == TT_IDENTIFIER:
            # Look ahead to see if it's a predicate
            next_tok = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_tok and next_tok.type == TT_LPAREN:
                return self.predicate()
            else:
                name = self.current_tok.value
                self.advance()
                return Term(name)
        
        elif self.current_tok.type == TT_TRUTH_VALUE:
            value = self.current_tok.value
            self.advance()
            return TruthValue(value)

        raise Exception(f"Unexpected token: {self.current_tok}")

    # ----------------------
    # Predicate parsing
    # ----------------------
    def predicate(self):
        """
        Parse a predicate:
          name(arg1, arg2, ...)
        """
        if self.current_tok.type != TT_IDENTIFIER:
            raise Exception("Expected predicate name")

        name = self.current_tok.value
        self.advance()

        if self.current_tok is None or self.current_tok.type != TT_LPAREN:
            raise Exception("Expected '(' after predicate name")

        self.advance()  # consume '('
        args = []
        if self.current_tok and self.current_tok.type != TT_RPAREN:
            args.append(self.expr())
            while self.current_tok and self.current_tok.type == TT_COMMA:
                self.advance()
                args.append(self.expr())    # Parse remaining arguments

        if self.current_tok.type != TT_RPAREN:
            raise Exception("Expected ')' after predicate arguments")

        self.advance()  # consume ')'
        return Predicate(name, args)

    # ----------------------
    # Boolean literal parser
    # ----------------------
    def truth_value(self):
        """Parse TRUE, FALSE, or UNKNOWN."""
        tok = self.current_tok

        if tok.type != TT_TRUTH_VALUE:
            raise Exception("Expected truth value")

        self.advance()

        if tok.value in ("TRUE", "FALSE", "UNKNOWN"):
            return TruthValue(tok.value)
        else:
            raise Exception(f"Unknown truth value: {tok.value}")

    # ----------------------
    # Conditional parsing
    # ----------------------
    def conditional(self):
        """
        Parse a conditional statement: IF antecedent THEN consequent
        """
        self.advance()  # skip 'IF'
        antecedent = self.statement(True)

        if not self.current_tok or not (self.current_tok.type == TT_KEYWORD and self.current_tok.value == "THEN"):
            raise Exception("Expected THEN keyword")
        self.advance()

        consequent = self.statement(True)
        return Conditional(antecedent, consequent)

    # ----------------------
    # Quantifier parsing
    # ----------------------
    def quantified(self):
        """
        Parse a quantifier statement: FORALL(vars): expr or EXISTS(vars): expr
        Supports nested quantifiers.
        """
        quant_type = self.current_tok.value  # FORALL or EXISTS
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            raise Exception("Expected '(' after quantifier")
        self.advance()

        vars = []
        if self.current_tok.type == TT_IDENTIFIER:
            vars.append(Variable(self.current_tok.value))
            self.advance()

            while self.current_tok and self.current_tok.type == TT_COMMA:
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    raise Exception("Expected identifier after ',' in quantifier")
                vars.append(Variable(self.current_tok.value))
                self.advance()
        else:
            raise Exception("Expected variable inside quantifier")

        if self.current_tok.type != TT_RPAREN:
            raise Exception("Expected ')' after variable(s)")
        self.advance()

        if self.current_tok.type != TT_COLON:
            raise Exception("Expected ':' after quantifier")
        self.advance()

        # Nested quantifier support
        if self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value in ("FORALL", "EXISTS"):
            expr = self.quantified()
        else:
            expr = self.statement(partial=True)

        return Quantifier(quant_type, tuple(vars), expr)