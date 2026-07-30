# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python 3.11+ | Domínio prévio, stdlib cobre tudo que o desafio pede sem dependência externa | Node/TS e Go: sem ganho real para o escopo, e o tempo é curto para reaprender ferramenta |
| Testes | `pytest` | Sintaxe enxuta para nomear teste = requisito (`test_rn001_...`), fixtures simples para carregar o JSON de exemplo | `unittest` da stdlib: mais verboso, sem ganho de robustez para este escopo |
| Parsing/validação | `dataclasses` + validação manual em uma função `parse_entrada()` | O volume de campos é pequeno (12 campos); dataclass já dá tipagem e legibilidade | `pydantic`: dependência externa desnecessária para este volume; adicionaria uma camada de "mágica" que dificulta explicar o código na correção |
| Aritmética monetária | `decimal.Decimal` (stdlib) | Elimina erro de arredondamento binário do `float` — crítico para dinheiro | `float`: fonte de bug clássica e previsível; `int` em centavos: resolveria o mesmo problema, mas `Decimal` já resolve nativamente sem conversão manual em cada regra |
| CLI | `argparse` (stdlib) | Só duas flags fixas (`--input`, `--output`); não justifica dependência | `click`/`typer`: dependência extra sem necessidade para uma interface tão pequena |

## 2. Arquitetura

```
JSON de despesas
      │
      ▼
CLI + parsing (adaptador)         valida schema de entrada, monta objetos de domínio
      │
      ▼
┌─────────────────────────────────────────┐
│  Núcleo — regras puras (sem I/O)         │
│                                           │
│  pipeline de regras (RN-001..RN-010)     │
│              │                           │
│  config da política (limites como dados) │
└─────────────────────────────────────────┘
      │
      ▼
Agregação + serialização (adaptador)   monta resumo, escreve JSON
      │
      ▼
JSON de resultado
```

**Fronteiras:** tudo que sabe da existência de "arquivo", "JSON" ou "linha de
comando" fica nos adaptadores (`cli.py`, `io_json.py`). O núcleo (`regras.py`,
`politica.py`, `motor.py`) recebe e devolve apenas objetos Python — nenhuma
regra de negócio importa `json` ou `argparse`. Essa fronteira é o que torna o
núcleo testável sem I/O e é o que absorve mudança de requisito sem propagar
para os adaptadores (e vice-versa: mudar o formato de saída não deveria exigir
tocar em nenhuma regra de negócio).

## 3. Modelo de dados

- `Colaborador` — id, nome, centro_custo (passthrough)
- `Periodo` — competencia, inicio, fim (usado por RN-007)
- `Despesa` — id, data, categoria, descricao, fornecedor, valor (`Decimal`),
  tem_nota_fiscal — representação interna de uma linha da entrada, já com
  `valor` normalizado (AMB-009) e `categoria` normalizada (AMB-008)
- `ResultadoItem` — id, categoria, valor_lancado, valor_reembolsado, status
  (enum: `aprovado` / `parcial` / `recusado` / `ignorado`), motivo,
  regras_aplicadas (lista de ids `RN-00X`)
- `Resultado` — colaborador, periodo, resumo (calculado a partir dos itens),
  itens (lista de `ResultadoItem`)

Cada regra do pipeline recebe `(despesa, contexto)` — onde `contexto` inclui
as demais despesas do mesmo colaborador/dia, necessárias para as regras de
agregação diária (RN-001, RN-002) e de duplicata (RN-006) — e devolve um
`ResultadoItem` ou `None` (sinalizando "não decidiu, próxima regra avalia").
A primeira regra que devolve um resultado decisivo encerra a cadeia para
aquela despesa, na ordem definida na spec (seção 8).

## 4. Como a política é representada

Os limites (R$60, R$80, R$250, R$100 para nota fiscal, 50% de ampliação por
viagem) vivem em um único módulo `politica.py`, como constantes/dataclass —
não espalhados como números mágicos dentro das funções de regra. Isso é
deliberado: se o envelope do Dia 2 trouxer uma mudança de valor (ex.: novo
teto) ou uma nova categoria com limite próprio, a mudança normalmente cabe
neste único arquivo mais um ajuste pontual na função de regra correspondente
— sem reescrever o pipeline inteiro.

## 5. Decisões técnicas

### DT-001 — `Decimal` em vez de `float` para todo valor monetário

**Contexto:** cálculos de limite, corte de excedente e soma de totais diários
exigem precisão exata de centavos.
**Decisão:** todo `valor` é convertido para `Decimal` já na etapa de parsing,
e toda a aritmética do núcleo usa `Decimal`.
**Alternativa descartada:** `float` (erro de arredondamento binário
inaceitável em dinheiro); inteiro em centavos (resolveria o mesmo problema,
mas exigiria conversão manual de ida e volta em cada ponto de I/O, sem
vantagem sobre `Decimal` em Python).
**Consequência:** serialização para JSON precisa de um encoder específico
(JSON não tem tipo `Decimal` nativo) — tratado no adaptador de saída, não no
núcleo.

