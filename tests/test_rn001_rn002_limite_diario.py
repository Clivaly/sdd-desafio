from datetime import date
from decimal import Decimal

from src.modelos import Despesa, ResultadoItem
from src.politica import Politica
from src.regras import rn001_limite_diario_alimentacao, rn002_limite_diario_transporte


def test_rn001_limite_diario_alimentacao_aprovado_total():
    despesa = Despesa(
        id="d1",
        data=date(2024, 6, 1),
        categoria="alimentacao",
        descricao="Almoço",
        fornecedor="Restaurante",
        valor=Decimal("80.00"),
        tem_nota_fiscal=True,
    )
    resultado = rn001_limite_diario_alimentacao(despesa, [], Politica())

    assert isinstance(resultado, ResultadoItem)
    assert resultado.valor_reembolsado == Decimal("60.00")
    assert resultado.status == "parcial"
    assert resultado.motivo == "dentro do limite diário de alimentacao"


def test_rn001_limite_diario_alimentacao_parcial():
    despesa = Despesa(
        id="d2",
        data=date(2024, 6, 1),
        categoria="alimentacao",
        descricao="Jantar",
        fornecedor="Lanchonete",
        valor=Decimal("60.00"),
        tem_nota_fiscal=True,
    )
    itens_anteriores = [
        ResultadoItem(
            id="d1",
            data=date(2024, 6, 1),
            categoria="alimentacao",
            valor_lancado=Decimal("50.00"),
            valor_reembolsado=Decimal("50.00"),
            status="aprovado",
            motivo="dentro do limite diário de alimentacao",
            regras_aplicadas=["RN-001"],
        )
    ]
    resultado = rn001_limite_diario_alimentacao(despesa, itens_anteriores, Politica())

    assert resultado.valor_reembolsado == Decimal("10.00")
    assert resultado.status == "parcial"
    assert resultado.motivo == "dentro do limite diário de alimentacao"


def test_rn001_limite_diario_alimentacao_excede_limite():
    despesa = Despesa(
        id="d3",
        data=date(2024, 6, 1),
        categoria="alimentacao",
        descricao="Almoço executivo",
        fornecedor="Padaria",
        valor=Decimal("150.00"),
        tem_nota_fiscal=True,
    )
    itens_anteriores = [
        ResultadoItem(
            id="d1",
            data=date(2024, 6, 1),
            categoria="alimentacao",
            valor_lancado=Decimal("60.00"),
            valor_reembolsado=Decimal("60.00"),
            status="aprovado",
            motivo="dentro do limite diário de alimentacao",
            regras_aplicadas=["RN-001"],
        )
    ]
    resultado = rn001_limite_diario_alimentacao(despesa, itens_anteriores, Politica())

    assert resultado.valor_reembolsado == Decimal("0.00")
    assert resultado.status == "recusado"
    assert resultado.motivo == "excedente do limite diário de alimentacao"


def test_rn002_limite_diario_transporte_aprovado_total():
    despesa = Despesa(
        id="d4",
        data=date(2024, 6, 2),
        categoria="transporte_urbano",
        descricao="Corrida",
        fornecedor="Uber",
        valor=Decimal("15.00"),
        tem_nota_fiscal=True,
    )
    resultado = rn002_limite_diario_transporte(despesa, [], Politica())

    assert resultado.valor_reembolsado == Decimal("15.00")
    assert resultado.status == "aprovado"
    assert resultado.motivo == "dentro do limite diário de transporte urbano"


def test_rn002_limite_diario_transporte_parcial():
    despesa = Despesa(
        id="d5",
        data=date(2024, 6, 2),
        categoria="transporte_urbano",
        descricao="Bilhete",
        fornecedor="Metrô",
        valor=Decimal("25.00"),
        tem_nota_fiscal=True,
    )
    itens_anteriores = [
        ResultadoItem(
            id="d4",
            data=date(2024, 6, 2),
            categoria="transporte_urbano",
            valor_lancado=Decimal("10.00"),
            valor_reembolsado=Decimal("10.00"),
            status="aprovado",
            motivo="dentro do limite diário de transporte urbano",
            regras_aplicadas=["RN-002"],
        )
    ]
    resultado = rn002_limite_diario_transporte(despesa, itens_anteriores, Politica())

    assert resultado.valor_reembolsado == Decimal("25.00")
    assert resultado.status == "aprovado"
    assert resultado.motivo == "dentro do limite diário de transporte urbano"


def test_rn002_limite_diario_transporte_excede_limite():
    despesa = Despesa(
        id="d6",
        data=date(2024, 6, 2),
        categoria="transporte_urbano",
        descricao="Corrida longa",
        fornecedor="Táxi",
        valor=Decimal("40.00"),
        tem_nota_fiscal=True,
    )
    itens_anteriores = [
        ResultadoItem(
            id="d4",
            data=date(2024, 6, 2),
            categoria="transporte_urbano",
            valor_lancado=Decimal("15.00"),
            valor_reembolsado=Decimal("15.00"),
            status="aprovado",
            motivo="dentro do limite diário de transporte urbano",
            regras_aplicadas=["RN-002"],
        )
    ]
    resultado = rn002_limite_diario_transporte(despesa, itens_anteriores, Politica())

    assert resultado.valor_reembolsado == Decimal("40.00")
    assert resultado.status == "aprovado"
    assert resultado.motivo == "dentro do limite diário de transporte urbano"
