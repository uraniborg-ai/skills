#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from generate_subtitles import generate
from project_config import load_project
from validate_project import validate


def write_minimal_project(path: Path) -> None:
    (path / "images").mkdir(parents=True)
    (path / "images" / "slide.png").write_bytes(b"placeholder")
    (path / "narration.json").write_text(
        json.dumps(
            {
                "voice": {"voice_id": "${ELEVENLABS_VOICE_ID}"},
                "slides": [
                    {
                        "image": "images/slide.png",
                        "segments": [{"text": "[calm] Hello world.", "pause_after_ms": 0}],
                    }
                ],
            }
        ),
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

    def test_generate_subtitles_uses_neutral_transcript_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            presentation_dir = Path(tmp) / "presentation"
            presentation_dir.mkdir()
            write_minimal_project(presentation_dir)
            timeline_dir = presentation_dir / "build" / "voiceover"
            timeline_dir.mkdir(parents=True)
            (timeline_dir / "timeline.json").write_text(
                json.dumps(
                    {
                        "video": {"width": 1920, "height": 1080, "fps": 30},
                        "slides": [
                            {
                                "index": 1,
                                "image": "images/slide.png",
                                "audio": "build/voiceover/audio/slide-001.mp3",
                                "duration": 1.0,
                                "segments": [
                                    {
                                        "index": 1,
                                        "text": "[calm] Hello world.",
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

            status = generate(str(presentation_dir))
            transcript = (presentation_dir / "transcript.md").read_text(encoding="utf-8")

        self.assertEqual(status, 0)
        self.assertTrue(transcript.startswith("# Presentation Transcript\n"))


if __name__ == "__main__":
    unittest.main()
