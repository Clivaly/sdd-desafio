# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>`

---

## Fase 1 — Fundação

- [x] **T-001** — Modelo de dados de entrada (`Colaborador`, `Periodo`, `Despesa`) e função de parsing/validação do JSON
  - **Atende:** spec seção 4 (entrada)
  - **Aceite:** `test_parse_carrega_despesas_exemplo` — parseia `exemplos/despesas-exemplo.json` sem erro e retorna 14 despesas
  - **Commit:**

- [x] **T-002** — Normalização de entrada: categoria em minúsculas e valor arredondado a 2 casas decimais
  - **Atende:** AMB-008, AMB-009
  - **Aceite:** `test_amb008_categoria_maiuscula_normalizada` (`d-014`) e `test_amb009_valor_tres_casas_normalizado` (`d-011` → `33.33`)
  - **Commit:**

- [x] **T-003** — Modelo de dados de saída (`ResultadoItem`, `Resultado`) e serialização para JSON, incluindo conversão de `Decimal`
  - **Atende:** spec seção 4 (saída)
  - **Aceite:** `test_serializa_resultado_item` — gera JSON com todos os campos do schema de saída
  - **Commit:**

- [ ] **T-004** — Config da política como dados (`politica.py`): limites de alimentação, transporte, hospedagem, threshold de nota fiscal, multiplicador de viagem
  - **Atende:** RN-001, RN-002, RN-004, RN-005, RN-010
  - **Aceite:** `test_politica_valores_batem_com_spec` — cada constante importada é igual ao valor citado na spec
  - **Commit:**

## Fase 2 — Regras de negócio (elegibilidade, ordem 2–6 da spec)

- [x] **T-005** — RN-008: categoria fora da política → recusa integral
  - **Atende:** RN-008, AMB-007
  - **Aceite:** `test_rn008_categoria_fora_politica_recusa` (`d-005`, `coworking`)
  - **Commit:**

- [x] **T-006** — RN-007: despesa fora do período de competência → recusa integral
  - **Atende:** RN-007, AMB-006
  - **Aceite:** `test_rn007_fora_periodo_competencia_recusa` (`d-008`)
  - **Commit:**

- [x] **T-007** — RN-009: valor negativo → ignorado, não entra em nenhuma agregação
  - **Atende:** RN-009, AMB-010
  - **Aceite:** `test_rn009_valor_negativo_ignorado` (`d-009`)
  - **Commit:**

- [x] **T-008** — RN-006: detecção de duplicata (mesma data, categoria, fornecedor, valor) → recusa a partir da segunda ocorrência
  - **Atende:** RN-006, AMB-005
  - **Aceite:** `test_rn006_duplicata_recusa_segunda_ocorrencia` (`d-006` aprovado, `d-007` recusado)
  - **Commit:**

- [x] **T-009** — RN-004: nota fiscal obrigatória acima de R$100 (fronteira exclusiva) → ausência recusa integral
  - **Atende:** RN-004, AMB-003, AMB-012
  - **Aceite:** `test_rn004_limite_exato_nao_exige_nf` (`d-003`, R$100,00), `test_rn004_acima_limite_sem_nf_recusa` (`d-004`, R$100,01)
  - **Commit:**

## Fase 3 — Regras de cálculo (ordem 7 da spec)

- [x] **T-010** — RN-001/RN-002: agregação diária por categoria (alimentação e transporte urbano) + RN-003: corte parcial do excedente
  - **Atende:** RN-001, RN-002, RN-003, AMB-001, AMB-002
  - **Aceite:** `test_rn001_soma_diaria_alimentacao_corta_excedente` (`d-001`+`d-002` → R$60,00 no dia), `test_rn002_transporte_urbano_corta_excedente` (`d-003` isolado → R$80,00)
  - **Commit:**

- [x] **T-011** — RN-010: limite por diária de hospedagem (lançamento tratado como unidade única) + corte parcial
  - **Atende:** RN-010, AMB-011
  - **Aceite:** `test_rn010_hospedagem_multi_diaria_limite_unico` (`d-010`, R$480,00 → R$250,00 reembolsado)
  - **Commit:**

- [x] **T-012** — RN-005: ampliação por viagem — implementada como regra desativada (documentar por que não altera nenhum resultado nesta versão)
  - **Atende:** RN-005, AMB-004
  - **Aceite:** `test_rn005_sem_dado_viagem_nenhum_limite_ampliado` — roda o conjunto de exemplo inteiro e garante que nenhum item tem `RN-005` em `regras_aplicadas`
  - **Commit:**

