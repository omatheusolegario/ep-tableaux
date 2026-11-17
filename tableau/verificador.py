from code_base_EP1 import Proposition, Variable, Constant

class FormulaMarcada:
    def __init__(self, marca: bool, formula: Proposition, id: int = None):
        self.marca = marca
        self.formula = formula
        self.id = id

    def __repr__(self):
        m = "T" if self.marca else "F"
        return f"{m}({self.formula})"

class Ramo:
    def __init__(self, formulas=None, id=0):
        self.id = id
        self.formulas = formulas if formulas is not None else []
        self.expandidos = set()

    def esta_fechado(self) -> bool:
        n = len(self.formulas)
        for i in range(n):
            for j in range(i + 1, n):
                f1 = self.formulas[i]
                f2 = self.formulas[j]
                if f1.formula.is_identical(f2.formula) or f1.formula.is_equivalent(f2.formula):
                    if f1.marca != f2.marca:
                        return True
        return False

    def esta_saturado(self) -> bool:
        for idx, fm in enumerate(self.formulas):
            if idx in self.expandidos:
                continue
            if not isinstance(fm.formula, (Variable, Constant)):
                return False
        return True
