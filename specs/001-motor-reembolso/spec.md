# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** rascunho (proposto por Claude, pendente de revisão do autor) · **Última alteração:** `<preencher data>`

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o `plan.md`.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

> **Nota sobre este rascunho:** as decisões abaixo foram propostas por mim (Claude)
> a partir do cruzamento da política com `exemplos/despesas-exemplo.json`. Cada uma
> tem uma leitura alternativa possível — revise, concorde, discorde e reescreva a
> justificativa com as suas próprias palavras antes de considerar isto "seu". O
> relatório final vai te pedir para defender essas escolhas.

---

## 1. Problema

Hoje o financeiro confere manualmente cada despesa lançada por um colaborador
contra a política de reembolso, item por item, numa planilha. O processo é lento
e sujeito a erro humano, e não deixa rastro de por que uma despesa foi aprovada
ou recusada.

## 2. Objetivo

Dado o conjunto de despesas de um colaborador num período, o sistema decide
automaticamente quanto é reembolsável por item e devolve uma justificativa
verificável para cada decisão.

## 3. Fora de escopo

- Não integra com sistemas de folha de pagamento ou efetua o pagamento em si —
  apenas calcula o valor reembolsável e justifica.
- Não faz OCR ou validação de conteúdo de nota fiscal — o campo `tem_nota_fiscal`
  é tratado como já verificado na origem.
- Não infere o status "em viagem" a partir de nenhum outro dado da entrada
  (ver AMB-004) — trata isso como informação ausente nesta versão.
- Não interpreta texto livre do campo `descricao` para extrair quantidade de
  diárias, número de participantes ou qualquer outro dado estruturado
  (ver AMB-011).
- Não implementa fila de aprovação manual de itens com valor reembolsável acima
  de R$500 neste ciclo; esses itens seguem a avaliação automática padrão.
- Não processa múltiplos colaboradores ou múltiplos períodos numa mesma execução.

## 4. Entrada e saída

**Entrada:** conforme `exemplos/despesas-exemplo.json`. Campos e significado:

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | string | Identificador do colaborador | Sim |
| `colaborador.nome` | string | Nome do colaborador | Sim |
| `colaborador.centro_custo` | string | Centro de custo, informativo | Sim |
| `periodo.competencia` | string (AAAA-MM) | Mês de competência do lote | Sim |
| `periodo.inicio` / `periodo.fim` | string (AAAA-MM-DD) | Limites do período de competência | Sim |
| `despesas[].id` | string | Identificador único da despesa | Sim |
| `despesas[].data` | string (AAAA-MM-DD) | Data em que a despesa ocorreu | Sim |
| `despesas[].categoria` | string | Categoria da despesa (`alimentacao`, `transporte_urbano`, `hospedagem` ou outra) | Sim |
| `despesas[].descricao` | string | Texto livre, informativo | Sim |
| `despesas[].fornecedor` | string | Nome do fornecedor/estabelecimento | Sim |
| `despesas[].valor` | número | Valor da despesa na moeda especificada ou BRL se `moeda` ausente | Sim |
| `despesas[].moeda` | string | Código ISO 4217 da moeda da despesa (opcional, padrão BRL) | Não |
| `despesas[].tem_nota_fiscal` | booleano | Se a despesa possui nota fiscal | Sim |

**Nota:** todos os valores internos e de saída são reportados em BRL. Despesas
em moeda estrangeira são convertidas para BRL usando a taxa da data da despesa.

