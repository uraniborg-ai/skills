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
created_at: 2026-06-25T00:00:00Z
updated_at: 2026-06-25T00:00:00Z
---
```

`NNN` is local to the proposal directory. `author` is singular by field name but
stores a YAML list of PEP-style strings such as `Name` or
`Name <email@example.com>`.

Use canonical statuses for new or normalized proposals: `draft`, `proposed`,
`accepted`, `implemented`, `superseded`, and `rejected`. Legacy `shipped` maps
to `implemented` unless the body says a later proposal replaces it; in that case
flag it as a `superseded` candidate. Legacy `active` must be interpreted case by
case. Do not rewrite archived metadata unless the user asks for migration.

Use only these standard frontmatter fields for new proposals:

- `title`
- `description`
- `author`
- `status`
- `created_at`
- `updated_at`

`created_at` and `updated_at` are required ISO 8601 timestamps. Set both to the
same timestamp when creating a proposal. Update only `updated_at` after
substantive edits.

Legacy or project-specific metadata such as `date`, `created`, `updated`,
`related`, `tags`, `features`, `audience`, `summary`, `implemented_by`,
`implemented_commits`, `decision_note`, `depends_on`, `supersedes`,
`superseded_by`, and `follow_up` may be read for compatibility, but do not add
them to new standard proposals. Put lifecycle relationships, implementation
evidence, follow-up work, and related links in body sections such as
`References`, `Implementation Notes`, `Follow-On Work`, and
`Supersedes`/`Superseded By`.

When a repository has legacy proposals and no shared standard yet, ask the user
whether to archive the legacy set before starting the standard or migrate the
legacy set first. Do not choose automatically.

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

Keep the shared frontmatter field names and canonical status values in English
even when section headings and body text are Korean.

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

## Legacy Section Mapping

When reviewing or normalizing legacy proposals, map section intent before
criticizing section names:

- `Goal`, `Summary`, `목표`, and `목적` can describe the proposal job.
- `Decision`, `결정`, `핵심 판단`, and `구현 결정` can carry the durable choice.
- `Out Of Scope`, `Out of Scope`, `Non-Goals`, `비목표`, and `범위 제외` can carry
  exclusions.
- `Acceptance Criteria`, `Acceptance Scenarios`, `검증 기준`, `완료 기준`, and
  `성공 기준` can carry observable acceptance.
- `Next`, `Follow-On Work`, `후속`, and `후속 고려사항` can carry later work.

Keep supporting sections such as `Privacy`, `Storage Boundary`, `Migration`,
`Risks`, and `References` when they expose decision risk, compatibility,
security, data loss, or source-of-truth consequences.

## Common Smells

- Status appears in prose but not frontmatter.
- Frontmatter is missing `title`, `description`, `author`, `status`,
  `created_at`, or `updated_at`.
- New standard frontmatter adds custom metadata keys instead of body sections.
- A new proposal uses a dated filename instead of a numbered id.
- The document starts with background and hides the decision.
- `Open Questions` contains work items instead of decisions.
- Non-goals are missing from proposals that could grow in scope.
- Acceptance criteria describe implementation steps rather than observable
  behavior.
- Storage, API, identity, ownership, or security boundaries are implied but not
  stated.
