# Git Safety Policy

`ub-workspace` is designed for researchers and engineers who maintain many
small or medium projects at once. It should give a calm workspace overview and
perform only conservative synchronization. In docs-led workspaces, the repo set
comes from `docs/workspace.toml`; filesystem discovery is a diagnostic mode.

## Status Categories

- `up_to_date`: current branch matches upstream.
- `behind`: upstream has commits not present locally.
- `ahead`: local branch has commits not present upstream.
- `diverged`: local and upstream both have unique commits.
- `no_upstream`: current branch has no configured upstream.
- `detached`: repository has no current branch.
- `dirty`: repository has local uncommitted or untracked changes.
- `missing`: repository is declared in the workspace manifest but is not cloned.

## Sync Categories

- `fast_forwarded`: pulled successfully with `git pull --ff-only`.
- `would_fast_forward`: dry run found a safe fast-forward.
- `dirty_skipped`: fast-forward may be available, but local changes exist.
- `local_ahead`: local branch contains commits not on upstream.
- `diverged`: user must decide how to integrate histories.
- `missing`: user must bootstrap or clone the declared repository.
- `no_upstream`: user must configure tracking before sync.
- `failed`: Git command failed.

## Invariants

- Never hide dirty worktrees.
- Never choose merge or rebase policy for the user.
- Never use destructive commands as part of this skill.
- Mention when status data may be stale because no fetch was run.
