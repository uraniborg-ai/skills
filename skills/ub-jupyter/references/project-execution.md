# Project Execution

Use this reference before executing notebooks or diagnosing execution failures.
Notebook execution must be project-aware.

## Environment Diagnosis

Read setup sources before choosing commands:

- `README*`, `CONTRIBUTING*`, and relevant `docs/`
- `pyproject.toml`, `uv.lock`, `requirements*.txt`, `environment*.yml`
- Docker files and CI workflow files
- Notebook `metadata.kernelspec` and `metadata.language_info`
- Nearby data files and paths referenced from code cells

Identify:

- project root
- notebook path
- execution cwd
- Python version and package source of truth
- kernel name and whether it maps to the project environment
- data path assumptions
- network or credential requirements
- timeout and side-effect risk

## uv Policy

- If the project has `pyproject.toml`, `uv.lock`, or documented uv commands,
  use `uv run` as the Python entrypoint.
- Follow `ub-uv` for Python version, project dependency, temporary dependency,
  and script-local dependency decisions.
- Do not run `uv add`, sync dependencies, update lockfiles, or create durable
  environments unless the user explicitly asks.
- For one-off helper packages, consider `uv run --with ...` before changing
  project dependencies.

## Execution Policy

- Execute only after the user asks or the invoked workflow clearly requires it.
- Prefer a separate output notebook such as `analysis-executed.ipynb` unless
  project docs or the user asks for in-place execution.
- Record cwd, runner, kernel, timeout, output path, and whether execution was
  complete or partial.
- If a notebook fails, report the failing cell, exception summary, relevant
  traceback, output state, and likely next environment fix.

## Runner Selection

- Use the project's documented notebook command when one exists.
- Use `nbclient` when you need programmatic execution control, explicit timeout,
  resources, or output path handling.
- Use `jupyter execute` when the project already exposes it and the command
  matches the needed behavior.
- Use Papermill when parameterization or run metadata is central to the task.

When no runner is installed but temporary dependencies are acceptable, use
`uv run --with nbclient --with nbformat ...` or an equivalent temporary tool
command rather than adding dependencies to the project.
