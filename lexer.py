import string


# ----------------------
# Character sets
# ----------------------
LETTERS = string.ascii_letters  # All ASCII letters: a-z and A-Z
DIGITS = "0123456789"           # All digit characters

# ----------------------
# Keywords in the language
# ----------------------
# Includes quantifiers, logical operators, and boolean literals
KEYWORDS = {
    "TRUE", "FALSE", "IF", "THEN",
    "AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR",
    "FORALL", "EXISTS"
}

# ----------------------
# Token types
# ----------------------
TT_TRUTH_VALUE  = "TRUTH_VALUE"     # TRUE, FALSE, UNKNOWN
TT_IDENTIFIER   = "IDENTIFIER"      # User-defined names (variables, predicate names)
TT_KEYWORD      = "KEYWORD"         # Language keywords (IF, THEN, AND, OR, etc.)
TT_QUANTIFIER   = "QUANTIFIER"      # FORALL, EXISTS (handled via KEYWORDS)
TT_EQ           = "EQ"              # =
TT_QMARK        = "QMARK"           # ?
TT_LPAREN       = "LPAREN"          # (
TT_RPAREN       = "RPAREN"          # )
TT_COMMA        = "COMMA"           # ,
TT_COLON        = "COLON"           # :

# ----------------------
# Token class
# ----------------------
class Token:
    """Represents a single lexical token with a type and optional value."""
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}:{self.value}" if self.value else self.type

# ----------------------
# Lexer class
# ----------------------
class Lexer:
    """
    Converts an input string into a list of tokens.
    Handles identifiers, keywords, boolean literals, and basic symbols.
    """
    def __init__(self):
        self.text = ""
        self.pos = -1               # Current position in the text
        self.current_char = None    # Current character under examination

    def advance(self):
        """
        Move the 'cursor' forward one character.
        Updates current_char to the next character or None if end of text.
        """
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def tokenize(self, text):
        """
        Main entry point: tokenize an input string.
        Returns a list of Token objects.
        """
        self.text = text.upper()
        self.pos = -1
        self.current_char = None
        self.advance()
        
        tokens = []

        while self.current_char is not None:
            # Ignore whitespace characters
            if self.current_char in ' \t\n\r':
                self.advance()
            
            # Single-character tokens
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

            # Identifiers, keywords, or boolean literals
            elif self.current_char in LETTERS or self.current_char == '_':
                tokens.append(self.make_identifier())

            else:
                # Unknown character
                raise Exception(f"Illegal character '{self.current_char}' at position {self.pos}")

        return tokens

    def make_identifier(self):
        """
        Build a multi-character identifier or keyword.
        Accepts letters, digits, and underscores.
        Checks if the result is a boolean literal or keyword.
        """
        result = ''
        while self.current_char is not None and (self.current_char in LETTERS or self.current_char == '_' or self.current_char in DIGITS):
            result += self.current_char
            self.advance()

        upper_result = result.upper()   # Case-insensitive comparison

        # Boolean literals
        if upper_result in ("TRUE", "FALSE", "UNKNOWN"):
            return Token(TT_TRUTH_VALUE, upper_result)
        # Language keywords (IF, THEN, AND, etc.)
        elif upper_result in KEYWORDS:
            return Token(TT_KEYWORD, upper_result)
        # Otherwise, it's a user-defined identifier
        else:
            return Token(TT_IDENTIFIER, result)