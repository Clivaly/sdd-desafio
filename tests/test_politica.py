from decimal import Decimal
from pathlib import Path

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


def test_politica_fallback_para_padrao_quando_centro_desconhecido():
    envelope_path = Path("envelope/politica-v4.json")
    politica = Politica.carregar_por_centro_custo(envelope_path, "CC-SUPORTE-N2")

    assert politica.limite_alimentacao_diaria == Decimal("60.00")
    assert politica.limite_transporte_urbano_diario == Decimal("80.00")
    assert politica.limite_hospedagem_diaria == Decimal("250.00")
    assert politica.valor_nota_fiscal_obrigatoria == Decimal("100.00")
    assert politica.multiplicador_viagem == Decimal("1.50")
    assert politica.categorias_reembolsaveis == {"alimentacao", "transporte_urbano", "hospedagem"}
