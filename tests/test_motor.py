from decimal import Decimal
from datetime import date

from src.io_json import parse_entrada
from src.motor import calcular_resultado
from src.modelos import ResultadoItem
from src.politica import Politica


def test_motor_resumo_bate_com_soma_dos_itens():
    raw = {
        "colaborador": {
            "id": "c-0417",
            "nome": "Marina Volpi",
            "centro_custo": "CC-ENG-PLATAFORMA",
        },
        "periodo": {
            "competencia": "2026-07",
            "inicio": "2026-07-01",
            "fim": "2026-07-31",
        },
        "despesas": [
            {
                "id": "d-001",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "Almoço",
                "fornecedor": "Restaurante",
                "valor": "72.50",
                "tem_nota_fiscal": True,
            },
            {
                "id": "d-002",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "Jantar",
                "fornecedor": "Lanchonete",
                "valor": "38.00",
                "tem_nota_fiscal": True,
            },
        ],
    }

    colaborador, periodo, despesas = parse_entrada(raw)
    resultado = calcular_resultado(colaborador, periodo, despesas, Politica())

    assert resultado.resumo["total_despesas"] == 2
    assert resultado.resumo["total_valor_lancado"] == Decimal("110.50")
    assert resultado.resumo["total_reembolsavel"] == sum(
        (item.valor_reembolsado for item in resultado.itens), Decimal("0.00")
    )
    assert resultado.resumo["total_recusado"] == Decimal("110.50") - resultado.resumo["total_reembolsavel"]
    assert all(isinstance(item, ResultadoItem) for item in resultado.itens)
