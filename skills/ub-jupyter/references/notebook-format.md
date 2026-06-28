# Notebook Format

Use this reference when reading, editing, validating, or explaining `.ipynb`
structure.

## Principles

- Treat `.ipynb` as a Jupyter notebook document, not plain JSON text.
- Use `nbformat.read(path, as_version=4)` and `nbformat.write` when possible.
- Validate after structural edits with `nbformat.validate`.
- Avoid ad hoc string replacement in notebook JSON.

## Structure To Preserve

- Top-level `nbformat`, `nbformat_minor`, and `metadata`.
- Notebook `metadata.kernelspec` and `metadata.language_info`.
- Cell order, `cell_type`, `source`, `metadata`, and `id`.
- Code cell `outputs` and `execution_count` unless the task explicitly changes
  execution state.
- Markdown cell `attachments`.
- Widget state and rich display output, especially large HTML, image, Vega, or
  JavaScript bundles.

## Source Handling

Jupyter source fields may appear as strings or lists of strings on disk. Let
`nbformat` normalize this for edits, then write the notebook through the same
API.

## Editing Rules

- Make the smallest cell-level change that satisfies the request.
- Use `nbformat.v4.new_code_cell`, `new_markdown_cell`, or equivalent helpers
  for inserted cells.
- Preserve unknown metadata unless it is clearly generated clutter and the user
  asked to clean it.
- Do not renumber execution counts by hand.
- Do not remove outputs to make diffs smaller unless output stripping is the
  requested task or a documented project policy.

## Validation

For one-off validation without adding project dependencies, prefer temporary
tool execution such as:

```sh
uv run --with nbformat python -c "import nbformat, sys; nb = nbformat.read(sys.argv[1], as_version=4); nbformat.validate(nb)" notebook.ipynb
```

If a one-liner would be hard to read or adapt, use a short Python validation
snippet with `nbformat.read(..., as_version=4)` and `nbformat.validate`.
