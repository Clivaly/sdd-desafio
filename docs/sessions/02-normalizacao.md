# Sessão 02 — Normalização de entrada

- Data: 2026-07-30
- Objetivo: implementar T-002, normalização de categoria e valor.
- Atividades:
  - Adicionei normalização de `categoria` para lowercase.
  - Arredondei `valor` de despesas para 2 casas decimais usando `Decimal` e `ROUND_HALF_UP`.
  - Criei testes de bordo para categoria maiúscula e valor com 3 casas decimais.
- Observações:
  - A implementação segue o plano de manter a camada de parsing independente.
