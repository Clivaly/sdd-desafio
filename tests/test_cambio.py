import json
from decimal import Decimal
from pathlib import Path

from src.io_json import carregar_entrada
from src.motor import calcular_resultado
from src.politica import Politica


def test_converte_euro_para_brl(tmp_path):
    raw = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "e-002",
                "data": "2026-07-14",
                "categoria": "alimentacao",
                "descricao": "Almoco - Lisboa",
                "fornecedor": "Taberna do Chiado",
                "valor": 22.00,
                "moeda": "EUR",
                "tem_nota_fiscal": True,
            }
        ],
    }

    entrada_path = tmp_path / "entrada.json"
    with entrada_path.open("w", encoding="utf-8") as handle:
        json.dump(raw, handle, ensure_ascii=False)

    cambio_path = Path(__file__).resolve().parents[1] / "envelope" / "cambio.json"
    _, _, despesas = carregar_entrada(entrada_path, cambio_path)

    assert despesas[0].valor == Decimal("130.46")
    assert despesas[0].taxa_de_cambio == Decimal("5.93")


def test_moeda_ausente_assume_brl(tmp_path):
    raw = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "e-010",
                "data": "2026-07-27",
                "categoria": "alimentacao",
                "descricao": "Almoco",
                "fornecedor": "Bistro Central",
                "valor": 88.00,
                "tem_nota_fiscal": True,
            }
        ],
    }

    entrada_path = tmp_path / "entrada.json"
    with entrada_path.open("w", encoding="utf-8") as handle:
        json.dump(raw, handle, ensure_ascii=False)

    cambio_path = Path(__file__).resolve().parents[1] / "envelope" / "cambio.json"
    _, _, despesas = carregar_entrada(entrada_path, cambio_path)

    assert despesas[0].valor == Decimal("88.00")
    assert despesas[0].taxa_de_cambio == Decimal("1.00")
    assert despesas[0].moeda == "BRL"


def test_recusa_moeda_nao_suportada(tmp_path):
    raw = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "e-006",
                "data": "2026-07-21",
                "categoria": "alimentacao",
                "descricao": "Almoco com parceiro - Londres",
                "fornecedor": "The Ivy",
                "valor": 55.00,
                "moeda": "GBP",
                "tem_nota_fiscal": True,
            }
        ],
    }

    entrada_path = tmp_path / "entrada.json"
    with entrada_path.open("w", encoding="utf-8") as handle:
        json.dump(raw, handle, ensure_ascii=False)

    cambio_path = Path(__file__).resolve().parents[1] / "envelope" / "cambio.json"
    colaborador, periodo, despesas = carregar_entrada(entrada_path, cambio_path)
    resultado = calcular_resultado(colaborador, periodo, despesas, Politica())

    assert resultado.itens[0].status == "recusado"
    assert resultado.itens[0].motivo == "taxa de câmbio indisponível"
    assert resultado.itens[0].regras_aplicadas == ["RN-012"]


def test_recusa_sem_taxa_de_cambio_para_data(tmp_path):
    raw = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-08", "inicio": "2026-08-01", "fim": "2026-08-31"},
        "despesas": [
            {
                "id": "e-011",
                "data": "2026-08-03",
                "categoria": "alimentacao",
                "descricao": "Almoco fora do livro",
                "fornecedor": "Restaurante Inexistente",
                "valor": 20.00,
                "moeda": "EUR",
                "tem_nota_fiscal": True,
            }
        ],
    }

    entrada_path = tmp_path / "entrada.json"
    with entrada_path.open("w", encoding="utf-8") as handle:
        json.dump(raw, handle, ensure_ascii=False)

    cambio_path = Path(__file__).resolve().parents[1] / "envelope" / "cambio.json"
    colaborador, periodo, despesas = carregar_entrada(entrada_path, cambio_path)
    resultado = calcular_resultado(colaborador, periodo, despesas, Politica())

    assert resultado.itens[0].status == "recusado"
    assert resultado.itens[0].motivo == "taxa de câmbio indisponível"
    assert resultado.itens[0].regras_aplicadas == ["RN-012"]
