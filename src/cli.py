from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .io_json import carregar_entrada, escrever_saida
from .motor import calcular_resultado


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calcular",
        description="Calcula reembolso de despesas a partir de um arquivo JSON de entrada.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    calcular_parser = subparsers.add_parser(
        "calcular",
        help="Processa as despesas e gera o JSON de resultado.",
    )
    calcular_parser.add_argument(
        "--input",
        required=True,
        help="Caminho para o arquivo JSON de entrada com despesas.",
    )
    calcular_parser.add_argument(
        "--output",
        required=True,
        help="Caminho para o arquivo JSON de saída com o resultado.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "calcular":
        parser.print_help()
        return 1

    colaborador, periodo, despesas = carregar_entrada(Path(args.input))
    resultado = calcular_resultado(colaborador, periodo, despesas)
    escrever_saida(resultado, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
