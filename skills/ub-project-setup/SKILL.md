---
name: ub-project-setup
description: Establish or improve project-level development guidance by inspecting repositories, planning development environments, and creating or refining technical documentation. Use when Codex needs to set up a new project, fill source-of-truth gaps in an existing project, document contributor workflows or architecture, or record an optional proposal or TODO. Treat implemented proposals as immutable and add annotations only when explicitly requested. Do not use for ordinary code implementation, Git operations, Python execution, or generic writing.
---

# UB Project Setup

Use this skill to establish the project-level sources of truth that let humans
and agents develop a project consistently. Its primary job is to understand the
development environment and document the resulting workflow. Apply it to new
project setup and to focused improvements in an existing repository.

## Workflow

1. Inspect local guidance and setup sources before recommending changes:
   `AGENTS.md`, `CLAUDE.md`, `README*`, `CONTRIBUTING*`, relevant `docs/`,
   dependency manifests, lockfiles, version files, Docker files, CI config,
   and documented bootstrap scripts.
2. Classify the task as development environment, technical documentation,
   agent guidance, or optional proposal/TODO recording. Proposal work is a
   supporting mode, not the default purpose of this skill.
3. Identify explicit user choices, existing sources of truth, and the smallest
   documentation gap. Preserve a declared Conda or other environment instead
   of replacing it with the defaults below.
4. Read only the references needed for the selected modes:
   - development environment planning or diagnosis:
     `references/development-environment.md`
   - proposals, RFCs, ADRs, decision records, or lifecycle:
     `references/proposals.md`
   - README, AGENTS, development guides, architecture notes, changelogs, or
     other project technical docs: `references/technical-documentation.md`
5. Present a read-only diagnosis first when the user has not requested edits or
   environment changes.
6. If `docs/` has no current development guidance, create or propose
   `docs/development.md`. If it has no technical documentation guide, create or
   propose `docs/technical-documentation.md`, unless an equivalent local source
   of truth already exists.
7. For a new project that needs agent entry points, create `AGENTS.md` as the
   shared canonical file and `CLAUDE.md` as its pointer by default. Link the
   owning development and documentation guides from both files. Keep detailed
   guidance in `docs/`, not duplicated in agent entry points.
8. If only `CLAUDE.md` exists, inspect whether it contains Claude-specific
   intent. Ask before moving, deleting, or rewriting ambiguous content.
9. If `AGENTS.md` and `CLAUDE.md` conflict on commands, runtimes,
   dependencies, ownership, source of truth, or safety, ask the user before
   editing either file. Recommend consolidating shared guidance in
   `AGENTS.md` and making `CLAUDE.md` a pointer.
10. When edits are requested, update the owning source of truth and validate the
   changed files with the project's documented checks.

## Boundaries And Handoffs

- Preserve local conventions, stable terminology, and source-of-truth
  boundaries before applying this skill's defaults.
- Default to macOS, Linux, and WSL2 for development-environment guidance.
  Treat native Windows as a separate setup scope.
- Assume that users may not know Unix CLI conventions. Explain command purpose,
  PATH and shell-profile effects, permissions, platform differences, and
  verification steps.
- When no tool is selected, consider Homebrew, Node.js, uv, GitHub CLI, and Git
  for the default workflow. Use Homebrew for system tools, direct Homebrew
  Node.js for a single Node version, and nvm only when multiple Node versions
  or project constraints require it.
- Use `.python-version` for the local Python version, `requires-python` for
  supported ranges, and `uv.lock` for resolved dependencies. Do not invent an
  exact Python version or silently resolve a conflict.
- Add new Ruff configuration to `.ruff.toml`, default to formatter line length
  88, and do not generate `target-version` unless the project explicitly owns
  that setting.
- For Python projects, put a concise `uv` instruction in `AGENTS.md` and the
  `CLAUDE.md` pointer while keeping the detailed workflow in `docs/`.
- Treat `implemented` proposals as immutable. Do not edit their body or
  frontmatter, including stale paths, commands, links, typos, or wording.
- For an implemented proposal, follow this decision table:
  - a request to fix, update, or modernize it: make no proposal change
  - an explicit request to append an annotation: append only the annotation
  - a changed decision: write a new proposal
- Never recommend or add `Revision Notes`, `Implementation Notes`, an
  `updated_at` change, or an annotation for an implemented proposal unless the
  user explicitly asks for an annotation. Route current information to current
  documentation, a changelog, an issue, or a new proposal.
- Treat TODOs, backlogs, follow-up work, and improvement ideas as optional
  proposal-record candidates when they should remain in the repository for
  later review. Use an existing issue tracker as the source of truth when the
  project already has one, and do not create duplicate records for ephemeral
  tasks.
- Use `$ub-uv` for Python versions, environments, dependencies, and execution.
- Use `$ub-git` for repository state, staging, commits, branches, and sync.
- Use `$ub-codex` for sandbox, cache, network, credential, or permission
  failures.
- Do not use this skill for ordinary feature implementation, code debugging,
  generic prose, marketing copy, personal writing, or presentation scripts.
- Treat installs, upgrades, shell-profile edits, service startup, login,
  dependency changes, and project file writes as mutation.

## Output

Report the inspected sources, selected modes, source-of-truth decisions,
environment findings and recommendations, created or updated documentation,
agent-file links, validation results, unresolved conflicts, and any actions
that still require explicit approval.
