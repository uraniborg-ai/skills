# Development Environment

Use this reference to understand a project's development environment, document
the current setup, and recommend a small team workflow when the user has not
chosen one.

## Inspection

Inspect the project sources that own setup decisions before choosing commands:

- `README*`, `CONTRIBUTING*`, and relevant `docs/`
- `AGENTS.md` and `CLAUDE.md`, including nested copies that may own local rules
- `pyproject.toml`, `uv.lock`, `requirements*.txt`, and `environment*.yml`
- `package.json`, lockfiles, `.nvmrc`, and `.node-version`
- `.python-version`, Docker files, CI config, and documented bootstrap scripts
- project-local agent skill directories such as `.agents/skills/`,
  `.claude/skills/`, and `.cursor/skills/`, including `SKILL.md` files,
  symlinks, and project-specific installation metadata

Identify the target platform, project root, shell assumptions, required system
tools, runtime versions, dependency sources of truth, credentials, services,
and validation commands. Distinguish observed facts from recommendations. Ask
before inventing a runtime version when the project does not own one.

Assume macOS, Linux, or WSL2 unless the project or user states otherwise.
Native Windows setup is a separate scope. Since users may not know Unix CLI
conventions, record command purpose, PATH and shell-profile effects, permission
requirements, platform differences, and post-install verification.

## Tool Policy

- Prefer Homebrew for system-level developer tools when it is available on
  macOS, Linux, or WSL. Explain that first-time Homebrew setup may require
  administrator approval even though many later package installs do not.
- Prefer a direct Homebrew-managed `node` installation when one Node.js version
  is sufficient. Consider nvm only when multiple Node versions or project
  constraints require it, and choose the version from `.nvmrc`, `.node-version`,
  `package.json` engines, CI, or other project-owned configuration.
- Use `uv` for Python versions, environments, dependency sync, and Python tool
  execution. Follow `$ub-uv` for project and script dependency decisions.
- Use GitHub CLI (`gh`) for GitHub authentication, issues, pull requests,
  releases, and workflows. Recommend `gh auth login` when authentication is
  needed, but never place a PAT or other credential in project documentation.
- Prefer WSL instructions over native Windows package management unless the
  user explicitly requests native Windows setup.
- Prefer project-local dependency commands after system and runtime tools are
  resolved.
- If the user explicitly chooses Conda or another environment manager, document
  that environment as the source of truth and do not replace it with uv.

## Agent Skills And `npx skills`

- Default to Node.js and `npx skills`; do not require a global installation of
  the `skills` package. Verify `node --version` and `npx --version` when agent
  skills are part of the project workflow.
- Inspect existing project-local skill directories and their source-of-truth
  policy before suggesting a new installation. Preserve an existing skill
  manager or project-owned `SKILL.md` files.
- When no conflicting local policy exists and the project would benefit from
  reusable workflows, search the Uraniborg owner and propose relevant `ub-*`
  skills from the results:

  ```sh
  npx skills find --owner uraniborg-ai
  ```

- If the work is known, narrow the search with a keyword:

  ```sh
  npx skills find jupyter --owner uraniborg-ai
  ```

- Match recommendations to the work instead of installing every skill:
  `ub-project-setup` for environment and documentation guidance, `ub-uv` for
  Python projects, `ub-jupyter` for notebook projects, `ub-git` for Git
  workflows, and `ub-codex` for Codex sandbox, cache, permission, or tool
  problems.
- After the user approves the source, selected skills, target agent, and scope,
  install the selected source with an explicit command such as:

  ```sh
  npx skills add <source-from-search> \
    --skill <skill-name> \
    --agent <codex-or-other-agent>
  ```

- If the user needs ongoing skill discovery and no suitable tool is already
  installed, separately propose the Vercel `find-skills` skill as a global
  installation:

  ```sh
  npx skills add https://github.com/vercel-labs/skills \
    --skill find-skills \
    --global
  ```

  Ask for an explicit agent target when more than one supported agent is
  available. Do not install this global skill automatically as part of project
  setup.

- Prefer project scope and an explicit `--agent`. Use `--global` only when the
  user wants the skill available across projects. Do not use `--all` by default.
- Treat `add`, `update`, and `remove` as mutations. Use `--yes` only when the
  user has already made the installation decision. For an exploratory trial,
  `npx skills use <source>` can avoid a persistent installation, but the remote
  source should still be reviewed before it is passed to an agent.
- Verify an approved installation with `npx skills list`, the target agent
  directory, symlink targets, and project status. Record the source, selected
  skills, target agent, scope, and update policy in project documentation when
  they affect reproducibility.
- Review remote skill contents and provenance before installation. The
  `skills.sh` security audits are advisory and do not guarantee that a skill is
  safe. The CLI also supports opting out of anonymous telemetry with
  `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1`.

See the [`skills` CLI reference](https://skills.sh/docs/cli) and the
[`skills` source README](https://github.com/vercel-labs/skills/blob/main/README.md)
for current source formats and options.

## Python And Ruff

- Treat `.python-version` as the local default Python interpreter.
- Treat `project.requires-python` in `pyproject.toml` as the supported version
  range and dependency-resolution constraint.
- Treat `uv.lock` as the resolved dependency source of truth.
- If `.python-version` conflicts with `requires-python`, report the conflict
  and ask the user before changing either file.
- If no exact Python version is owned by the project, do not invent one.
- When a project needs a new Ruff configuration, create `.ruff.toml` rather
  than moving configuration into `pyproject.toml`.
- Default new Ruff formatting to line length 88, double quotes, space
  indentation, preserved magic trailing commas, automatic line endings, and
  no `target-version` entry.
- Use `ruff format --check` for formatter validation. Keep lint rules such as
  E501 separate from formatter policy.

## Plan Output

Include:

- detected requirements and their source files
- target platform and assumptions
- observed environment facts versus recommended changes
- system tools and installation source
- Node.js and Python version decisions
- agent-skill candidates, owner-search results, source, target agent, scope,
  and approval state
- project-local dependency commands
- GitHub CLI, service, credential, and network requirements
- PATH, shell-profile, permission, and platform-specific notes
- validation commands
- mutations that require explicit approval

## Safety

- Start with a read-only diagnosis unless the user asks to apply changes.
- Treat install, upgrade, shell-profile edits, service startup, login,
  dependency or lockfile changes, agent-skill changes, and project file writes
  as mutation.
- Prefer the smallest useful command sequence over a broad bootstrap command.
- If a command fails because of sandbox, cache, network, credentials, or
  permissions, follow `$ub-codex` instead of retrying unchanged.
