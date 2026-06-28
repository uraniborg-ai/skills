#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2>=3.1",
#   "yt-dlp>=2025.1.1",
# ]
# ///
"""Fetch a YouTube transcript and save it as structured Markdown."""

from __future__ import annotations

import argparse
import json
import os
import re
from urllib.request import urlopen

import jinja2
import yt_dlp


def format_srt_time(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"


def find_subtitle_url(info: dict, language: str) -> str | None:
    for key in ("subtitles", "automatic_captions"):
        subtitles = info.get(key, {})
        languages = [language] if language in subtitles else list(subtitles.keys())
        for lang in languages:
            for item in subtitles.get(lang, []):
                if item.get("ext") == "json3":
                    return item.get("url")
    return None


def parse_json3(data: dict) -> list[dict]:
    snippets = []
    for event in data.get("events", []):
        segments = event.get("segs")
        if not segments:
            continue
        text = "".join(segment.get("utf8", "") for segment in segments).strip()
        if not text or text == "\n":
            continue
        snippets.append(
            {
                "text": text,
                "start": event.get("tStartMs", 0) / 1000.0,
                "duration": event.get("dDurationMs", 0) / 1000.0,
            }
        )
    return snippets


def format_transcript(snippets: list[dict], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(snippets, ensure_ascii=False, indent=2)
    if output_format == "srt":
        parts = []
        for index, snippet in enumerate(snippets, 1):
            start = format_srt_time(snippet["start"])
            end = format_srt_time(snippet["start"] + snippet["duration"])
            parts.append(f"{index}\n{start} --> {end}\n{snippet['text']}\n")
        return "\n".join(parts)

    lines = []
    for snippet in snippets:
        hours, remainder = divmod(snippet["start"], 3600)
        minutes, seconds = divmod(remainder, 60)
        stamp = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        lines.append(f"[{stamp}] {snippet['text']}")
    return "\n".join(lines) + "\n"


def download_transcript(url: str, output_format: str) -> tuple[dict, str]:
    options = {
        "skip_download": True,
        "quiet": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "json3",
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        raw_info = ydl.extract_info(url, download=False)
        info = ydl.sanitize_info(raw_info)

    language = info.get("language", "en")
    subtitle_url = find_subtitle_url(raw_info, language)
    if not subtitle_url:
        raise SystemExit("No json3 subtitles or automatic captions are available for this video.")

    with urlopen(subtitle_url) as response:
        snippets = parse_json3(json.loads(response.read().decode()))
    if not snippets:
        raise SystemExit("Subtitle data is empty.")
    return info, format_transcript(snippets, output_format)


def render_markdown(info: dict, transcript: str) -> str:
    upload_date = info.get("upload_date", "")
    if upload_date and len(upload_date) == 8:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"

    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)
    template = env.get_template("transcript.md.j2")
    return template.render(
        title=info.get("title", "Untitled Video"),
        webpage_url=info.get("webpage_url", ""),
        video_id=info.get("id", ""),
        channel=info.get("channel", "Unknown"),
        duration=info.get("duration", 0),
        uploader=info.get("uploader", "Unknown"),
        upload_date=upload_date,
        description=info.get("description", ""),
        transcript_text=transcript,
    )


def sanitize_filename(value: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", value).strip() or "youtube_transcript"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-o", "--output", help="output Markdown file")
    parser.add_argument("-f", "--format", choices=["txt", "json", "srt"], default="txt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    info, transcript = download_transcript(args.url, args.format)
    output = args.output or f"{sanitize_filename(info.get('title', 'youtube_transcript'))}.md"
    with open(output, "w", encoding="utf-8") as handle:
        handle.write(render_markdown(info, transcript))
    print(f"Transcript saved to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
