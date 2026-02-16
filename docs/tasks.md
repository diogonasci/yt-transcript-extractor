# Tarefas de Implementacao — Study CLI

Status: `[ ]` pendente | `[x]` concluido | `[-]` pulado

Referencia: `docs/prd-v2.md`

---

## FASE 1 — Reestruturacao base

Objetivo: Migrar a estrutura do projeto de `yt_transcript_extractor` para `study`, sem quebrar funcionalidade existente.

---

### Tarefa 1.1 — Criar estrutura de diretorios e pyproject.toml

Status: `[x]`

**O que fazer:**

Criar a arvore de diretorios do novo projeto e atualizar `pyproject.toml`.

**Acoes:**

1. Criar a arvore de diretorios:
   ```
   src/study/
     __init__.py
     __main__.py
     cli/
       __init__.py
     transcript/
       __init__.py
     ai/
       __init__.py
     obsidian/
       __init__.py
     core/
       __init__.py
   ```
2. Cada `__init__.py` pode ser vazio por enquanto
3. `__main__.py` conteudo minimo:
   ```python
   from study.cli.main import app

   if __name__ == "__main__":
       app()
   ```
4. Atualizar `pyproject.toml`:
   - name: `study-cli`
   - dependencies: `yt-dlp>=2024.0`, `typer>=0.9.0`, `anthropic>=0.40.0`, `python-dotenv>=1.0`, `pyyaml>=6.0`
   - dev: `pytest>=7.0`
   - script entry point: `study = "study.cli.main:app"`
   - requires-python: `>=3.11`
5. NAO remover `src/yt_transcript_extractor/` ainda (sera removido na Tarefa 1.6)

**Criterios de aceite:**

- Diretorio `src/study/` existe com todos os subdiretorios
- `pyproject.toml` atualizado com novas deps e entry point
- `pip install -e ".[dev]"` funciona sem erro

---

### Tarefa 1.2 — Implementar core/config.py

Status: `[x]`

**O que fazer:**

Criar a configuracao central que carrega do `.env` e fornece defaults.

**Arquivos a criar:** `src/study/core/config.py`

**Arquivos de referencia:** `src/yt_transcript_extractor/config.py` (ver padroes existentes)

**Implementar:**

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Settings:
    vault_path: Path
    claude_backend: str          # "api" ou "cli"
    anthropic_api_key: str       # pode ser vazio se backend=cli
    claude_model: str            # default: "claude-sonnet-4-5-20250929"
    transcript_lang: str         # default: "en"
    subtitle_format: str         # default: "json3"
    content_lang: str            # default: "pt-BR"
    data_dir: Path               # default: Path("data")
    archive_file: Path           # default: Path("data/archive.txt")
    verbose: bool                # default: False

def load_settings(**overrides) -> Settings:
    """Load settings from .env file, with CLI overrides."""
    # 1. Carregar .env com python-dotenv
    # 2. Ler variaveis de ambiente
    # 3. Aplicar overrides dos argumentos CLI
    # 4. Validar: vault_path deve existir, backend deve ser "api" ou "cli"
    # 5. Retornar Settings
```

**Criterios de aceite:**

- `load_settings()` carrega do `.env` corretamente
- Overrides via kwargs sobrescrevem valores do `.env`
- Validacao levanta `ValueError` se `vault_path` nao existir
- Validacao levanta `ValueError` se `claude_backend` nao for "api" ou "cli"
- Teste em `tests/test_config.py` cobre os cenarios acima

---

### Tarefa 1.3 — Implementar core/models.py

Status: `[x]`

**O que fazer:**

Criar os modelos de dominio usados por todo o projeto.

**Arquivos a criar:** `src/study/core/models.py`

**Implementar:**

```python
from dataclasses import dataclass, field

@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float

