from datetime import date
from decimal import Decimal

from src.modelos import Despesa
from src.politica import Politica
from src.regras import rn005_ampliacao_limites_viagem


def test_rn005_ampliacao_limites_viagem_nao_aplicada():
    despesa = Despesa(
        id="d13",
        data=date(2024, 6, 4),
        categoria="alimentacao",
        descricao="Almoço em viagem",
        fornecedor="Restaurante",
        valor=Decimal("70.00"),
        tem_nota_fiscal=True,
    )

    resultado = rn005_ampliacao_limites_viagem(despesa, Politica())

    assert resultado is None
