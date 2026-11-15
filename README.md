---
title: Uraniborg Skills
description: Public agent skills for Python with uv, Git workflows, and Codex execution issues.
status: active
---

# Uraniborg Skills

Reusable agent skills for scientific and engineering work.

## Skills

| Skill | Purpose |
| --- | --- |
| `uv` | Use uv for Python environments, dependencies, and execution. |
| `git` | Inspect and operate Git repositories safely. |
| `codex` | Handle Codex sandbox, permissions, caches, and escalation. |

## Install

List the catalog, then install the skills needed for your project:

```sh
npx skills add uraniborg-ai/skills --list
npx skills add uraniborg-ai/skills --skill uv git codex --agent codex
```

Run from the target project. Select another supported agent with `--agent`;
use `--global` only when you want a user-level installation.
Inspect installed skills with `npx skills list` and project installation
records in `skills-lock.json`.

## Migration from 0.8.x

Version 0.9.0 renames `ub-uv`, `ub-git`, and `ub-codex` to `uv`, `git`, and
`codex`. Update skill invocations and project guidance to the new names.
`ub-project-setup` and `ub-jupyter` are removed with no automatic replacement.

Review and preserve local changes to installed skills, install and verify the
new names, then remove the old copies using the installation tool for the same
scope and agents. Do not assume an update automatically renames or removes
every existing installation. Keep one source per skill name in a project.

## Development

Read [AGENTS.md](AGENTS.md) and the [development guide](docs/development.md).
Validate the public catalog with:

```sh
npm run smoke
```

## Versioning

Git release tags and `CHANGELOG.md` identify published releases. A version in
the working tree is a release candidate until its tag is published.
Use a release reference when a reproducible installation is needed.
