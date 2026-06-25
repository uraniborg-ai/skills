# Uraniborg Skills

Reusable agent skills for scientific and engineering work.

This repository is a small skill catalog for workflows that researchers and
engineers tend to repeat across many projects: reading PDFs, extracting video
transcripts, running Python projects with uv, maintaining decision proposals,
and writing concise docs.

## Skills

| Skill | Purpose |
| --- | --- |
| `ub-pdf-reader` | Search, inspect, render, and cite PDF evidence. |
| `ub-youtube-transcript` | Extract YouTube transcripts into structured Markdown. |
| `ub-uv` | Use uv consistently for Python project setup and execution. |
| `ub-codex` | Handle Codex sandbox, cache, and escalation issues. |
| `ub-proposals` | Draft and review decision-first development proposals. |
| `ub-writing` | Draft, rewrite, and review concise repo docs. |

## Install

List available skills:

```sh
npx skills add uraniborg-ai/skills --list
```

Install the default research skill set for Codex:

```sh
npx skills add uraniborg-ai/skills \
  --skill ub-pdf-reader \
  --skill ub-youtube-transcript \
  --skill ub-uv \
  --skill ub-codex \
  --skill ub-proposals \
  --skill ub-writing \
  --agent codex
```

Install one skill globally:

```sh
npx skills add uraniborg-ai/skills --skill ub-pdf-reader --global --agent codex
```

Update installed skills:

```sh
npx skills update --global
```

## Versioning

The repository uses semantic versions through Git tags and `CHANGELOG.md`.
The repository tag is the release source of truth.

Install from a Git tag or update from a release reference when you need a pinned
version in a reproducible environment.
