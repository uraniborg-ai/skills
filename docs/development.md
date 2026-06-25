# Development

## Direction

- Prefix public skills with `ub-` to avoid collisions with built-in or personal
  skills.
- Keep the public skill set small, practical, and reusable.
- Prefer workflows that help researchers and engineers handle evidence,
  scripts, and project documentation.
- Use scientific and engineering language over software-infra metaphors when
  naming public skills.

## Skill Structure

- Every public skill must include `SKILL.md` with `name` and `description`
  frontmatter.
- Every public skill must include `agents/openai.yaml` for Codex UI metadata.
- Put optional details in `references/` only when the skill needs progressive
  disclosure.
- Keep deterministic scripts close to the skill that uses them.
- Use `templates/` for output templates that a script or workflow renders.

## Writing

- Keep each `SKILL.md` concise. Move details into `references/` only when they
  are useful after the skill triggers.
- Write documentation in concise, clear language.
- Avoid context-heavy explanations unless they directly help an agent do the
  task.
- Prefer deterministic scripts for repetitive or safety-critical workflows.
- Default to read-only behavior. Write, sync, or network operations must be
  explicit in the user request or the invoked workflow.

## OpenAI Metadata

- Use `agents/openai.yaml` for Codex-facing metadata.
- Keep `display_name` short and use the `UB ...` naming style.
- Keep `short_description` action-oriented and human-facing.
- Include the canonical `$ub-*` skill invocation in `default_prompt`.
- Do not add icons, brand colors, policy, or tool dependencies unless the skill
  actually needs them.

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

## Validation

- Run `npm run smoke` after adding, removing, or changing a public skill.
- Add new public skills to `tests/smoke/check_structure.py`.
- Make sure `agents/openai.yaml` stays aligned with the skill `name` and
  purpose.
- Run Ruff format and format check after changing Python scripts.