**Saída:** definida por mim. Estrutura e significado de cada campo:

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador` | objeto | Repassado da entrada, sem alteração |
| `periodo` | objeto | Repassado da entrada, sem alteração |
| `resumo.total_despesas` | inteiro | Quantidade de despesas processadas |
| `resumo.total_valor_lancado` | número | Soma de todos os valores lançados (positivos) |
| `resumo.total_reembolsavel` | número | Soma de todos os valores efetivamente reembolsados |
| `resumo.total_recusado` | número | Soma do valor não reembolsado (lançado − reembolsado, exceto estornos) |
| `itens[].id` | string | Id da despesa original |
| `itens[].categoria` | string | Categoria normalizada (minúscula) |
| `itens[].valor_lancado` | número | Valor original, normalizado para 2 casas decimais |
| `itens[].valor_reembolsado` | número | Valor efetivamente reembolsável (0 se recusado) |
| `itens[].status` | string | Um de: `aprovado`, `parcial`, `recusado`, `ignorado` |
| `itens[].motivo` | string | Explicação legível da decisão, citando a regra aplicada |
| `itens[].regras_aplicadas` | lista de strings | IDs das regras (`RN-00X`) que determinaram o resultado |

Exemplo de saída para duas despesas (mesmo dia, mesma categoria, uma delas
duplicada):

```json
{
  "colaborador": { "id": "c-0417", "nome": "Marina Volpi", "centro_custo": "CC-ENG-PLATAFORMA" },
  "periodo": { "competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31" },
  "resumo": {
    "total_despesas": 2,
    "total_valor_lancado": 109.80,
    "total_reembolsavel": 54.90,
    "total_recusado": 54.90
  },
  "itens": [
    {
      "id": "d-006",
      "categoria": "alimentacao",
      "valor_lancado": 54.90,
      "valor_reembolsado": 54.90,
      "status": "aprovado",
      "motivo": "dentro do limite diário de alimentação (R$54,90 de R$60,00)",
      "regras_aplicadas": ["RN-001"]
    },
    {
      "id": "d-007",
      "categoria": "alimentacao",
      "valor_lancado": 54.90,
      "valor_reembolsado": 0.00,
      "status": "recusado",
      "motivo": "duplicata de d-006 (mesma data, categoria, fornecedor e valor)",
      "regras_aplicadas": ["RN-006"]
    }
  ]
}
```

## 5. Regras de negócio

### RN-001 — Limite diário de alimentação

**Regra:** o total de despesas de categoria `alimentacao` lançadas por um
colaborador em uma mesma data não pode exceder R$60,00. O que exceder é
reembolsado parcialmente (ver RN-003).
**Origem:** política do RH, item 1
**Aceite:** despesas `d-001` (R$72,50) + `d-002` (R$38,00), ambas em 2026-07-03,
somam R$110,50; o sistema reembolsa R$60,00 no total do dia.

### RN-002 — Limite diário de transporte urbano

**Regra:** o total de despesas de categoria `transporte_urbano` lançadas por um
colaborador em uma mesma data não pode exceder R$80,00.
**Origem:** política do RH, item 2
**Aceite:** despesa `d-003` (R$100,00, sem nota fiscal) sozinha no dia (`d-004` é
recusada antes por RN-004) é reembolsada em R$80,00.

### RN-003 — Reembolso parcial por excedente de limite

**Regra:** quando o total sujeito a um limite (diário ou por diária) excede o
teto, o sistema reembolsa até o teto e recusa apenas o valor excedente — nunca
recusa a despesa inteira por causa do limite.
**Origem:** política do RH, item 4
**Aceite:** ver RN-001 e RN-010.

### RN-004 — Nota fiscal obrigatória acima de R$100

**Regra:** despesas com valor estritamente maior que R$100,00 exigem
`tem_nota_fiscal: true`. Se exigida e ausente, a despesa é recusada
integralmente (reembolso R$0,00), independentemente de estar dentro de
qualquer limite de valor.
**Origem:** política do RH, item 5
**Aceite:** `d-003` (R$100,00 exato, sem NF) não é bloqueada por esta regra;
`d-004` (R$100,01, sem NF) é recusada integralmente por esta regra.

### RN-005 — Ampliação de limites para colaborador em viagem

**Regra:** nesta versão, a entrada não contém nenhum campo que indique se o
colaborador está em viagem. A regra existe na política, mas **não é aplicada**
em nenhuma despesa — nenhum limite é ampliado em 50% enquanto esse dado não
existir na entrada.
**Origem:** política do RH, item 6
**Aceite:** para qualquer despesa do conjunto de exemplo, os limites aplicados
são sempre os limites-base (R$60 / R$80 / R$250), nunca os ampliados.

### RN-006 — Tratamento de duplicatas

**Regra:** duas despesas são consideradas duplicadas quando têm a mesma `data`,
`categoria`, `fornecedor` e `valor`. Entre despesas duplicadas, apenas a de
menor `id` (primeira lançada) é elegível a reembolso; as demais são recusadas
integralmente com motivo "duplicata".
**Origem:** política do RH, item 8
**Aceite:** `d-006` e `d-007` são idênticas em data, categoria, fornecedor e
valor; `d-006` segue para as demais regras, `d-007` é recusada por esta regra.

### RN-007 — Período de competência

**Regra:** despesas com `data` fora do intervalo `[periodo.inicio,
periodo.fim]` (limites inclusivos) são recusadas integralmente, com motivo
"fora do período de competência".
**Origem:** política do RH, item 7
**Aceite:** `d-008` tem `data: 2026-04-15`, fora do intervalo
`2026-07-01`–`2026-07-31`; é recusada por esta regra antes de qualquer outra
avaliação.

### RN-008 — Categorias fora da política

**Regra:** apenas as categorias `alimentacao`, `transporte_urbano` e
`hospedagem` (comparadas de forma insensível a maiúsculas/minúsculas) são
reembolsáveis. Qualquer outra categoria é recusada integralmente.
**Origem:** política do RH, item 9
**Aceite:** `d-005` (categoria `coworking`) é recusada por esta regra.

### RN-009 — Valores negativos (estornos)

**Regra:** despesas com `valor` negativo não geram reembolso, não são somadas
a nenhum limite diário de outras despesas, e aparecem no resultado com status
`ignorado`.
**Origem:** não coberto explicitamente pela política; decisão de projeto (ver AMB-010)
**Aceite:** `d-009` (`valor: -45.00`) aparece como `ignorado`, com
`valor_reembolsado: 0.00`, e não altera o total diário de transporte urbano do
dia 2026-07-11.

### RN-010 — Limite por diária de hospedagem

**Regra:** cada lançamento de categoria `hospedagem` é avaliado individualmente
contra o teto de R$250,00 — não há divisão pelo número de noites mencionado em
texto livre. Valor que excede R$250,00 num único lançamento é reembolsado
parcialmente (RN-003).
**Origem:** política do RH, item 3
**Aceite:** `d-010` (R$480,00, descrito como "2 diárias") é reembolsado em
R$250,00, com R$230,00 recusado por excedente.

### RN-011 — Política por centro de custo

**Regra:** os limites de cada categoria são carregados de arquivo externo e
variam por `colaborador.centro_custo`. A política vigente é a tabela em
`envelope/politica-v4.json`; para centros de custo não presentes nessa tabela,
aplica-se a seção `padrao`. Categorias só são reembolsáveis se estiverem
definidas na política aplicada.
**Origem:** envelope v4, item A
**Aceite:** `e-001` e `e-006` usam limites de `CC-COMERCIAL`; `f-004` usa a
política padrão porque `CC-SUPORTE-N2` não existe na tabela; `CC-ENG-PLATAFORMA`
recusa hospedagem por limite zero.

### RN-012 — Conversão de moeda para BRL

**Regra:** se `despesas[].moeda` estiver presente e diferente de `BRL`, o valor
é convertido para BRL usando a taxa correspondente à data da despesa em
`envelope/cambio.json`. Se `moeda` estiver ausente, assume-se `BRL`. Se não
houver taxa disponível para a data ou para a moeda, a despesa é recusada
integralmente por `taxa de câmbio indisponível`.
**Origem:** envelope v4, item B
**Aceite:** `e-002` e `e-003` em EUR usam as taxas de 2026-07-14 e 2026-07-15;
`e-005` em USD usa a taxa de 2026-07-20; `f-004` em USD usa a taxa de 2026-07-21.

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia" / "Transporte
urbano tem limite de R$ 80 por dia."
**O que não está claro:** o limite é por despesa individual ou pela soma de
todas as despesas da mesma categoria no mesmo dia?
**Decisão:** o limite é aplicado à soma diária por categoria, não por despesa
isolada.
**Justificativa:** a política diz "por dia", não "por despesa"; interpretar por
despesa permitiria múltiplos lançamentos no mesmo dia para burlar o teto.
**Regra afetada:** RN-001, RN-002

### AMB-002 — Significado de "reembolsadas parcialmente"

**Texto original do RH:** "Despesas acima do limite são reembolsadas
parcialmente."
**O que não está claro:** "parcialmente" pode significar "paga até o teto e
recusa o excedente" ou "recusa a despesa inteira, já que só uma parte dela
seria válida".
**Decisão:** paga até o teto e recusa apenas o excedente.
**Justificativa:** "reembolsadas parcialmente" descreve um pagamento que
acontece (ainda que parcial), não uma recusa total — a leitura mais literal do
próprio adjetivo "parcial".
**Regra afetada:** RN-003

### AMB-003 — Fronteira de "acima de R$100" para nota fiscal

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** uma despesa de exatamente R$100,00 conta como
"acima"?
**Decisão:** "acima de" é estritamente maior que — R$100,00 exato não exige
nota fiscal; R$100,01 exige.
**Justificativa:** "acima de X" em português exclui o próprio valor de
referência; qualquer leitura inclusiva exigiria reescrever a regra como
"a partir de" ou "maior ou igual a".
**Regra afetada:** RN-004

### AMB-004 — "Em viagem" é um dado que não existe na entrada

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em
50%."
**O que não está claro:** a entrada não tem nenhum campo (`em_viagem` ou
similar) que indique esse estado. Não há como aplicar a regra sem inventar uma
fonte de dado.
**Decisão:** a regra fica registrada, mas não é aplicada nesta versão — nenhum
limite é ampliado, para nenhuma despesa, até que a entrada inclua esse dado
explicitamente.
**Justificativa:** qualquer heurística para inferir "viagem" a partir de outros
campos (ex.: presença de despesa de hospedagem no período) seria uma regra de
negócio nova, inventada por mim, e não pelo RH — mais arriscado do que
simplesmente não aplicar o benefício.
**Regra afetada:** RN-005
**Alternativa descartada:** inferir viagem quando há pelo menos uma despesa de
`hospedagem` no período. Descartada porque generaliza demais (uma diária de
hospedagem já classificaria o período inteiro como "viagem", inclusive
despesas de dias sem hospedagem).

### AMB-013 — O que significa aplicar a política padrão

**Texto original do RH:** "Alguns centros de custo não têm entrada na tabela.
Nesse caso, aplica-se a política padrão."
**O que não está claro:** a política padrão deve ser aplicada apenas como
fallback quando o centro de custo não existir, ou deve também influenciar
categorias e limites em outros casos?
**Decisão:** a política padrão é o fallback usado somente quando o centro de
custo não consta em `envelope/politica-v4.json`. Se o centro existir, usa-se
apenas sua configuração específica.
**Justificativa:** a frase "aplica-se a política padrão" descreve um caminho
default e não uma mistura de políticas; misturar limites de dois centros criaria
comportamento ambíguo.
**Regra afetada:** RN-011

### AMB-014 — Taxa da data da despesa

**Texto original do RH:** "A conversão usa a taxa da data da despesa, não a taxa
de hoje."
**O que não está claro:** se a taxa para aquela data estiver ausente, o que deve
acontecer? Deve-se usar a taxa do último dia útil anterior, recusar a despesa, ou
falhar o lote inteiro?
**Decisão:** a despesa é recusada integralmente se não houver taxa disponível
para a data da despesa e para a moeda informada. O lote continua a ser processado
normalmente para as demais despesas.
**Justificativa:** é melhor dar um resultado verificável por despesa do que falhar
o lote inteiro por dados faltantes de câmbio.
**Regra afetada:** RN-012

### AMB-015 — Moeda ausente assume BRL

**Texto original do RH:** "Quando ausente, assume-se BRL."
**O que não está claro:** isso vale apenas para a conversão, ou também deve afetar
se `valor` pode ser escrito em outra moeda implícita sem o campo `moeda`?
**Decisão:** se `moeda` estiver ausente, o valor é interpretado como BRL. O campo
`moeda` é obrigatório apenas quando a despesa estiver em outra moeda.
**Justificativa:** essa é a leitura mais direta de um campo opcional; não há
motivo para inferir uma moeda diferente sem que ela esteja declarada.
**Regra afetada:** RN-012

### AMB-005 — Critério e tratamento de duplicatas

**Texto original do RH:** "Duplicatas devem ser tratadas."
**O que não está claro:** o que define uma duplicata (mesmo valor? mesma data?
mesmo fornecedor? alguma combinação?) e o que "tratadas" significa (recusar,
somar, sinalizar para revisão humana).
**Decisão:** duplicata = mesma `data` + `categoria` + `fornecedor` + `valor`.
Entre duplicatas, apenas a primeira (menor `id`) é elegível; as demais são
recusadas.
**Justificativa:** são os únicos campos disponíveis para correlação sem um
identificador de transação externo; exigir os quatro simultaneamente reduz
falsos positivos (dois almoços genuinamente diferentes no mesmo fornecedor e
dia, mas com valores diferentes, não seriam pegos como duplicata).
**Regra afetada:** RN-006

### AMB-006 — Consequência de estar fora do período de competência

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de
competência."
**O que não está claro:** a política não diz o que acontece com uma despesa
fora do período — apenas que "devem" estar dentro.
**Decisão:** despesa com data fora de `[periodo.inicio, periodo.fim]`
(intervalo fechado nos dois extremos) é recusada integralmente.
**Justificativa:** trata-se de uma condição de elegibilidade, não de um teto de
valor — não faz sentido "reembolsar parcialmente" uma despesa que nem deveria
ter sido lançada neste lote.
**Regra afetada:** RN-007

### AMB-007 — Consequência de categoria fora da política

**Texto original do RH:** "Categorias fora da política não são
reembolsáveis."
**O que não está claro:** quais categorias estão, de fato, "na política"? A
política só nomeia três (alimentação, transporte urbano, hospedagem) — mas não
lista explicitamente todas as categorias existentes.
**Decisão:** apenas as três categorias citadas na política são reembolsáveis;
qualquer outra é recusada.
**Justificativa:** a política enumera exatamente essas três com regra de
limite própria; na ausência de uma quarta regra, a categoria não está "na
política".
**Regra afetada:** RN-008

### AMB-008 — Normalização de categoria (maiúsculas/minúsculas)

**Texto original do RH:** não coberto — é um problema do dado, não da
política.
**O que não está claro:** `d-014` usa a categoria `ALIMENTACAO` em maiúsculas,
enquanto as demais usam `alimentacao` em minúsculas. Uma comparação literal
trataria isso como categoria diferente (e, por RN-008, recusaria).
**Decisão:** a comparação de categoria é sempre insensível a
maiúsculas/minúsculas.
**Justificativa:** tratar como categoria distinta contrariaria a intenção
visível do dado — é a mesma categoria com formatação inconsistente, não uma
categoria nova.
**Regra afetada:** RN-001, RN-002, RN-008, RN-010

### AMB-009 — Arredondamento de valores com mais de duas casas decimais

**Texto original do RH:** não coberto.
**O que não está claro:** `d-011` tem `valor: 33.333` (três casas decimais),
incompatível com centavos de real.
**Decisão:** todo valor de entrada é normalizado para 2 casas decimais
(arredondamento padrão) antes de qualquer regra ser aplicada.
**Justificativa:** o real não tem subdivisão menor que o centavo; um valor com
mais casas é tratado como imprecisão de lançamento a ser normalizada, não como
um novo valor "verdadeiro".
**Regra afetada:** todas (etapa de normalização, anterior a qualquer RN-00X)

### AMB-010 — Valores negativos (estornos)

**Texto original do RH:** não coberto.
**O que não está claro:** `d-009` tem `valor: -45.00` — a política não
menciona estornos em nenhum momento.
**Decisão:** despesas com valor negativo não são reembolsadas nem abatem
limites de outras despesas; aparecem no resultado como `ignorado`.
**Justificativa:** reembolso negativo não tem significado de negócio definido;
isolar o estorno evita que ele altere silenciosamente o cálculo de outras
despesas do mesmo dia.
**Regra afetada:** RN-009
**Alternativa descartada:** usar o estorno para abater o total diário de
transporte urbano do mesmo dia. Descartada por não haver nenhuma indicação na
política de que estornos compensam outras despesas.

### AMB-011 — Número de diárias de hospedagem não é um dado estruturado

**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária."
**O que não está claro:** "diária" é uma unidade de uma noite, mas a entrada
não tem um campo de quantidade de noites — só um `valor` total por lançamento
e uma `descricao` em texto livre que às vezes menciona a quantidade (ex.: "2
diárias", "3 noites").
**Decisão:** o limite de R$250,00 é aplicado ao valor total de cada
*lançamento* de hospedagem, tratando cada lançamento como uma unidade única —
não se tenta extrair a quantidade de noites do texto de `descricao`.
**Justificativa:** interpretar texto livre para extrair um número é parsing de
linguagem natural, frágil e não verificável a partir da spec; a leitura
literal do único dado estruturado disponível (`valor`) é a mais defensável,
mesmo sabendo que produz um resultado mais conservador para hospedagens
multi-noite.
**Regra afetada:** RN-010
**Consequência assumida:** `d-010` ("2 diárias", R$480,00) é limitada a
R$250,00 no total, e não a R$500,00 (250 × 2) — um resultado que um humano
lendo a descrição discordaria. Ver seção 10.

### AMB-012 — Consequência de nota fiscal ausente quando obrigatória

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** a política diz que é "obrigatória", mas não diz o
que acontece se estiver ausente — recusa o item inteiro, recusa só o
excedente acima de R$100, ou apenas sinaliza para revisão?
**Decisão:** ausência de nota fiscal quando obrigatória recusa a despesa
integralmente (R$0,00), mesmo que o valor esteja dentro do limite diário da
categoria.
**Justificativa:** nota fiscal é um requisito de compliance/comprovação, não
um teto de valor — tratá-la como um corte parcial equivaleria a dizer que
R$100,00 do valor "não precisam" de comprovação, o que não está na política.
**Regra afetada:** RN-004

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Duas despesas da mesma categoria no mesmo dia somam mais que o limite | `d-001` + `d-002` | Reembolsa até o limite diário somado, recusa o excedente | RN-001, AMB-001 |
| Valor exatamente igual ao limite de nota fiscal | `d-003` (R$100,00) | Não exige nota fiscal | RN-004, AMB-003 |
| Valor um centavo acima do limite de nota fiscal | `d-004` (R$100,01) | Exige nota fiscal; ausente → recusa integral | RN-004, AMB-003, AMB-012 |
| Categoria não prevista na política | `d-005` (`coworking`) | Recusa integral | RN-008, AMB-007 |
| Duas despesas idênticas em data, categoria, fornecedor e valor | `d-006` / `d-007` | Primeira aprovada, segunda recusada como duplicata | RN-006, AMB-005 |
| Despesa com data fora do período de competência | `d-008` | Recusa integral | RN-007, AMB-006 |
| Despesa com valor negativo | `d-009` | Ignorada, não afeta outros cálculos do dia | RN-009, AMB-010 |
| Hospedagem cujo valor implica mais de uma diária pelo texto da descrição | `d-010`, `d-013` | Limite de R$250 aplicado ao lançamento inteiro, não multiplicado por noites | RN-010, AMB-011 |
| Valor com mais de duas casas decimais | `d-011` (33.333) | Normalizado para 2 casas antes de qualquer regra | AMB-009 |
| Categoria em maiúsculas | `d-014` (`ALIMENTACAO`) | Tratada como `alimentacao` | RN-008, AMB-008 |
| Nenhum dado de viagem na entrada | todas as despesas | Nenhum limite ampliado em 50% | RN-005, AMB-004 |

## 8. Ordem de aplicação das regras

Quando várias regras incidem sobre a mesma despesa, a ordem abaixo é aplicada
até a primeira que decide o destino do item (recusa integral encerra a
avaliação daquela despesa; as regras seguintes não se aplicam mais a ela):

1. Normalização (categoria em minúsculas, valor arredondado a 2 casas) — AMB-008, AMB-009
2. RN-008 — categoria fora da política → recusa integral e encerra
3. RN-007 — fora do período de competência → recusa integral e encerra
4. RN-009 — valor negativo (estorno) → ignorado e encerra
5. RN-006 — duplicata de uma despesa já processada → recusa integral e encerra
6. RN-004 — nota fiscal obrigatória ausente → recusa integral e encerra
7. RN-001 / RN-002 / RN-010 — limite diário ou por diária → reembolso parcial (RN-003) se exceder
8. RN-005 — ampliação por viagem (nesta versão, nunca se aplica — ver AMB-004)

**Por que essa ordem:** condições de elegibilidade (categoria, período,
estorno, duplicata, nota fiscal) são binárias e mais baratas de decidir do que
o cálculo de limite, que depende de agregar todas as despesas do mesmo dia.
Decidir a elegibilidade primeiro evita que uma despesa inelegível "ocupe"
espaço no limite diário de outra despesa válida.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Processa `exemplos/despesas-exemplo.json` sem erro e produz um item de
      saída para cada uma das 14 despesas de entrada.
- [ ] `d-001` + `d-002` somam R$60,00 de reembolso no dia 2026-07-03 (RN-001).
- [ ] `d-003` é reembolsada em R$80,00 sem exigir nota fiscal (RN-002, RN-004).
- [ ] `d-004` é recusada integralmente por falta de nota fiscal (RN-004, AMB-012).
- [ ] `d-005` é recusada por categoria fora da política (RN-008).
- [ ] `d-006` é aprovada e `d-007` é recusada como duplicata (RN-006).
- [ ] `d-008` é recusada por estar fora do período de competência (RN-007).
- [ ] `d-009` aparece como `ignorado`, com valor reembolsado zero (RN-009).
- [ ] `d-010` é reembolsada em R$250,00, com R$230,00 recusado por excedente (RN-010).
- [ ] `d-011` é normalizada para R$33,33 antes de qualquer cálculo (AMB-009).
- [ ] `d-013` é recusada integralmente por falta de nota fiscal, antes mesmo do
      limite de hospedagem ser avaliado (RN-004, seção 8).
- [ ] `d-014` é tratada com a mesma categoria de `alimentacao` (AMB-008).
- [ ] O `resumo` da saída bate com a soma dos `itens` individuais.
- [ ] Todas as regras de negócio (`RN-00X`) e ambiguidades (`AMB-00X`) desta
      spec têm ao menos um teste automatizado correspondente.

## 10. O que fica em aberto

- **AMB-004 (viagem):** a decisão de não aplicar a regra 6 é defensável, mas
  deixa a política parcialmente não implementada. Se surgir um campo de
  viagem na entrada (envelope do Dia 2?), a regra RN-005 já está desenhada
  para ser ativada sem redesenhar o pipeline — só falta o dado.
- **AMB-011 (diárias de hospedagem):** a decisão conservadora (tratar cada
  lançamento como uma diária) provavelmente sub-reembolsa hospedagens de
  múltiplas noites descritas corretamente pelo colaborador. Uma leitura
  alternativa — dividir o valor pelo número de noites extraído do texto — foi
  descartada por depender de parsing de linguagem natural não verificável.
- **AMB-006 (fora do período):** a política não diz explicitamente se uma
  despesa fora do período deveria ao menos aparecer no relatório como
  "recusada" ou ser omitida por completo. Decidi mantê-la no relatório com
  status `recusado` para preservar rastreabilidade, mas um RH real poderia
  preferir que ela nem aparecesse.
- **Limite de duas casas decimais em `resumo`:** não há regra explícita sobre
  arredondamento de totais agregados (soma primeiro e arredonda, ou arredonda
  cada item e soma). Adotei "arredonda cada item, depois soma" — pode gerar
  diferença de centavo em relação a "soma tudo, depois arredonda". Não testado
  neste rascunho.
