from decimal import Decimal

from src.io_json import parse_entrada
from src.politica import DEFAULT_POLITICA
from src.regras import rn008_categoria_fora_politica


def test_rn008_categoria_fora_politica_recusa():
    raw = {
        "colaborador": {"id": "c-0001", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-005",
                "data": "2026-07-03",
                "categoria": "coworking",
                "descricao": "Espaço de trabalho compartilhado",
                "fornecedor": "WeWork",
                "valor": "150.00",
                "tem_nota_fiscal": False,
            }
        ],
    }

    _, _, despesas = parse_entrada(raw)
    resultado = rn008_categoria_fora_politica(despesas[0], DEFAULT_POLITICA)

    assert resultado is not None
    assert resultado.id == "d-005"
    assert resultado.status == "recusado"
    assert resultado.valor_reembolsado == Decimal("0.00")
    assert resultado.motivo == "categoria fora da política"
    assert resultado.regras_aplicadas == ["RN-008"]
