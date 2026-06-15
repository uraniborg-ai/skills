# Workspace Proposals

Use a root `docs` Git repository as the workspace anchor. The machine-readable
workspace project inventory lives at `docs/workspace.toml`. Workspace-level
proposals live in `docs/proposals`.

## Manifest

`docs/workspace.toml` is the source of truth for child projects:

```toml
version = 1

[workspace]
name = "uess"

[[projects]]
name = "skills"
repo = "https://github.com/uraniborg-ai/skills.git"
path = "skills"
branch = "main"
required = true
```

Required fields:

- `version`: must be `1`.
- `projects[].name`: stable project label.
- `projects[].repo`: clone URL.
- `projects[].path`: workspace-relative checkout path. Do not use absolute paths
  or `..`.

Optional fields:

- `workspace.name`: human-readable workspace name.
- `projects[].branch`: preferred branch after clone.
- `projects[].required`: boolean. Defaults to `true`.

Unknown project keys are validation errors so typos are caught early.

## Proposals

- Workspace proposal filenames use `docs/proposals/NNN-<title>.md`.
- `docs/proposals/001-*.md` is reserved for the workspace projects proposal.
- The `001` proposal explains the intent, scope, non-goals, and acceptance
  scenarios for the manifest. It does not duplicate the project list.
- Project-specific decisions stay in each child project's own proposal system.

## Empty Docs Repo

If the docs repo exists but `docs/workspace.toml` is missing:

1. Do not clone child projects yet.
2. Ask whether to create `docs/workspace.toml` and
   `docs/proposals/001-workspace-projects.md`.
3. If confirmed, generate the manifest from currently cloned sibling Git
   repositories.
4. Ask the user to review repo URLs, paths, branches, and required/optional
   status before treating the manifest as authoritative.

Use `$ub-proposals` when drafting or reviewing the prose around the decision,
scope, non-goals, acceptance scenarios, and open questions.
