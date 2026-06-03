---
name: ub-uv
description: Use uv for Python project setup, dependency management, script execution, validation, and one-off Python commands in scientific, engineering, data analysis, and research software projects. Trigger whenever Codex needs to run Python code, sync dependencies, inspect pyproject.toml or uv.lock, or choose between python, pip, venv, and uv.
metadata:
  version: 0.1.0
  stability: stable
  domain: python
---

# UB uv

Use `uv` as the default Python entrypoint when a project has `pyproject.toml`,
`uv.lock`, or existing uv usage.

## Commands

```sh
uv sync
uv run python path/to/script.py
uv run python -m module_name
uv add package-name
uv remove package-name
uv run python -m py_compile path/to/file.py
```

## Rules

- Prefer `uv run` over bare `python`, `python3`, or `pip` for project work.
- Keep `pyproject.toml` and `uv.lock` as the dependency source of truth.
- Do not hand-edit `uv.lock`.
- Do not create ad hoc virtual environments inside the repository.
- If a dependency is a Python package, add it with `uv add`.
- If a dependency is a native executable, document the system dependency instead
  of trying to install it with uv.

