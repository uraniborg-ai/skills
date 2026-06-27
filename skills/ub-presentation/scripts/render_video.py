#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from project_config import final_video_path, load_project, timeline_path, voiceover_video_path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def _resolve_timeline_path(project, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = project.presentation_dir / path
    return path.resolve()


def render(project_file: str, *, overwrite: bool = False) -> int:
    project = load_project(project_file)
    timeline_file = timeline_path(project)
    if not timeline_file.exists():
        print(f"ERROR: Missing timeline: {timeline_file}", file=sys.stderr)
        return 1

    timeline = json.loads(timeline_file.read_text(encoding="utf-8"))
    render_dir = project.output_dir / "render"
    render_dir.mkdir(parents=True, exist_ok=True)

    clips: list[Path] = []
    for item in timeline["slides"]:
        index = int(item["index"])
        image = _resolve_timeline_path(project, item["image"])
        audio = _resolve_timeline_path(project, item["audio"])
        duration = str(item["duration"])
        clip = render_dir / f"clip-{index:03d}.mp4"
        clips.append(clip)

        if clip.exists() and not overwrite:
            print(f"Skipping existing clip: {clip}")
            continue

        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-t",
                duration,
                "-i",
                str(image),
                "-i",
                str(audio),
                "-vf",
                f"scale={project.video.width}:{project.video.height}:force_original_aspect_ratio=decrease,pad={project.video.width}:{project.video.height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                "-r",
                str(project.video.fps),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                str(clip),
            ]
        )

    concat_file = render_dir / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8"
    )

    voiceover_path = voiceover_video_path(project)
    if voiceover_path.exists() and not overwrite:
        print(
            f"ERROR: Voiceover video already exists: {voiceover_path}. Use --overwrite.",
            file=sys.stderr,
        )
        return 1

    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(voiceover_path),
        ]
    )

    final_path = final_video_path(project)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if final_path.exists() and not overwrite:
        print(
            f"ERROR: Export video already exists: {final_path}. Use --overwrite.", file=sys.stderr
        )
        return 1
    shutil.copy2(voiceover_path, final_path)
    print(f"Wrote {voiceover_path}")
    print(f"Wrote {final_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the final presentation video.")
    parser.add_argument("project", help="Presentation directory or narration.json path")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    raise SystemExit(render(args.project, overwrite=args.overwrite))


if __name__ == "__main__":
    main()
