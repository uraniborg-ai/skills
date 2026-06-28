---
name: ub-youtube-transcript
description: Extract YouTube video transcripts and convert them into structured Markdown with metadata for research, engineering, lectures, seminars, tutorials, and technical talks. Use when the user provides a YouTube URL, asks to summarize a YouTube video, or needs captions, subtitles, or video content converted to text.
metadata:
  version: 0.1.0
  stability: stable
  domain: media-notes
---

# UB YouTube Transcript

Use this skill to convert YouTube captions into a source-preserving Markdown
document before summarizing or analyzing the video.

## Workflow

1. Extract the transcript with the bundled script when available:

   ```sh
   uv run --script skills/ub-youtube-transcript/scripts/fetch_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.md
   ```

2. Preserve title, URL, channel, duration, upload date, and timestamps.
3. When summarizing, mention that automatic captions may contain recognition
   errors and that names or technical terms may need verification.
4. Do not present transcript text as a substitute for source licensing or
   publication rights. Use it for personal research notes and source-grounded
   analysis.

## Formats

```sh
uv run --script skills/ub-youtube-transcript/scripts/fetch_transcript.py URL --format txt
uv run --script skills/ub-youtube-transcript/scripts/fetch_transcript.py URL --format srt
uv run --script skills/ub-youtube-transcript/scripts/fetch_transcript.py URL --format json
```
