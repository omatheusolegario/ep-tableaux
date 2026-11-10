from code_base import ArgumentForm
from estruturas import *

def iniciar(argument: ArgumentForm) -> Ramo:
    premissas = argument.premises;
    conclusao = argument.conclusion;
    formulas = []

    for premissa in premissas:
        formulas.append(FormulaMarcada(premissa, True))
    
    formulas.append(FormulaMarcada(conclusao, False))

    return Ramo(formulas, set())