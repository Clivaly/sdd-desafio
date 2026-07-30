from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Colaborador:
    id: str
    nome: str
    centro_custo: str


@dataclass(frozen=True)
class Periodo:
    competencia: str
    inicio: date
    fim: date


@dataclass(frozen=True)
class Despesa:
    id: str
    data: date
    categoria: str
    descricao: str
    fornecedor: str
    valor: Decimal
    moeda: str = "BRL"
    taxa_de_cambio: Optional[Decimal] = None
    tem_nota_fiscal: bool = False


@dataclass(frozen=True)
class ResultadoItem:
    id: str
    data: date
    categoria: str
    valor_lancado: Decimal
    valor_reembolsado: Decimal
    status: str
    motivo: str
    regras_aplicadas: List[str]


@dataclass(frozen=True)
class Resultado:
    colaborador: Colaborador
    periodo: Periodo
    resumo: Dict[str, Any]
    itens: List[ResultadoItem]
