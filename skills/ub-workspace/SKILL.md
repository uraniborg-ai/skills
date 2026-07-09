---
name: ub-workspace
description: Manage a local workspace containing many sibling Git repositories with a `.ub-workspace/config.toml` control file. Use when Codex needs to inventory projects, summarize repository status across a workspace, compare branches with upstreams, separate references repositories, run fetch-oriented audits, or apply safe multi-repository sync workflows using ub-git repository safety rules.
metadata:
  version: 0.1.0
  stability: experimental
  domain: workspace-operations
---

# UB Workspace

Use this skill to operate a multi-repository workspace from a local
`.ub-workspace/config.toml` file.

## Rules

- Treat status and inventory requests as read-only by default.
- Read `.ub-workspace/config.toml` before classifying repositories when it
  exists. Use Python's standard `tomllib`; do not require YAML.
- Discover sibling Git repositories automatically. Use config entries only for
  groups, exceptions, and repository-specific policy.
- Apply policy in this order: repository entry, then group entry, then
  defaults.
- Separate `references/*` from regular projects when the config defines a
  references group.
- Apply `$ub-git` for repository-level safety: explicit remote operations,
  fast-forward-only pulls, dirty worktree protection, push restrictions, first
  commit checks, and Git LFS review.

## Workflows

For a read-only workspace report:

```sh
uv run --script skills/ub-workspace/scripts/workspace_status.py --root /Users/hyounggyu/Works
```

For machine-readable status:

```sh
uv run --script skills/ub-workspace/scripts/workspace_status.py --root /Users/hyounggyu/Works --json
```

For a fetch and safe fast-forward dry run:

```sh
uv run --script skills/ub-workspace/scripts/workspace_sync.py --root /Users/hyounggyu/Works --dry-run
```

For an actual conservative sync:

```sh
uv run --script skills/ub-workspace/scripts/workspace_sync.py --root /Users/hyounggyu/Works
```

For first commits, Git LFS, staging, commits, pushes, or single-repository Git
decisions inside a workspace, use `$ub-git`.
