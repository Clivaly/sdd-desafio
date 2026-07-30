# Sessão 05 — Política como dados

- Data: 2026-07-30
- Objetivo: implementar T-004, representar limites e multiplicador em `politica.py`.
- Atividades:
  - Criei `src/politica.py` com `Politica` e `DEFAULT_POLITICA`.
  - Defini limites base de alimentação, transporte e hospedagem e o valor de nota fiscal obrigatória.
  - Adicionei `multiplicador_viagem` e `categorias_reembolsaveis` no mesmo local para manter a política centralizada.
  - Criei `tests/test_politica.py` que valida os valores exatos da spec.
- Observações:
  - A política é isolada do motor e das regras, permitindo mudar valores sem afetar a lógica de decisão.
