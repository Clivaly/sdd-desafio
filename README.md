# Motor de Reembolso de Despesas

Este projeto calcula quanto deve ser reembolsado para despesas corporativas e produz um JSON de saída com valor reembolsável, status e justificativas.

## Executar o projeto

No terminal, rode:

```bash
python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json
```

No PowerShell:

```powershell
python -m src.cli calcular --input exemplos\despesas-exemplo.json --output resultado.json
```

O arquivo `resultado.json` será criado no diretório atual.

## Testes

Execute todos os testes com:

```bash
python -m pytest
```

## Estrutura

- `src/cli.py`: interface de linha de comando
- `src/io_json.py`: entrada/saída JSON
- `src/modelos.py`: modelos de domínio e tipos
- `src/politica.py`: parâmetros da política de reembolso
- `src/regras.py`: regras de negócio RN-001..RN-010
- `src/motor.py`: motor que aplica as regras na ordem da spec
- `tests/`: testes unitários e de integração

## O que está implementado

- Regras de limite diário para alimentação e transporte
- Reembolso parcial de despesas acima do limite
- Nota fiscal obrigatória para valores altos
- Duplicatas detectadas e tratadas
- Valores negativos ignorados
- Regras de período de competência
- Limite por diária de hospedagem
- CLI `calcular --input <arquivo> --output <arquivo>`

## Observações

- Todos os valores monetários usam `decimal.Decimal`.
- O sistema não faz I/O no núcleo de regras: só recebe e devolve objetos Python.
- O formato de saída segue o schema descrito em `specs/001-motor-reembolso/spec.md`.

## Tarefas concluídas

- T-001..T-014: implementadas e testadas
- T-015: README com instruções de instalação, execução e testes
