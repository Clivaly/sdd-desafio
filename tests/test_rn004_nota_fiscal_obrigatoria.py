from decimal import Decimal

from src.io_json import parse_entrada
from src.regras import rn004_nota_fiscal_obrigatoria


def test_rn004_limite_exato_nao_exige_nf():
    raw = {
        "colaborador": {"id": "c-0005", "nome": "Teste 5", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-003",
                "data": "2026-07-04",
                "categoria": "transporte_urbano",
                "descricao": "Taxi sem nota fiscal",
                "fornecedor": "Táxi",
                "valor": "100.00",
                "tem_nota_fiscal": False,
            }
        ],
    }

    _, _, despesas = parse_entrada(raw)
    resultado = rn004_nota_fiscal_obrigatoria(despesas[0])

    assert resultado is None


def test_rn004_acima_limite_sem_nf_recusa():
    raw = {
        "colaborador": {"id": "c-0006", "nome": "Teste 6", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-004",
                "data": "2026-07-04",
                "categoria": "transporte_urbano",
                "descricao": "Taxi acima de 100 sem nota fiscal",
                "fornecedor": "Táxi",
                "valor": "100.01",
                "tem_nota_fiscal": False,
            }
        ],
    }

    _, _, despesas = parse_entrada(raw)
    resultado = rn004_nota_fiscal_obrigatoria(despesas[0])

    assert resultado is not None
    assert resultado.id == "d-004"
    assert resultado.status == "recusado"
    assert resultado.valor_reembolsado == Decimal("0.00")
    assert resultado.motivo == "nota fiscal obrigatória ausente"
    assert resultado.regras_aplicadas == ["RN-004"]
