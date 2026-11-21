from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from typing import Iterable

@dataclass
class FormulaMarcada:
    id: int=field(init=False)
    formula: Any
    marca: bool
    
    _contador_id = 0
    def __post_init__(self):
        FormulaMarcada._contador_id +=1 
        self.id = FormulaMarcada._contador_id

@dataclass
class Ramo:
    id: int=field(init=False)
    formulas: list[FormulaMarcada] = field(default_factory=list)
    expandidos: set[int] = field(default_factory=set)

    _contador_id = 0
    def __post_init__(self):
        Ramo._contador_id +=1 
        self.id = Ramo._contador_id

@dataclass
class EventoHistorico:
    id_ramo: int
    acao: str
    id_formula: int
    formula: FormulaMarcada | None = None,
    nome_regra: str | None = None,
    expansao: str | None = None,
    geradas: Iterable[Iterable[FormulaMarcada]] | None = None,

@dataclass
class EstadoTableau:
    ramo_atual: Ramo | None = None
    ramos_pendentes: list[Ramo] = field(default_factory=list)
    historico: list[EventoHistorico] = field(default_factory=list)

@dataclass 
class ResultadoTableau:
    valido: bool
    historico: list[EventoHistorico]
    contraexemplo: dict[str, bool] | None = None
    ramo_aberto: Ramo | None = None