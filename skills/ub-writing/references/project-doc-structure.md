# Project Document Routing

Use this reference when a technical decision, workflow, or operating note needs
to be written down. Do not require a fixed document set. Prefer the smallest
existing source of truth that can hold the new information clearly.

## Routing

- Project overview, quick start, representative commands, and current status:
  use an existing `README.md` or nearby introduction document.
- Agent-critical execution, validation, safety, and source-of-truth pointers:
  use `AGENTS.md` only when the project needs an agent entry point.
- Long agent-specific notes, legacy Claude instructions, or model-specific
  operating detail: move them out of `AGENTS.md` into a suitable `docs/`
  document when they are not needed before every task.
- Development environment, local loop, checks, and done criteria: use an
  existing development guide; suggest `docs/development.md` only when a new
  source of truth is useful.
- System boundaries, ownership, data/runtime/API contracts, and durable
  source-of-truth decisions: use an existing architecture document; suggest
  `docs/architecture.md` only when the decision needs a stable home.
- Product or engineering principles: use an existing philosophy/principles
  document; suggest a new one only when the principle is repeatedly used to make
  project decisions.
- Current focus, proposal links, release snapshots, and maintainer planning:
  use an existing roadmap document. If none exists, first consider a short
  README section, issue, or milestone.
- Release procedure: use `CHANGELOG.md` for shipped history. Suggest a release
  runbook only when version bumps, artifacts, publishing, or deployment checks
  are too complex for a short section.

## Proposal Handoff

`ub-writing` does not own proposal lifecycle rules. For `docs/proposals/`,
RFCs, ADRs, decision records, proposal status, frontmatter, non-goals,
acceptance scenarios, or proposal lifecycle work:

- Check whether `$ub-proposals` is available.
- Use `$ub-proposals` with `$ub-writing` when available.
- If `$ub-proposals` is not available, suggest installing it before drafting or
  rewriting the proposal.
- Continue without `$ub-proposals` only when the user declines or the
  environment cannot install skills. In that case, follow local conventions and
  state any fallback assumptions.

## Generated Documents

Generated reference docs are in scope for review, but not for direct editing.
When generated text is wrong or unclear, route the fix to one of these places:

- source comments or docstrings
- generator code
- templates or config
- wrapper README text
- regenerate command or validation script

Preserve tool contracts and site routes from Sphinx, MkDocs, Docusaurus,
Cargo/rustdoc, TypeDoc, Go/pkgsite, or project-specific site builds. Do not
rename paths such as `docs/reference/`, `docs/api/`, or `target/doc/` only to
match a local naming preference.

## Commit Messages

Git commit messages are in scope for drafting and review as
`maintainer-facing` writing. Before writing one, check local rules in
`AGENTS.md`, `CONTRIBUTING.md`,
`docs/commit-conventions.md`, release docs, or maintainer docs. When local rules
exist, follow them.

When the project has no local commit convention, use Conventional Commits
v1.0.0:

- Write messages in English by default.
- Use `type(scope): description` when a useful scope is clear.
- Use an imperative, lowercase description with no trailing period.
- Use `!` after the type or scope, or a `BREAKING CHANGE:` footer, for breaking
  changes.
- Prefer the staged diff from `git diff --cached`. If there is no staged diff,
  state that the message is a draft based on unstaged changes.
- If the diff mixes unrelated changes, suggest splitting the commit before
  writing a single message.
- Do not run `git commit` unless the user explicitly asks.

## Naming Guidance

Use local conventions first. When creating a new manual documentation area and
the project has no convention, plural directory names are usually clearer for
collections:

- `proposals/`
- `releases/`
- `agents/`
- `data-structures/`
- `platforms/`
- `references/`
- `archives/`

Single-purpose guides can remain files such as `architecture.md`,
`development.md`, `roadmap.md`, or `philosophy.md`. Treat these names as
routing options, not required files.

## Writing Style

- Classify the document job as `user-facing`, `contributor-facing`,
  `maintainer-facing`, `generated`, or `proposal`.
- Use Diataxis as a lens, not as a forced directory scheme: how-to, reference,
  explanation, and tutorial documents answer different reader needs.
- Put the useful sentence first.
- Keep one judgment per sentence.
- Preserve stable project terms and source-of-truth boundaries.
- Prefer deleting repeated context before adding new explanation.
