# Sessão 07 — Período de competência

- Data: 2026-07-30
- Objetivo: implementar T-006, RN-007 para recusar despesas fora do período.
- Atividades:
  - Adicionei `rn007_fora_periodo_competencia` em `src/regras.py`.
  - A regra valida se `despesa.data` está dentro do intervalo inclusivo de `periodo`.
  - Criei `tests/test_rn007_fora_periodo_competencia.py` cobrindo `d-008`.
- Observações:
  - A sessão registra a decisão de manter o período como critério binário sem exceções.
  - Isto preserva o processo para as próximas tasks.
