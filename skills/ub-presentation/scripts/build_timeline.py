#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from project_config import (
    load_project,
    relative_to_presentation,
    segment_audio_path,
    slide_audio_path,
    timeline_path,
)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def estimated_segment_durations(
    slide_duration: float, texts: list[str], pauses_ms: list[int]
) -> list[float]:
    pause_seconds = sum(pauses_ms) / 1000
    spoken_duration = max(0.001, slide_duration - pause_seconds)
    weights = [max(1, len(text)) for text in texts]
    total_weight = sum(weights)
    return [spoken_duration * (weight / total_weight) for weight in weights]


def build(project_file: str) -> int:
    project = load_project(project_file)
    entries = []

    for slide in project.slides:
        slide_audio = slide_audio_path(project, slide)
        if not slide_audio.exists():
            print(f"ERROR: Missing audio for slide {slide.index}: {slide_audio}", file=sys.stderr)
            return 1
        try:
            slide_duration = probe_duration(slide_audio)
        except Exception as exc:
            print(f"ERROR: Could not read duration for {slide_audio}: {exc}", file=sys.stderr)
            return 1

        segment_entries = []
        fallback_durations = estimated_segment_durations(
            slide_duration,
            [segment.text for segment in slide.segments],
            [segment.pause_after_ms for segment in slide.segments],
        )
        for segment, fallback_duration in zip(slide.segments, fallback_durations, strict=True):
            segment_audio = segment_audio_path(project, slide, segment)
            if segment_audio.exists():
                try:
                    duration = probe_duration(segment_audio)
                except Exception:
                    duration = fallback_duration
                audio_value = relative_to_presentation(project, segment_audio)
            else:
                duration = fallback_duration
                audio_value = None
            segment_entries.append(
                {
                    "index": segment.index,
                    "text": segment.text,
                    "audio": audio_value,
                    "duration": round(duration, 3),
                    "pause_after_ms": segment.pause_after_ms,
                }
            )

        entries.append(
            {
                "index": slide.index,
                "image": relative_to_presentation(project, slide.image),
                "audio": relative_to_presentation(project, slide_audio),
                "duration": round(slide_duration, 3),
                "segments": segment_entries,
            }
        )

    timeline = {
        "video": {
            "width": project.video.width,
            "height": project.video.height,
            "fps": project.video.fps,
        },
        "slides": entries,
    }
    path = timeline_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a slide/audio timeline JSON.")
    parser.add_argument("project", help="Presentation directory or narration.json path")
    args = parser.parse_args()

    raise SystemExit(build(args.project))


if __name__ == "__main__":
    main()
