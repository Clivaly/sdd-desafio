from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .modelos import Colaborador, Despesa, Periodo


def _parse_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Campo '{field_name}' deve ser uma string")
    return value


def _parse_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"Campo '{field_name}' deve ser um booleano")
    return value


def _parse_decimal(value: Any, field_name: str) -> Decimal:
    if not isinstance(value, (int, float, str, Decimal)):
        raise ValueError(f"Campo '{field_name}' deve ser numérico")
    decimal_value = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return decimal_value


def _parse_date(value: Any, field_name: str) -> date:
    raw = _parse_string(value, field_name)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"Campo '{field_name}' deve ser data no formato AAAA-MM-DD") from exc


def _parse_colaborador(data: Any) -> Colaborador:
    if not isinstance(data, dict):
        raise ValueError("Campo 'colaborador' deve ser um objeto")

    return Colaborador(
        id=_parse_string(data.get("id"), "colaborador.id"),
        nome=_parse_string(data.get("nome"), "colaborador.nome"),
        centro_custo=_parse_string(data.get("centro_custo"), "colaborador.centro_custo"),
    )


def _parse_periodo(data: Any) -> Periodo:
    if not isinstance(data, dict):
        raise ValueError("Campo 'periodo' deve ser um objeto")

    return Periodo(
        competencia=_parse_string(data.get("competencia"), "periodo.competencia"),
        inicio=_parse_date(data.get("inicio"), "periodo.inicio"),
        fim=_parse_date(data.get("fim"), "periodo.fim"),
    )


def _normalize_categoria(categoria: str) -> str:
    return categoria.strip().lower()


def _parse_despesa(data: Any) -> Despesa:
    if not isinstance(data, dict):
        raise ValueError("Cada item de 'despesas' deve ser um objeto")

    categoria = _normalize_categoria(_parse_string(data.get("categoria"), "despesas[].categoria"))
    return Despesa(
        id=_parse_string(data.get("id"), "despesas[].id"),
        data=_parse_date(data.get("data"), "despesas[].data"),
        categoria=categoria,
        descricao=_parse_string(data.get("descricao"), "despesas[].descricao"),
        fornecedor=_parse_string(data.get("fornecedor"), "despesas[].fornecedor"),
        valor=_parse_decimal(data.get("valor"), "despesas[].valor"),
        tem_nota_fiscal=_parse_bool(data.get("tem_nota_fiscal"), "despesas[].tem_nota_fiscal"),
    )


def parse_entrada(raw: Any) -> Tuple[Colaborador, Periodo, List[Despesa]]:
    if not isinstance(raw, dict):
        raise ValueError("A entrada JSON deve ser um objeto")

    colaborador = _parse_colaborador(raw.get("colaborador"))
    periodo = _parse_periodo(raw.get("periodo"))

    despesas_raw = raw.get("despesas")
    if not isinstance(despesas_raw, list):
        raise ValueError("Campo 'despesas' deve ser uma lista")

    despesas = [_parse_despesa(item) for item in despesas_raw]
    return colaborador, periodo, despesas


def carregar_entrada(path: str | Path) -> Tuple[Colaborador, Periodo, List[Despesa]]:
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return parse_entrada(raw)
