#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2>=3.1",
#   "yt-dlp>=2025.1.1",
# ]
# ///
"""Fetch a YouTube playlist or Watch Later list as research notes."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jinja2
import yt_dlp

import fetch_transcript


WATCH_LATER_URL = "https://www.youtube.com/playlist?list=WL"
BROWSER_CHOICES = [
    "chrome",
    "firefox",
    "safari",
    "edge",
    "chromium",
    "brave",
    "opera",
    "vivaldi",
]


def format_duration(seconds: int | float | None) -> str:
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_upload_date(value: str | None) -> str | None:
    if value and len(value) == 8:
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
    return value or None


def video_url(entry: dict[str, Any]) -> str:
    url = entry.get("webpage_url") or entry.get("url") or ""
    if url.startswith("http"):
        return url
    video_id = entry.get("id") or url
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return ""


def sanitize_filename(value: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", value).strip() or "youtube_playlist"


def fetch_playlist(url: str, browser: str | None) -> dict[str, Any]:
    options: dict[str, Any] = {
        "extract_flat": True,
        "ignoreerrors": True,
        "quiet": True,
        "skip_download": True,
    }
    if browser:
        options["cookiesfrombrowser"] = (browser,)

    with yt_dlp.YoutubeDL(options) as ydl:
        raw_info = ydl.extract_info(url, download=False)
        return ydl.sanitize_info(raw_info)


def normalize_entries(entries: list[dict[str, Any] | None]) -> list[dict[str, Any]]:
    videos = []
    for entry in entries:
        if not entry:
            continue
        duration = entry.get("duration")
        videos.append(
            {
                "title": entry.get("title") or "Untitled",
                "url": video_url(entry),
                "channel": entry.get("channel") or entry.get("uploader"),
                "duration": duration,
                "duration_formatted": format_duration(duration),
                "upload_date": format_upload_date(entry.get("upload_date")),
                "video_id": entry.get("id") or "",
                "description": entry.get("description") or "",
                "transcript_status": "not_requested",
                "transcript_path": None,
                "transcript_error": None,
            }
        )
    return videos


def collect_transcripts(
    videos: list[dict[str, Any]],
    output_path: Path,
    limit: int,
    browser: str | None,
) -> None:
    transcript_dir = output_path.parent / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)

    for video in videos[:limit]:
        if not video["url"]:
            video["transcript_status"] = "failed"
            video["transcript_error"] = "Missing video URL."
            continue
        video_id = video["video_id"] or sanitize_filename(video["title"])
        transcript_path = transcript_dir / f"{video_id}.md"
        try:
            info, transcript = fetch_transcript.download_transcript(
                video["url"], "txt", browser=browser
            )
            transcript_path.write_text(
                fetch_transcript.render_markdown(info, transcript),
                encoding="utf-8",
            )
        except SystemExit as error:
            video["transcript_status"] = "missing"
            video["transcript_error"] = str(error)
            continue
        except Exception as error:
            video["transcript_status"] = "failed"
            video["transcript_error"] = str(error)
            continue
        video["transcript_status"] = "saved"
        video["transcript_path"] = os.path.relpath(transcript_path, output_path.parent)

    for video in videos[limit:]:
        video["transcript_status"] = "skipped_limit"


def render_markdown(context: dict[str, Any]) -> str:
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)
    template = env.get_template("playlist.md.j2")
    return template.render(**context)


def build_context(
    playlist: dict[str, Any],
    videos: list[dict[str, Any]],
    source_url: str,
    source_kind: str,
    fetched_at: str,
    transcript_limit: int | None,
) -> dict[str, Any]:
    total_seconds = sum(video["duration"] or 0 for video in videos)
    return {
        "title": playlist.get("title")
        or ("YouTube Watch Later" if source_kind == "watch_later" else "YouTube Playlist"),
        "source_url": source_url,
        "source_kind": source_kind,
        "fetched_at": fetched_at,
        "playlist_id": playlist.get("id") or "",
        "channel": playlist.get("channel") or playlist.get("uploader") or "",
        "total_videos": len(videos),
        "total_duration": format_duration(total_seconds),
        "with_transcripts": transcript_limit is not None,
        "transcript_limit": transcript_limit,
        "videos": videos,
    }


def default_output(title: str, output_format: str) -> Path:
    date = datetime.now().strftime("%Y-%m-%d")
    suffix = "json" if output_format == "json" else "md"
    return Path(f"{sanitize_filename(title)}_{date}.{suffix}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="YouTube playlist URL")
    parser.add_argument(
        "--watch-later", action="store_true", help="fetch the logged-in Watch Later playlist"
    )
    parser.add_argument("-o", "--output", help="output file path")
    parser.add_argument("-f", "--format", choices=["md", "json"], default="md")
    parser.add_argument(
        "-b", "--browser", choices=BROWSER_CHOICES, help="browser to extract cookies from"
    )
    parser.add_argument(
        "--with-transcripts",
        action="store_true",
        help="also save per-video transcripts beside the playlist export",
    )
    parser.add_argument(
        "--limit", type=int, default=25, help="maximum videos for --with-transcripts"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.watch_later and args.url:
        raise SystemExit("Pass either a playlist URL or --watch-later, not both.")
    if not args.watch_later and not args.url:
        raise SystemExit("Pass a playlist URL or --watch-later.")
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1.")

    source_url = WATCH_LATER_URL if args.watch_later else args.url
    source_kind = "watch_later" if args.watch_later else "playlist"
    browser = args.browser or ("chrome" if args.watch_later else None)
    playlist = fetch_playlist(source_url, browser)
    videos = normalize_entries(playlist.get("entries", []))
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = playlist.get("title") or (
        "YouTube Watch Later" if args.watch_later else "YouTube Playlist"
    )
    output_path = Path(args.output) if args.output else default_output(title, args.format)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    transcript_limit = args.limit if args.with_transcripts else None
    if args.with_transcripts:
        collect_transcripts(videos, output_path, args.limit, browser)

    context = build_context(playlist, videos, source_url, source_kind, fetched_at, transcript_limit)
    if args.format == "json":
        output_path.write_text(
            json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    else:
        output_path.write_text(render_markdown(context), encoding="utf-8")

    print(f"Saved {len(videos)} videos to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
