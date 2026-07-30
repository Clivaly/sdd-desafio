from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


DEFAULT_CATEGORIAS_REEMBOLSAVEIS = frozenset({"alimentacao", "transporte_urbano", "hospedagem"})


@dataclass(frozen=True)
class Politica:
    limite_alimentacao_diaria: Decimal = Decimal("60.00")
    limite_transporte_urbano_diario: Decimal = Decimal("80.00")
    limite_hospedagem_diaria: Decimal = Decimal("250.00")
    valor_nota_fiscal_obrigatoria: Decimal = Decimal("100.00")
    multiplicador_viagem: Decimal = Decimal("1.50")
    categorias_reembolsaveis: set[str] = DEFAULT_CATEGORIAS_REEMBOLSAVEIS

    @classmethod
    def carregar_por_centro_custo(cls, path: str | Path, centro_custo: str) -> "Politica":
        path_obj = Path(path)
        with path_obj.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        padrao = raw.get("padrao", {})
        centros = raw.get("centros_custo", {})
        politica_centro = centros.get(centro_custo, padrao)

        nota_fiscal_obrigatoria = Decimal(str(raw.get("nota_fiscal_obrigatoria_acima_de", "100.00")))
        percentual_viagem = Decimal(str(raw.get("acrescimo_em_viagem_percentual", 50)))
        multiplicador_viagem = Decimal("1.00") + (percentual_viagem / Decimal("100"))

        limite_alimentacao = Decimal(str(politica_centro.get("alimentacao", {}).get("limite", 0.00)))
        limite_transporte = Decimal(str(politica_centro.get("transporte_urbano", {}).get("limite", 0.00)))
        limite_hospedagem = Decimal(str(politica_centro.get("hospedagem", {}).get("limite", 0.00)))

        categorias = set(politica_centro.keys())
        if not categorias:
            categorias = set(DEFAULT_CATEGORIAS_REEMBOLSAVEIS)

        return cls(
            limite_alimentacao_diaria=limite_alimentacao,
            limite_transporte_urbano_diario=limite_transporte,
            limite_hospedagem_diaria=limite_hospedagem,
            valor_nota_fiscal_obrigatoria=nota_fiscal_obrigatoria,
            multiplicador_viagem=multiplicador_viagem,
            categorias_reembolsaveis=categorias,
        )


DEFAULT_POLITICA = Politica()
