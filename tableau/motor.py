from .estruturas import EstadoTableau, Ramo, ResultadoTableau
from .historico import registrar_evento
from .inicializador import iniciar
from .seletor import selecionar_formula
from .regras import aplicar_regra
from .verificador import verificar_fechamento, extrair_contraexemplo

def resolver(argumento):
    """Testa premissas T e conclusão F; para no primeiro ramo aberto saturado."""
    estado = EstadoTableau(ramos_pendentes=[iniciar(argumento)])
    primeiro_ramo = True

    while estado.ramos_pendentes:
        ramo = estado.ramos_pendentes.pop()
        estado.ramo_atual = ramo
        if not primeiro_ramo:
            registrar_evento(estado, ramo, "retorno")
        primeiro_ramo = False

        # Expansões lineares permanecem no mesmo ramo.
        while True:
            if verificar_fechamento(ramo):
                registrar_evento(estado, ramo, "fechamento")
                break

            formula = selecionar_formula(ramo)
            if formula[0] is None:
                registrar_evento(estado, ramo, "saturacao")
                return ResultadoTableau(
                    valido=False,
                    historico=estado.historico,
                    contraexemplo=extrair_contraexemplo(ramo),
                    ramo_aberto=ramo,
                )
            if formula[0].id in ramo.expandidos:
                raise ValueError("O seletor devolveu uma fórmula já expandida.")

            alternativas = aplicar_regra(formula)
            if len(alternativas) not in (1, 2):
                raise ValueError("Uma regra deve gerar uma ou duas alternativas.")
            registrar_evento(
                estado, ramo, "expansao", formula=formula[0],
                nome_regra=formula[1], expansao="alpha" if formula[1].startswith("a") else "beta", geradas=alternativas,
            )
            ramo.expandidos.add(formula[0].id)

            if formula[1].startswith("a"):
                ramo.formulas.extend(alternativas[0])
                continue

            filhos = [
                Ramo(
                    formulas=ramo.formulas + alternativa,
                    expandidos=ramo.expandidos,
                )
                for alternativa in alternativas
            ]
            # A pilha visita a primeira alternativa antes da segunda.
            estado.ramos_pendentes.extend(reversed(filhos))
            break

    estado.ramo_atual = None
    return ResultadoTableau(valido=True, historico=estado.historico)