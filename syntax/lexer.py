# logos/syntax/lexer.py

import re
from collections import namedtuple

# Token definition
Token = namedtuple("Token", ["type", "value", "line", "column"])

# Reserved keywords (case-insensitive)
KEYWORDS = {
    "TRUE", "FALSE", "UNKNOWN",
    "IF", "ELIF", "ELSE",
    "FOR", "IN", "WHILE", "DEF", "RETURN",
    "CASE", "OF", "END",
    "ENTITY", "PREDICATE", "RELATION", "TEMPORAL_RELATION",
    "TIME_INTERVAL", "RELATION_CONTEXT", "QUANTIFIED_RELATION",
    "SAVE_ONTOLOGY", "LOAD_ONTOLOGY", "QUERY", "ADD_ALIAS",
    "DESCRIBE_HIERARCHY", "ADD_INVERSE_PREDICATE",
    "AND", "OR", "NOT", "EXISTS", "FORALL"
}

# Token regex patterns
TOKEN_SPECIFICATION = [
    # Comments
    ("MCOMMENT", r"/\*[\s\S]*?\*/"),
    ("SCOMMENT", r"#.*"),

    # Strings
    ("STRING", r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\''),

    # Numbers (integers and floats)
    ("NUMBER", r"\d+(\.\d+)?"),

    # Operators
    ("OPERATOR", r"\+|\-|\*{1,2}|\/|%|==|!=|>=|<=|>|<|="),

    # Delimiters
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("COMMA", r","),
    ("COLON", r":"),
    ("SEMICOLON", r";"),

    # Set literal start
    ("LSET", r"<"),
    ("RSET", r">"),

    # Identifiers and Entities/Predicates
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),

    # Newlines
    ("NEWLINE", r"\n"),

    # Skip spaces and tabs
    ("SKIP", r"[ \t]+"),

    # Any other character
    ("MISMATCH", r"."),
]

# Compile regex
TOK_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION)
TOK_REGEX_COMPILED = re.compile(TOK_REGEX, re.IGNORECASE)


def tokenize(code):
    """
    Token generator for Logos source code.
    Yields Token(type, value, line, column)
    """
    line_num = 1
    line_start = 0

    # mo: match object
    for mo in TOK_REGEX_COMPILED.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == "SKIP":
            continue
        elif kind in ("SCOMMENT", "MCOMMENT"):
            continue
        elif kind == "IDENTIFIER":
            if value.upper() in KEYWORDS:
                kind = value.upper()
        elif kind == "NUMBER":
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        elif kind == "STRING":
            value = value[1:-1]  # Remove quotes

        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character {value!r} at line {line_num} column {column}")

        yield Token(kind, value, line_num, column)


# Simple test
if __name__ == "__main__":
    code = '''
    # This is a comment
    x = 42
    y = <DOG, CAT, BIRD>
    IF ISDOG(FIDO) THEN BARK(FIDO)
    '''
    for token in tokenize(code):
        print(token)
