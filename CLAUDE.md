# CLAUDE.md

## O projeto

Motor de cálculo de reembolso de despesas corporativas. CLI que lê um JSON de
despesas e emite um JSON com o valor reembolsável e a justificativa de cada item.

## Fonte da verdade

`specs/001-motor-reembolso/spec.md` define **o que** o sistema faz.
`specs/001-motor-reembolso/plan.md` define **como**.
`specs/001-motor-reembolso/tasks.md` define **em que ordem**.

Quando o código e a spec discordarem, a spec está certa e o código é o bug —
a menos que a spec esteja errada, e nesse caso corrigimos a spec primeiro e
registramos em `DECISIONS.md`.

**Antes de implementar qualquer coisa, leia a task correspondente em `tasks.md`.**
Se o que eu pedi não está coberto por nenhuma task, me avise em vez de implementar.

## Regras de trabalho

- Toda regra de negócio vive na spec, não no chat e não em comentário de código.
- Se eu te explicar uma regra que não está na spec, **pare e me diga isso** antes
  de escrever código. Isso é um bug de spec.
- Todo commit referencia uma task: `feat(T-003): <descrição>`.
  Mudanças de documentação: `docs(spec):`, `docs(plan):`, `docs(tasks):`.
- Nenhuma regra de negócio entra sem teste.

## Stack e comandos

- Linguagem: Python 3.11+
- Rodar: `python -m src.cli calcular --input <arquivo> --output <arquivo>`
- Testes: `python -m pytest`
- Lint/format: `<preencher se adotar black/ruff>`

## Convenções de código

- Núcleo de regras (`src/regras.py`, `src/politica.py`, `src/motor.py`) não
  importa `json`, `argparse` nem faz I/O de arquivo — só recebe e devolve
  objetos Python. Isso é a fronteira definida em `plan.md` seção 2; não a
  quebre por conveniência.
- Cada regra de negócio (`RN-00X`) é uma função independente, testável sem
  as demais.
- Valores monetários: sempre `decimal.Decimal`, nunca `float`, em qualquer
  ponto do núcleo. Conversão para tipo serializável em JSON acontece só no
  adaptador de saída.
- Teste nomeado a partir do id da regra ou do caso de borda que cobre
  (`test_rn004_...`, `test_d004_...`) — é o que fecha a rastreabilidade.

## Fora de escopo

- Não infere "em viagem" de nenhum dado além de um campo explícito que ainda
  não existe na entrada (ver `spec.md`, AMB-004).
- Não faz parsing de linguagem natural sobre o campo `descricao`.
- Não lida com múltiplos colaboradores/períodos numa mesma execução.
- Não integra com sistemas de pagamento.
