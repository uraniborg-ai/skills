---
name: ub-proposals
description: Draft, review, audit, summarize, or maintain development proposals, design proposals, ADR-like decision records, RFCs, implementation plans, scope boundaries, non-goals, acceptance criteria, numbered proposal filenames, PEP-style author metadata, proposal frontmatter, and proposal status conventions across research and engineering repositories.
---

# UB Proposals

Use this skill for decision-first proposal work. Preserve the local repository's
proposal conventions before introducing a new shape.

## Workflow

1. Find local conventions first:
   - `docs/proposals/README.md`
   - nearby numbered, accepted, implemented, or superseded proposals
   - linked philosophy, architecture, roadmap, or data-structure docs
2. Identify the proposal job: draft, review, rewrite, summarize, inventory, or
   status hygiene.
3. For new proposals, choose the next local `NNN` id before drafting.
4. Keep the decision near the top. If the proposal intentionally defers the
   decision, say that explicitly and list the open questions.
5. Separate durable decisions from implementation notes, background, and
   transient task tracking.
6. Preserve project terminology and source-of-truth boundaries.

For observed proposal shapes and section mappings, read
`references/proposal-shapes.md` when creating a new proposal or normalizing an
inconsistent one.

## Default Shape

If the repository has no local convention, use:

```text
NNN-short-title.md
```

`NNN` is a zero-padded, monotonically increasing proposal id within the local
proposal directory, usually `docs/proposals`. Inspect existing `NNN-*.md`
files, then use max id + 1. If the directory only has legacy dated proposals,
start numbered proposals at `001` unless local docs reserve another number.
Do not rename legacy dated proposals automatically.

```yaml
---
title: Short Proposal Title
description: One-sentence decision or scope summary.
author:
  - Author Name
status: draft
---
```

Use `author` as a YAML list of PEP-style author strings:

- `Name`
- `Name <email@example.com>`

List multiple authors as multiple entries. Add `Codex` as an author only when
Codex materially co-authored the proposal, not for trivial formatting, typo
fixes, or review comments.

Sections:

- `Decision`
- `Rationale`
- `Scope`
- `Non-Goals`
- `Acceptance Scenarios`
- `Open Questions`

Use `Scope`/`Out of Scope` instead of implementation detail when the proposal
mainly decides boundaries. Use `Implementation Plan` only when order, rollout,
or migration is part of the decision.

## Review Checklist

Check in this order:

- New or normalized proposals use `NNN-short-title.md`.
- Frontmatter includes `title`, `description`, `author`, and `status`.
- `title` matches the H1 unless local conventions say otherwise.
- `description` is one concise sentence about the decision, boundary, or job.
- `author` is a list of PEP-style author strings.
- `status` is canonical for new or normalized proposals.
- The audience and job are clear.
- The decision is explicit, or the proposal clearly says it is still shaping.
- Product, data, API, runtime, storage, or ownership boundaries are named.
- Non-goals prevent likely scope creep.
- Acceptance scenarios are observable and testable.
- Risks, migration, compatibility, or security consequences are not buried.
- Open questions are real decisions, not vague todos.
- Links point to owning docs or superseding proposals.

## Review Output

For review-only requests, lead with findings:

```text
Findings
- [P1] file:line - Source-of-truth, compatibility, security, data loss, or
  irreversible-decision risk.
- [P2] file:line - Ambiguous decision, missing boundary, missing non-goal, or
  untestable acceptance criterion.
- [P3] file:line - Status hygiene, terminology, structure, or clarity issue.

Notes
- Optional non-blocking observations.
```

For drafting or rewrites:

- Follow local section conventions while using the shared metadata default for
  new proposals.
- Prefer deletion or tighter wording before adding new sections.
- Keep implementation detail only where it supports a decision, tradeoff,
  rollout, migration, or acceptance test.
- Leave open questions as explicit bullets when the user has not decided.

## Status Hygiene

Use these statuses for new or normalized proposals:

- `draft`: being shaped.
- `proposed`: ready for review.
- `accepted`: approved for implementation.
- `implemented`: completed in the product.
- `superseded`: replaced by another proposal.
- `rejected`: closed without implementation.

Legacy dated filenames are compatible and are not automatically wrong. Preserve
archived proposal metadata unless the user explicitly asks for migration.

When reading legacy statuses:

- Treat `shipped` as `implemented`.
- Treat `active` as ambiguous; resolve it case by case into `draft`,
  `proposed`, `accepted`, or `implemented`.

Do not rename a proposal only because its status changes unless local
conventions require it.
