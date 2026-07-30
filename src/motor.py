from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from .modelos import Colaborador, Despesa, Periodo, Resultado, ResultadoItem
from .politica import Politica
from .regras import (
    rn001_limite_diario_alimentacao,
    rn002_limite_diario_transporte,
    rn004_nota_fiscal_obrigatoria,
    rn005_ampliacao_limites_viagem,
    rn006_duplicata,
    rn007_fora_periodo_competencia,
    rn008_categoria_fora_politica,
    rn009_valor_negativo_ignorado,
    rn010_limite_por_diaria_hospedagem,
    rn012_taxa_cambio_indisponivel,
)


def _total_valor_lancado(despesas: Sequence[Despesa]) -> Decimal:
    return sum((despesa.valor for despesa in despesas if despesa.valor > Decimal("0.00")), Decimal("0.00"))


def _total_reembolsavel(itens: Sequence[ResultadoItem]) -> Decimal:
    return sum((item.valor_reembolsado for item in itens), Decimal("0.00"))


def _processar_despesa(
    despesa: Despesa,
    periodo: Periodo,
    itens_anteriores: Sequence[ResultadoItem],
    despesas_anteriores: Sequence[Despesa],
    politica: Politica,
) -> ResultadoItem:
    regra = rn008_categoria_fora_politica(despesa, politica)
    if regra is not None:
        return regra

    regra = rn007_fora_periodo_competencia(despesa, periodo)
    if regra is not None:
        return regra

    regra = rn009_valor_negativo_ignorado(despesa)
    if regra is not None:
        return regra

    regra = rn006_duplicata(despesa, despesas_anteriores)
    if regra is not None:
        return regra

    regra = rn012_taxa_cambio_indisponivel(despesa)
    if regra is not None:
        return regra

    regra = rn004_nota_fiscal_obrigatoria(despesa)
    if regra is not None:
        return regra

    regra = rn001_limite_diario_alimentacao(despesa, itens_anteriores, politica)
    if regra is not None:
        return regra

    regra = rn002_limite_diario_transporte(despesa, itens_anteriores, politica)
    if regra is not None:
        return regra

    regra = rn010_limite_por_diaria_hospedagem(despesa, politica)
    if regra is not None:
        return regra

    regra = rn005_ampliacao_limites_viagem(despesa, politica)
    if regra is not None:
        return regra

    raise RuntimeError(f"Nenhuma regra decidiu o destino da despesa {despesa.id}")


def calcular_resultado(
    colaborador: Colaborador,
    periodo: Periodo,
    despesas: Sequence[Despesa],
    politica: Politica = Politica(),
) -> Resultado:
    itens: list[ResultadoItem] = []
    despesas_anteriores: list[Despesa] = []

    for despesa in despesas:
        item = _processar_despesa(despesa, periodo, itens, despesas_anteriores, politica)
        itens.append(item)
        despesas_anteriores.append(despesa)

    total_valor_lancado = _total_valor_lancado(despesas)
    total_reembolsavel = _total_reembolsavel(itens)

    resumo = {
        "total_despesas": len(despesas),
        "total_valor_lancado": total_valor_lancado,
        "total_reembolsavel": total_reembolsavel,
        "total_recusado": total_valor_lancado - total_reembolsavel,
    }

    return Resultado(
        colaborador=colaborador,
        periodo=periodo,
        resumo=resumo,
        itens=itens,
    )
