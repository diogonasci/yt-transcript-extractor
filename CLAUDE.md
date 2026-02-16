# Study — YouTube → Obsidian Knowledge Compiler

## O que é este projeto

CLI Python que extrai transcrições de vídeos do YouTube, processa com Claude (IA) e gera notas estruturadas para Obsidian com conceitos linkados bidirecionalmente.

PRD completo: `docs/prd-v2.md`
Tarefas de implementação: `docs/tasks.md`

## Como retomar o trabalho

1. Leia `docs/tasks.md` — encontre a primeira tarefa com status `[ ]` (pendente)
2. Leia a seção da tarefa para entender o que fazer
3. Marque como `[x]` ao concluir
4. Rode os testes: `python -m pytest tests/ -v`
5. Passe para a próxima tarefa

**IMPORTANTE**: Antes de iniciar qualquer tarefa, leia os arquivos listados em "Arquivos a modificar/criar" da tarefa. Nunca modifique código que você não leu.

## Estrutura do projeto

```
src/study/                    # Código-fonte principal
  cli/                        # Interface CLI (typer)
  transcript/                 # Extração e parsing de transcrições (yt-dlp)
  ai/                         # Integração com Claude (API + CLI backends)
  obsidian/                   # Geração de notas Markdown para Obsidian
  core/                       # Config, modelos, estado, utilidades

tests/                        # Testes (pytest)
data/                         # Runtime: transcrições, archive, estado
docs/                         # PRD, diagramas, tarefas
```

## Convenções de código

- Python 3.11+
- Type hints em todas as funções públicas
- Dataclasses para modelos de dados (não Pydantic)
- Imports absolutos: `from study.core.config import Settings`
- Nomes de módulos em snake_case
- Classes em PascalCase
- Constantes em UPPER_SNAKE_CASE
- Docstrings apenas em funções/classes públicas, formato de uma linha
- Testes com pytest, classes `TestNomeFuncionalidade`, sem docstrings nos testes
- Sem emojis em código ou docs
- Conteúdo gerado pelo Claude (notas Obsidian) em pt-BR
- Código e comentários em inglês

## Comandos

```bash
# Instalar em modo dev
pip install -e ".[dev]"

# Rodar testes
python -m pytest tests/ -v

# Rodar app
study ingest video <url>
study transcript video <url>
study process <video_id>
study status
```

## Regras de implementacao

- Cada tarefa em `docs/tasks.md` tem critérios de aceite claros — siga-os
- Rode testes após cada tarefa. Não passe para a próxima se testes falharem
- Não adicione dependências além das listadas no PRD sem justificativa
- Mantenha funções pequenas (< 50 linhas)
- Tratamento de erros: log + continue (não crash o pipeline inteiro)
- Ao mover código existente, garanta que testes antigos continuem passando (adapte imports)

## Arquivos de referência importantes

- `docs/prd-v2.md` — Especificação completa do que construir
- `docs/tasks.md` — Lista de tarefas ordenada com dependências
- `src/study/core/models.py` — Modelos de domínio (criado na Tarefa 1.3)
- `src/study/core/config.py` — Configuração central (criado na Tarefa 1.2)
