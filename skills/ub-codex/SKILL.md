---
name: ub-codex
description: Handle Codex sandbox, permission, cache, dependency download, credential, escalation, validation, tool behavior, and dirty-worktree issues while running project commands. Use when Codex hits Operation not permitted, permission denied, home-directory cache failures, uv cache errors, Go cache errors, package download failures, approval questions, validation failures, or ambiguous failures that may be caused by restricted filesystem or network access.
metadata:
  version: 0.2.0
  stability: stable
  domain: codex-operations
---

# UB Codex

Use this skill to adapt commands to Codex's sandbox without changing normal
developer defaults.

## Rules

- Keep Codex-only paths in the command invocation, not in project scripts.
- Prefer repo-local or `/private/tmp` caches for sandboxed commands.
- If a network or permission failure is important to the task, retry with
  escalation instead of inventing an indirect workaround.
- Do not repeat the same sandbox, network, or dependency command after it fails;
  change one relevant condition or request escalation with the narrowest command.
- Do not copy credentials from the home directory into temporary paths unless
  the user explicitly asks.
- Treat sandbox failure as environment evidence, not proof that the project is
  broken.
- Do not revert user changes in a dirty worktree while debugging Codex-only
  failures.
- Keep durable Codex operating knowledge in the project agent docs, not in
  project scripts.

## Common Fixes

Use a local uv cache when home cache access fails:

```sh
UV_CACHE_DIR=.uv-cache uv run ruff format --check .
UV_CACHE_DIR=.uv-cache uv run --script path/to/script.py
```

Use temporary Go caches when Go writes outside the sandbox:

```sh
GOCACHE=/private/tmp/ub-go-cache GOMODCACHE=/private/tmp/ub-go-mod-cache go test ./...
```

For tools that write sessions or settings under the home directory, first look
for environment variables that redirect session/cache paths to `/private/tmp`.
For authenticated or model-backed smoke tests, prefer a bounded command and ask
for escalation when sandboxed credentials are not available.

## Project Notes

If a Codex-only issue is repeatable, record the smallest useful note in the
project's agent documentation, such as `docs/agents/codex.md` or `AGENTS.md`.

Record:

- repeated sandbox, permission, cache, or metadata-directory failures
- dependency, registry, or network escalation patterns
- validation tool setup that differs only in Codex
- safe approved-command-prefix guidance
- user-visible Codex limitations

Do not record:

- one-time command output
- general Git, Python, Rust, or Markdown usage
- product or domain decisions unrelated to Codex operation
- speculation that did not change the fix

## Reporting

When reporting a sandbox issue, include:

- the command that failed
- the relevant error line
- the smallest known environment override or escalation needed
- the validation result after the fix
- whether the fix should stay Codex-only
