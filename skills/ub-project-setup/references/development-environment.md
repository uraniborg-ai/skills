# Development Environment

Use this reference to turn project setup requirements into a team development
environment plan or to diagnose gaps in an existing setup.

## Inspection

Inspect the project sources that own setup decisions before choosing commands:

- `README*`, `CONTRIBUTING*`, and relevant `docs/`
- `pyproject.toml`, `uv.lock`, `requirements*.txt`, and `environment*.yml`
- `package.json`, lockfiles, `.nvmrc`, and `.node-version`
- `.python-version`, Docker files, CI config, and documented bootstrap scripts

Identify the target platform, project root, required system tools, runtime
versions, dependency sources of truth, credentials, services, and validation
commands. Ask before inventing a runtime version when the project does not own
one.

## Tool Policy

- Prefer Homebrew for system-level developer tools when it is available on
  macOS, Linux, or WSL.
- Install `nvm` with Homebrew when appropriate, but manage Node.js versions with
  `nvm`, not Homebrew-managed `node`.
- Choose Node.js from `.nvmrc`, `.node-version`, `package.json` engines, CI, or
  other project-owned configuration.
- Use `uv` for Python versions, environments, dependency sync, and Python tool
  execution. Follow `$ub-uv` for project and script dependency decisions.
- Use GitHub CLI (`gh`) for GitHub authentication, issues, pull requests,
  releases, and workflows.
- Prefer WSL instructions over native Windows package management unless the
  user explicitly requests native Windows setup.
- Prefer project-local dependency commands after system and runtime tools are
  resolved.

## Plan Output

Include:

- detected requirements and their source files
- target platform and assumptions
- system tools and installation source
- Node.js and Python version decisions
- project-local dependency commands
- GitHub CLI, service, credential, and network requirements
- validation commands
- mutations that require explicit approval

## Safety

- Start with a read-only diagnosis unless the user asks to apply changes.
- Treat install, upgrade, shell-profile edits, service startup, login,
  dependency or lockfile changes, and project file writes as mutation.
- Prefer the smallest useful command sequence over a broad bootstrap command.
- If a command fails because of sandbox, cache, network, credentials, or
  permissions, follow `$ub-codex` instead of retrying unchanged.
