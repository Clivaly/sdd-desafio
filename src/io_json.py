from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .modelos import Colaborador, Despesa, Periodo, Resultado, ResultadoItem


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
    moeda_raw = data.get("moeda")
    if moeda_raw is None:
        moeda = "BRL"
    else:
        moeda = _parse_string(moeda_raw, "despesas[].moeda").strip().upper()

    return Despesa(
        id=_parse_string(data.get("id"), "despesas[].id"),
        data=_parse_date(data.get("data"), "despesas[].data"),
        categoria=categoria,
        descricao=_parse_string(data.get("descricao"), "despesas[].descricao"),
        fornecedor=_parse_string(data.get("fornecedor"), "despesas[].fornecedor"),
        valor=_parse_decimal(data.get("valor"), "despesas[].valor"),
        moeda=moeda,
        taxa_de_cambio=None,
        tem_nota_fiscal=_parse_bool(data.get("tem_nota_fiscal"), "despesas[].tem_nota_fiscal"),
    )


def _load_taxas_cambio(path: Path) -> Dict[str, Dict[str, Decimal]]:
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    taxas_raw = raw.get("taxas", {})
    taxas: Dict[str, Dict[str, Decimal]] = {}
    for data_str, cotacoes in taxas_raw.items():
        taxas[data_str] = {moeda.upper(): Decimal(str(valor)) for moeda, valor in cotacoes.items()}
    return taxas


def _obter_taxa(taxas: Dict[str, Dict[str, Decimal]], data: date, moeda: str) -> Optional[Decimal]:
    if moeda == "BRL":
        return Decimal("1.00")

    dia = data.isoformat()
    return taxas.get(dia, {}).get(moeda)


def _aplicar_cambio(despesas: List[Despesa], cambio_path: Path) -> List[Despesa]:
    taxas = _load_taxas_cambio(cambio_path)
    despesas_com_cambio: List[Despesa] = []

    for despesa in despesas:
        taxa = _obter_taxa(taxas, despesa.data, despesa.moeda)
        if taxa is None and despesa.moeda == "BRL":
            taxa = Decimal("1.00")

        if taxa is not None:
            valor_brl = despesa.valor * taxa
            valor_brl = valor_brl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            despesas_com_cambio.append(
                replace(despesa, valor=valor_brl, taxa_de_cambio=taxa)
            )
        else:
            despesas_com_cambio.append(despesa)

    return despesas_com_cambio


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


def _decimal_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value.quantize(Decimal("0.01")))
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def resultado_item_para_dict(item: ResultadoItem) -> Dict[str, Any]:
    return {
        "id": item.id,
        "categoria": item.categoria,
        "valor_lancado": item.valor_lancado,
        "valor_reembolsado": item.valor_reembolsado,
        "status": item.status,
        "motivo": item.motivo,
        "regras_aplicadas": item.regras_aplicadas,
    }


def resultado_para_dict(resultado: Resultado) -> Dict[str, Any]:
    return {
        "colaborador": {
            "id": resultado.colaborador.id,
            "nome": resultado.colaborador.nome,
            "centro_custo": resultado.colaborador.centro_custo,
        },
        "periodo": {
            "competencia": resultado.periodo.competencia,
            "inicio": resultado.periodo.inicio.isoformat(),
            "fim": resultado.periodo.fim.isoformat(),
        },
        "resumo": {
            "total_despesas": resultado.resumo["total_despesas"],
            "total_valor_lancado": resultado.resumo["total_valor_lancado"],
            "total_reembolsavel": resultado.resumo["total_reembolsavel"],
            "total_recusado": resultado.resumo["total_recusado"],
        },
        "itens": [resultado_item_para_dict(item) for item in resultado.itens],
    }


def escrever_saida(resultado: Resultado, path: str | Path) -> None:
    path_obj = Path(path)
    with path_obj.open("w", encoding="utf-8") as handle:
        json.dump(resultado_para_dict(resultado), handle, default=_decimal_default, ensure_ascii=False, indent=2)


def carregar_entrada(path: str | Path, cambio_path: str | Path | None = None) -> Tuple[Colaborador, Periodo, List[Despesa]]:
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    colaborador, periodo, despesas = parse_entrada(raw)
    if cambio_path is not None:
        despesas = _aplicar_cambio(despesas, Path(cambio_path))
    return colaborador, periodo, despesas
