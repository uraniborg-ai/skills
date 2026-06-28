---
name: ub-presentation
description: Create, validate, migrate, narrate, caption, and render presentation projects with slide images, segmented narration, ElevenLabs voiceover audio, YouTube subtitles, transcripts, and final video exports. Use when working with a presentation directory that contains narration.json, images, build artifacts, and optional draft.md or slides.md files.
---

# UB Presentation

Use this skill for presentation projects that keep source material and generated
artifacts together.

## Project Shape

Each presentation can live in any directory. `contents/YYYY/NN-title/` is a
common shape, not a requirement:

```text
presentation.yaml
draft.md
slides.md
narration.json
transcript.md
youtube.srt
images/
build/voiceover/
exports/
```

Use `draft.md` for long-form thinking, `slides.md` for slide titles or
structure, and `narration.json` as the executable voiceover input. Only
`narration.json` and referenced slide images are required by the validator.
Narration uses `slides[].segments[]`; the legacy `slides[].text` shape is not
valid.

## Workflow

Run scripts with `uv run --script`.

1. Convert legacy paragraph narration when needed:

   ```sh
   uv run --script skills/ub-presentation/scripts/segment_narration.py path/to/presentation --dry-run
   uv run --script skills/ub-presentation/scripts/segment_narration.py path/to/presentation
   ```

2. Validate the project:

   ```sh
   uv run --script skills/ub-presentation/scripts/validate_project.py path/to/presentation --skip-api-key
   ```

3. Generate or reuse segment and slide audio:

   ```sh
   uv run --script skills/ub-presentation/scripts/generate_audio.py path/to/presentation
   ```

4. Build the timeline:

   ```sh
   uv run --script skills/ub-presentation/scripts/build_timeline.py path/to/presentation
   ```

5. Generate YouTube subtitles and transcript:

   ```sh
   uv run --script skills/ub-presentation/scripts/generate_subtitles.py path/to/presentation
   ```

6. Render the video:

   ```sh
   uv run --script skills/ub-presentation/scripts/render_video.py path/to/presentation --overwrite
   ```

For a no-API planning check:

```sh
uv run --script skills/ub-presentation/scripts/run_pipeline.py path/to/presentation --dry-run
```

## Notes

- Keep `timeline.json` paths relative to the presentation directory.
- Keep generated YouTube captions in `youtube.srt`.
- Keep the readable script in `transcript.md`.
- When editing spoken narration, avoid reading dense slide bullets verbatim;
  see `references/script-editing.md` for script, terminology, and regeneration
  guidance.
- When revising slide image prompts, use reference assets and pilot images
  before broad regeneration; see `references/image-prompting.md`.
- Use ElevenLabs v3 audio tags sparingly at the start of segment text, for example `[calm]` or `[thoughtful][slight emphasis]`.
- Segment audio is generated under `build/voiceover/audio/slide-001/segment-001.mp3` and concatenated into `build/voiceover/audio/slide-001.mp3`.
- Store real API keys only in `.env` or the process environment. Scripts read
  the nearest `.env` found from the presentation directory upward and do not
  override existing environment values.
- See `references/input-schema.md`, `references/elevenlabs.md`, and `references/ffmpeg.md` when changing script behavior.
