from decimal import Decimal

from src.io_json import parse_entrada
from src.regras import rn006_duplicata


def test_rn006_duplicata_recusa_segunda_ocorrencia():
    raw = {
        "colaborador": {"id": "c-0004", "nome": "Teste 4", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-006",
                "data": "2026-07-05",
                "categoria": "alimentacao",
                "descricao": "Almoço",
                "fornecedor": "Restaurante",
                "valor": "50.00",
                "tem_nota_fiscal": True,
            },
            {
                "id": "d-007",
                "data": "2026-07-05",
                "categoria": "alimentacao",
                "descricao": "Almoço duplicado",
                "fornecedor": "Restaurante",
                "valor": "50.00",
                "tem_nota_fiscal": True,
            },
        ],
    }

    _, _, despesas = parse_entrada(raw)
    resultado_primeira = rn006_duplicata(despesas[0], [])
    resultado_segunda = rn006_duplicata(despesas[1], [despesas[0]])

    assert resultado_primeira is None
    assert resultado_segunda is not None
    assert resultado_segunda.id == "d-007"
    assert resultado_segunda.status == "recusado"
    assert resultado_segunda.valor_reembolsado == Decimal("0.00")
    assert resultado_segunda.motivo == "duplicata"
    assert resultado_segunda.regras_aplicadas == ["RN-006"]
