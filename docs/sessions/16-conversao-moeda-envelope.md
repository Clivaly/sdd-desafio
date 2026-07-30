# Sessão 16 — Conversão de despesas internacionais do envelope de câmbio

- Data: 2026-07-30
- Objetivo: implementar T-017, aceitando despesas em moeda estrangeira e convertendo-as para BRL usando as taxas do envelope `envelope/cambio.json`.
- Atividades:
  - Adicionei carga de taxas de câmbio em `src/io_json.py` e apliquei conversão para BRL por data de despesa.
  - Atualizei o modelo `Despesa` em `src/modelos.py` para incluir `moeda` e `taxa_de_cambio`.
  - Incluí a regra `RN-012` em `src/regras.py` para recusar despesas internacionais sem taxa disponível.
  - Ajustei o pipeline em `src/motor.py` para avaliar a disponibilidade de taxa antes de aplicar regras de validação e limites.
  - Escrevi testes em `tests/test_cambio.py` para:
    - converter EUR para BRL com taxa correta;
    - assumir BRL quando `moeda` estiver ausente;
    - recusar moeda não suportada;
    - recusar despesa com taxa ausente para a data.
- Observações:
  - O commit anterior foi feito prematuramente; este arquivo documenta a sessão de T-017 e será incluído no histórico do desafio.
  - Após a criação da sessão, o commit será ajustado para refletir a ordem correta do processo.
