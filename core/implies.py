from .truth import TruthState, TruthValue
from .relation import Relation

class ImpliesRelation(Relation):
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent

    def infer_consequent_truth(self):
        if self.consequent.truth is not None:
            return self.consequent.truth_value

        if self.truth == TruthValue.FALSE:
            return TruthValue(TruthState.UNKNOWN)

        if self.antecedent.truth == TruthValue.TRUE and self.truth == TruthValue.TRUE:
            return TruthValue(TruthState.TRUE)

        if self.antecedent.truth == TruthValue.FALSE:
            return TruthValue(TruthState.UNKNOWN)

        return TruthValue(TruthState.UNKNOWN)

    def __repr__(self):
        return f"IMPLIES({self.antecedent} → {self.consequent}): {self.truth_value}"