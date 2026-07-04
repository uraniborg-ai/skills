---
name: ub-youtube
description: Collect YouTube videos and playlists as source-preserving Markdown or JSON research notes. Use when the user provides a YouTube video, playlist, or Watch Later request; asks to summarize YouTube material; or needs captions, metadata, descriptions, playlists, or transcripts gathered for research, engineering, lectures, seminars, tutorials, and technical talks.
metadata:
  version: 0.1.0
  stability: stable
  domain: media-notes
---

# UB YouTube

Use this skill to collect YouTube source material into source-preserving
Markdown or JSON before summarizing or analyzing it.

## Workflow

1. Extract a single video transcript with the bundled script when available:

   ```sh
   uv run --script skills/ub-youtube/scripts/fetch_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.md
   ```

2. Export a playlist index as Markdown or JSON:

   ```sh
   uv run --script skills/ub-youtube/scripts/fetch_playlist.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o playlist.md
   uv run --script skills/ub-youtube/scripts/fetch_playlist.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --format json -o playlist.json
   ```

3. Export Watch Later only when the user explicitly asks for it:

   ```sh
   uv run --script skills/ub-youtube/scripts/fetch_playlist.py --watch-later --browser chrome -o watch_later.md
   ```

4. Add `--with-transcripts` to collect per-video transcripts beside the
   playlist export. The default batch limit is 25 videos; change it with
   `--limit N`.
5. Preserve title, URL, channel, duration, upload date, descriptions, playlist
   source, timestamps, and transcript status.
6. When summarizing, mention that automatic captions may contain recognition
   errors and that names or technical terms may need verification.
7. Do not present transcript text as a substitute for source licensing or
   publication rights. Use it for personal research notes and source-grounded
   analysis.

## Formats

```sh
uv run --script skills/ub-youtube/scripts/fetch_transcript.py URL --format txt
uv run --script skills/ub-youtube/scripts/fetch_transcript.py URL --format srt
uv run --script skills/ub-youtube/scripts/fetch_transcript.py URL --format json
uv run --script skills/ub-youtube/scripts/fetch_playlist.py URL --format md
uv run --script skills/ub-youtube/scripts/fetch_playlist.py URL --format json
```

## Authentication

Default to public, cookie-free YouTube access. Use `--browser` only when the
user explicitly requests Watch Later or a private playlist that requires a
logged-in browser session.
