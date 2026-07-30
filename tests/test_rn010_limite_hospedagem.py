from datetime import date
from decimal import Decimal

from src.modelos import Despesa
from src.politica import Politica
from src.regras import rn010_limite_por_diaria_hospedagem


def test_rn010_limite_por_diaria_hospedagem_aprovado_total():
    despesa = Despesa(
        id="d10",
        data=date(2024, 6, 3),
        categoria="hospedagem",
        descricao="Hospedagem padrão",
        fornecedor="Hotel",
        valor=Decimal("200.00"),
        tem_nota_fiscal=True,
    )
    resultado = rn010_limite_por_diaria_hospedagem(despesa, Politica())

    assert resultado.valor_reembolsado == Decimal("200.00")
    assert resultado.status == "aprovado"
    assert resultado.motivo == "dentro do limite diário de hospedagem"


def test_rn010_limite_por_diaria_hospedagem_parcial():
    despesa = Despesa(
        id="d11",
        data=date(2024, 6, 3),
        categoria="hospedagem",
        descricao="Hospedagem longa",
        fornecedor="Resort",
        valor=Decimal("480.00"),
        tem_nota_fiscal=True,
    )
    resultado = rn010_limite_por_diaria_hospedagem(despesa, Politica())

    assert resultado.valor_reembolsado == Decimal("250.00")
    assert resultado.status == "parcial"
    assert resultado.motivo == "dentro do limite diário de hospedagem"


def test_rn010_limite_por_diaria_hospedagem_excede_limite_total():
    despesa = Despesa(
        id="d12",
        data=date(2024, 6, 3),
        categoria="hospedagem",
        descricao="Suite VIP",
        fornecedor="Hotel Luxo",
        valor=Decimal("300.00"),
        tem_nota_fiscal=True,
    )
    resultado = rn010_limite_por_diaria_hospedagem(despesa, Politica())

    assert resultado.valor_reembolsado == Decimal("250.00")
    assert resultado.status == "parcial"
    assert resultado.motivo == "dentro do limite diário de hospedagem"
