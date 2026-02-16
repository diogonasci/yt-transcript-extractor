# Usage Guide

## Quick start

### 1. Install

```bash
pip install -e ".[dev]"
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
VAULT_PATH=/home/user/ObsidianVault
CLAUDE_BACKEND=api
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Run

```bash
study ingest video "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

This extracts the transcript, sends it to Claude for analysis, and generates notes in your vault.

## Workflows

### Process a single video end-to-end

```bash
study ingest video "https://youtube.com/watch?v=VIDEO_ID"
```

Output:
- `data/transcripts/{channel}/{video_id}.json` -- raw transcript
- `data/ai_responses/{video_id}.json` -- Claude analysis
- `{vault}/Sources/YouTube/{channel}/Videos/{title}.md` -- video note
- `{vault}/Sources/YouTube/{channel}/{channel}.md` -- channel index (created/updated)
- `{vault}/Concepts/{concept}.md` -- one file per extracted concept (created/updated)

### Bulk process a channel

```bash
# All videos
study ingest channel "https://youtube.com/@channel"

# Only recent videos
study ingest channel "https://youtube.com/@channel" --after 20240601
```

The pipeline processes videos one at a time. If it fails midway (e.g., API rate limit), run the same command again -- already-processed videos are skipped.

### Two-step workflow (extract first, process later)

Useful when you want to review transcripts before spending API credits:

```bash
# Step 1: extract transcripts only
study transcript channel "https://youtube.com/@channel"

# Step 2: check what was extracted
study status

# Step 3: process all pending transcripts
study process --all
```

### Reprocess a video

If you change the Claude model or want fresh results:

```bash
# Reprocess one video
study ingest video "https://youtube.com/watch?v=VIDEO_ID" --reprocess

# Re-extract transcript (e.g., subtitle language changed)
study ingest video "https://youtube.com/watch?v=VIDEO_ID" --force
```

### Use Claude Code CLI instead of API

If you have a Claude Pro/Max subscription and Claude Code installed:

```bash
# Via env var
CLAUDE_BACKEND=cli

# Or per command
study ingest video "https://youtube.com/watch?v=VIDEO_ID" --backend cli
```

## Generated note examples

### Video note

```markdown
---
type: video
video_id: dQw4w9WgXcQ
title: "Video Title"
channel: Channel Name
url: https://youtube.com/watch?v=dQw4w9WgXcQ
concepts:
  - "[[Concept A]]"
  - "[[Concept B]]"
tags:
  - youtube
  - Channel Name
status: processed
created: "2024-06-15T10:30:00"
---

# Video Title

## TLDR

Brief 2-3 line summary of the video content.

## Resumo

Detailed multi-paragraph summary in Markdown...

## Conceitos

- **[[Concept A]]**: Definition of concept A.
- **[[Concept B]]**: Definition of concept B.
```

### Concept note

```markdown
---
type: concept
name: Concept A
---

# Concept A

Definition of concept A.

## Fontes

- [[Video Title]]
- [[Another Video]]
```

## Troubleshooting

### "Error: could not load settings"

Check that `.env` exists and `VAULT_PATH` points to a valid directory.

### Transcript extraction returns no results

- Verify the video has subtitles in the configured language (`TRANSCRIPT_LANG`)
- Try a different subtitle format: `--format vtt` or `--format srt`
- Check if yt-dlp is up to date: `pip install -U yt-dlp`

### AI processing fails

- **API backend**: verify `ANTHROPIC_API_KEY` is valid; check rate limits
- **CLI backend**: verify `claude` is installed and accessible in your PATH
- The pipeline retries automatically (3 attempts for API, 2 for CLI)

### Notes not appearing in Obsidian

- Confirm `VAULT_PATH` in `.env` points to your open vault
- Notes are in `Sources/YouTube/{channel}/Videos/` -- check the folder exists
- Obsidian may need a moment to index new files
