# PRD — YouTube → Obsidian Knowledge Compiler v2

Version: 2.0
Status: Ready for implementation
Base: Evolução do projeto `yt-transcript-extractor` existente
Target user: Personal use
Interface: CLI
Frontend: Obsidian Vault
LLM Provider: Claude (Anthropic API + Claude Code CLI)

---

# 1. Overview

## Objetivo

Evoluir o projeto `yt-transcript-extractor` para um **compilador de conhecimento** que:

1. Ingere vídeos, playlists ou canais do YouTube
2. Extrai e **persiste transcrições** como JSON
3. Processa transcrições com Claude para extrair conhecimento estruturado
4. Gera notas Markdown para Obsidian com summaries, conceitos e links bidirecionais
5. Mantém um grafo global de conceitos
6. Suporta reprocessamento seguro (idempotente)

O sistema atua como um **pipeline de conhecimento**: YouTube → Transcrição → IA → Obsidian.

## Decisão: Evoluir, não reescrever

O projeto atual já resolve a etapa mais complexa (extração de transcrições via yt-dlp) com código testado e funcional. A evolução adiciona novas camadas sem descartar o que já funciona.

### O que se mantém do projeto atual

- Módulo `downloader.py` — orquestração do yt-dlp
- Módulo `parser.py` — parsing de json3, vtt, srt
- Módulo `utils.py` — sanitização de nomes, logging
- Deduplicação via arquivo de archive
- Dataclasses `TranscriptResult`, `TranscriptSegment`

### O que muda

- CLI migra de `argparse` para `typer`
- Novo nome do comando: `study`
- Adição de módulos: `ai/`, `obsidian/`
- Configuração via `.env` + opções CLI
- Transcrições passam a ser salvas (JSON) além de gerar notas Obsidian

---

# 2. Requisitos Funcionais

## Core

- Ingerir vídeo individual, playlist ou canal
- Extrair transcrição via yt-dlp (manter engine atual)
- **Salvar transcrições** como JSON em diretório dedicado
- Processar transcrição com Claude para gerar:
  - TLDR (2-3 linhas)
  - Resumo detalhado (5-20 parágrafos)
  - Lista de conceitos com definições
- Gerar nota de vídeo no Obsidian vault
- Gerar/atualizar notas de conceitos globais
- Criar links bidirecionais entre notas
- Prevenir duplicação (idempotência)
- Todo conteúdo gerado em **Português (pt-BR)**

## Modos de operação

O pipeline tem etapas independentes que podem ser executadas separadamente:

```
study ingest video <url>           # Extrai transcrição + processa com IA + gera notas
study ingest playlist <url>        # Mesmo para playlist
study ingest channel <url>         # Mesmo para canal

study transcript video <url>       # Apenas extrai e salva transcrição (sem IA)
study transcript playlist <url>    # Mesmo para playlist
study transcript channel <url>     # Mesmo para canal

study process <video_id>           # Processa transcrição existente com IA
study process --all                # Processa todas as transcrições pendentes
```

---

# 3. Integração com Claude

## Dois backends suportados

### Backend 1: Anthropic API (padrão)

- Biblioteca: `anthropic`
- Modelo padrão: `claude-sonnet-4-5-20250929` (configurável)
- Requer: `ANTHROPIC_API_KEY` em `.env`
- Vantagem: structured output confiável, retry automático
- Formato de resposta: JSON com schema validado

### Backend 2: Claude Code CLI

- Invocação: `claude -p "<prompt>" --output-format json`
- Usa a assinatura do usuário (Pro/Max) sem custos adicionais de API
- Requer: `claude` CLI instalado e autenticado
- Vantagem: sem custo extra para quem tem assinatura
- Desvantagem: mais lento, menos controle sobre formato

### Configuração

```bash
# No .env
CLAUDE_BACKEND=api          # "api" ou "cli"
ANTHROPIC_API_KEY=sk-...    # Necessário apenas se CLAUDE_BACKEND=api
CLAUDE_MODEL=claude-sonnet-4-5-20250929  # Modelo para backend API
```

```bash
# Override via CLI
study ingest video <url> --backend cli
study ingest video <url> --backend api --model claude-sonnet-4-5-20250929
```

## Prompt e formato de resposta

Claude DEVE retornar JSON válido:

```json
{
  "tldr": "string (pt-BR)",
  "summary": "string em Markdown (pt-BR)",
  "concepts": [
    {
      "name": "string",
      "definition": "string (pt-BR)"
    }
  ]
}
```

O sistema DEVE validar o JSON. Em caso de resposta inválida:
- Backend API: retry até 3 vezes
- Backend CLI: retry até 2 vezes, depois falha graciosamente

---

# 4. Estrutura do Vault Obsidian

```
Vault/
  Sources/
    YouTube/
      {channel_name}/
        {channel_name}.md           # Index do canal
        Videos/
          {video_title}.md          # Nota do vídeo

  Concepts/
    {concept_name}.md               # Nota do conceito global
```

---

# 5. Estrutura da Nota de Vídeo

Path: `Sources/YouTube/{channel}/Videos/{video}.md`

