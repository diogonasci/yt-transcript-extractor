# Study

CLI that extracts YouTube transcripts, processes them with Claude AI, and generates structured notes for Obsidian with bidirectional concept linking.

```
YouTube URL  -->  Transcript (yt-dlp)  -->  Claude AI  -->  Obsidian Notes
                  json3 / vtt / srt         tldr            [[Concepts]]
                                            summary         Video notes
                                            concepts        Channel index
```

## Features

- **Transcript extraction** from videos, playlists, and channels via yt-dlp
- **AI processing** with Claude (Anthropic API or Claude Code CLI backends)
- **Obsidian note generation** with YAML frontmatter and `[[wikilinks]]`
- **Bidirectional concept linking** -- concept notes reference source videos, video notes link to concepts
- **Idempotent pipeline** -- safe to re-run without duplicating work
- **Incremental processing** -- `study process --all` picks up where it left off
- Subtitle formats: json3, vtt, srt
- Channel date filtering with `--after`

## Requirements

- Python 3.11+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- An Obsidian vault (or any folder for the Markdown output)
- Anthropic API key **or** Claude Code CLI installed

## Installation

```bash
git clone https://github.com/your-user/study-cli.git
cd study-cli

pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Required settings:

| Variable | Description |
|---|---|
| `VAULT_PATH` | Absolute path to your Obsidian vault |
| `CLAUDE_BACKEND` | `api` (Anthropic API) or `cli` (Claude Code CLI) |
| `ANTHROPIC_API_KEY` | Required when backend is `api` |

Optional settings:

| Variable | Default | Description |
|---|---|---|
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model to use |
| `TRANSCRIPT_LANG` | `en` | Subtitle language |
| `SUBTITLE_FORMAT` | `json3` | Subtitle format (`json3`, `vtt`, `srt`) |
| `CONTENT_LANG` | `pt-BR` | Language for generated notes |
| `DATA_DIR` | `data` | Directory for transcripts, state, and AI responses |
| `VERBOSE` | `false` | Enable verbose logging |

Verify your configuration:

```bash
study config
```

## Usage

### Full pipeline (extract + AI + notes)

```bash
# Single video
study ingest video "https://youtube.com/watch?v=VIDEO_ID"

# Entire playlist
study ingest playlist "https://youtube.com/playlist?list=PLAYLIST_ID"

# Channel (all videos)
study ingest channel "https://youtube.com/@channel"

# Channel (only videos after a date)
study ingest channel "https://youtube.com/@channel" --after 20240101
```

### Extract transcripts only (no AI)

```bash
study transcript video "https://youtube.com/watch?v=VIDEO_ID"
study transcript playlist "https://youtube.com/playlist?list=PLAYLIST_ID"
study transcript channel "https://youtube.com/@channel"
```

### Process existing transcripts with AI

```bash
# Single video by ID
study process VIDEO_ID

# All pending transcripts
study process --all
```

### Check status

```bash
study status
```

### Common flags

| Flag | Description |
|---|---|
| `--backend api\|cli` | Override AI backend |
| `--model MODEL` | Override Claude model |
| `--lang LANG` | Subtitle language |
| `--format FMT` | Subtitle format |
| `--after YYYYMMDD` | Only videos after this date (channels) |
| `--force` | Re-extract transcripts even if archived |
| `--reprocess` | Re-run AI + notes even if already done |
| `--verbose` | Enable debug logging |

## Generated vault structure

```
Vault/
  Sources/
    YouTube/
      Channel Name/
        Channel Name.md           # Channel index with video list
        Videos/
          Video Title.md          # Video note (TLDR, summary, concepts)
  Concepts/
    Concept Name.md               # Concept definition + source videos
```

Video notes contain YAML frontmatter with metadata (video_id, URL, tags) and Markdown body with TLDR, detailed summary, and concept links. Concept notes are created or updated automatically -- existing definitions are preserved, new source videos are appended.

## Data directory

The pipeline persists intermediate results in `data/` (configurable via `DATA_DIR`):

```
data/
  transcripts/{channel}/{video_id}.json   # Raw transcripts
  ai_responses/{video_id}.json            # Claude AI output
  processing_state.json                   # Pipeline state tracking
  archive.txt                             # yt-dlp deduplication
```

This enables incremental processing. If the AI step fails mid-batch, already-extracted transcripts are preserved and `study process --all` picks up the remaining ones.

## Project structure

```
src/study/
  cli/            # CLI commands (typer)
  transcript/     # Extraction, parsing, storage (yt-dlp)
  ai/             # Claude integration (API + CLI backends)
  obsidian/       # Note generation (video, concept, channel)
  core/           # Config, models, state, utilities

tests/            # 148 tests (pytest)
docs/             # PRD, architecture, tasks
```

## Running tests

```bash
python -m pytest tests/ -v
```

All tests use mocks for external dependencies (yt-dlp, Anthropic API, filesystem) and run without network access.

## License

MIT
