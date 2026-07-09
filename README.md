# Uraniborg Skills

Reusable agent skills for scientific and engineering work.

This repository is a small skill catalog for workflows that researchers and
engineers tend to repeat across many projects: reading PDFs, working with
Jupyter notebooks, collecting YouTube research notes, producing narrated
presentations, running Python projects with uv, operating Git repositories,
maintaining decision proposals, and writing concise docs.

## Skills

| Skill | Purpose |
| --- | --- |
| `ub-pdf-reader` | Search, inspect, render, and cite PDF evidence. |
| `ub-jupyter` | Inspect, edit, validate, and explicitly execute Jupyter notebooks. |
| `ub-presentation` | Author, caption, and render structured narrated presentations. |
| `ub-youtube` | Collect YouTube transcripts and playlist research notes. |
| `ub-uv` | Use uv consistently for Python project setup and execution. |
| `ub-git` | Operate Git repositories safely. |
| `ub-codex` | Handle Codex sandbox, cache, and escalation issues. |
| `ub-dev-env` | Plan team development environments. |
| `ub-workspace` | Operate multi-repo workspaces safely. |
| `ub-proposals` | Draft, review, and refactor decision-first development proposals. |
| `ub-writing` | Draft, rewrite, and review project technical docs. |
| `ub-skill-catalog` | Maintain and share Uraniborg public skills. |

## Install

List available skills:

```sh
npx skills add uraniborg-ai/skills --list
```

Install the default research skill set:

```sh
npx skills add uraniborg-ai/skills \
  --skill ub-pdf-reader \
  --skill ub-jupyter \
  --skill ub-presentation \
  --skill ub-youtube \
  --skill ub-uv \
  --skill ub-git \
  --skill ub-codex \
  --skill ub-dev-env \
  --skill ub-workspace \
  --skill ub-proposals \
  --skill ub-writing \
  --skill ub-skill-catalog
```

Use the `npx skills` CLI options when you need to target a specific supported
agent or install location.

Install `ub-skill-catalog`:

```sh
npx skills add uraniborg-ai/skills --skill ub-skill-catalog
```

Install one skill globally:

```sh
npx skills add uraniborg-ai/skills --skill ub-pdf-reader --global
```

Check installed copies by inspecting `~/.agents/.skill-lock.json`,
`~/.agents/skills`, and `~/.claude/skills`.

Update installed skills:

```sh
npx skills update --global
```

Global updates can affect installed skills beyond this `ub-*` catalog.
Updates also clean up skills that have been removed from the public catalog.

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
