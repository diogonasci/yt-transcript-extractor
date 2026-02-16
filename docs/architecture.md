# Architecture

## Overview

Study is a three-stage pipeline that converts YouTube content into a structured Obsidian knowledge base.

```
                    +-------------------+
                    |   CLI (typer)     |
                    |  ingest / transcript / process  |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+   +-----v------+  +----v--------+
     | transcript/ |   |    ai/     |  |  obsidian/  |
     | extractor   |   | api_backend|  | video_note  |
     | parser      |   | cli_backend|  | concept_note|
     | storage     |   | prompts    |  | channel_note|
     +--------+----+   | schemas    |  | vault       |
              |        +-----+------+  | frontmatter |
              |              |         +----+--------+
              +--------------+--------------+
                             |
                    +--------v----------+
                    |      core/        |
                    | config  models    |
                    | state   utils     |
                    +-------------------+
```

## Pipeline stages

### 1. Transcript extraction

- Uses yt-dlp to download subtitles (no video download)
- Supports json3, vtt, and srt subtitle formats
- Parser normalizes all formats into `TranscriptSegment` objects
- `TranscriptStorage` persists results as JSON to `data/transcripts/{channel}/{video_id}.json`
- Archive file (`data/archive.txt`) prevents re-downloading

### 2. AI processing

- Two interchangeable backends behind the `AIBackend` abstract class:
  - `AnthropicAPIBackend` -- direct API calls with retry logic (3 attempts, exponential backoff)
  - `ClaudeCliBackend` -- spawns `claude -p` subprocess (2 attempts)
- Backend is selected via `CLAUDE_BACKEND` env var; factory in `ai/__init__.py`
- Prompt asks Claude to return JSON with `tldr`, `summary`, and `concepts`
- Response is validated by `schemas.py` and converted to `AIResponse` dataclass
- Results persisted to `data/ai_responses/{video_id}.json`

### 3. Obsidian note generation

- `Vault` class manages directory structure and path resolution
- Three note types:
  - **Video note**: TLDR + summary + concept links, placed in `Sources/YouTube/{channel}/Videos/`
  - **Concept note**: definition + list of source videos, placed in `Concepts/`
  - **Channel note**: index of all processed videos, placed in `Sources/YouTube/{channel}/`
- Concept notes use merge logic: existing definitions are preserved, new sources are appended
- All notes include YAML frontmatter for Obsidian metadata

## State management

`ProcessingStateManager` tracks three boolean flags per video:

| Flag | Set after |
|---|---|
| `transcript_extracted` | Transcript saved to disk |
| `ai_processed` | AI response saved to disk |
| `notes_generated` | All Obsidian notes written |

State is persisted to `data/processing_state.json` and updated immediately after each step. This enables:

- **Incremental runs**: `study process --all` skips already-processed videos
- **Crash recovery**: partial progress is preserved
- **Override flags**: `--force` (re-extract) and `--reprocess` (re-process AI + notes)

## Data models

All models are Python dataclasses (no Pydantic):

```
TranscriptSegment(text, start, duration)
TranscriptResult(id, title, channel, upload_date, webpage_url, transcript[])
Concept(name, definition)
AIResponse(tldr, summary, concepts[])
ProcessingState(video_id, transcript_extracted, ai_processed, notes_generated, updated_at)
```

## Configuration

`Settings` dataclass loaded from `.env` via python-dotenv. Validated at load time:
- `vault_path` must exist
- `claude_backend` must be `api` or `cli`
- API key required when backend is `api`

CLI flags override env vars for per-command flexibility.
