#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import os
import sys

from project_config import (
    audio_path,
    final_video_path,
    load_project,
    require_tools,
    timeline_path,
    voiceover_video_path,
)


def validate(
    project_file: str,
    *,
    require_audio: bool = False,
    require_api_key: bool = True,
    require_ffmpeg: bool = True,
) -> int:
    errors: list[str] = []

    try:
        project = load_project(project_file)
    except Exception as exc:
        print(f"Invalid project: {exc}", file=sys.stderr)
        return 1

    if require_api_key:
        if not os.environ.get("ELEVENLABS_API_KEY"):
            errors.append("ELEVENLABS_API_KEY is required in .env or the process environment")
        if not project.voice.voice_id:
            errors.append("voice.voice_id or ELEVENLABS_VOICE_ID is required")

    for slide in project.slides:
        if not slide.image.exists():
            errors.append(f"Slide image does not exist: {slide.image}")
        elif not slide.image.is_file():
            errors.append(f"Slide image is not a file: {slide.image}")
        if require_audio:
            path = audio_path(project, slide)
            if not path.exists():
                errors.append(f"Slide audio does not exist: {path}")

    if require_ffmpeg:
        missing = require_tools("ffmpeg", "ffprobe")
        for name in missing:
            errors.append(f"{name} is required on PATH")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Presentation: {project.presentation_dir}")
    print(f"Narration: {project.path}")
    print(f"Slides: {len(project.slides)}")
    print(f"Segments: {sum(len(slide.segments) for slide in project.slides)}")
    print(f"Voice model: {project.voice.model_id}")
    print(f"Output directory: {project.output_dir}")
    print(f"Audio directory: {project.output_dir / 'audio'}")
    print(f"Timeline: {timeline_path(project)}")
    print(f"Voiceover video: {voiceover_video_path(project)}")
    print(f"Export video: {final_video_path(project)}")
    print("Validation passed.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a UB Presentation project.")
    parser.add_argument("project", help="Presentation directory or narration.json path")
    parser.add_argument(
        "--require-audio", action="store_true", help="Require generated slide audio files."
    )
    parser.add_argument(
        "--skip-api-key", action="store_true", help="Do not require ELEVENLABS_API_KEY or voice id."
    )
    parser.add_argument(
        "--skip-ffmpeg", action="store_true", help="Do not require ffmpeg and ffprobe."
    )
    args = parser.parse_args()

    raise SystemExit(
        validate(
            args.project,
            require_audio=args.require_audio,
            require_api_key=not args.skip_api_key,
            require_ffmpeg=not args.skip_ffmpeg,
        )
    )


if __name__ == "__main__":
    main()
