from .ast_nodes import *

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