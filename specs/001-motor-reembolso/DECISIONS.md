# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-002 — Política externa e despesas internacionais · 2026-07-30

**Gatilho:** envelope lacrado v4 com nova política por centro de custo e despesas em moeda estrangeira.

**O que mudou na spec:** a política deixou de ser estática no código e passou a ser carregada de `envelope/politica-v4.json`; os limites agora variam por `colaborador.centro_custo` com fallback para a seção `padrao`. Também foi adicionada conversão de despesas internacionais para BRL usando `envelope/cambio.json` e o campo opcional `despesas[].moeda`.

**Por quê:** o RH exigiu que os limites sejam mantidos fora do código e que o motor avalie despesas de viagem internacional com taxa da data de despesa.

**O que isso invalidou:** a configuração de política fixa em `politica.py`; a suposição de que as categorias reembolsáveis são sempre as mesmas; a suposição de que todas as despesas estão em BRL; o uso de limites hard-coded em RN-001/RN-002/RN-010.

**Tasks afetadas:** criação de T-016..T-020; revisão de T-005, T-010 e T-011 para garantir que usem política dinâmica e conversão de moeda.

**Custo:** 4 arquivos de especificação/documentação atualizados (`spec.md`, `plan.md`, `tasks.md`, `DECISIONS.md`), 2 arquivos de dados adicionados (`envelope/politica-v4.json`, `envelope/cambio.json`) e novos testes de envelope.

---

## D-001 — <título curto> · `<data>`

**Gatilho:**

**O que mudou na spec:**

**Por quê:**

**O que isso invalidou:**

**Tasks afetadas:**

**Custo:**
