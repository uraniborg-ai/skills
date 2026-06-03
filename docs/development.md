# Development

- Prefix public skills with `ub-` to avoid collisions with built-in or personal
  skills.
- Keep each `SKILL.md` concise. Move details into `references/` only when they
  are useful after the skill triggers.
- Prefer deterministic scripts for repetitive or safety-critical workflows.
- Default to read-only behavior. Write, sync, or network operations must be
  explicit in the user request or the invoked workflow.
- Use scientific and engineering language over software-infra metaphors when
  naming public skills.

## Python Scripts

- Use PEP 723 inline metadata for script runtime dependencies.
- Run scripts with `uv run --script path/to/script.py`.
- Keep skill runtime dependencies in the script header, not in a shared project
  dependency list.
- Use repo-level `pyproject.toml` only for development and test tools.
- Use script lockfiles only when reproducibility requires them.
- Format every Python script with Ruff before committing.

Standard header:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

Add dependencies in the header:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2>=3.1",
#   "yt-dlp>=2025.1.1",
# ]
# ///
```

Format scripts:

```sh
UV_CACHE_DIR=.uv-cache uv run ruff format .
UV_CACHE_DIR=.uv-cache uv run ruff format --check .
```
