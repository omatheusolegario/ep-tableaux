from inicializador import iniciar
from seletor import selecionar_formula
from regras import aplicar_regra, criar_ramos
from verificador import verificar_fechamento, verificar_saturacao, obter_contraexemplo, criar_resultado
from historico import registrar_evento

def resolver(argumento):
    ramo_inicial = iniciar(argumento)
    pilha = [ramo_inicial]
    while pilha:
        ramo = pilha.pop()

        if verificar_fechamento(ramo):
            registrar_evento(ramo, "fechamento")
            continue

        formula = selecionar_formula(ramo)
        if formula is None:
            contraexemplo = obter_contraexemplo(ramo)
            return criar_resultado(False, contraexemplo)

        ramo.expandidos.add(formula.id)

        alternativas = aplicar_regra(formula) #devolve uma lista de listas: [[alpha]] ou [[beta 1], [beta 2]]
        novos_ramos = criar_ramos(ramo, alternativas)

        for novo_ramo in reversed(novos_ramos):
            pilha.append(novo_ramo)

    return criar_resultado(True)