## Fase 4 — Saída e CLI

- [x] **T-013** — Motor: função que aplica o pipeline de regras na ordem da spec (seção 8) e monta `Resultado` com `resumo` agregado
  - **Atende:** spec seção 8, spec seção 4 (`resumo`)
  - **Aceite:** `test_motor_resumo_bate_com_soma_dos_itens` — para o conjunto de exemplo, `resumo.total_reembolsavel` é igual à soma de `valor_reembolsado` de todos os itens
  - **Commit:**

- [x] **T-014** — CLI `calcular --input <arquivo> --output <arquivo>`
  - **Atende:** interface fixa do desafio (`DESAFIO.md`)
  - **Aceite:** `test_cli_end_to_end` — roda o comando com `exemplos/despesas-exemplo.json` e o arquivo de saída tem 14 itens e é JSON válido
  - **Commit:**

- [x] **T-015** — README com instruções de instalação, execução e testes
  - **Atende:** requisito de entrega (`DESAFIO.md`, "O que entregar")
  - **Aceite:** seguir o README do zero (ambiente limpo) resulta em `resultado.json` gerado sem intervenção manual
  - **Commit:**

---

## Fase 5 — Envelope (criar no Dia 2)

- [x] **T-016** — Política por centro de custo carregada de arquivo externo
  - **Atende:** item A do envelope, leitura de `envelope/politica-v4.json`
  - **Aceite:** `test_politica_por_centro_custo_carrega_limites_externos` e `test_politica_fallback_para_padrao`
  - **Commit:** `feat(T-016): carregar política por centro de custo de envelope v4`

- [x] **T-017** — Conversão de despesas internacionais para BRL usando taxa da data
  - **Atende:** item B do envelope, leitura de `envelope/cambio.json`
  - **Aceite:** `test_converte_euro_para_brl`, `test_moeda_ausente_assume_brl`, `test_recusa_moeda_nao_suportada`, `test_recusa_sem_taxa_de_cambio`
  - **Commit:**

- [x] **T-018** — Adaptação das regras de limite à política dinâmica e novos limites/ categorias
  - **Atende:** item A do envelope, categorias variáveis por centro de custo e limite zero para `hospedagem` em `CC-ENG-PLATAFORMA`
  - **Aceite:** `test_representacao_reembolsavel_em_cc_comercial`, `test_hospedagem_cc_eng_plataforma_recusa`, `test_centro_desconhecido_usa_padrao`
  - **Commit:**
**

- [ ] **T-019** — Atualizar `spec.md`, `plan.md`, `DECISIONS.md`, `tasks.md` e documentação com os novos requisitos do envelope
  - **Atende:** linha 35-39 do envelope, processar a mudança antes de codificar
  - **Aceite:** `spec.md` e `tasks.md` refletem o envelope; `DECISIONS.md` registra a mudança; `envelope/*` está versionado
  - **Commit:**

- [ ] **T-020** — Testes e validação ponta a ponta do envelope com `envelope/despesas-envelope.json` e `envelope/despesas-envelope-cc-desconhecido.json`
  - **Atende:** garantir que a nova política e conversão funcionam em casos reais do envelope
  - **Aceite:** `test_envelope_principal` e `test_envelope_cc_desconhecido` passam
  - **Commit:**

---

## Cobertura

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-010 | `test_rn001_soma_diaria_alimentacao_corta_excedente` |
| RN-002 | T-010 | `test_rn002_transporte_urbano_corta_excedente` |
| RN-003 | T-010, T-011 | (coberto pelos testes de RN-001/RN-002/RN-010) |
| RN-004 | T-009 | `test_rn004_limite_exato_nao_exige_nf`, `test_rn004_acima_limite_sem_nf_recusa` |
| RN-005 | T-012 | `test_rn005_sem_dado_viagem_nenhum_limite_ampliado` |
| RN-006 | T-008 | `test_rn006_duplicata_recusa_segunda_ocorrencia` |
| RN-007 | T-006 | `test_rn007_fora_periodo_competencia_recusa` |
| RN-008 | T-005 | `test_rn008_categoria_fora_politica_recusa` |
| RN-009 | T-007 | `test_rn009_valor_negativo_ignorado` |
| RN-010 | T-011 | `test_rn010_hospedagem_multi_diaria_limite_unico` |
| AMB-001 a AMB-012 | ver RN-00X correspondente acima | ver RN-00X correspondente acima |
