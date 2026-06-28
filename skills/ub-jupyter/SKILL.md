---
name: ub-jupyter
description: Work with local Jupyter notebooks in scientific and engineering projects. Use when Codex needs to inspect, summarize, edit, validate, review, or explicitly execute .ipynb notebooks; diagnose kernel, dependency, cwd, output, metadata, or data-path issues; coordinate notebook execution with project setup using ub-dev-env and uv using ub-uv; or handle Jupytext, nbdime, and nbstripout review hygiene.
---

# UB Jupyter

Use this skill for local filesystem Jupyter notebooks. The first version does
not control live JupyterLab, remote Jupyter Server, MCP servers, or kernel
gateways.

## Workflow

1. Start read-only. Inspect notebooks, project setup files, and existing
   notebook policy before writing files or executing cells.
2. Classify the task as notebook inspection, project environment diagnosis,
   notebook edit, explicit notebook execution, or Git review hygiene.
3. For `.ipynb` structure, metadata, outputs, or validation, read
   `references/notebook-format.md`.
4. For execution, read `references/project-execution.md` and use the
   `ub-dev-env` and `ub-uv` rules when those skills are available.
5. For Jupytext, nbdime, output stripping, or reviewable diffs, read
   `references/review.md`.
6. Report the execution environment, cwd, runner, output policy, and changed
   files when they matter.

## Inspection

- Load notebooks with `nbformat.read(..., as_version=4)` or an equivalent
  notebook-aware parser.
- Summarize kernel metadata, language info, cell count, markdown headings, code
  imports, output presence, widgets, attachments, and large embedded data.
- Do not execute stale or suspicious notebooks just to inspect them.
- If reproducibility is uncertain, identify the missing kernel, dependency,
  cwd, data file, or project setup source.

## Editing

- Edit notebooks at cell granularity and validate with `nbformat.validate`.
- Preserve cell `id`, metadata, attachments, outputs, and execution counts
  unless the user explicitly requests changes to them.
- Use `nbformat.v4.new_code_cell` and `new_markdown_cell` or equivalent helpers
  when adding cells.
- Do not strip outputs as a side effect of unrelated edits.

## Execution

- Execute only when the user explicitly asks, or when an invoked workflow clearly
  requires execution.
- Before executing, inspect project setup sources such as `README*`,
  `CONTRIBUTING*`, `docs/`, `pyproject.toml`, `uv.lock`, `requirements*.txt`,
  `environment*.yml`, Docker files, CI config, and kernelspec metadata.
- Prefer `uv run` from the notebook's project context when the project uses
  `pyproject.toml`, `uv.lock`, or existing uv commands.
- Choose cwd from the project docs, notebook-relative data paths, and package
  layout. Report the cwd and why it was chosen.
- Prefer a separate executed artifact such as `*-executed.ipynb` unless the user
  or project workflow asks for in-place execution.

## Safety

- Treat notebook execution as arbitrary code execution.
- Treat network access, dependency installation, lockfile updates, kernel
  startup, output deletion, and remote service access as explicit actions.
- If `uv` fails because of sandbox, cache, network, or credential restrictions,
  follow the `ub-codex` escalation guidance instead of retrying blindly.
