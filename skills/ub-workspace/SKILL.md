---
name: ub-workspace
description: Inspect and safely synchronize a workspace containing many Git-backed research, engineering, analysis, documentation, or software projects. Use when the user wants to check multiple project statuses, list dirty repositories, summarize recent work, identify ahead/behind/diverged branches, or run conservative fast-forward-only sync across sibling repositories.
metadata:
  version: 0.1.0
  stability: stable
  domain: research-workspace
---

# UB Workspace

Use this skill when a user works across many sibling repositories and needs a
workspace-level view rather than one project at a time.

## Commands

Run the bundled script from this skill directory:

```sh
python3 scripts/ub_workspace.py status --root /path/to/workspace
python3 scripts/ub_workspace.py report --root /path/to/workspace --days 7
python3 scripts/ub_workspace.py sync --root /path/to/workspace --dry-run
python3 scripts/ub_workspace.py sync --root /path/to/workspace
```

## Modes

- `status`: read-only. Scans immediate child Git repositories, reports local
  changes, branch relation, upstream, and recent commits using local refs.
- `report`: read-only. Emphasizes recent work across projects.
- `sync`: fetches remotes and performs `git pull --ff-only` only when safe.

## Safety Rules

- Do not merge, rebase, reset, force push, checkout, or delete branches.
- Skip automatic sync when a repository has uncommitted or untracked changes.
- Treat `status` and `report` as read-only. They must not fetch or mutate files.
- In `sync`, fetch before comparing with upstream.
- Pull only when the current branch can fast-forward to its upstream.
- Report dirty, local-ahead, diverged, detached, and no-upstream repositories as
  items requiring attention.

For detailed status categories, read `references/git-safety-policy.md`.

