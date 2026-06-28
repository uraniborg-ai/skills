# Review Hygiene

Use this reference for Git review, paired notebooks, and output policy.

## Diff Strategy

- Prefer project-native review tooling.
- If the project uses Jupytext pairing, inspect the paired source file and the
  `.ipynb` metadata before editing.
- If available, use `nbdime` for notebook-aware diff and merge inspection.
- Avoid presenting raw JSON diffs as the primary explanation when a cell-level
  summary is clearer.

## Jupytext

- Check notebook metadata for Jupytext pairing before editing.
- Keep paired source and `.ipynb` synchronized according to project policy.
- Do not introduce Jupytext into a project merely to make one task easier.
- Treat `jupytext --sync` as a write action.

## Outputs

- Do not strip outputs during unrelated edits.
- Strip outputs only when the user asks or a project policy such as pre-commit,
  `nbstripout`, or documentation requires it.
- If outputs are stripped, report that execution counts and rich outputs changed
  by design.

## Commands

Use these only when the tools are already available or temporary dependency use
is acceptable:

```sh
uv run --with nbdime nbdiff notebook.ipynb
uv run --with jupytext jupytext --sync notebook.ipynb
uv run --with nbstripout nbstripout notebook.ipynb
```

Each command can write, inspect large outputs, or require temporary package
downloads. Apply the repository's mutation and network rules before running it.
