from datetime import date
from decimal import Decimal
from pathlib import Path

from src.modelos import Colaborador, Despesa, Periodo
from src.motor import calcular_resultado
from src.politica import DEFAULT_POLITICA, Politica


def test_politica_valores_batem_com_spec():
    assert DEFAULT_POLITICA.limite_alimentacao_diaria == Decimal("60.00")
    assert DEFAULT_POLITICA.limite_transporte_urbano_diario == Decimal("80.00")
    assert DEFAULT_POLITICA.limite_hospedagem_diaria == Decimal("250.00")
    assert DEFAULT_POLITICA.valor_nota_fiscal_obrigatoria == Decimal("100.00")
    assert DEFAULT_POLITICA.multiplicador_viagem == Decimal("1.50")


def test_politica_por_centro_custo_carrega_limites_externos():
    envelope_path = Path("envelope/politica-v4.json")
    politica = Politica.carregar_por_centro_custo(envelope_path, "CC-COMERCIAL")

    assert politica.limite_alimentacao_diaria == Decimal("90.00")
    assert politica.limite_transporte_urbano_diario == Decimal("150.00")
    assert politica.limite_hospedagem_diaria == Decimal("400.00")
    assert politica.valor_nota_fiscal_obrigatoria == Decimal("100.00")
    assert politica.multiplicador_viagem == Decimal("1.50")
    assert "representacao" in politica.categorias_reembolsaveis


def test_representacao_reembolsavel_em_cc_comercial():
    envelope_path = Path("envelope/politica-v4.json")
    politica = Politica.carregar_por_centro_custo(envelope_path, "CC-COMERCIAL")
    colaborador = Colaborador(id="c-1", nome="Teste", centro_custo="CC-COMERCIAL")
    periodo = Periodo(competencia="2026-07", inicio=date(2026, 7, 1), fim=date(2026, 7, 31))
    despesas = [
        Despesa(
            id="t18-001",
            data=date(2026, 7, 14),
            categoria="representacao",
            descricao="Almoço com cliente",
            fornecedor="Restaurante",
            valor=Decimal("120.00"),
            tem_nota_fiscal=True,
        )
    ]

    resultado = calcular_resultado(colaborador, periodo, despesas, politica)

    assert resultado.itens[0].status == "aprovado"
    assert resultado.itens[0].valor_reembolsado == Decimal("120.00")
    assert resultado.itens[0].regras_aplicadas == ["RN-011"]


def test_hospedagem_cc_eng_plataforma_recusa():
    envelope_path = Path("envelope/politica-v4.json")
    politica = Politica.carregar_por_centro_custo(envelope_path, "CC-ENG-PLATAFORMA")
    colaborador = Colaborador(id="c-2", nome="Teste", centro_custo="CC-ENG-PLATAFORMA")
    periodo = Periodo(competencia="2026-07", inicio=date(2026, 7, 1), fim=date(2026, 7, 31))
    despesas = [
        Despesa(
            id="t18-002",
            data=date(2026, 7, 10),
            categoria="hospedagem",
            descricao="Hospedagem interna",
            fornecedor="Hotel",
            valor=Decimal("150.00"),
            tem_nota_fiscal=True,
        )
    ]

    resultado = calcular_resultado(colaborador, periodo, despesas, politica)

    assert resultado.itens[0].status == "recusado"
    assert resultado.itens[0].valor_reembolsado == Decimal("0.00")
    assert resultado.itens[0].regras_aplicadas == ["RN-010"]
    assert resultado.itens[0].motivo == "excedente do limite diário de hospedagem"


def test_centro_desconhecido_usa_padrao():
    envelope_path = Path("envelope/politica-v4.json")
    politica = Politica.carregar_por_centro_custo(envelope_path, "CC-SUPORTE-N2")

    assert politica.limite_alimentacao_diaria == Decimal("60.00")
    assert politica.limite_transporte_urbano_diario == Decimal("80.00")
    assert politica.limite_hospedagem_diaria == Decimal("250.00")
    assert politica.valor_nota_fiscal_obrigatoria == Decimal("100.00")
    assert politica.multiplicador_viagem == Decimal("1.50")
    assert politica.categorias_reembolsaveis == {"alimentacao", "transporte_urbano", "hospedagem"}
