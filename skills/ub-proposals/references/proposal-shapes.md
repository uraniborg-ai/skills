# Proposal Shapes

Use this reference when creating a new proposal, normalizing an inconsistent
proposal, or translating between project conventions.

## Metadata

For new or normalized proposals, use the shared filename and frontmatter
contract even when section names follow local conventions:

```text
NNN-short-title.md
```

```yaml
---
title: Short Proposal Title
description: One-sentence decision or scope summary.
author:
  - Author Name
status: draft
---
```

`NNN` is local to the proposal directory. `author` is singular by field name but
stores a YAML list of PEP-style strings such as `Name` or
`Name <email@example.com>`.

Use canonical statuses for new or normalized proposals: `draft`, `proposed`,
`accepted`, `implemented`, `superseded`, and `rejected`. Legacy `shipped` maps
to `implemented`; legacy `active` must be interpreted case by case. Do not
rewrite archived metadata unless the user asks for migration.

## Decision Proposal

Best for product, architecture, API, runtime, storage, release, or workflow
decisions.

Recommended sections:

- `Decision`: the chosen direction in a few direct paragraphs.
- `Rationale`: why this direction wins over alternatives.
- `Boundary` or `Product Boundary`: who owns what, and what must not cross.
- `Non-Goals`: explicit exclusions.
- `Acceptance Scenarios`: observable examples that prove the decision works.
- `Open Questions`: unresolved decisions that block acceptance or implementation.

Use this shape for large engineering proposals where future agents need a
source of truth.

## Korean Decision Proposal

Equivalent shape for Korean repositories:

- `목적`
- `핵심 판단`
- `경계` or domain-specific boundary section
- `비목표`
- `성공 기준`
- `열린 결정`

Keep stable domain terms consistent with the local docs. Do not translate
project-owned terms unless the repository already does.

## ADR-Style Proposal

Best for small changes or reference projects.

Recommended sections:

- `Decision`
- `Rationale`
- `Scope`
- `Out of Scope`
- `Environment Decision` when tooling or runtime choice matters

Keep ADR-style proposals short. Avoid full rollout plans unless rollout is the
decision.

## Implementation Proposal

Use when order, migration, release, or compatibility is part of the decision.

Useful sections:

- `Decision`
- `Current State`
- `Implementation Plan` or `Implementation Slices`
- `Migration`
- `Risks`
- `Acceptance Scenarios`

Do not let task lists replace the decision. The implementation plan should
follow from the decision, not define it indirectly.

## Common Smells

- Status appears in prose but not frontmatter.
- Frontmatter is missing `title`, `description`, `author`, or `status`.
- A new proposal uses a dated filename instead of a numbered id.
- The document starts with background and hides the decision.
- `Open Questions` contains work items instead of decisions.
- Non-goals are missing from proposals that could grow in scope.
- Acceptance criteria describe implementation steps rather than observable
  behavior.
- Storage, API, identity, ownership, or security boundaries are implied but not
  stated.
