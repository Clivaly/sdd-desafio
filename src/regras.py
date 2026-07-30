from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

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


def rn006_duplicata(despesa: Despesa, despesas_anteriores: Sequence[Despesa]) -> Optional[ResultadoItem]:
    for anterior in despesas_anteriores:
        if (
            despesa.data == anterior.data
            and despesa.categoria == anterior.categoria
            and despesa.fornecedor == anterior.fornecedor
            and despesa.valor == anterior.valor
        ):
            return ResultadoItem(
                id=despesa.id,
                categoria=despesa.categoria,
                valor_lancado=despesa.valor,
                valor_reembolsado=Decimal("0.00"),
                status="recusado",
                motivo="duplicata",
                regras_aplicadas=["RN-006"],
            )
    return None


def rn004_nota_fiscal_obrigatoria(despesa: Despesa) -> Optional[ResultadoItem]:
    if despesa.valor > Decimal("100.00") and not despesa.tem_nota_fiscal:
        return ResultadoItem(
            id=despesa.id,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="recusado",
            motivo="nota fiscal obrigatória ausente",
            regras_aplicadas=["RN-004"],
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


def rn009_valor_negativo_ignorado(despesa: Despesa) -> Optional[ResultadoItem]:
    if despesa.valor < Decimal("0.00"):
        return ResultadoItem(
            id=despesa.id,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="ignorado",
            motivo="estorno",
            regras_aplicadas=["RN-009"],
        )
    return None
