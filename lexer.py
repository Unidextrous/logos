import string

LETTERS = string.ascii_letters
DIGITS = "0123456789"
KEYWORDS = {
    "FORALL", "EXISTS", "IF", "THEN",
    "AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR",
    "TRUE", "FALSE"
}

TT_TRUTH_VALUE  = "TRUTH_VALUE"
TT_IDENTIFIER   = "IDENTIFIER"
TT_KEYWORD      = "KEYWORD"
TT_QUANTIFIER   = "QUANTIFIER"
TT_EQ           = "EQ"
TT_QMARK       = "QMARK"
TT_LPAREN       = "LPAREN"
TT_RPAREN       = "RPAREN"
TT_COMMA        = "COMMA"
TT_COLON        = "COLON"

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}:{self.value}" if self.value else self.type

class Lexer:
    def __init__(self):
        self.text = ""
        self.pos = -1
        self.current_char = None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def tokenize(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()
        
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t\n\r':
                self.advance()

            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA))
                self.advance()
            
            elif self.current_char == '=':
                tokens.append(Token(TT_EQ))
                self.advance()

            elif self.current_char == '?':
                tokens.append(Token(TT_QMARK))
                self.advance()
            
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON))
                self.advance()

            elif self.current_char in LETTERS or self.current_char == '_':
                tokens.append(self.make_identifier())

            else:
                # Unknown character
                raise Exception(f"Illegal character '{self.current_char}' at position {self.pos}")

        return tokens

    def make_identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char in LETTERS or self.current_char == '_' or self.current_char in DIGITS):
            result += self.current_char
            self.advance()

        upper_result = result.upper()
        if upper_result in ("TRUE", "FALSE", "UNKNOWN"):
            return Token(TT_TRUTH_VALUE, upper_result)
        elif upper_result in KEYWORDS:
            return Token(TT_KEYWORD, upper_result)
        else:
            return Token(TT_IDENTIFIER, result)