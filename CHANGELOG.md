# Changelog

## Unreleased

## 0.8.2 - 2026-08-16

- Teach `ub-project-setup` to inspect project-local agent skills, search the
  `uraniborg-ai` owner for relevant `ub-*` skills, and optionally propose the
  global Vercel `find-skills` skill through `npx skills` with explicit scope,
  target-agent, review, and approval guidance.

## 0.8.1 - 2026-08-16

- Expand `ub-project-setup` around development-environment analysis and current
  project documentation, including `.python-version`, `.ruff.toml`, Homebrew,
  Node.js, uv, GitHub CLI, agent guidance links, and optional PEP-inspired
  proposal/TODO records. Remove the proposal-specific frontmatter validator.

## 0.8.0 - 2026-08-15

- Remove `ub-pdf-reader` from the public catalog. Existing users should
  refresh their skill installations to remove the obsolete copy.
- Replace `ub-dev-env`, `ub-proposals`, and `ub-writing` with
  `ub-project-setup`, which establishes or improves project development
  environments, decision proposals, and technical documentation. Existing
  users should replace the old skill invocations when refreshing installations.
- Remove `ub-presentation`, `ub-youtube`, and `ub-workspace` from the public
  catalog. These workflows are now maintained as project-local tools rather
  than distributed agent skills. Existing installed copies remain until users
  refresh their skill installations.

## 0.7.0 - 2026-07-09

- Remove `ub-skill-catalog` from the public skill catalog.

## 0.6.0 - 2026-07-09

- Remove `ub-finance-data` from the public skill catalog. Existing users should
  refresh installed skills with `npx skills update --global` or their
  project-local update command so removed catalog entries are cleaned up.
- Expand `ub-proposals` with post-implementation edit guidance, including when
  implemented proposals need `Revision Notes` with the change and rationale.
- Add `ub-git` for conservative single-repository Git workflows, including
  status, staging, commits, commit messages, remote sync, first commits, Git
  LFS, and sensitive-file review.
- Move commit message guidance from `ub-writing` to `ub-git` so `ub-writing`
  focuses on project technical documentation.
- Refocus `ub-workspace` on multi-repository workspace orchestration and defer
  repository-level Git safety rules to `ub-git`.

## 0.5.1 - 2026-07-04

- Remove fixed `--agent` targets from README and `ub-skill-catalog`
  installation guidance so users can choose their supported agent target.

## 0.5.0 - 2026-07-04

- Add `ub-finance-data` for provenance-preserving Korean stock index and
  interest-rate data collection.
- Expand `ub-finance-data` with Korean stock OHLCV collection by ticker.

## 0.4.0 - 2026-07-04

- Add `ub-workspace` for `.ub-workspace/config.toml`-driven multi-repository
  workspace inventory and conservative fast-forward sync workflows.
- Rename `ub-youtube-transcript` to `ub-youtube` and expand it with playlist,
  Watch Later, Markdown/JSON export, and optional playlist transcript
  collection workflows. Existing users should replace the
  `ub-youtube-transcript` install target and `$ub-youtube-transcript`
  invocation with `ub-youtube` and `$ub-youtube`.
- Expand `ub-skill-catalog` release guidance to track skill rename and
  replacement migration notes before installed-copy refresh guidance.

## 0.3.0 - 2026-06-28

- Add `ub-jupyter` for local Jupyter notebook inspection, editing, validation,
  project-aware uv execution, and review hygiene.

## 0.2.2 - 2026-06-28

- Limit `ub-writing` commit guidance to commit message rules and leave commit
  operations to project or agent conventions.

## 0.2.1 - 2026-06-28

- Align `ub-youtube-transcript` with uv script execution and script-local
  dependencies.
- Clarify that `ub-writing` applies when creating Git commits and must check
  local commit message rules before committing.

## 0.2.0 - 2026-06-28

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
- Refactor `ub-presentation` around fixed `voiceover/`, `captions/`,
  `exports/`, and `build/` artifact directories.
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
