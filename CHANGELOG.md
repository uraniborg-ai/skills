# Changelog

## Unreleased

- Add `ub-presentation` for authoring, validating, narrating, captioning, and
  rendering presentation projects with segmented narration and video exports.
- Expand `ub-presentation` with script-editing guidance for spoken flow,
  terminology choices, and generated artifact regeneration.
- Expand `ub-presentation` with image-prompting guidance for reference assets
  and pilot image regeneration.
- Add visual consistency and contact-sheet QA guidance for presentation image
  updates.
- Expand `ub-presentation` image prompting guidance for recurring character
  consistency and action-readable operator poses.
- Clarify `ub-presentation` configurable voiceover output directories and
  asset-vs-build artifact guidance.
- Add `ub-skill-catalog` for maintaining, improving, validating, and sharing
  Uraniborg public skills from the source catalog.
- Teach `ub-skill-catalog` to inspect `.claude/skills` installed copies along
  with `.agents/skills`.
- Expand `ub-skill-catalog` with explicit-request-only `npx skills` install,
  update, and installed-copy check guidance for Codex and Claude Code.
- Add `ub-dev-env` and `ub-skill-catalog` to README catalog and install
  examples.
- Expand `ub-proposals` with refactoring, compression, terminology maturity,
  and core/supporting content guidance.
- Limit `ub-writing` to project technical documentation and add routing
  guidance for contributor docs, proposals, generated docs, agent instructions,
  and commit messages.
- Remove `ub-workspace` from the public skill catalog.

## 0.1.1

- Expand `ub-uv` with pyproject-owned Python version policy, PEP 723 script
  dependencies, temporary `uv run --with` usage, and validation guidance.
- Expand `ub-codex` with validation, tool behavior, dirty-worktree, escalation,
  project-note, and reporting guidance.
- Move `ub-workspace` from a standalone proposal-store model to a root `docs`
  repository with workspace proposals under `docs/proposals`.
- Add `ub-proposals` for drafting, reviewing, auditing, and maintaining
  decision-first development proposals.
- Standardize new proposal filenames on `NNN-<title>.md` and frontmatter on
  `title`, `description`, PEP-style `author`, and canonical `status`.
- Add `ub-writing` for concise, context-efficient repo documentation drafting,
  rewriting, and review.
- Add OpenAI agent metadata for canonical skills.

## 0.1.0

- Start the Uraniborg skill catalog.
- Add `ub-pdf-reader`, `ub-youtube-transcript`, `ub-uv`, and `ub-workspace`.
- Combine project status and safe repository sync workflows into `ub-workspace`.