### Frontmatter

```yaml
---
type: youtube_video
video_id: "dQw4w9WgXcQ"
title: "Video Title"
channel: "Channel Name"
url: "https://youtube.com/watch?v=dQw4w9WgXcQ"
upload_date: "2024-01-15"
created: "2025-02-16T10:30:00"
updated: "2025-02-16T10:30:00"
concepts:
  - "[[Conceito A]]"
  - "[[Conceito B]]"
tags:
  - youtube
status: complete
---
```

### Body

```markdown
# Video Title

## TLDR

Resumo curto (2-3 linhas).

---

## Resumo

Resumo detalhado em múltiplos parágrafos...

---

## Conceitos

- [[Conceito A]]
- [[Conceito B]]
```

---

# 6. Estrutura da Nota de Conceito

Path: `Concepts/{concept}.md`

### Frontmatter

```yaml
---
type: concept
name: "Conceito A"
created: "2025-02-16T10:30:00"
updated: "2025-02-16T10:30:00"
sources:
  - "[[Video Title]]"
tags:
  - concept
---
```

### Body

```markdown
# Conceito A

## Definição

Definição clara e concisa.

## Explicado em

- [[Video Title]]
```

---

# 7. Estrutura da Nota do Canal

Path: `Sources/YouTube/{channel}/{channel}.md`

### Frontmatter

```yaml
---
type: youtube_channel
name: "Channel Name"
url: "https://youtube.com/@channel"
created: "2025-02-16T10:30:00"
updated: "2025-02-16T10:30:00"
tags:
  - youtube
  - channel
---
```

### Body

```markdown
# Channel Name

## Vídeos Processados

- [[Video Title 1]]
- [[Video Title 2]]
```

---

# 8. Persistência de Transcrições

Transcrições DEVEM ser salvas como JSON. Diretório:

```
data/
  transcripts/
    {channel_name}/
      {video_id}.json
```

Formato do JSON:

```json
{
  "id": "video_id",
  "title": "Video Title",
  "channel": "Channel Name",
  "upload_date": "20240115",
  "webpage_url": "https://youtube.com/watch?v=...",
  "transcript": [
    {
      "text": "texto do segmento",
      "start": 0.0,
      "duration": 2.5
    }
  ],
  "full_text": "Texto completo concatenado da transcrição..."
}
```

O campo `full_text` é a concatenação de todos os segmentos, usado como input para o Claude.

---

# 9. Idempotência

### Regras de deduplicação

Identificador primário: `video_id`

**Transcrições:**
- Se transcrição já existe em `data/transcripts/`: NÃO recriar
- Flag `--force` permite re-extrair

**Notas de vídeo:**
- Se nota já existe no vault: NÃO recriar
- Flag `--reprocess` permite regenerar com Claude

**Notas de conceito:**
- Se conceito existe: APENAS atualizar lista de sources
- NUNCA recriar ou sobrescrever definição

**Arquivo de archive:** Mantido em `data/archive.txt` para rastrear vídeos já processados pelo yt-dlp.

**Arquivo de estado do processamento:** `data/processing_state.json`

```json
{
  "video_id": {
    "transcript_extracted": true,
    "ai_processed": true,
    "notes_generated": true,
    "last_processed": "2025-02-16T10:30:00"
  }
}
```

---

# 10. Estrutura do Codebase

```
src/study/
  __init__.py
  __main__.py

  cli/
    __init__.py
    main.py              # App typer + grupo de comandos
    ingest.py            # Comandos: ingest video/playlist/channel
    transcript.py        # Comandos: transcript video/playlist/channel
    process.py           # Comandos: process <id> / --all

  transcript/
    __init__.py
    extractor.py         # Orquestração yt-dlp (evoluído de downloader.py)
    parser.py            # Parsing json3/vtt/srt (mantido)
    storage.py           # Persistência de transcrições em JSON

  ai/
    __init__.py
    base.py              # Interface abstrata para backends
    api_backend.py       # Backend Anthropic API
    cli_backend.py       # Backend Claude Code CLI
    prompts.py           # Templates de prompts
    schemas.py           # Validação de resposta JSON

  obsidian/
    __init__.py
    vault.py             # Operações no vault (paths, criação de dirs)
    video_note.py        # Geração de nota de vídeo
    concept_note.py      # Geração/atualização de nota de conceito
    channel_note.py      # Geração/atualização de nota do canal
    frontmatter.py       # Serialização/desserialização YAML frontmatter

  core/
    __init__.py
    config.py            # Configuração central (dataclasses + .env)
    models.py            # Modelos de domínio (TranscriptResult, AIResponse, etc.)
    state.py             # Estado de processamento (idempotência)
    utils.py             # Utilitários (sanitização, logging)
```

---

# 11. CLI Interface

Framework: `typer`

### Comandos

