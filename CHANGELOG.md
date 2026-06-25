# Changelog

## Unreleased

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