### DT-002 — Regras como pipeline de funções puras, não uma classe com `if/elif` encadeados

**Contexto:** o número de regras de elegibilidade e cálculo é conhecido e vai
crescer no envelope do Dia 2.
**Decisão:** cada `RN-00X` é uma função independente `regra_rn00x(despesa,
contexto) -> ResultadoItem | None`, testável isoladamente; o motor aplica a
lista de funções na ordem da spec (seção 8) e para na primeira que decide.
**Alternativa descartada:** uma função única com `if/elif` para cada regra —
descartada porque acoplar todas as condições num só bloco dificulta testar
uma regra sem as outras e torna arriscado adicionar/remover regra sem efeito
colateral nas demais.
**Consequência:** adicionar uma regra nova (ex.: no envelope) é escrever uma
função nova e inseri-la na lista ordenada — não editar uma função gigante
existente.

### DT-003 — Sem biblioteca de validação de schema

**Contexto:** a entrada tem 12 campos e uma estrutura estável.
**Decisão:** validação manual simples em `parse_entrada()`, com mensagens de
erro específicas por campo ausente/tipo errado.
**Alternativa descartada:** `pydantic` ou `jsonschema` — resolveriam o mesmo
problema com menos código, mas adicionam uma dependência externa e uma camada
de abstração que dificulta a leitura do fluxo de validação na correção, para
um volume de campos que não justifica.

### DT-004 — Agregação diária calculada sob demanda, não pré-computada

**Contexto:** RN-001/RN-002/RN-006 precisam olhar para outras despesas do
mesmo dia/colaborador, não só para a despesa isolada.
**Decisão:** o `contexto` passado a cada regra inclui a lista completa de
despesas do lote (já normalizadas); cada regra que precisa agregar (ex.: soma
diária por categoria) faz o filtro/soma localmente, sem estado mutável
compartilhado entre chamadas.
**Alternativa descartada:** pré-computar um dicionário `{(data, categoria):
soma}` antes do pipeline — mais eficiente, mas acopla a etapa de agregação a
um formato de chave específico que qualquer nova regra de agregação (ex.: por
semana, no envelope) teria que reaproveitar ou duplicar. Para o volume de
dados deste desafio (dezenas de despesas), a diferença de performance é
irrelevante.

## 6. Estratégia de testes

- **Nível:** majoritariamente unitário (uma função de regra por teste, com
  despesas construídas à mão) + um teste de integração rodando o pipeline
  completo contra `exemplos/despesas-exemplo.json` + um teste de CLI
  ponta a ponta (subprocess ou chamada direta da função `main()`, comparando
  o JSON de saída contra um resultado esperado fixado em arquivo).
- **Cada `RN-NNN` da spec tem teste?** Sim — pelo menos um teste nomeado
  `test_rn0XX_<resumo>` por regra, usando os `id`s de despesa da spec (seção 9,
  critérios de aceite) como casos.
- **Casos de borda da seção 7 da spec:** cada linha da tabela vira um teste
  parametrizado ou um teste dedicado, nomeado a partir do `id` da despesa
  envolvida (ex.: `test_d004_acima_limite_nota_fiscal_recusa_integral`).
- **Nomenclatura:** `test_<rn_ou_amb>_<descrição curta>` — permite localizar,
  a partir de qualquer regra da spec, o teste que a verifica, sem precisar
  adivinhar (fecha a rastreabilidade cobrada no critério 2 da rubrica).

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| Ordem de aplicação das regras (seção 8 da spec) produzir resultado diferente do esperado para uma combinação de regras não coberta pelo exemplo | Média | Teste de integração cobre o arquivo de exemplo inteiro; qualquer resultado inesperado vira um caso de borda novo na spec + `DECISIONS.md`, não um ajuste silencioso no código |
| Envelope do Dia 2 introduzir um dado que a arquitetura atual não previu (ex.: campo de viagem, nova categoria) | Alta (é o objetivo do exercício) | Config da política isolada em `politica.py` e regras como funções independentes existem justamente para isso; se ainda assim exigir mudança estrutural, registrar em `DECISIONS.md` o que resistiu e por quê |
| `Decimal` mal serializado em algum ponto do JSON de saída volta a introduzir erro de arredondamento por fora do núcleo | Baixa | Um único ponto de serialização (`io_json.py`) concentra a conversão `Decimal -> str/float` de saída; testado isoladamente |
