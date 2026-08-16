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
- project-local dependency commands
- GitHub CLI, service, credential, and network requirements
- PATH, shell-profile, permission, and platform-specific notes
- validation commands
- mutations that require explicit approval

## Safety

- Start with a read-only diagnosis unless the user asks to apply changes.
- Treat install, upgrade, shell-profile edits, service startup, login,
  dependency or lockfile changes, and project file writes as mutation.
- Prefer the smallest useful command sequence over a broad bootstrap command.
- If a command fails because of sandbox, cache, network, credentials, or
  permissions, follow `$ub-codex` instead of retrying unchanged.
