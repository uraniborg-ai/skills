# Script Editing

Use these notes when revising spoken narration for a presentation project.

## Spoken Flow

- Treat `slides.md` as a visual outline and `narration.json` as the spoken
  script. The narration should explain relationships, causes, and flow instead
  of reading every bullet on the slide.
- Replace long noun lists with a few representative examples, then summarize
  the category in plain language. If the list still matters, split it across
  short sentences.
- Give repeated core messages different jobs across the talk: opening scene,
  formal definition, workflow explanation, and closing takeaway.

## Terminology

- Keep English or technical labels when they are product names, domain-standard
  terms, or intentional concept labels. Translate implementation details and
  ordinary operational language into the audience's language when that improves
  comprehension.
- Keep terminology aligned across `slides.md` and `narration.json`. Do not
  force the same rewrite into image filenames, asset identifiers, alt text, or
  source references when those names are serving as stable identifiers.
- When a term feels ambiguous in spoken form, prefer the phrase that explains
  the role it plays in the workflow over the phrase that mirrors the internal
  implementation.

## Vision Talks

- Be careful with negative definitions and boundary or governance explanations.
  They can be important for implementation, but in a vision talk they may
  interrupt the main message. Prefer positive definitions and collaboration
  flow unless the boundary is the point of the slide.
- When removing a boundary explanation, preserve the operational idea by
  showing how work moves from observation to decision, action, report, and
  review.

## Source And Generated Artifacts

- Separate text-source editing from media regeneration. Update `slides.md`,
  and `narration.json` first; regenerate audio, subtitles, and video only after
  the script is accepted or the user explicitly requests it.
- After deleting or renumbering slides, check for stale generated artifacts and
  references such as old slide audio, render clips, timeline entries, and SRT
  cues.
- Treat `voiceover/audio/`, `captions/`, and `exports/` as reviewable generated
  assets. Treat `build/` as disposable pipeline output.
