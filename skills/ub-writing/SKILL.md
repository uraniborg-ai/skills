---
name: ub-writing
description: Draft, rewrite, or review repository documentation for concise, clear, context-efficient writing. Use for README files, docs, proposals, architecture notes, guides, product copy, agent-facing docs, or skill docs when Codex should reduce context cost, clarify audience and job, remove repetition, tighten wording, identify ambiguity, preserve stable terminology, or produce review findings with shorter suggested wording.
---

# UB Writing

Use this skill for repo documentation that should be short, clear, and cheap
for humans and agents to load. Treat context as a limited resource.

## Workflow

1. Identify the document's audience and job in one sentence.
2. Read only the target sections needed for the task.
3. Check local project guidance first: `AGENTS.md`, `docs/philosophy.md`,
   nearby docs, and relevant proposals.
4. Preserve local source-of-truth boundaries and stable terms.
5. Remove weight before adding explanation.

Use `$ub-proposals` as well when proposal status, section shape, non-goals,
acceptance scenarios, or proposal lifecycle conventions matter.

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
  decision risk.
- `P2`: unclear audience/job, ambiguous actor or boundary, repeated rationale,
  or implementation detail in the wrong document.
- `P3`: wording, terminology, list shape, passive voice, or clarity cleanup.

For rewrite requests:

- Edit directly when asked to implement.
- Keep the document's audience, status, links, and code blocks intact.
- Delete sentences that add no reader value.
- Replace only when deletion would lose necessary meaning.
