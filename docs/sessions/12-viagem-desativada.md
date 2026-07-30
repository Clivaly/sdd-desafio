# Sessão 12 — Ampliação de limites por viagem desativada

- Data: 2026-07-30
- Objetivo: implementar T-012, documentar RN-005 como regra presente mas não aplicada.
- Atividades:
  - Adicionei `rn005_ampliacao_limites_viagem` em `src/regras.py`.
  - A função retorna `None` porque a entrada não traz campo que indique viagem.
  - Criei `tests/test_rn005_viagem_desativada.py` para garantir que a regra não altera o resultado.
- Observações:
  - Esta implementação corresponde a AMB-004: sem dado explícito, limites não são ampliados.
  - A regra está registrada no código para manter a rastreabilidade da política.
