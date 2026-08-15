---
name: ub-project-setup
description: Establish or improve project-level development guidance by inspecting repositories, planning development environments, drafting or reviewing proposals, RFCs, and ADRs, and creating or refining technical documentation. Use when Codex needs to set up a new project, fill source-of-truth gaps in an existing project, document contributor workflows or architecture, or manage proposal lifecycle. Treat implemented proposals as immutable and add annotations only when explicitly requested. Do not use for ordinary code implementation, Git operations, Python execution, or generic writing.
---

# UB Project Setup

Use this skill to establish the project-level sources of truth that let humans
and agents develop a project consistently. Apply it to new project setup and to
focused improvements in an existing repository.

## Workflow

1. Inspect local guidance and setup sources before recommending changes:
   `AGENTS.md`, `README*`, `CONTRIBUTING*`, relevant `docs/`, proposals,
   dependency manifests, lockfiles, version files, Docker files, and CI config.
2. Classify the task as development environment, proposal, technical
   documentation, or a combination of those modes.
3. Identify the existing source of truth and the smallest gap that blocks the
   requested work. Do not require a fixed document set.
4. Read only the references needed for the selected modes:
   - development environment planning or diagnosis:
     `references/development-environment.md`
   - proposals, RFCs, ADRs, decision records, or lifecycle:
     `references/proposals.md`
   - README, AGENTS, development guides, architecture notes, changelogs, or
     other project technical docs: `references/technical-documentation.md`
5. Present a read-only diagnosis first when the user has not requested edits or
   environment changes.
6. When edits are requested, update the owning source of truth and validate the
   changed files with the project's documented checks.

## Boundaries And Handoffs

- Preserve local conventions, stable terminology, and source-of-truth
  boundaries before applying this skill's defaults.
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
proposed or completed changes, validation results, and any actions that still
require explicit approval.
