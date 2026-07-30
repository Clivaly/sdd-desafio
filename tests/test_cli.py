import json
from pathlib import Path
from tempfile import TemporaryDirectory

from src.cli import main


def test_cli_end_to_end():
    input_path = Path("exemplos/despesas-exemplo.json")

    with TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "resultado.json"
        exit_code = main(["calcular", "--input", str(input_path), "--output", str(output_file)])

        assert exit_code == 0
        assert output_file.exists()

        with output_file.open("r", encoding="utf-8") as handle:
            conteúdo = json.load(handle)

        assert isinstance(conteúdo, dict)
        assert conteúdo["colaborador"]["id"] == "c-0417"
        assert isinstance(conteúdo["itens"], list)
        assert len(conteúdo["itens"]) == 14
        assert "resumo" in conteúdo
        assert conteúdo["resumo"]["total_despesas"] == 14
