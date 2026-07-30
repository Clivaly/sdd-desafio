from decimal import Decimal

from src.io_json import parse_entrada
from src.regras import rn007_fora_periodo_competencia


def test_rn007_fora_periodo_competencia_recusa():
    raw = {
        "colaborador": {"id": "c-0002", "nome": "Teste 2", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-008",
                "data": "2026-04-15",
                "categoria": "alimentacao",
                "descricao": "Almoço fora do período",
                "fornecedor": "Restaurante",
                "valor": "45.00",
                "tem_nota_fiscal": True,
            }
        ],
    }

    _, periodo, despesas = parse_entrada(raw)
    resultado = rn007_fora_periodo_competencia(despesas[0], periodo)

    assert resultado is not None
    assert resultado.id == "d-008"
    assert resultado.status == "recusado"
    assert resultado.valor_reembolsado == Decimal("0.00")
    assert resultado.motivo == "fora do período de competência"
    assert resultado.regras_aplicadas == ["RN-007"]
