from code_base import ArgumentForm
from .estruturas import FormulaMarcada, Ramo

def iniciar(argument: ArgumentForm) -> Ramo:
    """Recebe um sequente, marca como verdadeira as premissas e como falsa a conclusão, retorna um ramo."""
    premissas = argument.premises;
    conclusao = argument.conclusion;
    formulas = []

    for premissa in premissas:
        formulas.append(FormulaMarcada(premissa, True))
    
    formulas.append(FormulaMarcada(conclusao, False))

    return Ramo(formulas, set())