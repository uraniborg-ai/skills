# AGENTS

This repository publishes reusable Uraniborg AI skills for scientific and
engineering workflows.

## Direction

- Keep the public skill set small, practical, and reusable.
- Prefer workflows that help researchers and engineers handle evidence, scripts,
  and many project repositories.
- Prefix public skill names with `ub-`.

## Writing

- Write documentation in concise, clear language.
- Avoid context-heavy explanations unless they directly help an agent do the
  task.
- Put details in `references/` only when a skill needs progressive disclosure.

## Development

- Read `docs/development.md` before adding or changing Python scripts, bundled
  tools, or skill development conventions.
- Keep deterministic scripts close to the skill that uses them.
- Default to read-only behavior unless a workflow explicitly requires mutation.

