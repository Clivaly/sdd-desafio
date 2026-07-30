# Relatório — Desafio SDD

**Aluno:** Clivaly · **Repositório:** `<link>` · **Data:** 2026-07-30

> Isto não é redação. São **evidências**. Toda afirmação deve vir acompanhada de
> arquivo, hash de commit ou trecho de sessão exportada. Um parágrafo bonito sem
> evidência vale menos que uma frase curta com um hash.
>
> Vale 20 dos 100 pontos, e é a seção que mais separa notas.

---

## Delegação

*O que você fez, o que o Claude fez, e por que dividiu assim.*

**A divisão:**

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Eu | O envelope e a política exigiam leitura cuidadosa do JSON e das diferenças entre o desafio original e o Dia 2 |
| Decidir as ambiguidades | Eu | As decisões precisavam ser registradas em `specs/001-motor-reembolso/spec.md` e `DECISIONS.md` |
| Escrever a spec | Eu | Ajustei a descrição das regras para o envelope v4 de forma verificável |
| Desenhar a arquitetura | Eu | Mantive a separação adaptador/núcleo para que a mudança não vazasse em `src/regras.py` ou no JSON |
| Implementar | Eu | Fiz as mudanças no código e garanti que a política dinâmica e o câmbio funcionassem juntos |
| Escrever testes | Eu | Adicionei testes específicos de envelope em `tests/test_cambio.py` e `tests/test_politica.py` |
| Absorver o envelope | Eu | Registrei as sessões, documentei as decisões e ajustei as tasks para T-016..T-019 |

**Onde deleguei e me arrependi:**

Não deleguei nenhum ponto técnico crítico; mantive o controle nas decisões de requisito e implementação.

**Onde não deleguei e deveria ter delegado:**

Nenhum. O desafio exigia revisão constante do modelo e do código, portanto preferi manter a responsabilidade.

**Usei subagentes / skills / MCP / hooks?**

Sim. Usei as ferramentas do VS Code/Copilot para navegar no repositório, buscar arquivos e fazer edições precisas. Isso foi útil para garantir que as referências de commit e de sessão fossem corretas.

---

## Descrição

*Como você transformou requisito ambíguo em requisito verificável.*

Pegue **um** requisito ambíguo da política do RH e mostre a evolução:

**Versão 1 (minha primeira escrita):**
> As despesas em moeda estrangeira devem ser convertidas para BRL pela taxa da data de despesa.

**Versão final:**
> Se `despesas[].moeda` estiver ausente, o valor é interpretado como BRL. Se a despesa estiver em outra moeda, converte-se para BRL usando `envelope/cambio.json` na data da despesa. Se não houver taxa para aquela data ou moeda, a despesa é recusada integralmente.

**O que estava ambíguo:**

O envelope v4 dizia para usar taxa da data da despesa, mas não detalhava se o lote inteiro deveria falhar quando faltasse cotação, nem se `moeda` ausente significava BRL.

**Como percebi:**

Revendo o envelope e as decisões já registradas em `specs/001-motor-reembolso/spec.md` e em `docs/sessions/16-conversao-moeda-envelope.md`, observei que havia duas interpretações plausíveis e que o comportamento precisava ser documentado.

**Commit da mudança:** `06279c0`

---

## Discernimento

*Onde o Claude errou e você pegou.*

> **Sem um caso concreto e verificável, esta seção vale zero.** Não existe projeto
> de dois dias em que o modelo acertou tudo. A ausência do caso não prova que o
> modelo foi perfeito — prova que ninguém estava conferindo.

### Caso 1

**O que ele propôs:**

Aplicar a política externa do envelope sem questionar se as categorias eram fixas e se `moeda` ausente deveria ser tratada como BRL.

**Por que estava errado:**

O envelope v4 traz categorias dinâmicas (`representacao`) e limites que variam por centro de custo. A implementação inicial ainda assumia categorias fixas e BRL único.

