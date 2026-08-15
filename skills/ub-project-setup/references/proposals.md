# Proposals

Use this reference for proposals, RFCs, ADRs, decision records, implementation
plans, status hygiene, scope boundaries, non-goals, and acceptance criteria.

## Contents

- Workflow
- Standard Contract
- Proposal Shape
- Implemented Records
- Review

## Workflow

1. Find local conventions in `docs/proposals/README.md`, nearby proposals, and
   linked architecture, roadmap, philosophy, or data-structure documents.
2. Classify the job as draft, review, rewrite, summarize, inventory, status
   hygiene, or annotation.
3. Preserve local legacy conventions. Do not rename, normalize, archive, or
   migrate existing proposals unless the user explicitly asks.
4. For a new standard proposal, choose the next zero-padded `NNN` identifier in
   the local proposal directory.
5. Put the durable decision near the top. Separate it from background,
   implementation notes, examples, roadmap, terminology candidates, and task
   tracking.
6. Name ownership, product, data, API, runtime, storage, migration, security,
   and compatibility boundaries when they affect the decision.
7. Keep non-goals explicit and acceptance scenarios observable.

## Standard Contract

When the repository has no local convention, use `NNN-short-title.md` and this
frontmatter:

```yaml
---
title: Short Proposal Title
description: One-sentence decision or scope summary.
author:
  - Author Name
status: draft
created_at: 2026-06-25T00:00:00Z
updated_at: 2026-06-25T00:00:00Z
---
```

Use only `title`, `description`, `author`, `status`, `created_at`, and
`updated_at` for new standard proposals. Keep `author` as a non-empty YAML list
of PEP-style strings such as `Name` or `Name <email@example.com>`. Use ISO 8601
timestamps.

Use these statuses:

- `draft`: being shaped
- `proposed`: ready for review
- `accepted`: approved for implementation
- `implemented`: completed in the product
- `superseded`: replaced by another proposal; do not apply this status by
  editing an implemented record
- `rejected`: closed without implementation

Treat legacy `shipped` as `implemented` unless local history shows otherwise.
Treat legacy `active` as ambiguous and resolve it from the proposal body and
repository history.

## Proposal Shape

Use local section names first. When no convention exists, use:

- `Decision`: the chosen direction
- `Rationale`: why it wins over alternatives
- `Scope` or a domain boundary section: what the decision owns
- `Non-Goals`: explicit exclusions
- `Acceptance Scenarios`: observable behavior proving the decision
- `Open Questions`: unresolved decisions, not vague tasks

Use an implementation plan only when sequence, migration, release, or
compatibility is part of the decision. Keep implementation detail out of
architecture direction unless it changes a boundary or acceptance behavior.

## Implemented Records

Treat an `implemented` proposal as immutable decision history.

- Do not rewrite its body or frontmatter after implementation.
- Do not repair stale paths, commands, links, typos, or wording in place. They
  remain part of the historical record.
- Do not fold later behavior, cleanup, migration, or changed decisions into the
  implemented record.
- When a decision changes, write a new proposal. Record any supersession link
  in the new proposal without editing the implemented proposal.
- Put current operational corrections in the owning current documentation,
  changelog, issue, or a new proposal.
- Only append a clearly labeled annotation when the user explicitly requests
  one. Do not infer that an annotation is needed.
- Do not recommend `Revision Notes`, `Implementation Notes`, or an `updated_at`
  change for an implemented proposal. A generic request to fix, update, or
  modernize the proposal leaves the proposal unchanged.
- Keep annotations factual and non-normative. Do not use them to change the
  accepted decision, scope, ownership, non-goals, or acceptance behavior.
- Do not update immutable frontmatter solely because an annotation was added.

## Review

Check filename, required frontmatter, title/H1 alignment, canonical status,
timestamps, audience, decision clarity, boundaries, non-goals, acceptance
scenarios, migration and compatibility risks, terminology maturity, and links
to owning documents.

Lead review-only output with findings:

```text
Findings
- [P1] file:line - Source-of-truth, compatibility, security, data loss, or irreversible-decision risk.
- [P2] file:line - Ambiguous decision, missing boundary, missing non-goal, or untestable acceptance criterion.
- [P3] file:line - Status hygiene, terminology, structure, or clarity issue.

Notes
- Optional non-blocking observations.
```

Before finalizing a draft or rewrite, remove repeated rationale, stale
brainstorming scaffold, duplicated examples, and implementation detail that
does not support the decision.

Validate standard frontmatter with:

```sh
uv run --script skills/ub-project-setup/scripts/check_proposal_frontmatter.py docs/proposals
```

Use `--legacy` when legacy metadata and statuses should be warnings rather than
errors.
