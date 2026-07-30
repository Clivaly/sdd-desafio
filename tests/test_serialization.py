from decimal import Decimal
from datetime import date

from src.io_json import resultado_para_dict
from src.modelos import Colaborador, Periodo, Resultado, ResultadoItem


def test_serializa_resultado_item():
    colaborador = Colaborador(
        id="c-0417",
        nome="Marina Volpi",
        centro_custo="CC-ENG-PLATAFORMA",
    )
    periodo = Periodo(
        competencia="2026-07",
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
    )
    itens = [
        ResultadoItem(
            id="d-001",
            data=date(2026, 7, 2),
            categoria="alimentacao",
            valor_lancado=Decimal("72.50"),
            valor_reembolsado=Decimal("60.00"),
            status="parcial",
            motivo="dentro do limite diário de alimentação",
            regras_aplicadas=["RN-001", "RN-003"],
        )
    ]
    resultado = Resultado(
        colaborador=colaborador,
        periodo=periodo,
        resumo={
            "total_despesas": 1,
            "total_valor_lancado": Decimal("72.50"),
            "total_reembolsavel": Decimal("60.00"),
            "total_recusado": Decimal("12.50"),
        },
        itens=itens,
    )

    output = resultado_para_dict(resultado)

    assert output["colaborador"]["id"] == "c-0417"
    assert output["periodo"]["inicio"] == "2026-07-01"
    assert output["resumo"]["total_despesas"] == 1
    assert output["resumo"]["total_valor_lancado"] == Decimal("72.50")
    assert output["itens"][0]["valor_reembolsado"] == Decimal("60.00")
    assert output["itens"][0]["regras_aplicadas"] == ["RN-001", "RN-003"]
