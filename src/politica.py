from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Politica:
    limite_alimentacao_diaria: Decimal = Decimal("60.00")
    limite_transporte_urbano_diario: Decimal = Decimal("80.00")
    limite_hospedagem_diaria: Decimal = Decimal("250.00")
    valor_nota_fiscal_obrigatoria: Decimal = Decimal("100.00")
    multiplicador_viagem: Decimal = Decimal("1.50")
    categorias_reembolsaveis: set[str] = frozenset({"alimentacao", "transporte_urbano", "hospedagem"})


DEFAULT_POLITICA = Politica()
