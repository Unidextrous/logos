from .lexer import *
from .ast_nodes import *

class Parser:
    def __init__(self):
        self.tokens = []
        self.pos = -1
        self.current_tok = None

    def advance(self):
        self.pos += 1
        self.current_tok = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self, tokens):
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

    def statement(self, partial=False):
        # QUANTIFIER(X): ...
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value in ("FORALL", "EXISTS"):
            expr_node = self.quantified()
        # IF A THEN B
        elif self.current_tok.type == TT_KEYWORD and self.current_tok.value == "IF":
            expr_node = self.conditional()
        else:
            expr_node = self.expr()

        if partial:
            return expr_node
        
        # Assignment?
        if self.current_tok and self.current_tok.type == TT_EQ:
            self.advance()
            value = self.truth_value() if self.current_tok.type == TT_TRUTH_VALUE else self.expr()
            return Assignment(expr_node, value)

        # Query?
        if self.current_tok and self.current_tok.type == TT_QMARK:
            self.advance()
            return Query(expr_node)

        raise Exception("Expected '=' or '?' after expression")
    
    # Top-level expression parser entry point
    def expr(self):
        return self.parse_xnor()

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

    def parse_not(self):
        if self.current_tok and self.current_tok.type == TT_KEYWORD and self.current_tok.value == "NOT":
            op = self.current_tok.value
            self.advance()
            operand = self.parse_not()
            return LogicalOp(op, operand)
        elif self.current_tok and self.current_tok.type == TT_LPAREN:
            self.advance()
            expr = self.statement(True)
            if self.current_tok.type != TT_RPAREN:
                raise Exception("Expected ')' after expression")
            self.advance()
            return expr
        else:
            return self.atom()

    def atom(self):
        if self.current_tok.type == TT_IDENTIFIER:
            # Lookahead to see if it's a predicate
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

    def predicate(self):
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
                args.append(self.expr())

        if self.current_tok.type != TT_RPAREN:
            raise Exception("Expected ')' after predicate arguments")

        self.advance()  # consume ')'
        return Predicate(name, args)

    def truth_value(self):
        tok = self.current_tok

        if tok.type != TT_TRUTH_VALUE:
            raise Exception("Expected truth value")

        self.advance()

        if tok.value in ("TRUE", "FALSE", "UNKNOWN"):
            return TruthValue(tok.value)
        else:
            raise Exception(f"Unknown truth value: {tok.value}")

    def conditional(self):
        self.advance()  # skip 'IF'
        antecedent = self.statement(True)

        if not self.current_tok or not (self.current_tok.type == TT_KEYWORD and self.current_tok.value == "THEN"):
            raise Exception("Expected THEN keyword")
        self.advance()

        consequent = self.statement(True)
        return Conditional(antecedent, consequent)

    def quantified(self):
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