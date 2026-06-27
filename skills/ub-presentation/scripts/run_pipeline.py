#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse

from build_timeline import build
from generate_audio import generate
from generate_subtitles import generate as generate_subtitles
from project_config import (
    audio_path,
    final_video_path,
    load_project,
    segment_audio_path,
    timeline_path,
    voiceover_video_path,
)
from render_video import render
from validate_project import validate


def dry_run(project_file: str) -> int:
    status = validate(project_file, require_api_key=False, require_ffmpeg=True)
    if status != 0:
        return status

    project = load_project(project_file)
    print("Dry run output plan:")
    for slide in project.slides:
        print(f"  slide {slide.index:03d}: {slide.image} -> {audio_path(project, slide)}")
        print(f"    segments: {len(slide.segments)}")
        for segment in slide.segments:
            print(
                f"      segment {segment.index:03d}: {segment_audio_path(project, slide, segment)}"
            )
    print(f"  timeline: {timeline_path(project)}")
    print(f"  subtitles: {project.presentation_dir / 'youtube.srt'}")
    print(f"  transcript: {project.presentation_dir / 'transcript.md'}")
    print(f"  voiceover video: {voiceover_video_path(project)}")
    print(f"  export video: {final_video_path(project)}")
    return 0


def run(project_file: str, *, overwrite: bool = False, dry: bool = False) -> int:
    if dry:
        return dry_run(project_file)

    status = validate(project_file, require_api_key=True, require_ffmpeg=True)
    if status != 0:
        return status

    status = generate(project_file, overwrite=overwrite)
    if status != 0:
        return status
    status = build(project_file)
    if status != 0:
        return status
    status = generate_subtitles(project_file)
    if status != 0:
        return status
    return render(project_file, overwrite=overwrite)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the UB Presentation voiceover pipeline.")
    parser.add_argument("project", help="Presentation directory or narration.json path")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    raise SystemExit(run(args.project, overwrite=args.overwrite, dry=args.dry_run))


if __name__ == "__main__":
    main()
