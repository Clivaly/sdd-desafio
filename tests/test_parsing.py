from decimal import Decimal
from pathlib import Path

from src.io_json import carregar_entrada, parse_entrada


def test_parse_carrega_despesas_exemplo():
    caminho = Path(__file__).parent.parent / "exemplos" / "despesas-exemplo.json"
    colaborador, periodo, despesas = carregar_entrada(caminho)

    assert colaborador.id == "c-0417"
    assert periodo.competencia == "2026-07"
    assert len(despesas) == 14
    assert despesas[0].id == "d-001"
    assert despesas[0].categoria == "alimentacao"
    assert despesas[0].valor == Decimal("72.50")


def test_amb008_categoria_maiuscula_normalizada():
    raw = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-014",
                "data": "2026-07-31",
                "categoria": "ALIMENTACAO",
                "descricao": "Jantar de encerramento",
                "fornecedor": "Restaurante Tavola",
                "valor": 61.00,
                "tem_nota_fiscal": True,
            }
        ],
    }

    _, _, despesas = parse_entrada(raw)

    assert despesas[0].categoria == "alimentacao"


def test_amb009_valor_tres_casas_normalizado():
    raw = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-011",
                "data": "2026-07-15",
                "categoria": "alimentacao",
                "descricao": "Cafe da manha hotel",
                "fornecedor": "Hotel Copa Sul",
                "valor": 33.333,
                "tem_nota_fiscal": True,
            }
        ],
    }

    _, _, despesas = parse_entrada(raw)

    assert despesas[0].valor == Decimal("33.33")