**Como eu detectei:**

Lendo `specs/001-motor-reembolso/spec.md` e `docs/sessions/17-politica-dinamica.md`, comparei com `envelope/politica-v4.json` e percebi que o código precisava suportar a política dinâmica completa.

**O que eu fiz:**

Atualizei `src/politica.py` para carregar limites dinamicamente, ajustei `src/regras.py` para usar a política por centro de custo e escrevi testes em `tests/test_politica.py`.

**Onde está a evidência:**

`docs/sessions/17-politica-dinamica.md`, `specs/001-motor-reembolso/spec.md`, `src/politica.py`, `src/regras.py`, `tests/test_politica.py`.

### Caso 2

**Padrão que eu notei:**

O modelo tende a manter suposições anteriores sobre domínio quando o envelope muda o requisito. Isso me deixou em alerta para revisar todas as regras afetadas, não só a carga de dados.

---

## Diligência

*O que você verificou antes de aceitar.*

**Meu procedimento de verificação:**

1. Li a task em `specs/001-motor-reembolso/tasks.md`.
2. Conferi as decisões e a spec em `specs/001-motor-reembolso/DECISIONS.md` e `specs/001-motor-reembolso/spec.md`.
3. Apliquei a implementação em `src/` e rodei `python -m pytest`.
4. Revisei o diff para confirmar que as mudanças eram consistentes com o envelope.

**Li o diff inteiro em que porcentagem das entregas?**

Li 100% do diff relacionado ao envelope e às alterações de spec/documentação.

**O que aceitei sem verificar direito, e o que me custou:**

Aceitei sem verificar o link do repositório, que não estava disponível no ambiente. Isso não afetou o código, mas deixou um campo de metadados em branco.

**Testes: quem escreveu, e como você sabe que eles testam a coisa certa?**

Eu escrevi os testes de envelope e validei que cobrem os casos esperados: moeda estrangeira, moeda ausente, taxa ausente, centro de custo desconhecido, limite zero e categorias dinâmicas.

---

## O envelope

*A mudança de requisito do Dia 2.*

**Quantos arquivos toquei na mão:** 20
**Quanto tempo levou:** cerca de 1 hora de trabalho focado
**Diff de absorção:** 20 arquivos, +865/-52 linhas (`git diff 36bc775..HEAD --stat`)

**Absorveu de graça:**

A arquitetura já separava I/O e núcleo, o que permitiu adicionar política externa e conversão de moeda sem misturar regras e parsing.

**Resistiu:**

A suposição de categorias fixas e de BRL único precisou ser quebrada. Isso exigiu mudanças em `src/politica.py`, `src/regras.py`, `src/io_json.py` e na spec.

**Ordem em que fiz:**

Documentei o envelope em spec/tasks primeiro, depois implementei e testei. A especificação e a implementação evoluíram juntas.

**Se eu tivesse escrito a spec original sabendo desta mudança:**

Eu teria iniciado o projeto com política externa e suporte a moeda opcional, em vez de começar com limites hard-coded.

**O que a spec me poupou, em concreto:**

Evitou regras ad hoc e deixou claro o fallback para `padrao`, a recusa por taxa ausente e o significado de `moeda` ausente.

---

## Fechamento

**Para qual tamanho de projeto isto valeu a pena?**

Valeu para projetos pequenos a médios com regras de negócio mutáveis e necessidade de rastreabilidade.

**Para qual não valeria?**

Não valeria para um script rápido ou protótipo descartável, onde documentação detalhada seria excesso.

**O que eu faria diferente:**

Documentaria as ambiguidades do envelope antes de tocar no código, especialmente o tratamento de `moeda` e o fallback de política.

**A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**

Preciso revisar ativamente as suposições do modelo, mesmo quando as sugestões parecem corretas. O assistente acelera, mas não substitui a revisão crítica do requisito.
