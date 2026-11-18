from code_base import And, Or, Implies, Not
from .estruturas import FormulaMarcada, Ramo


def classificar(formula: FormulaMarcada) -> str | None:
    f = formula.formula
    marca = formula.marca

    if isinstance(f, And):
        return "alpha" if marca else "beta"
    if isinstance(f, Or):
        return "beta" if marca else "alpha"
    if isinstance(f, Implies):
        return "beta" if marca else "alpha"
    if isinstance(f, Not):
        return "alpha"
    return None


def _tamanho(proposicao) -> int:
    total = 1
    for filho in proposicao.children:
        total += _tamanho(filho)
    return total


def selecionar_formula(ramo: Ramo) -> FormulaMarcada | None:
    melhor_beta = None

    for formula in ramo.formulas:
        if formula.id in ramo.expandidos:
            continue

        tipo = classificar(formula)

        if tipo == "alpha":
            return formula

        if tipo == "beta":
            if melhor_beta is None or _tamanho(formula.formula) < _tamanho(melhor_beta.formula):
                melhor_beta = formula

    return melhor_beta
