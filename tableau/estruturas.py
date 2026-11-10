from dataclasses import dataclass, field
from enum import Enum
from typing import Any

@dataclass
class FormulaMarcada:
    id: int=field(init=False)
    _contador_id = 0
    def __post_init__(self, name, bases, dict, /, **kwds):
        FormulaMarcada._contador_id +=1 
        self.id = FormulaMarcada._contador_id
    formula: Any
    marca: bool
    

@dataclass
class Ramo:
    id: int=field(init=False)
    _contador_id = 0
    def __post_init__(self, name, bases, dict, /, **kwds):
        Ramo._contador_id +=1 
        self.id = Ramo._contador_id
    formulas: list[FormulaMarcada] = field(default_factory=list)
    expandidos: set[list] = field(default_factory=set)

@dataclass
class EventoHistorico:
    id_ramo: int
    acao: str

@dataclass
class EstadoTableau:
    ramo_atual: Ramo | None
    ramos_pendentes: list[Ramo] = field(default_factory=list)
    historico: list[EventoHistorico] = field(default_factory=list)
    id_proxima_formula: int = 1
    id_proximo_ramo: int = 1

@dataclass 
class ResultadoTableau:
    valido: bool
    historico: list[EventoHistorico]
    contraexemplo: dict[str, bool] | None = None
    ramo_aberto: Ramo |  None = None