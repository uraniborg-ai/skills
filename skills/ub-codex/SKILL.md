---
name: ub-codex
description: Handle Codex sandbox, permission, cache, dependency download, credential, and escalation issues while running project commands. Use when Codex hits Operation not permitted, permission denied, home-directory cache failures, uv cache errors, Go cache errors, package download failures, or ambiguous failures that may be caused by restricted filesystem or network access.
---

# UB Codex

Use this skill to adapt commands to Codex's sandbox without changing normal
developer defaults.

## Rules

- Keep Codex-only paths in the command invocation, not in project scripts.
- Prefer repo-local or `/private/tmp` caches for sandboxed commands.
- If a network or permission failure is important to the task, retry with
  escalation instead of inventing an indirect workaround.
- Do not copy credentials from the home directory into temporary paths unless
  the user explicitly asks.
- Treat sandbox failure as environment evidence, not proof that the project is
  broken.

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

## Reporting

When reporting a sandbox issue, include:

- the command that failed
- the relevant error line
- the smallest known environment override or escalation needed
- whether the fix should stay Codex-only

