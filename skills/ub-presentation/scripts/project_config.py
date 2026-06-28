#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
REMOVED_PATH_KEYS = ("output_dir", "exports_dir")


@dataclass(frozen=True)
class Segment:
    index: int
    text: str
    pause_after_ms: int


@dataclass(frozen=True)
class Slide:
    index: int
    image: Path
    segments: list[Segment]


@dataclass(frozen=True)
class VoiceConfig:
    voice_id: str
    model_id: str
    output_format: str


@dataclass(frozen=True)
class VideoConfig:
    width: int
    height: int
    fps: int


@dataclass(frozen=True)
class Project:
    path: Path
    root: Path
    presentation_dir: Path
    voiceover_dir: Path
    captions_dir: Path
    exports_dir: Path
    build_dir: Path
    voice: VoiceConfig
    video: VideoConfig
    slides: list[Slide]


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in [current, *current.parents]:
        if (path / "pyproject.toml").exists() or (path / ".git").exists():
            return path
    return current


def find_nearest_env(start: Path) -> Path | None:
    current = start.resolve()
    for path in [current, *current.parents]:
        env_path = path / ".env"
        if env_path.exists():
            return env_path
    return None


def load_env_file(env_path: Path | None) -> None:
    if env_path is None or not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def resolve_env_value(value: Any, *, required: bool = False) -> Any:
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = os.environ.get(name)
        if resolved is None:
            if required:
                raise ValueError(f"Environment variable {name} is required but not set")
            return ""
        return resolved

    return ENV_PATTERN.sub(replace, value)


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _resolve_input(path_arg: str | Path, root: Path) -> tuple[Path, Path]:
    path = Path(path_arg).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if path.is_dir():
        return path / "narration.json", path
    return path, path.parent


