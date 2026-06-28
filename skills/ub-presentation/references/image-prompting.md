# Image Prompting

Use these notes when revising slide image prompts or generated presentation
images.

## Reference Assets

- Separate reference images from slide images. A reference image defines
  character, palette, line style, or composition rules; it should not be wired
  into `slides.md` or `narration.json` unless it is also a real slide.
- For character or style consistency, create a compact reference sheet before
  regenerating many slide images. Reuse the reference as a visual contract in
  later prompts.
- Keep reference prompts inspectable next to generated assets, following the
  project image directory convention when one exists.

## Pilot Before Batch

- Before replacing a full deck of images, regenerate one reference image and
  one high-signal pilot slide. Use the pilot to check whether the style works
  with the existing deck.
- Prefer keeping image paths stable, such as `images/<slug>/cover.png`, so
  `slides.md`, `narration.json`, timelines, and render scripts do not need
  structural changes.
- Separate prompt updates from video regeneration. Regenerate or render media
  only after the user accepts the image direction or explicitly asks for it.

## Message Priority

- Individual slide images should make the slide concept the main subject. A
  recurring character can provide continuity, but should not become the hero of
  every slide unless the slide is about that character.
- Carry visual energy through layout, motion, color accents, framing, and
  rhythm rather than by enlarging decorative characters or adding unrelated
  spectacle.
- When borrowing inspiration from an external artwork, brand, film, or
  character, use abstract qualities such as palette, pacing, or composition.
  Do not ask for recognizable likenesses, costumes, logos, scenes, or named
  character replication.

## Recurring Characters

- Do not rely on `reference character` alone. Repeat the character's hair,
  clothing, silhouette, role, and on-slide scale in each prompt where visual
  identity matters.
- Before locking a character description, inspect close crops of the accepted
  reference or pilot image. Confirm the actual hairstyle, face silhouette, and
  clothing rather than naming them from memory.
- Avoid ambiguous hairstyle labels unless the crop confirms them. For example,
  distinguish a ponytail, bob cut, loose long hair, bun, or swept-back hair
  before carrying that phrase into the prompt.
- Keep repeated characters functional unless the slide is about the person.
  They can anchor continuity, but the slide concept should still dominate.

## Action-Readable Poses

- Avoid abstract pose instructions such as `natural pose`, `forearms on desk`,
  or `hands resting` when the character is doing operational work.
- Tie hands to tools and actions: typing on a keyboard, using a mouse, writing
  on a tablet or notebook, checking a list, or sorting record cards.
- Make the action match the slide message. A monitoring slide can show keyboard
  and mouse work; a review slide can show notes, tablet marks, or checklist
  updates.
- If a non-work pose is intentional, make it slide-specific. Do not let an
  exception such as a thinking pose become the default for the deck.

## Consistency And QA

- Keep visual prompts aligned with the accepted narration. If boundary,
  governance, or implementation details were removed from the script, check
  that old visual labels and diagrams do not bring them back.
- Search prompt files for stale terms after major script edits. Avoid putting
  exact stale phrases in negative prompts when that makes text search noisy;
  use a general avoid phrase instead.
- Build a contact sheet after regeneration to compare tone, character
  consistency, text density, and message focus across the deck. Inspect key
  slides individually when they define the deck's first impression or closing
  takeaway.
- For recurring characters, also build or inspect close crops. Check whether
  the person reads as the same character, whether the hair and clothing
  silhouette stay consistent, whether hands connect to tools, and whether the
  intended work action is readable.
- Judge pilot images for repeatability, not only single-image quality. Ask
  whether the pose, hairstyle, and tool interaction will remain believable when
  reused across many slides.
