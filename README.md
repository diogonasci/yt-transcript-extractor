# yt-transcript-extractor

Extract transcripts from YouTube videos, channels, and playlists — without downloading any video.

Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) under the hood to fetch subtitles (auto-generated or manual) and outputs clean, timestamped JSON files organized by channel.

## Features

- Extract from **channels**, **playlists**, or a **list of URLs**
- Supports **json3**, **vtt**, and **srt** subtitle formats
- Outputs enriched JSON with video metadata and timestamped segments
- Built-in **deduplication** via archive file (won't re-process videos)
- Filter channel videos by **date** (`--after`)
- Files organized as `transcripts/<channel>/<date> - <title>.json`

## Installation

```bash
# Requires Python 3.10+
pip install .

# Or in development mode
pip install -e ".[dev]"
```

## Usage

### From a channel

```bash
yt-transcript-extractor channel https://www.youtube.com/@channel

# Only videos after a specific date
yt-transcript-extractor channel https://www.youtube.com/@channel --after 20240101
```

### From playlists

```bash
yt-transcript-extractor playlist https://www.youtube.com/playlist?list=PLxxxxx
```

### From a file of URLs

```bash
# urls.txt — one URL per line, lines starting with # are ignored
yt-transcript-extractor list urls.txt
```

### Common options

| Option | Default | Description |
|---|---|---|
| `--output` | `transcripts` | Output directory |
| `--lang` | `en` | Subtitle language |
| `--format` | `json3` | Subtitle source format (`json3`, `vtt`, `srt`) |
| `--archive` | `archive.txt` | Archive file for deduplication |
| `--verbose` | off | Enable verbose logging |

## Output format

Each transcript is saved as a JSON file:

```json
{
  "id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "upload_date": "20240101",
  "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "transcript": [
    {
      "text": "Hello and welcome",
      "start": 0.0,
      "duration": 2.5
    }
  ]
}
```

## Library usage

```python
from yt_transcript_extractor import ExtractorConfig, extract_transcripts

config = ExtractorConfig(lang="en", subtitle_format="json3")
results = extract_transcripts(["https://www.youtube.com/watch?v=..."], config)

for result in results:
    print(f"{result.title}: {len(result.transcript)} segments")
```

## License

MIT
