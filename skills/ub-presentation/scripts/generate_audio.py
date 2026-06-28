#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from project_config import (
    Segment,
    Slide,
    concat_list_path,
    load_project,
    segment_audio_path,
    silence_audio_path,
    slide_audio_path,
)


API_BASE = "https://api.elevenlabs.io/v1/text-to-speech"


def silence_command(path: Path, duration_ms: int) -> list[str]:
    seconds = max(0, duration_ms) / 1000
    return [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=44100:cl=mono",
        "-t",
        f"{seconds:.3f}",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "128k",
        str(path),
    ]


def concat_list_lines(paths: list[Path]) -> str:
    return "".join(f"file '{path.as_posix()}'\n" for path in paths)


def concat_command(list_path: Path, target: Path) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        str(target),
    ]


def ensure_silence(path: Path, duration_ms: int, *, overwrite: bool = False) -> None:
    if duration_ms <= 0:
        return
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(silence_command(path, duration_ms), check=True, capture_output=True)


def generate_segment_audio(
    api_key: str, voice_id: str, model_id: str, output_format: str, text: str, target: Path
) -> None:
    query = urllib.parse.urlencode({"output_format": output_format})
    url = f"{API_BASE}/{urllib.parse.quote(voice_id)}?{query}"
    payload = {
        "text": text,
        "model_id": model_id,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        target.write_bytes(response.read())


def generate(project_file: str, *, overwrite: bool = False) -> int:
    project = load_project(project_file)
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print(
            "ERROR: ELEVENLABS_API_KEY is required in .env or the process environment",
            file=sys.stderr,
        )
        return 1
    if not project.voice.voice_id:
        print("ERROR: voice.voice_id or ELEVENLABS_VOICE_ID is required", file=sys.stderr)
        return 1
    if not project.voice.output_format.startswith("mp3_"):
        print(
            "ERROR: only mp3 ElevenLabs output formats are supported for segment concatenation",
            file=sys.stderr,
        )
        return 1

    for slide in project.slides:
        slide_target = slide_audio_path(project, slide)
        if slide_target.exists() and not overwrite:
            print(f"Skipping existing slide audio: {slide_target}")
            continue

        concat_parts: list[Path] = []
        for segment in slide.segments:
            segment_target = segment_audio_path(project, slide, segment)
            segment_target.parent.mkdir(parents=True, exist_ok=True)
            if segment_target.exists() and not overwrite:
                print(f"Skipping existing segment audio: {segment_target}")
            else:
                try:
                    generate_segment_audio(
                        api_key,
                        project.voice.voice_id,
                        project.voice.model_id,
                        project.voice.output_format,
                        segment.text,
                        segment_target,
                    )
                except urllib.error.HTTPError as exc:
                    detail = exc.read().decode("utf-8", errors="replace")
                    print(
                        f"ERROR: ElevenLabs request failed for slide {slide.index}, segment {segment.index}: HTTP {exc.code} {detail}",
                        file=sys.stderr,
                    )
                    return 1
                except urllib.error.URLError as exc:
                    print(
                        f"ERROR: ElevenLabs request failed for slide {slide.index}, segment {segment.index}: {exc}",
                        file=sys.stderr,
                    )
                    return 1
                print(f"Wrote {segment_target}")

            concat_parts.append(segment_target)
            if segment.pause_after_ms > 0:
                silence = silence_audio_path(project, segment.pause_after_ms)
                ensure_silence(silence, segment.pause_after_ms, overwrite=overwrite)
                concat_parts.append(silence)

        slide_target.parent.mkdir(parents=True, exist_ok=True)
        concat_file = concat_list_path(project, slide)
        concat_file.parent.mkdir(parents=True, exist_ok=True)
        concat_file.write_text(concat_list_lines(concat_parts), encoding="utf-8")
        try:
            subprocess.run(
                concat_command(concat_file, slide_target), check=True, capture_output=True
            )
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: Could not concatenate slide {slide.index} audio: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {slide_target}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate per-segment ElevenLabs TTS audio and slide-level MP3 files."
    )
    parser.add_argument("project", help="Presentation directory or narration.json path")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    raise SystemExit(generate(args.project, overwrite=args.overwrite))


if __name__ == "__main__":
    main()
