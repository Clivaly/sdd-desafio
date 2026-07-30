# Sessão 09 — Nota fiscal obrigatória acima de R$100

- Data: 2026-07-30
- Objetivo: implementar T-009, RN-004 para recusa de despesas sem nota fiscal acima de R$100.
- Atividades:
  - Adicionei `rn004_nota_fiscal_obrigatoria` em `src/regras.py`.
  - A regra recusa integralmente quando `valor > 100` e `tem_nota_fiscal` é falso.
  - Criei `tests/test_rn004_nota_fiscal_obrigatoria.py` com casos de `100.00` e `100.01`.
- Observações:
  - A decisão de usar `valor estritamente maior que R$100` vem diretamente da spec e da bordo de `d-003`/`d-004`.
