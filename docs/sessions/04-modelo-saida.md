# Sessão 04 — Modelo de saída e serialização

- Data: 2026-07-30
- Objetivo: implementar T-003, a modelagem de saída e a serialização JSON.
- Atividades:
  - Adicionei os modelos `ResultadoItem` e `Resultado` em `src/modelos.py`.
  - Implementei `resultado_para_dict` e `escrever_saida` em `src/io_json.py`.
  - Criei `tests/test_serialization.py` para validar a conversão de `Decimal` e os campos de saída.
- Observações:
  - Mantive a fronteira de I/O isolada do núcleo.
  - Esta sessão cobre a decisão de como serializar `Decimal` no adaptador, não no núcleo.
