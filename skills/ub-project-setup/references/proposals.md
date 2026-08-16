# Proposals And Follow-up Records

Use this reference for optional proposals, RFCs, ADRs, decision records, TODOs,
backlogs, follow-up work, and implementation plans. Development-environment
and current technical-documentation work remains the primary responsibility of
`ub-project-setup`.

## Workflow

1. Find local conventions in `docs/proposals/README.md`, nearby proposals, and
   linked architecture, roadmap, philosophy, or data-structure documents.
2. Classify the request as a draft, review, rewrite, summary, inventory, status
   update, TODO record, or annotation.
3. If the project has an issue tracker or task system that owns the work, use it
   as the source of truth instead of creating a duplicate proposal.
4. If a repository record is useful and no existing source owns the work,
   choose the next zero-padded `NNN` identifier and create
   `docs/proposals/NNN-<title>.md`.
5. Keep the durable decision or task near the top. Separate it from background,
   examples, implementation notes, and unresolved questions.
6. Name ownership, product, data, API, runtime, storage, migration, security,
   and compatibility boundaries when they affect the work.
7. Keep non-goals and observable validation or completion criteria explicit when
   they are relevant.

Proposal writing is optional. Do not create a proposal merely because a user
mentions a small immediate task.

## Standard Contract

When the repository has no local convention, use `NNN-short-title.md` and this
minimal frontmatter:

```yaml
---
title: Short Proposal or Task Title
description: One-sentence decision, task, or scope summary.
status: draft
---
```

Use only `title`, `description`, and `status` by default. Add `authors`,
`created_at`, `updated_at`, `supersedes`, or other fields only when the user
wants them or the local convention requires them.

Use these statuses:

- `draft`: being shaped
- `proposed`: ready for review
- `accepted`: approved for implementation
- `implemented`: completed in the project
- `superseded`: replaced by another record
- `rejected`: closed without implementation

Treat legacy `shipped` as `implemented` unless local history shows otherwise.
Treat legacy `active` as ambiguous and resolve it from the record body and
repository history.

## PEP-Inspired Shape

Use Python PEPs as a source of useful section ideas, not as a format to copy.
PEP 1's proposal guidance and PEP 12's template are references for sections
such as Abstract, Motivation, Specification, Rationale, compatibility,
security, alternatives, and open issues:

- https://peps.python.org/pep-0001/
- https://peps.python.org/pep-0012/

Keep the project format as Markdown with minimal frontmatter. Do not require
PEP numbering, RFC-style headers, reStructuredText, or every possible PEP
section.

For a normal decision or design proposal, choose only the sections that help:

```text
## Abstract
## Motivation
## Proposal
## Validation
## Open Questions
```

Add these only when relevant:

- `Scope`
- `Non-Goals`
- `Rationale`
- `Backwards Compatibility` or `Migration`
- `Security and Data Considerations`
- `Alternatives Considered`
- `Reference Implementation`

For a small data-analysis or engineering task, prefer a shorter record over a
full PEP-style document. A TODO can use:

```text
## Task
## Context
## Done When
## Open Questions
```

Map `Task` or `Abstract` to what should happen, `Context` or `Motivation` to
why it matters, and `Done When` or `Validation` to observable completion.

## Implemented Records

Treat an `implemented` proposal as immutable decision history.

- Do not rewrite its body or frontmatter after implementation.
- Do not repair stale paths, commands, links, typos, or wording in place.
- Do not fold later behavior, cleanup, migration, or changed decisions into
  the implemented record.
- When a decision changes, write a new proposal and link the superseded record
  from the new one without editing the old record.
- Put current operational corrections in the owning current documentation,
  changelog, issue, or a new proposal.
- Append an annotation only when the user explicitly requests one.
- Do not recommend `Revision Notes`, `Implementation Notes`, or an
  `updated_at` change for an implemented proposal unless explicitly requested.
- Keep annotations factual and non-normative.

Existing implemented records with older frontmatter or structure remain
legacy historical records and must not be normalized automatically.

## Review

Review records manually against the local convention and the following checks:

- filename and numbering
- minimal or locally required frontmatter
- title and document purpose
- current decision or task clarity
- ownership and source-of-truth boundaries
- non-goals when scope could expand
- observable validation or completion criteria
- migration, compatibility, security, and data risks when relevant
- terminology and links to owning documents
- unnecessary background, duplicated rationale, and stale implementation detail

Lead review-only output with prioritized findings:

```text
Findings
- [P1] file:line - Source-of-truth, compatibility, security, data loss, or irreversible-decision risk.
- [P2] file:line - Ambiguous decision, missing boundary, or untestable acceptance criterion.
- [P3] file:line - Status, terminology, structure, or clarity issue.

Notes
- Optional non-blocking observations.
```

Do not use a proposal-specific Python validator. Use the project's existing
Markdown, link, formatting, and diff checks when available.
