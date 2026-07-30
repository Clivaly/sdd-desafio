from decimal import Decimal

from src.politica import DEFAULT_POLITICA


def test_politica_valores_batem_com_spec():
    assert DEFAULT_POLITICA.limite_alimentacao_diaria == Decimal("60.00")
    assert DEFAULT_POLITICA.limite_transporte_urbano_diario == Decimal("80.00")
    assert DEFAULT_POLITICA.limite_hospedagem_diaria == Decimal("250.00")
    assert DEFAULT_POLITICA.valor_nota_fiscal_obrigatoria == Decimal("100.00")
    assert DEFAULT_POLITICA.multiplicador_viagem == Decimal("1.50")
