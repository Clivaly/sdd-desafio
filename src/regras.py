from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

from .modelos import Despesa, Periodo, ResultadoItem
from .politica import Politica


def _soma_reembolsado_anteriores(despesa: Despesa, itens_anteriores: Sequence[ResultadoItem]) -> Decimal:
    return sum(
        item.valor_reembolsado
        for item in itens_anteriores
        if item.categoria == despesa.categoria and item.data == despesa.data
    )


def _construir_resultado_limite_diario(
    despesa: Despesa,
    valor_reembolsado: Decimal,
    limite_label: str,
    regra_id: str,
) -> ResultadoItem:
    if valor_reembolsado == despesa.valor:
        status = "aprovado"
        motivo = f"dentro do limite diário de {limite_label}"
    elif valor_reembolsado == Decimal("0.00"):
        status = "recusado"
        motivo = f"excedente do limite diário de {limite_label}"
    else:
        status = "parcial"
        motivo = f"dentro do limite diário de {limite_label}"

    return ResultadoItem(
        id=despesa.id,
        data=despesa.data,
        categoria=despesa.categoria,
        valor_lancado=despesa.valor,
        valor_reembolsado=valor_reembolsado,
        status=status,
        motivo=motivo,
        regras_aplicadas=[regra_id],
    )


def _aplicar_limite_por_categoria(
    despesa: Despesa,
    politica: Politica,
    descricao_categoria: str,
    regra_id: str,
    itens_anteriores: Sequence[ResultadoItem] | None = None,
) -> Optional[ResultadoItem]:
    if despesa.categoria not in politica.categorias_reembolsaveis:
        return None

    limite = politica.limite_para_categoria(despesa.categoria)
    if politica.periodicidade_para_categoria(despesa.categoria) == "dia":
        consumido = _soma_reembolsado_anteriores(despesa, itens_anteriores or [])
        disponivel = max(Decimal("0.00"), limite - consumido)
        valor_reembolsado = min(despesa.valor, disponivel)
    else:
        valor_reembolsado = min(despesa.valor, limite)

    return _construir_resultado_limite_diario(
        despesa,
        valor_reembolsado,
        descricao_categoria,
        regra_id,
    )


def rn001_limite_diario_alimentacao(
    despesa: Despesa,
    itens_anteriores: Sequence[ResultadoItem],
    politica: Politica,
) -> Optional[ResultadoItem]:
    if despesa.categoria != "alimentacao":
        return None

    return _aplicar_limite_por_categoria(
        despesa,
        politica,
        "alimentacao",
        "RN-001",
        itens_anteriores,
    )


def rn002_limite_diario_transporte(
    despesa: Despesa,
    itens_anteriores: Sequence[ResultadoItem],
    politica: Politica,
) -> Optional[ResultadoItem]:
    if despesa.categoria != "transporte_urbano":
        return None

    return _aplicar_limite_por_categoria(
        despesa,
        politica,
        "transporte urbano",
        "RN-002",
        itens_anteriores,
    )


def rn010_limite_por_diaria_hospedagem(
    despesa: Despesa,
    politica: Politica,
) -> Optional[ResultadoItem]:
    if despesa.categoria != "hospedagem":
        return None

    return _aplicar_limite_por_categoria(
        despesa,
        politica,
        "hospedagem",
        "RN-010",
    )


def rn011_limite_categoria_dinamica(
    despesa: Despesa,
    itens_anteriores: Sequence[ResultadoItem],
    politica: Politica,
) -> Optional[ResultadoItem]:
    if despesa.categoria in {"alimentacao", "transporte_urbano", "hospedagem"}:
        return None
    if despesa.categoria not in politica.categorias_reembolsaveis:
        return None

    descricao_categoria = despesa.categoria.replace("_", " ")
    regra_id = "RN-011"

    return _aplicar_limite_por_categoria(
        despesa,
        politica,
        descricao_categoria,
        regra_id,
        itens_anteriores,
    )


def rn005_ampliacao_limites_viagem(
    despesa: Despesa,
    politica: Politica,
) -> Optional[ResultadoItem]:
    # Esta regra existe na política, mas a entrada não traz nenhum campo que
    # indique se o colaborador está em viagem. Portanto, ela não altera nenhum
    # resultado nesta versão.
    return None


def rn007_fora_periodo_competencia(despesa: Despesa, periodo: Periodo) -> Optional[ResultadoItem]:
    if despesa.data < periodo.inicio or despesa.data > periodo.fim:
        return ResultadoItem(
            id=despesa.id,
            data=despesa.data,
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
                data=despesa.data,
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
            data=despesa.data,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="recusado",
            motivo="nota fiscal obrigatória ausente",
            regras_aplicadas=["RN-004"],
        )
    return None


def rn012_taxa_cambio_indisponivel(despesa: Despesa) -> Optional[ResultadoItem]:
    if despesa.moeda != "BRL" and despesa.taxa_de_cambio is None:
        return ResultadoItem(
            id=despesa.id,
            data=despesa.data,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="recusado",
            motivo="taxa de câmbio indisponível",
            regras_aplicadas=["RN-012"],
        )
    return None


def rn008_categoria_fora_politica(despesa: Despesa, politica: Politica) -> Optional[ResultadoItem]:
    if despesa.categoria not in politica.categorias_reembolsaveis:
        return ResultadoItem(
            id=despesa.id,
            data=despesa.data,
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
            data=despesa.data,
            categoria=despesa.categoria,
            valor_lancado=despesa.valor,
            valor_reembolsado=Decimal("0.00"),
            status="ignorado",
            motivo="estorno",
            regras_aplicadas=["RN-009"],
        )
    return None
