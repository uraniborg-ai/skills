---
name: ub-git
description: Use conservative Git workflows for local repository status, diffs, staging, commits, commit messages, branch and upstream checks, fetch/pull/push safety, dirty worktree protection, first commits, Git LFS checks, and sensitive-file review. Use when Codex needs to inspect or change Git state, prepare or review commits, draft commit messages, sync branches, or decide safe Git commands in a single repository.
---

# UB Git

Use this skill for single-repository Git work. Prefer read-only inspection
before changing Git state, and protect user changes as the first constraint.

## Workflow

1. Inspect repository state before deciding:
   - `git status --short --branch`
   - `git diff --stat`
   - `git diff --cached --stat`
2. Separate staged, unstaged, and untracked changes. If unrelated changes are
   mixed together, propose or use separate commits instead of folding them into
   one.
3. Stage intentionally. Prefer `git add <path>` for the files in scope. Use
   broad staging only after reviewing the worktree.
4. Before committing, inspect `git diff --cached`. Do not commit when nothing is
   staged.
5. Fetch, pull, and push only when the user asks for remote synchronization or
   publication.

## Safety

- Do not revert user changes unless the user explicitly asks for that exact
  operation.
- Treat `git reset --hard`, `git checkout -- <path>`, `git clean`, forced
  pushes, rebases, merges, and stashes as explicit-request operations.
- In a dirty worktree, do not pull, merge, rebase, or stash automatically.
- Use `git pull --ff-only` for ordinary pulls. Report detached HEAD, no upstream,
  diverged branches, and local-ahead branches instead of resolving them
  implicitly.
- Do not push private documents, medical data, training scans, credentials,
  `.env` files, API keys, or other restricted material without explicit review
  and approval.
- If Git commands fail because of Codex sandbox permissions, follow
  `$ub-codex`.

## Commit Messages

- Check local message rules first: `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/commit-conventions.md`, release docs, or maintainer docs.
- When local rules exist, follow them.
- When no local rule exists, use Conventional Commits v1.0.0 in English:
  `type(scope): description` when a useful scope is clear.
- Write an imperative, lowercase description with no trailing period.
- Mark breaking changes with `!` after the type or scope, or with a
  `BREAKING CHANGE:` footer.
- Base the message on `git diff --cached` when changes are staged. If drafting
  from unstaged changes, say that the message is not yet based on staged
  content.

## First Commit And LFS

When preparing a new repository or first commit:

- Add `.gitignore` before staging generated files.
- Check whether large binary source files or datasets need Git LFS before
  `git add`.
- Verify ignored paths with `git check-ignore -v`.
- Verify LFS pointers with `git lfs status` or `git lfs ls-files`.
