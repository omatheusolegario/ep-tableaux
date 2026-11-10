from inicializador import iniciar
from seletor import selecionar_formula
from regras import aplicar_regra, criar_ramos
from verificador import verificar_fechamento, obter_contraexemplo
from historico import registrar_evento
from estruturas import *

def resolver(argumento):
    estado = EstadoTableau()
    ramo_inicial = iniciar(argumento)
    estado.ramos_pendentes.append(ramo_inicial)

    while estado.ramos_pendentes:

        estado.ramo_atual = estado.ramos_pendentes.pop()
        ramo = estado.ramo_atual

        if verificar_fechamento(ramo):
            registrar_evento(estado ,ramo, "fechamento")
            continue

        formula = selecionar_formula(ramo)
        if formula is None:
            contraexemplo = obter_contraexemplo(ramo)

            return ResultadoTableau(valido= False, historico = estado.historico, contraexemplo=contraexemplo, ramo_aberto=ramo)

        ramo.expandidos.add(formula.id)

        alternativas = aplicar_regra(formula) #devolve uma lista de listas: [[alpha]] ou [[beta 1], [beta 2]]
        novos_ramos = criar_ramos(ramo, alternativas)

        for novo_ramo in reversed(novos_ramos):
            estado.ramos_pendentes.append(novo_ramo)

    return ResultadoTableau(valido=True, historico=estado.historico)