from decimal import Decimal

from src.io_json import parse_entrada
from src.regras import rn009_valor_negativo_ignorado


def test_rn009_valor_negativo_ignorado():
    raw = {
        "colaborador": {"id": "c-0003", "nome": "Teste 3", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-009",
                "data": "2026-07-11",
                "categoria": "transporte_urbano",
                "descricao": "Estorno de passagem",
                "fornecedor": "Uber",
                "valor": "-45.00",
                "tem_nota_fiscal": False,
            }
        ],
    }

    _, _, despesas = parse_entrada(raw)
    resultado = rn009_valor_negativo_ignorado(despesas[0])

    assert resultado is not None
    assert resultado.id == "d-009"
    assert resultado.status == "ignorado"
    assert resultado.valor_reembolsado == Decimal("0.00")
    assert resultado.motivo == "estorno"
    assert resultado.regras_aplicadas == ["RN-009"]
