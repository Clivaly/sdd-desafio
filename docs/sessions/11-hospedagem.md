# Sessão 11 — Limite por diária de hospedagem

- Data: 2026-07-30
- Objetivo: implementar T-011, RN-010 para hospedagem e reembolso parcial.
- Atividades:
  - Adicionei `rn010_limite_por_diaria_hospedagem` em `src/regras.py`.
  - A regra aplica o teto de R$250,00 por lançamento de `hospedagem`.
  - Criei `tests/test_rn010_limite_hospedagem.py` com casos de valor abaixo do teto, acima do teto e parcial.
- Observações:
  - A decisão segue AMB-011: cada lançamento de hospedagem é tratado como uma unidade única, sem inferir número de diárias da descrição.
  - O valor excedente é recusado parcialmente, alinhado a RN-003.
