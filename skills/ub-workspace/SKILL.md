---
name: ub-workspace
description: Manage a local workspace containing many sibling Git repositories with a `.ub-workspace/config.toml` control file. Use when Codex needs to inventory projects, summarize dirty worktrees, compare branches with upstreams, separate references repositories, run fetch-oriented audits, perform only safe fast-forward pulls, prepare first commits with Git LFS, or report push restrictions for workspace repositories.
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
- Do not push automatically. Report `push = "explicit-approval"` and
  `push = "never"` as policy restrictions.
- Fetch or pull only when the user explicitly asks for a sync or fresh remote
  comparison.
- Pull only with `git pull --ff-only`, and only when the current branch can
  fast-forward to its upstream.
- Skip automatic pull for dirty repositories unless the user explicitly asks to
  include dirty worktrees.

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

## First Commit And LFS

When preparing a new repository in a workspace:

- Add `.gitignore` before staging generated files.
- Track large binary source files with Git LFS before `git add`.
- Verify ignored paths with `git check-ignore -v`.
- Verify LFS pointers with `git lfs status` or `git lfs ls-files`.
- Treat pushes containing private documents, medical data, training scans, or
  other restricted material as explicit-approval operations.
