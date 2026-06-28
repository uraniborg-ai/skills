#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import unittest
from pathlib import Path

from generate_audio import concat_command, concat_list_lines, silence_command
from project_config import (
    Project,
    Segment,
    Slide,
    VideoConfig,
    VoiceConfig,
    concat_list_path,
    final_video_path,
    render_clip_path,
    segment_audio_path,
    silence_audio_path,
    slide_audio_path,
    timeline_path,
    voiceover_video_path,
    youtube_srt_path,
)


class AudioHelperTests(unittest.TestCase):
    def make_project(self) -> Project:
        root = Path("/tmp/ub-presentation")
        presentation_dir = root / "contents/2026/01-example"
        return Project(
            path=presentation_dir / "narration.json",
            root=root,
            presentation_dir=presentation_dir,
            voiceover_dir=presentation_dir / "voiceover",
            captions_dir=presentation_dir / "captions",
            exports_dir=presentation_dir / "exports",
            build_dir=presentation_dir / "build",
            voice=VoiceConfig(
                voice_id="voice", model_id="eleven_v3", output_format="mp3_44100_128"
            ),
            video=VideoConfig(width=1920, height=1080, fps=30),
            slides=[],
        )

    def test_canonical_artifact_paths(self) -> None:
        project = self.make_project()
        slide = Slide(index=1, image=project.presentation_dir / "images/cover.png", segments=[])
        segment = Segment(index=2, text="[calm] 설명입니다.", pause_after_ms=350)

        self.assertEqual(
            segment_audio_path(project, slide, segment),
            project.presentation_dir / "voiceover/audio/slide-001/segment-002.mp3",
        )
        self.assertEqual(
            slide_audio_path(project, slide),
            project.presentation_dir / "voiceover/audio/slide-001.mp3",
        )
        self.assertEqual(
            silence_audio_path(project, 350),
            project.presentation_dir / "build/voiceover/silence/silence-0350ms.mp3",
        )
        self.assertEqual(
            concat_list_path(project, slide),
            project.presentation_dir / "build/voiceover/slide-001.concat.txt",
        )
        self.assertEqual(timeline_path(project), project.presentation_dir / "build/timeline.json")
        self.assertEqual(
            youtube_srt_path(project), project.presentation_dir / "captions/youtube.srt"
        )
        self.assertEqual(
            render_clip_path(project, 1), project.presentation_dir / "build/render/clip-001.mp4"
        )
        self.assertEqual(
            voiceover_video_path(project), project.presentation_dir / "build/render/final.mp4"
        )
        self.assertEqual(final_video_path(project), project.presentation_dir / "exports/final.mp4")

    def test_silence_command_uses_milliseconds(self) -> None:
        command = silence_command(Path("silence-0350ms.mp3"), 350)
        self.assertEqual(command[0], "ffmpeg")
        self.assertIn("0.350", command)
        self.assertEqual(command[-1], "silence-0350ms.mp3")

    def test_concat_helpers(self) -> None:
        lines = concat_list_lines([Path("segment-001.mp3"), Path("silence-0350ms.mp3")])
        self.assertEqual(lines, "file 'segment-001.mp3'\nfile 'silence-0350ms.mp3'\n")

        command = concat_command(Path("slide-001.concat.txt"), Path("slide-001.mp3"))
        self.assertEqual(command[:5], ["ffmpeg", "-y", "-f", "concat", "-safe"])
        self.assertEqual(command[-1], "slide-001.mp3")


if __name__ == "__main__":
    unittest.main()
