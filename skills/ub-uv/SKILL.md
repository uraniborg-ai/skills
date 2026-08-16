---
name: ub-uv
description: Use uv for Python project setup, dependency management, script execution, validation, and one-off Python commands in scientific, engineering, data analysis, and research software projects. Trigger whenever Codex needs to run Python code, sync dependencies, inspect pyproject.toml or uv.lock, or choose between python, pip, venv, and uv.
metadata:
  version: 0.2.0
  stability: stable
  domain: python
---

# UB uv

Use `uv` as the default Python entrypoint for scientific, engineering, data
analysis, and research software projects when the project does not explicitly
choose another environment manager such as Conda. Respect existing project
conventions before introducing uv.

## Commands

```sh
uv sync
uv run python path/to/script.py
uv run python -m module_name
uv run --with package-name python path/to/script.py
uv add package-name
uv remove package-name
uv run python -m py_compile path/to/file.py
```

## Rules

- Prefer `uv run` over bare `python`, `python3`, or `pip` for project work.
- Keep `pyproject.toml` dependency metadata and `uv.lock` as dependency sources
  of truth.
- Use `.python-version` as the local default Python interpreter when it exists
  or when the project setup establishes an exact version. Use
  `pyproject.toml` `requires-python` as the supported version range and
  dependency-resolution constraint.
- If `.python-version` and `requires-python` conflict, report the conflict and
  ask the user before changing either file.
- Do not invent an exact `.python-version` when the project only declares a
  version range or has no reliable version source.
- Do not hand-edit `uv.lock`.
- Do not create ad hoc virtual environments inside the repository.
- If a reusable dependency is a Python package used by the project, add it with
  `uv add`.
- If a dependency is a native executable, document the system dependency instead
  of trying to install it with uv.
- If uv fails because of sandbox, network, cache, or credential restrictions,
  follow `$ub-codex` instead of repeating the same command.

## Python Version

When a project already has `pyproject.toml`, inspect both its existing
`project.requires-python` value and `.python-version`. Keep the range and exact
local interpreter as separate decisions. If `pyproject.toml` lacks
`requires-python`, infer a conservative range from project tooling, lockfiles,
CI, Docker images, or runtime docs. If there is no clear source for an exact
local version, ask the user before creating `.python-version`.

When a project has no `pyproject.toml`, ask the user before creating one. A
minimal non-package Python tooling file usually looks like:

```toml
[project]
requires-python = ">=3.11"

[tool.uv]
package = false
```

## Script Dependencies

Prefer PEP 723 metadata for standalone helper scripts, validators, generators,
migration tools, document processors, and one-off analysis scripts:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0.2",
# ]
# ///

from __future__ import annotations


def main() -> None:
    ...


if __name__ == "__main__":
    main()
```

Run script-local tools with:

```sh
uv run --script path/to/script.py
```

For temporary dependencies that should not become project or script metadata,
use:

```sh
uv run --with pyyaml python path/to/script.py
```

Use project-wide dependencies only when several scripts share the same internal
package, the project is an importable Python package, or repeated script
metadata would create more maintenance cost than a shared dependency.

## Validation

After adding or changing a Python helper, run a bounded check such as:

```sh
uv run path/to/script.py --help
uv run python -m py_compile path/to/script.py
```
