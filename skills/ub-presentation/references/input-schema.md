# Input Schema

Use one `narration.json` file per presentation directory. The directory can be
any project-local path; `contents/YYYY/NN-title` is only a common convention.

```json
{
  "output_dir": "build/voiceover",
  "exports_dir": "exports",
  "video": {
    "width": 1920,
    "height": 1080,
    "fps": 30
  },
  "voice": {
    "voice_id": "${ELEVENLABS_VOICE_ID}",
    "model_id": "eleven_v3",
    "output_format": "${ELEVENLABS_OUTPUT_FORMAT}"
  },
  "slides": [
    {
      "image": "images/example/cover.png",
      "segments": [
        {
          "text": "[calm] 먼저, 왜 기존 방식이 힘든지부터 보겠습니다.",
          "pause_after_ms": 450
        },
        {
          "text": "[thoughtful][slight emphasis] 핵심은 발표 흐름을 작은 호흡 단위로 나누는 것입니다.",
          "pause_after_ms": 700
        }
      ]
    }
  ]
}
```

Paths are resolved relative to the presentation directory. `output_dir` can point to a temporary build location such as `build/voiceover` or a reusable voiceover asset directory such as `voiceover`.

`slides[].text` is a legacy shape and is rejected by the validator. Use `segment_narration.py` to create an initial `slides[].segments[]` draft from an older file.

Segment text is passed directly to ElevenLabs, including inline audio tags. Keep tags short and place them at the beginning of the segment. `pause_after_ms` controls the silence inserted after the segment before the slide-level MP3 is concatenated.

`slides.md` is optional. When present, `generate_subtitles.py` uses `##`
headings as transcript slide titles.

`generate_subtitles.py` reads `<output_dir>/timeline.json` and writes:

- `youtube.srt`
- `transcript.md`
