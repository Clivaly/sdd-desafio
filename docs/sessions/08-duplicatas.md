# Sessão 08 — Duplicatas

- Data: 2026-07-30
- Objetivo: implementar T-008, a regra RN-006 de duplicatas.
- Atividades:
  - Adicionei `rn006_duplicata` em `src/regras.py`.
  - A regra compara data, categoria, fornecedor e valor com despesas anteriores.
  - Criei `tests/test_rn006_duplicata.py` cobrindo `d-006` e `d-007`.
- Observações:
  - A decisão de tratar apenas a segunda ocorrência como duplicata foi registrada na própria spec.
  - Este arquivo de sessão documenta a entrega de T-008 antes de partir para T-009.
