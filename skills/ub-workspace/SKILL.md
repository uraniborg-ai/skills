---
name: ub-workspace
description: Bootstrap, inspect, and safely synchronize a docs-led workspace containing many Git-backed research, engineering, analysis, documentation, or software projects. Use when the user wants to install or recover a workspace from a docs repository, create or validate the required docs/workspace.toml project manifest, clone declared child projects, list dirty repositories, summarize recent work, identify ahead/behind/diverged branches, or run conservative fast-forward-only sync across projects declared in the manifest.
metadata:
  version: 0.2.0
  stability: stable
  domain: research-workspace
---

# UB Workspace

Use this skill when a workspace is governed by a root `docs` Git repository.
Treat `docs/workspace.toml` as the source of truth for which child projects
belong in the workspace.

Project-specific proposals stay inside each project. Workspace-level proposals
stay in the root `docs/proposals` directory.

## Workflow

1. Locate or ask for the docs repository.
2. Clone it into `<workspace>/docs` if it is missing.
3. Read `docs/workspace.toml`.
4. Validate its `[[projects]]` entries.
5. Clone missing declared projects when the user asked for bootstrap.
6. Run status, report, and sync against declared projects.

For the workspace manifest and `001` proposal contract, read
`references/workspace-proposals.md` before creating or changing the proposal.
For Git state categories and sync invariants, read
`references/git-safety-policy.md` when interpreting status or sync output.

## Commands

Run the bundled script from this skill directory:

```sh
python3 scripts/ub_workspace.py validate --root /path/to/workspace
python3 scripts/ub_workspace.py projects --root /path/to/workspace
python3 scripts/ub_workspace.py bootstrap --root /path/to/workspace --docs-repo DOCS_REPO_URL
python3 scripts/ub_workspace.py status --root /path/to/workspace
python3 scripts/ub_workspace.py report --root /path/to/workspace --days 7
python3 scripts/ub_workspace.py sync --root /path/to/workspace --dry-run
python3 scripts/ub_workspace.py sync --root /path/to/workspace
```

`validate-proposals` remains as a compatibility alias for `validate`.

Use `init-proposals` only after the user confirms that a missing workspace
manifest and supporting `001` proposal should be generated from the currently
cloned sibling repositories:

```sh
python3 scripts/ub_workspace.py init-proposals --root /path/to/workspace
```

Use `--discover` with `status`, `report`, or `sync` only as a compatibility or
diagnostic mode. The default is docs-led discovery.

## Safety Rules

- Do not merge, rebase, reset, force push, checkout, or delete branches.
- Do not invent the docs repository URL. Ask when it is unknown.
- Do not auto-create `docs/workspace.toml` or `docs/proposals/001-*.md` for an
  empty docs repo without user confirmation.
- Skip automatic sync when a repository has uncommitted or untracked changes.
- Treat `status`, `report`, `projects`, `validate`, and `validate-proposals` as
  read-only.
- In `sync`, fetch before comparing with upstream.
- Pull only when the current branch can fast-forward to its upstream.
- Report missing, dirty, local-ahead, diverged, detached, and no-upstream
  repositories as items requiring attention.

## Reporting

When finishing workspace work, include:

- docs repo path and `docs/workspace.toml` manifest used
- cloned, already-present, missing, and failed projects
- dirty worktrees and branch attention
- sync actions, especially fast-forwarded, skipped, diverged, and failed repos
- any commands that needed network or permission escalation
