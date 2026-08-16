# Technical Documentation

Use this reference to create, route, rewrite, or review project technical docs
while preserving a small, clear set of sources of truth. The primary output is
current, usable project guidance; proposals and TODO records are optional
supporting documents.

## Routing

- Project overview, quick start, representative commands, and current status:
  use an existing `README.md` or nearby introduction document.
- Agent-critical execution, validation, safety, and source-of-truth pointers:
  use `AGENTS.md` only when the project needs an agent entry point.
- Long agent-specific or model-specific operating detail: place it in a
  suitable `docs/` document when it is not needed before every task.
- Development environment, local loop, checks, and done criteria: use an
  existing development guide; use or suggest `docs/development.md` when a new
  source of truth is useful. If no current development guide exists, record
  the analyzed environment and recommendations there.
- Technical documentation conventions, document ownership, and review rules:
  use an existing documentation guide; use or suggest
  `docs/technical-documentation.md` when no equivalent exists.
- System boundaries, ownership, data, runtime, and API contracts: use an
  existing architecture document; suggest `docs/architecture.md` only when the
  decision needs a stable home.
- Current focus, proposal links, release snapshots, and maintainer planning:
  use an existing roadmap, README section, issue, or milestone.
- Shipped history: use `CHANGELOG.md`. Suggest a release runbook only when
  publishing or deployment checks need a durable procedure.
- Unresolved proposals, TODOs, backlogs, and follow-up work that should remain
  in the repository: use `docs/proposals/NNN-<title>.md` when no issue tracker
  is the existing source of truth.

Do not require a fixed document set when equivalent local sources already
exist. When `docs/` has no current development guidance, or contains only
`docs/proposals/`, create or propose `docs/development.md` and
`docs/technical-documentation.md` as the default pair. Link the owning
documents from `AGENTS.md` and the `CLAUDE.md` pointer.

When a new project needs agent entry points, create `AGENTS.md` as the shared
canonical file and `CLAUDE.md` as a pointer by default. If only `CLAUDE.md`
exists, preserve possible Claude-specific intent and ask before moving or
rewriting ambiguous content. If both files contain conflicting commands,
runtimes, dependencies, ownership, source-of-truth rules, or safety guidance,
ask the user before editing either file.

## Workflow

1. Classify the audience as `user-facing`, `contributor-facing`,
   `maintainer-facing`, `generated`, or `proposal`.
2. Classify the document state as current guidance, unresolved work, historical
   record, or generated output.
3. Read the target sections and nearby project guidance needed to preserve
   terminology, ownership, and links.
4. Check independent `AGENTS.md` and `CLAUDE.md` files for source-of-truth drift
   when both exist. Ask the user before editing if their commands, runtimes,
   dependencies, ownership, or safety rules conflict.
5. Put the useful sentence first and remove repeated context before adding
   explanation.
6. Keep implementation detail only when it changes a reader's decision,
   boundary, usage, migration, or acceptance test.
7. Validate commands, paths, versions, links, and generated outputs affected by
   the edit.

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
- Distinguish observed facts, project requirements, and recommendations.
- Make prerequisites, side effects, expected results, and verification commands
  explicit for setup or operational instructions.
- Prefer a short, executable workflow over a catalog of possible tools.

## Scientific And Engineering Projects

When the project analyzes data or produces scientific or engineering results,
document only the reproducibility details that affect a reader's ability to
repeat or interpret the work:

- data sources, expected paths, and whether data is tracked or external
- units, coordinate systems, schemas, conventions, and important assumptions
- Python and dependency sources of truth, including `.python-version`, uv, and
  lockfiles when present
- random seeds, notebook execution order, environment variables, and output
  locations when they affect results
- validation checks and known limitations

Do not require a full research protocol for a small analysis task. Add a detail
only when omitting it could change execution, interpretation, or reproducibility.

## Project Documentation Guide

When creating `docs/technical-documentation.md`, include the project's local
rules for:

- the roles of `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/`, proposals, and
  changelog
- current guidance versus unresolved work and historical records
- document naming, links, ownership, and update responsibility
- command, path, version, and generated-output verification
- sensitive data and credential redaction
- review checklist and stale-document handling

Use this structure as a recommendation, not a mandatory template:

```text
Purpose
Scope
Prerequisites
Workflow or Usage
Verification
Troubleshooting
Limitations
Related documents
```

## Generated Documents

Review generated docs, but route fixes to source comments, docstrings,
generator code, templates, config, wrapper text, or regeneration commands. Do
not directly edit generated output unless the project explicitly owns it as a
manual source.

Preserve tool contracts and routes from Sphinx, MkDocs, Docusaurus,
Cargo/rustdoc, TypeDoc, Go/pkgsite, or project-specific documentation builds.

## Boundaries

- Use `references/proposals.md` for proposal lifecycle and decision records.
- Treat proposal writing as optional. Route TODOs, backlogs, and follow-up work
  to `docs/proposals/NNN-<title>.md` only when a repository record is useful and
  no existing issue tracker owns the task.
- Use `$ub-git` for commit messages and repository operations.
- Do not apply these rules to literary writing, essays, blogs, marketing copy,
  personal notes, presentation prose, resumes, or prompt experiments unless the
  user explicitly requests a technical-doc pass.

For review-only requests, lead with prioritized findings and provide shorter
wording only when deletion would lose required meaning.
