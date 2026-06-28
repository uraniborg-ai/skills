#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from project_config import load_project, timeline_path, youtube_srt_path


AUDIO_TAG_PATTERN = re.compile(r"\[[^\]]+\]")


def strip_audio_tags(text: str) -> str:
    return re.sub(r"\s+", " ", AUDIO_TAG_PATTERN.sub("", text)).strip()


def wrap_caption(text: str, *, width: int = 42) -> str:
    words = text.split()
    if not words:
        return text
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def format_srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def parse_slide_titles(slides_file: Path) -> list[str]:
    if not slides_file.exists():
        return []
    titles: list[str] = []
    in_frontmatter = False
    for line_number, line in enumerate(slides_file.read_text(encoding="utf-8").splitlines()):
        if line_number == 0 and line == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if line.startswith("## "):
            titles.append(line.removeprefix("## ").strip())
    return titles


def generate(project_file: str) -> int:
    project = load_project(project_file)
    timeline_file = timeline_path(project)
    if not timeline_file.exists():
        print(f"ERROR: Missing timeline: {timeline_file}", file=sys.stderr)
        return 1

    timeline = json.loads(timeline_file.read_text(encoding="utf-8"))
    timeline_slides = timeline.get("slides")
    if not isinstance(timeline_slides, list) or len(timeline_slides) != len(project.slides):
        print("ERROR: timeline slides must match narration slides", file=sys.stderr)
        return 1

    cues: list[tuple[float, float, str]] = []
    current_start = 0.0
    for slide_item in timeline_slides:
        slide_offset = current_start
        segments = slide_item.get("segments")
        if not isinstance(segments, list) or not segments:
            print(
                f"ERROR: timeline slide {slide_item.get('index')} has no segment metadata",
                file=sys.stderr,
            )
            return 1
        for segment in segments:
            duration = float(segment["duration"])
            text = wrap_caption(strip_audio_tags(str(segment["text"])))
            cue_start = slide_offset
            cue_end = slide_offset + duration
            if text:
                cues.append((cue_start, cue_end, text))
            slide_offset = cue_end + (int(segment.get("pause_after_ms", 0)) / 1000)
        current_start += float(slide_item["duration"])

    srt_blocks = []
    for index, (start, end, text) in enumerate(cues, start=1):
        srt_blocks.append(f"{index}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}")

    srt_path = youtube_srt_path(project)
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

    print(f"Wrote {srt_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate YouTube SRT subtitles from segment timeline."
    )
    parser.add_argument("project", help="Presentation directory or narration.json path")
    args = parser.parse_args()

    raise SystemExit(generate(args.project))


if __name__ == "__main__":
    main()
