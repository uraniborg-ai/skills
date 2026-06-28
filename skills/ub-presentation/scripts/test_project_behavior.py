#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from generate_subtitles import generate, parse_slide_titles
from project_config import load_project
from run_pipeline import dry_run
from segment_narration import convert
from validate_project import validate


def write_minimal_project(path: Path, extra: dict | None = None) -> None:
    (path / "images").mkdir(parents=True)
    (path / "images" / "slide.png").write_bytes(b"placeholder")
    raw = {
        "voice": {"voice_id": "${ELEVENLABS_VOICE_ID}"},
        "slides": [
            {
                "image": "images/slide.png",
                "segments": [{"text": "[calm] Hello world.", "pause_after_ms": 0}],
            }
        ],
    }
    if extra:
        raw.update(extra)
    (path / "narration.json").write_text(json.dumps(raw), encoding="utf-8")


def write_minimal_timeline(path: Path) -> None:
    (path / "build").mkdir(parents=True)
    (path / "build" / "timeline.json").write_text(
        json.dumps(
            {
                "video": {"width": 1920, "height": 1080, "fps": 30},
                "slides": [
                    {
                        "index": 1,
                        "image": "images/slide.png",
                        "audio": "voiceover/audio/slide-001.mp3",
                        "duration": 1.0,
                        "segments": [
                            {
                                "index": 1,
                                "text": "[calm] Hello world.",
                                "audio": "voiceover/audio/slide-001/segment-001.mp3",
                                "duration": 1.0,
                                "pause_after_ms": 0,
                            }
                        ],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


class ProjectBehaviorTests(unittest.TestCase):
    def test_validate_allows_missing_draft_and_slides_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            presentation_dir = Path(tmp) / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(presentation_dir)

            status = validate(
                str(presentation_dir),
                require_api_key=False,
                require_ffmpeg=False,
            )

        self.assertEqual(status, 0)

    def test_load_project_rejects_removed_path_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            presentation_dir = Path(tmp) / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(
                presentation_dir,
                extra={"output_dir": "build/voiceover", "exports_dir": "exports"},
            )

            with self.assertRaisesRegex(ValueError, "output_dir, exports_dir"):
                load_project(presentation_dir)

    def test_load_project_uses_nearest_env_without_overriding_process_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text("ELEVENLABS_VOICE_ID=root-voice\n", encoding="utf-8")
            parent = root / "nested"
            parent.mkdir()
            (parent / ".env").write_text(
                "ELEVENLABS_VOICE_ID=near-voice\nELEVENLABS_MODEL_ID=near-model\n",
                encoding="utf-8",
            )
            presentation_dir = parent / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(presentation_dir)

            with patch.dict(os.environ, {"ELEVENLABS_MODEL_ID": "process-model"}, clear=True):
                project = load_project(presentation_dir)

        self.assertEqual(project.voice.voice_id, "near-voice")
        self.assertEqual(project.voice.model_id, "process-model")

    def test_segment_narration_drops_removed_path_keys(self) -> None:
        converted, _ = convert(
            {
                "output_dir": "build/voiceover",
                "exports_dir": "exports",
                "slides": [
                    {
                        "image": "images/slide.png",
                        "text": "Hello world. This is a legacy narration.",
                    }
                ],
            }
        )

        self.assertNotIn("output_dir", converted)
        self.assertNotIn("exports_dir", converted)
        self.assertIn("segments", converted["slides"][0])

    def test_generate_subtitles_writes_captions_only_and_preserves_legacy_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            presentation_dir = Path(tmp) / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(presentation_dir)
            write_minimal_timeline(presentation_dir)
            (presentation_dir / "youtube.srt").write_text("old captions\n", encoding="utf-8")
            (presentation_dir / "transcript.md").write_text("old transcript\n", encoding="utf-8")

            status = generate(str(presentation_dir))

            self.assertEqual(status, 0)
            self.assertTrue((presentation_dir / "captions" / "youtube.srt").exists())
            self.assertEqual(
                (presentation_dir / "youtube.srt").read_text(encoding="utf-8"), "old captions\n"
            )
            self.assertEqual(
                (presentation_dir / "transcript.md").read_text(encoding="utf-8"),
                "old transcript\n",
            )

    def test_generate_subtitles_does_not_create_root_legacy_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            presentation_dir = Path(tmp) / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(presentation_dir)
            write_minimal_timeline(presentation_dir)

            status = generate(str(presentation_dir))

            self.assertEqual(status, 0)
            self.assertFalse((presentation_dir / "youtube.srt").exists())
            self.assertFalse((presentation_dir / "transcript.md").exists())

    def test_parse_slide_titles_ignores_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            slides = Path(tmp) / "slides.md"
            slides.write_text(
                "---\n"
                "title: Example\n"
                "description: Deck\n"
                "status: active\n"
                "---\n"
                "\n"
                "# Deck\n"
                "\n"
                "## Opening\n"
                "## Closing\n",
                encoding="utf-8",
            )

            titles = parse_slide_titles(slides)

        self.assertEqual(titles, ["Opening", "Closing"])

    def test_dry_run_prints_canonical_paths_without_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            presentation_dir = Path(tmp) / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(presentation_dir)

            buffer = io.StringIO()
            with patch("run_pipeline.validate", return_value=0), redirect_stdout(buffer):
                status = dry_run(str(presentation_dir))

        output = buffer.getvalue()
        self.assertEqual(status, 0)
        self.assertIn("voiceover/audio/slide-001.mp3", output)
        self.assertIn("captions/youtube.srt", output)
        self.assertIn("build/timeline.json", output)
        self.assertIn("build/render/final.mp4", output)
        self.assertIn("exports/final.mp4", output)
        self.assertNotIn("transcript.md", output)


if __name__ == "__main__":
    unittest.main()
