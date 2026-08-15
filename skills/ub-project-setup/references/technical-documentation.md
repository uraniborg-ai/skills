# Technical Documentation

Use this reference to create, route, rewrite, or review project technical docs
while preserving a small, clear set of sources of truth.

## Routing

- Project overview, quick start, representative commands, and current status:
  use an existing `README.md` or nearby introduction document.
- Agent-critical execution, validation, safety, and source-of-truth pointers:
  use `AGENTS.md` only when the project needs an agent entry point.
- Long agent-specific or model-specific operating detail: place it in a
  suitable `docs/` document when it is not needed before every task.
- Development environment, local loop, checks, and done criteria: use an
  existing development guide; suggest `docs/development.md` only when a new
  source of truth is useful.
- System boundaries, ownership, data, runtime, and API contracts: use an
  existing architecture document; suggest `docs/architecture.md` only when the
  decision needs a stable home.
- Current focus, proposal links, release snapshots, and maintainer planning:
  use an existing roadmap, README section, issue, or milestone.
- Shipped history: use `CHANGELOG.md`. Suggest a release runbook only when
  publishing or deployment checks need a durable procedure.

Do not require a fixed document set. Before adding a file, check whether the
information belongs in an existing source of truth.

## Workflow

1. Classify the audience as `user-facing`, `contributor-facing`,
   `maintainer-facing`, `generated`, or `proposal`.
2. Read the target sections and nearby project guidance needed to preserve
   terminology, ownership, and links.
3. Check independent `AGENTS.md` and `CLAUDE.md` files for source-of-truth drift
   when both exist.
4. Put the useful sentence first and remove repeated context before adding
   explanation.
5. Keep implementation detail only when it changes a reader's decision,
   boundary, usage, migration, or acceptance test.
6. Validate commands, paths, and generated outputs affected by the edit.

## Writing Standard

- Keep one judgment per sentence.
- Prefer concrete nouns, named actors, and active voice.
- Use `must` for requirements, `can` for capability, and `should` for
  intentional guidance.
- Keep lists parallel.
- Prefer examples that reveal behavior over prose that explains it twice.
- Remove vague claims such as simple, powerful, seamless, flexible, and robust.
- Challenge ambiguous actor, scope, obligation, order, ownership, storage, or
  API boundaries.
- Avoid internal implementation detail in user-facing docs.

## Generated Documents

Review generated docs, but route fixes to source comments, docstrings,
generator code, templates, config, wrapper text, or regeneration commands. Do
not directly edit generated output unless the project explicitly owns it as a
manual source.

Preserve tool contracts and routes from Sphinx, MkDocs, Docusaurus,
Cargo/rustdoc, TypeDoc, Go/pkgsite, or project-specific documentation builds.

## Boundaries

- Use `references/proposals.md` for proposal lifecycle and decision records.
- Use `$ub-git` for commit messages and repository operations.
- Do not apply these rules to literary writing, essays, blogs, marketing copy,
  personal notes, presentation prose, resumes, or prompt experiments unless the
  user explicitly requests a technical-doc pass.

For review-only requests, lead with prioritized findings and provide shorter
wording only when deletion would lose required meaning.