@dataclass
class TranscriptResult:
    id: str                      # video_id
    title: str
    channel: str
    upload_date: str             # YYYYMMDD
    webpage_url: str
    transcript: list[TranscriptSegment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenated transcript text for AI processing."""
        return " ".join(seg.text for seg in self.transcript)

@dataclass
class Concept:
    name: str
    definition: str

@dataclass
class AIResponse:
    tldr: str
    summary: str
    concepts: list[Concept] = field(default_factory=list)

@dataclass
class ProcessingState:
    video_id: str
    transcript_extracted: bool = False
    ai_processed: bool = False
    notes_generated: bool = False
    last_processed: str = ""     # ISO8601
```

**Criterios de aceite:**

- Todos os dataclasses acima existem e sao importaveis
- `TranscriptResult.full_text` concatena textos dos segmentos com espaco
- Teste em `tests/test_models.py` valida `full_text` e criacao basica

---

### Tarefa 1.4 — Implementar core/utils.py

Status: `[x]`

**O que fazer:**

Migrar utilitarios existentes de `yt_transcript_extractor/utils.py` para `study/core/utils.py`.

**Arquivos de referencia:** `src/yt_transcript_extractor/utils.py`
**Arquivos a criar:** `src/study/core/utils.py`

**Acoes:**

1. Copiar `sanitize_filename()`, `setup_logging()` de `yt_transcript_extractor/utils.py`
2. Mudar o logger name de `yt_transcript_extractor` para `study`
3. Remover `build_output_path()` — sera substituido por logica nova no storage

**Criterios de aceite:**

- `sanitize_filename()` funciona identico ao original
- `setup_logging()` usa logger name `study`
- Teste em `tests/test_utils.py` (adaptar do existente)

---

### Tarefa 1.5 — Implementar core/state.py

Status: `[x]`

**O que fazer:**

Criar o gerenciador de estado de processamento para idempotencia.

**Arquivos a criar:** `src/study/core/state.py`

**Implementar:**

```python
class ProcessingStateManager:
    def __init__(self, state_file: Path):
        """Load state from JSON file."""

    def get(self, video_id: str) -> ProcessingState | None:
        """Get processing state for a video."""

    def update(self, video_id: str, **kwargs) -> None:
        """Update state fields for a video and persist."""

    def is_transcript_extracted(self, video_id: str) -> bool:
    def is_ai_processed(self, video_id: str) -> bool:
    def is_notes_generated(self, video_id: str) -> bool:

    def pending_ai_processing(self) -> list[str]:
        """Return video_ids with transcript but not yet AI processed."""

    def _save(self) -> None:
        """Persist state to JSON file."""
```

State file: `data/processing_state.json`

**Criterios de aceite:**

- Estado persiste em JSON e sobrevive restart
- `update()` salva imediatamente
- `pending_ai_processing()` retorna lista correta
- Teste em `tests/test_state.py` cobre create/read/update e pending

---

### Tarefa 1.6 — Implementar CLI base com typer

Status: `[x]`

Depende de: 1.1, 1.2

**O que fazer:**

Criar a estrutura CLI com typer, com grupos de comandos vazios (stubs).

**Arquivos a criar:**
- `src/study/cli/main.py`
- `src/study/cli/ingest.py`
- `src/study/cli/transcript.py`
- `src/study/cli/process.py`

**Implementar:**

`main.py`:
```python
import typer

app = typer.Typer(name="study", help="YouTube -> Obsidian Knowledge Compiler")

# Registrar subcomandos
app.add_typer(ingest_app, name="ingest")
app.add_typer(transcript_app, name="transcript")
app.add_typer(process_app, name="process")

@app.command()
def status():
    """Show processing status."""
    typer.echo("Status: not implemented yet")

@app.command()
def config():
    """Show current configuration."""
    typer.echo("Config: not implemented yet")
```

`ingest.py` (stubs):
```python
ingest_app = typer.Typer(help="Full pipeline: transcript + AI + notes")

@ingest_app.command()
def video(url: str): ...

@ingest_app.command()
def playlist(url: str): ...

@ingest_app.command()
def channel(url: str, after: str = None): ...
```

Mesmo padrao para `transcript.py` e `process.py`.

**Criterios de aceite:**

- `study --help` mostra comandos disponiveis
- `study ingest --help` mostra subcomandos video/playlist/channel
- `study transcript --help` mostra subcomandos
- `study process --help` mostra subcomandos
- Todos os comandos existem como stubs (print + exit)

---

### Tarefa 1.7 — Remover codigo antigo e adaptar testes

Status: `[x]`

Depende de: 1.1 a 1.6

**O que fazer:**

Remover `src/yt_transcript_extractor/` e adaptar testes para importar de `study.*`.

**Acoes:**

1. Remover diretorio `src/yt_transcript_extractor/` inteiro
2. Atualizar todos os arquivos em `tests/` para importar de `study.*`
3. Adaptar `tests/test_cli.py` para testar comandos typer (usar `typer.testing.CliRunner`)
4. Manter `tests/conftest.py` com sample data (SAMPLE_JSON3, SAMPLE_VTT, etc.)
5. Rodar `python -m pytest tests/ -v` — tudo deve passar

**Criterios de aceite:**

- `src/yt_transcript_extractor/` nao existe mais
- Todos os testes importam de `study.*`
- `python -m pytest tests/ -v` passa sem erros
- `study --help` funciona

---

## FASE 2 — Persistencia de transcricoes

Objetivo: Extrair transcricoes do YouTube e salvar como JSON em `data/transcripts/`.

---

### Tarefa 2.1 — Migrar extractor (downloader.py) para transcript/extractor.py

Status: `[ ]`

Depende de: Fase 1

**O que fazer:**

Mover a logica de extracao de `yt_transcript_extractor/downloader.py` para `study/transcript/extractor.py`, adaptando para usar os novos modelos e config.

**Arquivos de referencia:** `src/yt_transcript_extractor/downloader.py`
**Arquivos a criar:** `src/study/transcript/extractor.py`

**Acoes:**

1. Copiar funcoes de `downloader.py`: `_build_ydl_opts`, `_find_subtitle_file`, `_detect_format`, `_flatten_entries`, `extract_transcripts`, `extract_channel`, `extract_playlist`
2. Adaptar para usar `Settings` ao inves de `ExtractorConfig`
3. Adaptar para usar `TranscriptResult` e `TranscriptSegment` de `study.core.models`
4. Remover logica de `_is_archived` / `_record_in_archive` desta funcao — sera responsabilidade do `ProcessingStateManager`
5. A funcao `_process_entry` NAO deve mais escrever arquivo diretamente — deve retornar `TranscriptResult` apenas
6. Manter logica de archive do yt-dlp (opcao `download_archive` no ydl_opts) para evitar re-download

**Criterios de aceite:**

- `extract_transcripts(urls, settings)` retorna lista de `TranscriptResult`
- Nao escreve arquivos — apenas retorna dados
- Testes adaptados de `test_downloader.py` passam

---

### Tarefa 2.2 — Migrar parser para transcript/parser.py

Status: `[ ]`

Depende de: Fase 1

**O que fazer:**

Mover `yt_transcript_extractor/parser.py` para `study/transcript/parser.py`.

**Arquivos de referencia:** `src/yt_transcript_extractor/parser.py`
**Arquivos a criar:** `src/study/transcript/parser.py`

**Acoes:**

1. Copiar `parse_json3`, `parse_vtt`, `parse_srt`, `parse_subtitle_file`
2. Copiar `result_to_dict`
3. Adaptar imports para `study.core.models`
4. Remover `write_result` daqui — escrita de arquivo sera responsabilidade do `storage.py`

**Criterios de aceite:**

- Todos os parsers funcionam identico ao original
- Testes adaptados de `test_parser.py` passam

---

### Tarefa 2.3 — Implementar transcript/storage.py

Status: `[ ]`

Depende de: 1.3, 2.2

**O que fazer:**

Criar modulo de persistencia de transcricoes em JSON.

**Arquivos a criar:** `src/study/transcript/storage.py`

**Implementar:**

```python
class TranscriptStorage:
    def __init__(self, data_dir: Path):
        self.base_dir = data_dir / "transcripts"

    def save(self, result: TranscriptResult) -> Path:
        """Save transcript as JSON. Returns path to saved file.
        Path: data/transcripts/{channel}/{video_id}.json
        Include full_text field in the JSON."""

    def load(self, video_id: str) -> TranscriptResult | None:
        """Load transcript by video_id. Search all channel dirs."""

    def exists(self, video_id: str) -> bool:
        """Check if transcript already exists."""

    def list_all(self) -> list[str]:
        """Return all video_ids that have saved transcripts."""

    def get_path(self, channel: str, video_id: str) -> Path:
        """Build the storage path for a transcript."""
```

Formato do JSON salvo:
```json
{
  "id": "video_id",
  "title": "...",
  "channel": "...",
  "upload_date": "...",
  "webpage_url": "...",
  "transcript": [...segments...],
  "full_text": "texto completo concatenado"
}
```

**Criterios de aceite:**

- `save()` cria arquivo JSON com full_text incluso
- `load()` reconstroi `TranscriptResult` a partir do JSON
- `exists()` retorna True/False corretamente
- `list_all()` retorna todos os video_ids salvos
- Teste em `tests/test_storage.py`

---

### Tarefa 2.4 — Implementar comando `study transcript`

Status: `[ ]`

Depende de: 1.6, 2.1, 2.2, 2.3

**O que fazer:**

Implementar os comandos `study transcript video/playlist/channel` que extraem e salvam transcricoes.

**Arquivos a modificar:** `src/study/cli/transcript.py`

**Logica de cada comando:**

```
1. Carregar Settings
2. Criar TranscriptStorage e ProcessingStateManager
3. Chamar extract_transcripts() para obter TranscriptResult[]
4. Para cada result:
   a. Se state.is_transcript_extracted(result.id) e nao --force: skip
   b. storage.save(result)
   c. state.update(result.id, transcript_extracted=True)
5. Imprimir resumo: X transcricoes extraidas, Y ja existiam
```

**Opcoes CLI:**
- `--lang` (default: en)
- `--format` (default: json3)
- `--after` (apenas channel)
- `--force` (re-extrair mesmo se ja existe)
- `--verbose`

**Criterios de aceite:**

- `study transcript video <url>` extrai e salva JSON em `data/transcripts/`
- Transcricao ja existente e pulada (sem --force)
- `--force` re-extrai e sobrescreve
- Estado atualizado em `processing_state.json`
- Output no terminal mostra progresso

---

## FASE 3 — Integracao Claude

Objetivo: Processar transcricoes com Claude para gerar TLDR, resumo e conceitos.

---

### Tarefa 3.1 — Implementar ai/base.py (interface abstrata)

Status: `[ ]`

Depende de: 1.3

**O que fazer:**

Criar a interface abstrata que ambos os backends implementam.

**Arquivos a criar:** `src/study/ai/base.py`

**Implementar:**

```python
from abc import ABC, abstractmethod

class AIBackend(ABC):
    @abstractmethod
    def process_transcript(self, transcript_text: str, video_title: str) -> AIResponse:
        """Send transcript to AI and return structured response."""

    def _build_prompt(self, transcript_text: str, video_title: str) -> str:
        """Build the prompt for the AI. Shared by all backends."""
        # Usar template de ai/prompts.py
```

**Criterios de aceite:**

- Interface abstrata definida
- Metodo `_build_prompt` implementado na base class (nao abstrato)

---

### Tarefa 3.2 — Implementar ai/prompts.py

Status: `[ ]`

**O que fazer:**

Criar os templates de prompts para o Claude.

**Arquivos a criar:** `src/study/ai/prompts.py`

**Implementar:**

```python
SYSTEM_PROMPT = """You are a knowledge extraction assistant. ..."""

USER_PROMPT_TEMPLATE = """
Analise a transcricao do video "{title}" e retorne um JSON com:

1. "tldr": Resumo de 2-3 linhas em portugues (pt-BR)
2. "summary": Resumo detalhado em Markdown, 5-20 paragrafos, em portugues (pt-BR)
3. "concepts": Lista de conceitos-chave, cada um com "name" e "definition" em portugues

Transcricao:
---
{transcript}
---

Retorne APENAS o JSON valido, sem markdown code fences.
"""
```

**Criterios de aceite:**

- Prompts definidos como constantes
- Template usa placeholders `{title}` e `{transcript}`
- Instrucoes claras para retornar JSON valido em pt-BR

---

### Tarefa 3.3 — Implementar ai/schemas.py

Status: `[ ]`

Depende de: 1.3

**O que fazer:**

Criar validacao do JSON de resposta do Claude.

**Arquivos a criar:** `src/study/ai/schemas.py`

**Implementar:**

```python
def validate_ai_response(data: dict) -> AIResponse:
    """Validate and parse AI response dict into AIResponse.
    Raises ValueError if format is invalid."""
    # Verificar campos obrigatorios: tldr, summary, concepts
    # Verificar que concepts e lista de dicts com name e definition
    # Retornar AIResponse

def parse_ai_response(raw_text: str) -> AIResponse:
    """Parse raw text response (possibly with markdown fences) into AIResponse."""
    # Limpar markdown code fences se presentes
    # Fazer json.loads
    # Chamar validate_ai_response
```

**Criterios de aceite:**

- `parse_ai_response` aceita JSON puro e JSON envolto em ```json ... ```
- Levanta `ValueError` para JSON invalido ou campos faltando
- Teste em `tests/test_schemas.py` com exemplos validos e invalidos

---

### Tarefa 3.4 — Implementar ai/api_backend.py (Anthropic API)

Status: `[ ]`

Depende de: 3.1, 3.2, 3.3

**O que fazer:**

Implementar o backend que usa a biblioteca `anthropic` para chamar a API.

**Arquivos a criar:** `src/study/ai/api_backend.py`

**Implementar:**

```python
class AnthropicAPIBackend(AIBackend):
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def process_transcript(self, transcript_text: str, video_title: str) -> AIResponse:
        # 1. Build prompt
        # 2. Call API com retry (max 3)
        # 3. Parse response
        # 4. Validate
        # 5. Return AIResponse
```

**Criterios de aceite:**

- Chama API Anthropic com system prompt + user prompt
- Retry ate 3 vezes em caso de erro
- Parse e valida resposta JSON
- Teste com mock do client anthropic em `tests/test_api_backend.py`

---

### Tarefa 3.5 — Implementar ai/cli_backend.py (Claude Code CLI)

Status: `[ ]`

Depende de: 3.1, 3.2, 3.3

**O que fazer:**

Implementar o backend que invoca `claude` CLI como subprocesso.

**Arquivos a criar:** `src/study/ai/cli_backend.py`

**Implementar:**

```python
class ClaudeCliBackend(AIBackend):
    def process_transcript(self, transcript_text: str, video_title: str) -> AIResponse:
        # 1. Build prompt
        # 2. Invocar: subprocess.run(["claude", "-p", prompt, "--output-format", "json"], ...)
        # 3. Capturar stdout
        # 4. Parse response (o output pode ter formato diferente do API)
        # 5. Validate
        # 6. Return AIResponse
```

**Criterios de aceite:**

- Invoca `claude -p` como subprocesso
- Captura output e faz parse
- Retry ate 2 vezes
- Erro claro se `claude` nao estiver instalado
- Teste com mock de subprocess em `tests/test_cli_backend.py`

---

### Tarefa 3.6 — Implementar factory de backend e comando `study process`

Status: `[ ]`

Depende de: 3.4, 3.5, 1.5, 2.3

**O que fazer:**

1. Criar factory function que retorna o backend correto baseado na config
2. Implementar comando `study process`

**Arquivos a criar/modificar:**
- `src/study/ai/__init__.py` — factory
- `src/study/cli/process.py` — comando

**Factory:**
```python
def create_backend(settings: Settings) -> AIBackend:
    if settings.claude_backend == "api":
        return AnthropicAPIBackend(settings.anthropic_api_key, settings.claude_model)
    elif settings.claude_backend == "cli":
        return ClaudeCliBackend()
    raise ValueError(f"Unknown backend: {settings.claude_backend}")
```

**Comando `study process`:**
```
study process <video_id>     # Processa uma transcricao
study process --all           # Processa todas as pendentes
```

Logica:
```
1. Carregar Settings, Storage, StateManager
2. Criar backend via factory
3. Para cada video_id:
   a. Se state.is_ai_processed(id) e nao --reprocess: skip
   b. Carregar transcricao do storage
   c. backend.process_transcript(full_text, title)
   d. Salvar AIResponse (em data/ai_responses/{video_id}.json)
   e. state.update(id, ai_processed=True)
4. Imprimir resumo
```

**Criterios de aceite:**

- `study process <id>` processa uma transcricao
- `study process --all` processa todas as pendentes
- `--reprocess` forca reprocessamento
- AIResponse salvo em `data/ai_responses/{video_id}.json`
- Estado atualizado

---

## FASE 4 — Geracao Obsidian

Objetivo: Gerar notas Markdown estruturadas no vault do Obsidian.

---

### Tarefa 4.1 — Implementar obsidian/frontmatter.py

Status: `[ ]`

**O que fazer:**

Criar serializador/desserializador de YAML frontmatter para notas Obsidian.

**Arquivos a criar:** `src/study/obsidian/frontmatter.py`

**Implementar:**

```python
def serialize_frontmatter(metadata: dict) -> str:
    """Convert dict to YAML frontmatter string (with --- delimiters)."""

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse markdown file content into (frontmatter_dict, body_text)."""

def update_frontmatter(content: str, updates: dict) -> str:
    """Update specific frontmatter fields without touching the body."""
```

**Criterios de aceite:**

- Gera YAML frontmatter valido com delimitadores `---`
- Parse separa frontmatter do body corretamente
- Update modifica apenas campos especificados
- Teste em `tests/test_frontmatter.py`

---

### Tarefa 4.2 — Implementar obsidian/vault.py

Status: `[ ]`

Depende de: 1.2

**O que fazer:**

Criar operacoes de gerenciamento do vault.

**Arquivos a criar:** `src/study/obsidian/vault.py`

**Implementar:**

```python
class Vault:
    def __init__(self, vault_path: Path):
        self.root = vault_path
        self.sources_dir = vault_path / "Sources" / "YouTube"
        self.concepts_dir = vault_path / "Concepts"

    def ensure_structure(self) -> None:
        """Create base vault directories if they don't exist."""

    def channel_dir(self, channel_name: str) -> Path:
        """Return path: Sources/YouTube/{channel}/"""

    def video_note_path(self, channel_name: str, video_title: str) -> Path:
        """Return path: Sources/YouTube/{channel}/Videos/{title}.md"""

    def concept_note_path(self, concept_name: str) -> Path:
        """Return path: Concepts/{concept}.md"""

    def channel_note_path(self, channel_name: str) -> Path:
        """Return path: Sources/YouTube/{channel}/{channel}.md"""

    def video_note_exists(self, video_id: str) -> bool:
        """Check if a video note already exists (by scanning frontmatter)."""

    def concept_note_exists(self, concept_name: str) -> bool:
        """Check if concept note exists."""
```

**Criterios de aceite:**

- Cria estrutura de diretorios correta
- Paths seguem a convencao do PRD
- Nomes de arquivo sanitizados
- Teste em `tests/test_vault.py`

---

### Tarefa 4.3 — Implementar obsidian/video_note.py

Status: `[ ]`

Depende de: 4.1, 4.2, 1.3

**O que fazer:**

Criar gerador de notas de video.

**Arquivos a criar:** `src/study/obsidian/video_note.py`

**Implementar:**

```python
def create_video_note(
    vault: Vault,
    transcript: TranscriptResult,
    ai_response: AIResponse,
) -> Path:
    """Create or update a video note in the vault. Returns path to note."""
    # 1. Build frontmatter (type, video_id, title, channel, url, concepts, etc.)
    # 2. Build body (# Title, ## TLDR, ## Resumo, ## Conceitos)
    # 3. Write to vault path
    # 4. Return path
```

Formato conforme secao 5 do PRD.

**Criterios de aceite:**

- Nota gerada com frontmatter YAML correto
- Body contem TLDR, Resumo e Conceitos com [[links]]
- Se nota ja existe: atualiza (nao duplica)
- Teste em `tests/test_video_note.py`

---

### Tarefa 4.4 — Implementar obsidian/concept_note.py

Status: `[ ]`

Depende de: 4.1, 4.2, 1.3

**O que fazer:**

Criar gerador de notas de conceito com logica de merge.

**Arquivos a criar:** `src/study/obsidian/concept_note.py`

**Implementar:**

```python
def create_or_update_concept(
    vault: Vault,
    concept: Concept,
    source_video_title: str,
) -> Path:
    """Create concept note or add source to existing one."""
    # Se conceito NAO existe:
    #   - Criar nota com definicao e source
    # Se conceito JA existe:
    #   - Ler nota existente
    #   - Adicionar source_video_title a lista de sources (se nao ja presente)
    #   - Atualizar frontmatter.updated
    #   - NAO sobrescrever definicao
```

Formato conforme secao 6 do PRD.

**Criterios de aceite:**

- Conceito novo: cria nota completa
- Conceito existente: apenas adiciona source, nao sobrescreve definicao
- Links bidirecionais: conceito aponta para video, video aponta para conceito
- Teste em `tests/test_concept_note.py`

---

### Tarefa 4.5 — Implementar obsidian/channel_note.py

Status: `[ ]`

Depende de: 4.1, 4.2

**O que fazer:**

Criar gerador de nota-index do canal.

**Arquivos a criar:** `src/study/obsidian/channel_note.py`

**Implementar:**

```python
def create_or_update_channel(
    vault: Vault,
    channel_name: str,
    channel_url: str,
    video_title: str,
) -> Path:
    """Create channel index or add video to existing one."""
```

Formato conforme secao 7 do PRD.

**Criterios de aceite:**

- Canal novo: cria nota-index
- Canal existente: adiciona video a lista
- Nao duplica videos na lista
- Teste em `tests/test_channel_note.py`

---

## FASE 5 — Pipeline completo

Objetivo: Integrar todas as etapas e implementar o comando `study ingest`.

---

### Tarefa 5.1 — Implementar comando `study ingest`

Status: `[ ]`

Depende de: Fases 2, 3, 4

**O que fazer:**

Implementar o pipeline completo que encadeia: transcricao → IA → Obsidian.

**Arquivos a modificar:** `src/study/cli/ingest.py`

**Logica:**

```
1. Carregar Settings
2. Criar instancias: TranscriptStorage, ProcessingStateManager, AIBackend, Vault
3. Extrair transcricoes (transcript/extractor.py)
4. Para cada TranscriptResult:
   a. Salvar transcricao (storage.save)
   b. Processar com IA (backend.process_transcript)
   c. Gerar nota de video (video_note.create_video_note)
   d. Para cada conceito: criar/atualizar nota (concept_note.create_or_update_concept)
   e. Atualizar nota do canal (channel_note.create_or_update_channel)
   f. Atualizar estado (state.update com tudo = True)
5. Imprimir resumo final
```

**Opcoes CLI:**
- `--backend api|cli`
- `--model` (override modelo)
- `--lang` (idioma da transcricao)
- `--format` (formato subtitle)
- `--after` (filtro data, apenas channel)
- `--force` (re-extrair transcricao)
- `--reprocess` (re-processar com IA)
- `--verbose`

**Criterios de aceite:**

- `study ingest video <url>` executa pipeline completo
- Transcricao salva em `data/transcripts/`
- AIResponse salvo em `data/ai_responses/`
- Notas geradas no vault Obsidian
- Estado atualizado
- Idempotente: rodar de novo nao duplica nada
- Se IA falhar, transcricao ainda e salva (progresso parcial)

---

### Tarefa 5.2 — Implementar comando `study status`

Status: `[ ]`

Depende de: 1.5, 2.3

**O que fazer:**

Implementar comando que mostra o estado atual do processamento.

**Arquivos a modificar:** `src/study/cli/main.py`

**Output esperado:**

```
Study — Processing Status

Transcripts:  15 extracted
AI processed: 12 completed, 3 pending
Notes:        12 generated, 3 pending

Pending AI processing:
  - abc123 (Video Title 1)
  - def456 (Video Title 2)
  - ghi789 (Video Title 3)
```

**Criterios de aceite:**

- Mostra contadores corretos
- Lista videos pendentes com titulo
- Usa `rich` para formatacao (ja e dependencia do typer)

---

### Tarefa 5.3 — Implementar comando `study config`

Status: `[ ]`

Depende de: 1.2

**O que fazer:**

Implementar comando que mostra a configuracao atual.

**Arquivos a modificar:** `src/study/cli/main.py`

**Output esperado:**

```
Study — Configuration

Vault path:      /home/user/vault
Claude backend:  api
Claude model:    claude-sonnet-4-5-20250929
Transcript lang: en
Content lang:    pt-BR
Data dir:        data/
```

**Criterios de aceite:**

- Mostra todas as configuracoes ativas
- Indica se .env foi carregado
- Masca API key (mostra apenas ultimos 4 chars)

---

### Tarefa 5.4 — Testes de integracao

Status: `[ ]`

Depende de: 5.1

**O que fazer:**

Criar testes de integracao que validam o pipeline completo com mocks.

**Arquivos a criar:** `tests/test_integration.py`

**Cenarios a testar:**

1. Pipeline completo com mock do yt-dlp e mock do Claude
2. Idempotencia: rodar duas vezes nao duplica notas
3. Progresso parcial: IA falha mas transcricao e salva
4. Conceito compartilhado entre dois videos
5. `--force` re-extrai transcricao
6. `--reprocess` regenera notas

**Criterios de aceite:**

- Todos os cenarios acima tem teste
- Testes nao fazem chamadas reais (tudo mockado)
- `python -m pytest tests/ -v` passa

---

### Tarefa 5.5 — Criar .env.example e atualizar README

Status: `[ ]`

Depende de: 5.1

**O que fazer:**

1. Criar `.env.example` com todas as variaveis documentadas
2. Atualizar `README.md` com instrucoes de uso do novo projeto

**Criterios de aceite:**

- `.env.example` tem todas as variaveis com comentarios explicativos
- `README.md` documenta: instalacao, configuracao, uso basico, backends Claude
