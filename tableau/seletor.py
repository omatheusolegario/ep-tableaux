from code_base import And, Or, Implies, Not
from .estruturas import FormulaMarcada, Ramo


def classificar(formula: FormulaMarcada) -> str | None:
    f = formula.formula
    marca = formula.marca

    if isinstance(f, And):
        return "alpha_and" if marca else "beta_and"
    if isinstance(f, Or):
        return "beta_or" if marca else "alpha_or"
    if isinstance(f, Implies):
        return "beta_implies" if marca else "alpha_implies"
    if isinstance(f, Not):
        return "alpha_not" if marca else "beta_not"
    return None


def _tamanho(proposicao) -> int:
    total = 1
    for filho in proposicao.children:
        total += _tamanho(filho)
    return total


def selecionar_formula(ramo: Ramo) -> tuple[FormulaMarcada | None, str | None]:
    melhor_beta = None

    for index, formula in enumerate(ramo.formulas):
        if index in ramo.expandidos:
            continue

        tipo = classificar(formula)

        if tipo is not None and tipo[0].startswith("a"):
            return formula, tipo

        if tipo is not None and tipo[0].startswith("b"):
            if melhor_beta is None or _tamanho(formula.formula) < _tamanho(melhor_beta.formula):
                melhor_beta = formula

    return melhor_beta, tipo
