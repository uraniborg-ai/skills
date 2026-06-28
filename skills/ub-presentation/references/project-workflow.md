# Project Workflow

Use one presentation directory as the unit of work. The directory can live
anywhere in a project; `contents/YYYY/NN-title/` is only a common convention.

## Structure

```text
draft.md
slides.md
narration.json
images/
voiceover/
  audio/
captions/
  youtube.srt
exports/
  final.mp4
build/
  timeline.json
  voiceover/
  render/
```

`draft.md` develops the presentation idea, background, logic, and examples.
`slides.md` coordinates slide flow and message. `narration.json` is the only
pipeline input for voiceover, captions, and rendering.

`voiceover/`, `captions/`, and `exports/` are reviewable or reusable generated
assets. `build/` contains disposable computed artifacts such as timeline data,
silence files, concat lists, render clips, and intermediate videos.

## Markdown Frontmatter

`draft.md` and `slides.md` can use the same minimal frontmatter:

```yaml
---
title: Presentation Title
description: One-sentence presentation purpose or message.
author:
  - Hyounggyu Kim <code@hyounggyu.com>
status: draft
created_at: 2026-06-28T00:00:00+09:00
updated_at: 2026-06-28T00:00:00+09:00
---
```

Allowed document statuses are `draft`, `active`, `superseded`, and `archived`.
Frontmatter describes document state only; it does not control pipeline
behavior.

## Workflow

1. Develop the presentation idea in `draft.md`.
2. Settle slide flow and image direction in `slides.md`.
3. Reflect the agreed flow in `narration.json` using `slides[].segments[]` and
   `slides[].image`.
4. Generate or update slide images in `images/`.
5. Generate voiceover audio in `voiceover/audio/`.
6. Build `build/timeline.json`, then generate `captions/youtube.srt`.
7. Render intermediate video under `build/render/`, then export
   `exports/final.mp4`.

Old root-level `youtube.srt` or `transcript.md` files can remain in existing
projects, but new runs do not create or update them.
