from .estruturas import EstadoTableau, Ramo, ResultadoTableau
from .historico import registrar_evento
from .inicializador import iniciar
from .seletor import selecionar_formula
from .regras import aplicar_regra
from .verificador import verificar_fechamento, extrair_contraexemplo

def resolver(argumento):
    """Testa premissas T e conclusão F; para no primeiro ramo aberto saturado."""

    # Inicia o tableau marcando com True as premissas e False a conclusão
    estado = EstadoTableau(ramos_pendentes=[iniciar(argumento)])
    primeiro_ramo = True

    # Enquanto existirem ramos na pilha não expandidos
    while estado.ramos_pendentes:
        # Tira um ramo do topo da pilha e usa ele como atual
        ramo = estado.ramos_pendentes.pop()
        estado.ramo_atual = ramo
        if not primeiro_ramo:
            registrar_evento(estado, ramo, "retorno")
        primeiro_ramo = False

        # Expansões alpha permanecem no mesmo ramo
        while True:
    
            if verificar_fechamento(ramo):
                registrar_evento(estado, ramo, "fechamento")
                break

            # Seleciona a melhor formula para ser expandida (pode ser nenhuma == ramo saturado)
            formula = selecionar_formula(ramo)
            if formula[0] is None:
                registrar_evento(estado, ramo, "saturacao")
                return ResultadoTableau(
                    valido=False,
                    historico=estado.historico,
                    contraexemplo=extrair_contraexemplo(ramo),
                    ramo_aberto=ramo,
                )

            # Expande a formula selecionada em uma lista de listas de FormulaMarcada
            alternativas = aplicar_regra(formula)

            registrar_evento(
                estado, ramo, "expansao", formula=formula[0],
                nome_regra=formula[1], expansao="alpha" if formula[1].startswith("a") else "beta", geradas=alternativas,
            )

            # Marca a formula como expandida
            ramo.expandidos.add(formula[0].id)

            # Se é formula alpha, continua no While == permanece no mesmo ramo
            if formula[1].startswith("a"):
                ramo.formulas.extend(alternativas[0])
                continue

            # Se é formula beta, cria dois ramos copiando o que tinha no ramo pai e adicionando as formulas expandidas
            filhos = [
                Ramo(
                    formulas=ramo.formulas.copy() + alternativa,
                    expandidos=ramo.expandidos.copy(),
                )
                for alternativa in alternativas
            ]

            # Coloca invertido para que na pilha a ordem fique usual
            estado.ramos_pendentes.extend(reversed(filhos))
            break

    # Se chegou aqui é porque é valida, sem ramos abertos, todos fechados com contradição
    estado.ramo_atual = None
    return ResultadoTableau(valido=True, historico=estado.historico)