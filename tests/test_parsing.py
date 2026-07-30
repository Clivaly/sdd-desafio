from decimal import Decimal
from pathlib import Path

from src.io_json import carregar_entrada


def test_parse_carrega_despesas_exemplo():
    caminho = Path(__file__).parent.parent / "exemplos" / "despesas-exemplo.json"
    colaborador, periodo, despesas = carregar_entrada(caminho)

    assert colaborador.id == "c-0417"
    assert periodo.competencia == "2026-07"
    assert len(despesas) == 14
    assert despesas[0].id == "d-001"
    assert despesas[0].categoria == "alimentacao"
    assert despesas[0].valor == Decimal("72.50")
