from code_base import Variable
from .estruturas import Ramo

def verificar_fechamento(ramo: Ramo) -> bool:
    """Devolve um valor booleano indicando se o ramo fornecido está fechado."""
    num_formulas = len(ramo.formulas)
    for i in range(num_formulas):
        for j in range(i + 1, num_formulas):
            f1 = ramo.formulas[i]
            f2 = ramo.formulas[j]
            if f1.formula.is_identical(f2.formula):
                if f1.marca != f2.marca:
                    return True
    return False

def extrair_contraexemplo(ramo: Ramo) -> dict:
    """Extrai do ramo um contraexemplo."""
    contraexemplo = {}
    for f in ramo.formulas:
        if isinstance(f.formula, Variable):
            var_name = f.formula.name
            contraexemplo[var_name] = f.marca
    return contraexemplo