```bash
# Pipeline completo: transcrição + IA + notas
study ingest video <url> [--backend api|cli] [--lang pt] [--verbose]
study ingest playlist <url> [--backend api|cli] [--after YYYYMMDD]
study ingest channel <url> [--backend api|cli] [--after YYYYMMDD]

# Apenas transcrição (sem IA)
study transcript video <url> [--lang en] [--format json3]
study transcript playlist <url>
study transcript channel <url> [--after YYYYMMDD]

# Processar transcrições existentes com IA
study process <video_id> [--backend api|cli] [--reprocess]
study process --all [--backend api|cli]

# Utilidades
study status                       # Mostra estado: transcrições pendentes, notas geradas
study config                       # Mostra configuração atual
```

---

# 12. Configuração

Arquivo `.env` na raiz do projeto:

```bash
# Obrigatório
VAULT_PATH=/caminho/absoluto/para/vault

# Claude Backend (api ou cli)
CLAUDE_BACKEND=api

# Necessário se CLAUDE_BACKEND=api
ANTHROPIC_API_KEY=sk-ant-...

# Opcionais
CLAUDE_MODEL=claude-sonnet-4-5-20250929
TRANSCRIPT_LANG=en
SUBTITLE_FORMAT=json3
CONTENT_LANG=pt-BR
```

---

# 13. Dependências

Python: `>=3.11`

```
# Core
yt-dlp>=2024.0
typer>=0.9.0
rich>=13.0              # Output formatado no terminal (já é dependência do typer)
anthropic>=0.40.0
python-dotenv>=1.0
pyyaml>=6.0

# Dev
pytest>=7.0
```

---

# 14. Pipeline de Processamento

### Etapa 1 — Extração de transcrição

```
Input: URL do YouTube
  ↓
yt-dlp: fetch metadata + subtitles (sem baixar vídeo)
  ↓
Parser: json3/vtt/srt → TranscriptResult
  ↓
Storage: salva JSON em data/transcripts/{channel}/{video_id}.json
  ↓
State: marca transcript_extracted=true
```

### Etapa 2 — Processamento com Claude

```
Input: TranscriptResult (full_text)
  ↓
Backend (API ou CLI): envia prompt com transcrição
  ↓
Validação: verifica JSON de resposta
  ↓
Output: AIResponse (tldr, summary, concepts)
  ↓
State: marca ai_processed=true
```

### Etapa 3 — Geração de notas Obsidian

```
Input: TranscriptResult + AIResponse
  ↓
video_note.py: cria/atualiza nota do vídeo
  ↓
concept_note.py: cria novos conceitos / atualiza sources dos existentes
  ↓
channel_note.py: atualiza index do canal
  ↓
State: marca notes_generated=true
```

---

# 15. Tratamento de Erros

O sistema DEVE:

- Continuar processando itens restantes se um vídeo falhar
- Logar erros com contexto (video_id, etapa que falhou)
- Salvar progresso parcial (ex: transcrição extraída mesmo se IA falhar)
- Retry em falhas de API (max 3 tentativas com backoff)
- Validar JSON de resposta do Claude antes de gerar notas
- Falhar graciosamente se vault path não existir

---

# 16. Ordem de Implementação

### Fase 1 — Reestruturação base
1. Reorganizar codebase na nova estrutura de diretórios
2. Migrar CLI de argparse para typer
3. Implementar configuração via .env
4. Implementar modelos de domínio (`core/models.py`)
5. Implementar estado de processamento (`core/state.py`)

### Fase 2 — Persistência de transcrições
6. Implementar `transcript/storage.py`
7. Adaptar `transcript/extractor.py` para salvar transcrições
8. Implementar comando `study transcript`
9. Gerar campo `full_text` concatenado

### Fase 3 — Integração Claude
10. Implementar `ai/base.py` (interface abstrata)
11. Implementar `ai/api_backend.py` (Anthropic API)
12. Implementar `ai/cli_backend.py` (Claude Code CLI)
13. Implementar `ai/prompts.py` (templates)
14. Implementar `ai/schemas.py` (validação)
15. Implementar comando `study process`

### Fase 4 — Geração Obsidian
16. Implementar `obsidian/vault.py`
17. Implementar `obsidian/frontmatter.py`
18. Implementar `obsidian/video_note.py`
19. Implementar `obsidian/concept_note.py`
20. Implementar `obsidian/channel_note.py`

### Fase 5 — Pipeline completo
21. Implementar comando `study ingest` (pipeline completo)
22. Implementar `study status`
23. Testes de integração
24. Documentação de uso

---

# 17. Critérios de Sucesso

O sistema é considerado funcional quando:

- `study transcript video <url>` extrai e salva transcrição como JSON
- `study ingest video <url>` gera nota completa no Obsidian com conceitos
- Reprocessamento não cria duplicatas
- Conceitos são linkados bidirecionalmente
- Backend CLI funciona com assinatura Claude (sem API key)
- Backend API funciona com structured output confiável
- Vault é navegável no Obsidian com graph view funcional
- Transcrições persistidas podem ser reprocessadas independentemente

---

# 18. Roadmap Futuro

- v2.1: Suporte a Ollama como backend local
- v2.2: Embeddings para busca semântica no vault
- v2.3: Chat CLI integrado com contexto do vault
- v2.4: Plugin Obsidian para ingestão direta
- v2.5: Suporte multi-idioma (input e output)
