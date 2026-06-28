#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

SENTENCE_PATTERN = re.compile(r"[^.!?\n。！？]+[.!?。！？]?")
TAG_PATTERN = re.compile(r"^\s*(\[[^\]]+\]\s*)+")
FILE_DOT_PATTERN = re.compile(
    r"\b([A-Za-z0-9_-]+)\.(yaml|yml|json|toml|md|typ|py|js|ts|tsx|pdf|docx|pptx)\b", re.IGNORECASE
)
FILE_DOT_TOKEN = "__UB_FILE_DOT__"
KEY_CLAIM_HINTS = ("핵심", "중요", "문제", "정리하면", "결론", "즉", "따라서", "확인할")
TRANSITION_HINTS = ("먼저", "다음", "이제", "여기서", "그래서", "정리하면", "마지막으로")
TARGET_CHARS = 95
MAX_CHARS = 145
REMOVED_PATH_KEYS = {"output_dir", "exports_dir"}


def resolve_narration_path(path_arg: str) -> tuple[Path, Path]:
    path = Path(path_arg).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if path.is_dir():
        return path / "narration.json", path
    return path, path.parent


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    normalized = FILE_DOT_PATTERN.sub(
        lambda match: f"{match.group(1)}{FILE_DOT_TOKEN}{match.group(2)}", normalized
    )
    sentences = [match.group(0).strip() for match in SENTENCE_PATTERN.finditer(normalized)]
    return [sentence.replace(FILE_DOT_TOKEN, ".") for sentence in sentences if sentence]


def group_sentences(sentences: list[str]) -> list[str]:
    groups: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        if current and current_len >= TARGET_CHARS:
            groups.append(" ".join(current))
            current = []
            current_len = 0

        if current and current_len + sentence_len > MAX_CHARS:
            groups.append(" ".join(current))
            current = []
            current_len = 0

        current.append(sentence)
        current_len += sentence_len

    if current:
        groups.append(" ".join(current))

    return groups


def choose_tag(text: str, *, slide_index: int, segment_index: int, slide_count: int) -> str:
    if slide_index == slide_count:
        return "[confident]"
    if slide_index == 1 and segment_index == 1:
        return "[warmly]"
    if segment_index == 1 and any(hint in text for hint in TRANSITION_HINTS):
        return "[warmly]"
    if any(hint in text for hint in KEY_CLAIM_HINTS):
        return "[thoughtful][slight emphasis]"
    return "[calm]"


def pause_after(text: str, *, is_last_segment: bool) -> int:
    if is_last_segment:
        return 700
    if text.rstrip().endswith(("?", "？")) or any(hint in text for hint in TRANSITION_HINTS):
        return 500
    return 350


def tag_text(text: str, tag: str) -> str:
    if TAG_PATTERN.match(text):
        return text.strip()
    return f"{tag} {text.strip()}"


def convert(raw: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    slides_raw = raw.get("slides")
    if not isinstance(slides_raw, list) or not slides_raw:
        raise ValueError("slides must be a non-empty array")

    converted_slides: list[dict[str, Any]] = []
    plan: list[dict[str, Any]] = []
    slide_count = len(slides_raw)

    for slide_index, slide in enumerate(slides_raw, start=1):
        if not isinstance(slide, dict):
            raise ValueError(f"slides[{slide_index}] must be an object")
        if "segments" in slide:
            raise ValueError(f"slides[{slide_index}] already has segments")

        text = slide.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"slides[{slide_index}].text is required for conversion")

        chunks = group_sentences(split_sentences(text))
        if not chunks:
            raise ValueError(f"slides[{slide_index}].text did not produce any segments")

        segments: list[dict[str, Any]] = []
        for segment_index, chunk in enumerate(chunks, start=1):
            tag = choose_tag(
                chunk, slide_index=slide_index, segment_index=segment_index, slide_count=slide_count
            )
            segments.append(
                {
                    "text": tag_text(chunk, tag),
                    "pause_after_ms": pause_after(
                        chunk, is_last_segment=segment_index == len(chunks)
                    ),
                }
            )

        image = slide.get("image")
        converted_slides.append({"image": image, "segments": segments})
        plan.append(
            {
                "slide": slide_index,
                "image": image,
                "segments": len(segments),
                "preview": segments[0]["text"],
            }
        )

    voice = raw.get("voice", {})
    if not isinstance(voice, dict):
        voice = {}
    voice = {**voice, "model_id": "eleven_v3"}

    converted = {
        key: value for key, value in raw.items() if key != "slides" and key not in REMOVED_PATH_KEYS
    }
    converted["voice"] = voice
    converted["slides"] = converted_slides
    return converted, plan


def print_plan(plan: list[dict[str, Any]], *, narration_path: Path) -> None:
    total = sum(item["segments"] for item in plan)
    print(f"Narration: {narration_path}")
    print(f"Slides: {len(plan)}")
    print(f"Segments: {total}")
    for item in plan:
        print(f"  slide {item['slide']:03d}: {item['segments']} segments")
        print(f"    {item['preview']}")


def run(project: str, *, dry_run: bool = False, force: bool = False) -> int:
    narration_path, presentation_dir = resolve_narration_path(project)
    if not narration_path.exists():
        print(f"narration file does not exist: {narration_path}", file=sys.stderr)
        return 1

    raw = json.loads(narration_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        print("narration JSON must be an object", file=sys.stderr)
        return 1

    try:
        converted, plan = convert(raw)
    except Exception as exc:
        print(f"Could not segment narration: {exc}", file=sys.stderr)
        return 1

    print_plan(plan, narration_path=narration_path)
    if dry_run:
        print("Dry run only; no files changed.")
        return 0

    backup_path = presentation_dir / "narration.legacy.json"
    if backup_path.exists() and not force:
        print(
            f"Backup already exists: {backup_path}. Use --force to overwrite it.", file=sys.stderr
        )
        return 1

    shutil.copy2(narration_path, backup_path)
    narration_path.write_text(
        json.dumps(converted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Backed up legacy narration: {backup_path}")
    print(f"Wrote segmented narration: {narration_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert legacy slides[].text narration to slides[].segments[]."
    )
    parser.add_argument("project", help="Presentation directory or narration.json path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print the segment plan without writing files."
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite narration.legacy.json if it already exists."
    )
    args = parser.parse_args()

    raise SystemExit(run(args.project, dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
