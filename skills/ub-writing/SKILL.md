---
name: ub-writing
description: Draft, rewrite, or review project technical documentation and Git commit messages for concise, clear, context-efficient writing. Use for contributor-facing docs, README updates, development guides, architecture notes, changelogs, agent instructions, generated-doc review, commit message review, requests to create or amend Git commits, and technical doc routing when Codex should clarify audience and job, preserve source-of-truth boundaries, reduce repetition, or identify ambiguity.
---

# UB Writing

Use this skill for project technical documentation that should be short, clear,
and cheap for humans and agents to load. Treat context as a limited resource.

## Scope

Use this skill for technical docs, contributor-facing operating docs,
maintainer notes, changelogs, generated-doc review, Git commit messages, and
agent instructions.

Do not use it by default for literary writing, essays, blog posts, marketing
copy, personal notes, presentation prose, resumes, or prompt experiments unless
the user explicitly asks for a technical-docs pass.

## Workflow

1. Classify the document job as `user-facing`, `contributor-facing`,
   `maintainer-facing`, `generated`, or `proposal`.
2. Read only the target sections needed for the task.
3. Check local project guidance first: `AGENTS.md`, nearby docs, and relevant
   proposals. If `CLAUDE.md` exists independently, check for source-of-truth
   drift against `AGENTS.md`.
4. Preserve local source-of-truth boundaries and stable terms.
5. Remove weight before adding explanation.

Do not require a fixed document set. Before suggesting a new document, check
whether the information belongs in an existing source of truth. Use
`references/project-doc-structure.md` for routing decisions.

For proposal, RFC, ADR, decision record, `docs/proposals/`, proposal status,
frontmatter, non-goals, acceptance scenarios, or proposal lifecycle work, first
check whether `$ub-proposals` is available. Use it with `$ub-writing` when
available. If it is not available, suggest installing it before drafting or
rewriting the proposal; continue with local-convention fallback only when the
user declines or installation is not possible.

For generated reference docs, review the output but do not edit generated files
directly. Route wording fixes to source comments, docstrings, generator code,
templates, config, wrapper README text, or regenerate commands.

For Git commit message requests, treat any request to create, amend, squash, or
prepare a Git commit as a commit message request. Inspect local commit rules
first: `AGENTS.md`, `CONTRIBUTING.md`, `docs/commit-conventions.md`, release
docs, relevant proposals, or maintainer docs. If no explicit local rule exists,
inspect recent subjects with `git log --oneline -10` before falling back to
Conventional Commits v1.0.0 in English. Prefer staged changes via
`git diff --cached`; if only unstaged changes exist, say the message is a draft.
Treat commit messages as `maintainer-facing` writing. Suggest splitting
unrelated changes. Do not run `git commit` unless the user explicitly asks.

Before committing:

- Use `git diff --cached` for the message when changes are staged.
- If nothing is staged, inspect the unstaged diff and stage only the intended
  files.
- Choose the commit type and optional scope.
- Use an imperative, lowercase subject with no trailing period.
- Run `git commit` only when the user explicitly asked to commit.

## Writing Standard

- Put the useful sentence first.
- Keep one judgment per sentence.
- Prefer concrete nouns, named actors, and active voice.
- Use `must` for requirements, `can` for capability, and `should` for
  intentional guidance.
- Prefer examples that reveal behavior over prose that explains it twice.
- Keep lists parallel.
- Keep implementation detail only when it changes the reader's decision,
  boundary, usage, migration, or acceptance test.

## Remove Or Challenge

- Repeated rationale.
- Obvious explanation.
- Vague modifiers such as simple, powerful, seamless, flexible, and robust.
- Long lead-ins before the useful sentence.
- Passive sentences that hide who acts.
- Ambiguous actor, scope, obligation, order, ownership, storage, or API boundary.
- Product claims stronger than the project owns.
- Internal implementation detail in user-facing docs.

## Review Output

For review-only requests, lead with findings:

```text
Findings
- [P1/P2/P3] file:line - Issue. Suggested shorter wording.

Notes
- Optional observations with no required change.
```

Use priorities this way:

- `P1`: source-of-truth, safety, compatibility, data loss, or irreversible
  decision risk, including conflicting independent `AGENTS.md` and `CLAUDE.md`
  instructions.
- `P2`: unclear audience/job, ambiguous actor or boundary, repeated rationale,
  or implementation detail in the wrong document.
- `P3`: wording, terminology, list shape, passive voice, or clarity cleanup.

For rewrite requests:

- Edit directly when asked to implement.
- Keep the document's audience, status, links, and code blocks intact.
- Delete sentences that add no reader value.
- Replace only when deletion would lose necessary meaning.
