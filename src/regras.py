from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .modelos import Despesa, ResultadoItem
from .politica import Politica


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
