from .ast_nodes import *

# --------------------------
# Three-valued logical system
# --------------------------
# Each function here takes one or two TruthValue objects
# (TRUE, FALSE, or UNKNOWN) and returns the logical result
# as a new TruthValue object.
#
# This extends classical Boolean logic to handle UNKNOWN values,
# which allows reasoning in cases where information is incomplete.

def logical_not(value):
    if value == TruthValue("TRUE"):
        return TruthValue("FALSE")
    elif value == TruthValue("FALSE"):
        return TruthValue("TRUE")
    return TruthValue("UNKNOWN")

def logical_and(a, b):
    if a == TruthValue("TRUE") and b == TruthValue("TRUE"):
        return TruthValue("TRUE")
    elif a == TruthValue("FALSE") or b == TruthValue("FALSE"):
        return TruthValue("FALSE")
    return TruthValue("UNKNOWN")

def logical_or(a, b):
    if a == TruthValue("TRUE") or b == TruthValue("TRUE"):
        return TruthValue("TRUE")
    elif a == TruthValue("FALSE") and b == TruthValue("FALSE"):
        return TruthValue("FALSE")
    return TruthValue("UNKNOWN")

def logical_nand(a, b):
    if a == TruthValue("FALSE") or b == TruthValue("FALSE"):
        return TruthValue("TRUE")
    elif a == TruthValue("TRUE") and b == TruthValue("TRUE"):
        return TruthValue("FALSE")
    return TruthValue("UNKNOWN")

def logical_nor(a, b):
    if a == TruthValue("FALSE") and b == TruthValue("FALSE"):
        return TruthValue("TRUE")
    elif a == TruthValue("TRUE") or b == TruthValue("TRUE"):
        return TruthValue("FALSE")
    return TruthValue("UNKNOWN")

def logical_xor(a, b):
    if (a == TruthValue("TRUE") or b == TruthValue("TRUE")) and not (a == TruthValue("TRUE") and b == TruthValue("TRUE")):
        return TruthValue("TRUE")
    elif (a == TruthValue("TRUE") and b == TruthValue("TRUE")) or (a == TruthValue("FALSE") and b == TruthValue("FALSE")):
        return TruthValue("FALSE")
    return TruthValue("UNKNOWN")

def logical_xnor(a, b):
    if (a == TruthValue("TRUE") and b == TruthValue("TRUE")) or (a == TruthValue("FALSE") and b == TruthValue("FALSE")):
        return TruthValue("TRUE")
    elif (a == TruthValue("TRUE") or b == TruthValue("TRUE")):
        return TruthValue("FALSE")
    return TruthValue("UNKNOWN")

# ------------------------------
# Operator lookup dictionary
# ------------------------------
LOGICAL_OPERATORS = {
    "NOT":  (logical_not, 1),   # unary operator, takes 1 argument
    "AND":  (logical_and, 2),   # binary operator, takes 2 arguments
    "OR":   (logical_or, 2),
    "NAND": (logical_nand, 2),
    "NOR":  (logical_nor, 2),
    "XOR":  (logical_xor, 2),
    "XNOR": (logical_xnor, 2),
}