def _resolve_project_path(presentation_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = presentation_dir / path
    return path.resolve()


def relative_to_presentation(project: Project, path: Path) -> str:
    try:
        return path.resolve().relative_to(project.presentation_dir).as_posix()
    except ValueError:
        return os.path.relpath(path.resolve(), project.presentation_dir).replace(os.sep, "/")


def _reject_removed_path_keys(raw: dict[str, Any]) -> None:
    present = [key for key in REMOVED_PATH_KEYS if key in raw]
    if present:
        keys = ", ".join(present)
        raise ValueError(
            f"{keys} are no longer supported; use fixed directories "
            "voiceover/, captions/, exports/, and build/."
        )


def load_project(project_path: str | Path) -> Project:
    path, presentation_dir = _resolve_input(project_path, Path.cwd())
    load_env_file(find_nearest_env(presentation_dir))
    root = find_project_root(presentation_dir)

    if not path.exists():
        raise ValueError(f"narration file does not exist: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        raise ValueError("narration JSON must be an object")
    _reject_removed_path_keys(raw)

    voice_raw = raw.get("voice", {})
    if voice_raw is None:
        voice_raw = {}
    if not isinstance(voice_raw, dict):
        raise ValueError("voice must be an object when provided")

    voice_id = resolve_env_value(voice_raw.get("voice_id", "${ELEVENLABS_VOICE_ID}"))
    model_id = resolve_env_value(
        voice_raw.get("model_id", os.environ.get("ELEVENLABS_MODEL_ID", "eleven_v3"))
    )
    output_format = resolve_env_value(
        voice_raw.get("output_format", os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128"))
    )

    video_raw = raw.get("video", {})
    if video_raw is None:
        video_raw = {}
    if not isinstance(video_raw, dict):
        raise ValueError("video must be an object when provided")

    video = VideoConfig(
        width=_positive_int(video_raw.get("width", 1920), "video.width"),
        height=_positive_int(video_raw.get("height", 1080), "video.height"),
        fps=_positive_int(video_raw.get("fps", 30), "video.fps"),
    )

    slides_raw = raw.get("slides")
    if not isinstance(slides_raw, list) or not slides_raw:
        raise ValueError("slides must be a non-empty array")

    slides: list[Slide] = []
    for slide_idx, item in enumerate(slides_raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"slides[{slide_idx}] must be an object")
        if "text" in item:
            raise ValueError(
                f"slides[{slide_idx}].text is no longer supported; "
                "run segment_narration.py to convert to slides[].segments[]"
            )
        image_raw = resolve_env_value(item.get("image"))
        if not isinstance(image_raw, str) or not image_raw.strip():
            raise ValueError(f"slides[{slide_idx}].image is required")

        segments_raw = item.get("segments")
        if not isinstance(segments_raw, list) or not segments_raw:
            raise ValueError(f"slides[{slide_idx}].segments must be a non-empty array")

        segments: list[Segment] = []
        for segment_idx, segment_raw in enumerate(segments_raw, start=1):
            if not isinstance(segment_raw, dict):
                raise ValueError(f"slides[{slide_idx}].segments[{segment_idx}] must be an object")
            text = resolve_env_value(segment_raw.get("text"))
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"slides[{slide_idx}].segments[{segment_idx}].text is required")
            pause_after_ms = _non_negative_int(
                segment_raw.get("pause_after_ms", 350),
                f"slides[{slide_idx}].segments[{segment_idx}].pause_after_ms",
            )
            segments.append(
                Segment(index=segment_idx, text=text.strip(), pause_after_ms=pause_after_ms)
            )

        slides.append(
            Slide(
                index=slide_idx,
                image=_resolve_project_path(presentation_dir, image_raw),
                segments=segments,
            )
        )

    return Project(
        path=path.resolve(),
        root=root,
        presentation_dir=presentation_dir.resolve(),
        voiceover_dir=(presentation_dir / "voiceover").resolve(),
        captions_dir=(presentation_dir / "captions").resolve(),
        exports_dir=(presentation_dir / "exports").resolve(),
        build_dir=(presentation_dir / "build").resolve(),
        voice=VoiceConfig(
            voice_id=str(voice_id),
            model_id=str(model_id),
            output_format=str(output_format),
        ),
        video=video,
        slides=slides,
    )


def require_tools(*names: str) -> list[str]:
    return [name for name in names if shutil.which(name) is None]


def voiceover_audio_dir(project: Project) -> Path:
    return project.voiceover_dir / "audio"


def build_voiceover_dir(project: Project) -> Path:
    return project.build_dir / "voiceover"


def build_render_dir(project: Project) -> Path:
    return project.build_dir / "render"


def slide_audio_path(project: Project, slide: Slide) -> Path:
    return voiceover_audio_dir(project) / f"slide-{slide.index:03d}.mp3"


def segment_audio_path(project: Project, slide: Slide, segment: Segment) -> Path:
    return (
        voiceover_audio_dir(project)
        / f"slide-{slide.index:03d}"
        / f"segment-{segment.index:03d}.mp3"
    )


def silence_audio_path(project: Project, duration_ms: int) -> Path:
    return build_voiceover_dir(project) / "silence" / f"silence-{duration_ms:04d}ms.mp3"


def concat_list_path(project: Project, slide: Slide) -> Path:
    return build_voiceover_dir(project) / f"slide-{slide.index:03d}.concat.txt"


def audio_path(project: Project, slide: Slide) -> Path:
    return slide_audio_path(project, slide)


def timeline_path(project: Project) -> Path:
    return project.build_dir / "timeline.json"


def youtube_srt_path(project: Project) -> Path:
    return project.captions_dir / "youtube.srt"


def render_clip_path(project: Project, slide_index: int) -> Path:
    return build_render_dir(project) / f"clip-{slide_index:03d}.mp4"


def render_concat_path(project: Project) -> Path:
    return build_render_dir(project) / "concat.txt"


def voiceover_video_path(project: Project) -> Path:
    return build_render_dir(project) / "final.mp4"


def final_video_path(project: Project) -> Path:
    return project.exports_dir / "final.mp4"
