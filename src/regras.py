from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .modelos import Despesa, Periodo, ResultadoItem
from .politica import Politica


def rn007_fora_periodo_competencia(despesa: Despesa, periodo: Periodo) -> Optional[ResultadoItem]:
    if despesa.data < periodo.inicio or despesa.data > periodo.fim:
        return ResultadoItem(
            id=despesa.id,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="recusado",
            motivo="fora do período de competência",
            regras_aplicadas=["RN-007"],
        )
    return None


def rn008_categoria_fora_politica(despesa: Despesa, politica: Politica) -> Optional[ResultadoItem]:
    if despesa.categoria not in politica.categorias_reembolsaveis:
        return ResultadoItem(
            id=despesa.id,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="recusado",
            motivo="categoria fora da política",
            regras_aplicadas=["RN-008"],
        )
    return None
