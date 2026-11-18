
from dataclasses import dataclass
from typing import Iterable

if __package__:
    from .estruturas import EstadoTableau, EventoHistorico, FormulaMarcada, Ramo
else:
    from estruturas import EstadoTableau, EventoHistorico, FormulaMarcada, Ramo


@dataclass
class RegistroHistorico(EventoHistorico):
    """Evento com os detalhes da expansão, compatível com EventoHistorico.
    """

    id_formula: int | None = None
    formula: str | None = None
    expansao: str | None = None
    nome_regra: str | None = None
    geradas: tuple[tuple[str, ...], ...] = ()


def _formula_marcada(formula: FormulaMarcada) -> str:
    marca = "T" if formula.marca else "F"
    return f"{marca}({formula.formula})"


def registrar_evento(
    estado: EstadoTableau,
    ramo: Ramo,
    acao: str,
    *,
    formula: FormulaMarcada | None = None,
    nome_regra: str | None = None,
    expansao: str | None = None,
    geradas: Iterable[Iterable[FormulaMarcada]] | None = None,
) -> RegistroHistorico:
    """Acrescenta um evento ao histórico global e devolve o registro.
    """
    if acao == "expansao" and (formula is None or not nome_regra):
        raise ValueError("Uma expansão precisa de fórmula e nome da regra.")

    alternativas = () if geradas is None else tuple(
        tuple(_formula_marcada(item) for item in alternativa)
        for alternativa in geradas
    )

    evento = RegistroHistorico(
        id_ramo=ramo.id,
        acao=acao,
        id_formula=formula.id if formula is not None else None,
        formula=_formula_marcada(formula) if formula is not None else None,
        expansao=expansao,
        nome_regra=nome_regra,
        geradas=alternativas,
    )
    estado.historico.append(evento)
    return evento


def sequencia_regras(
    historico: Iterable[EventoHistorico],
) -> list[tuple[str, str]]:
    """Devolve [(regra, fórmula), ...], como solicitado no enunciado.

    Eventos de controle da busca não são aplicações de regras de expansão.
    """
    return [
        (evento.nome_regra, evento.formula)
        for evento in historico
        if isinstance(evento, RegistroHistorico)
        and evento.acao == "expansao"
        and evento.nome_regra is not None
        and evento.formula is not None
    ]


def formatar_historico(historico: Iterable[EventoHistorico]) -> str:
    """Produz uma descrição numerada dos eventos, na ordem de registro."""
    linhas = []
    for numero, evento in enumerate(historico, start=1):
        linha = f"{numero}. Ramo {evento.id_ramo}: {evento.acao}"
        if isinstance(evento, RegistroHistorico):
            if evento.nome_regra is not None:
                linha += f" | regra: {evento.nome_regra}"
            if evento.expansao is not None:
                linha += f" | tipo: {evento.expansao}"
            if evento.formula is not None:
                linha += f" | fórmula #{evento.id_formula}: {evento.formula}"
            if evento.geradas:
                alternativas = [
                    "[" + ", ".join(alternativa) + "]"
                    for alternativa in evento.geradas
                ]
                linha += " | geradas: " + " ou ".join(alternativas)
        linhas.append(linha)
    return "\n".join(linhas) if linhas else "Histórico vazio."
