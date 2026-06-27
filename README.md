# Uraniborg Skills

Reusable agent skills for scientific and engineering work.

This repository is a small skill catalog for workflows that researchers and
engineers tend to repeat across many projects: reading PDFs, extracting video
transcripts, producing narrated presentations, running Python projects with uv,
maintaining decision proposals, and writing concise docs.

## Skills

| Skill | Purpose |
| --- | --- |
| `ub-pdf-reader` | Search, inspect, render, and cite PDF evidence. |
| `ub-presentation` | Author, caption, and render narrated presentations. |
| `ub-youtube-transcript` | Extract YouTube transcripts into structured Markdown. |
| `ub-uv` | Use uv consistently for Python project setup and execution. |
| `ub-codex` | Handle Codex sandbox, cache, and escalation issues. |
| `ub-dev-env` | Plan team development environments. |
| `ub-proposals` | Draft and review decision-first development proposals. |
| `ub-writing` | Draft, rewrite, and review concise repo docs. |
| `ub-skill-catalog` | Maintain and share Uraniborg public skills. |

## Install

List available skills:

```sh
npx skills add uraniborg-ai/skills --list
```

Install the default research skill set for Codex:

```sh
npx skills add uraniborg-ai/skills \
  --skill ub-pdf-reader \
  --skill ub-presentation \
  --skill ub-youtube-transcript \
  --skill ub-uv \
  --skill ub-codex \
  --skill ub-dev-env \
  --skill ub-proposals \
  --skill ub-writing \
  --skill ub-skill-catalog \
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

## Development

For contribution and skill authoring rules, read `AGENTS.md` and
`docs/development.md`. The `docs/` directory holds the project development
guidance.

Check the skill catalog structure with:

```sh
npm run smoke
```

## Versioning

The repository uses semantic versions through Git tags and `CHANGELOG.md`.
The repository tag is the release source of truth.

Install from a Git tag or update from a release reference when you need a pinned
version in a reproducible environment.
