# Sessão 14 — CLI de execução do motor

- Data: 2026-07-30
- Objetivo: implementar T-014, a interface CLI `calcular --input <arquivo> --output <arquivo>`.
- Atividades:
  - Criei `src/cli.py` com `argparse` e subcomando `calcular`.
  - A CLI usa `src.io_json.carregar_entrada`, `src.motor.calcular_resultado` e `src.io_json.escrever_saida`.
  - Criei `tests/test_cli.py` para validar o fluxo end-to-end com `exemplos/despesas-exemplo.json`.
- Observações:
  - O comando foi implementado conforme a interface fixa do desafio.
  - O teste verifica saída JSON válida, 14 itens e resumo presente.
