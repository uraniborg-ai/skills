---
name: ub-dev-env
description: Plan and diagnose team development environments for Linux, macOS, and Windows WSL using Homebrew-first system tooling, nvm-managed Node.js versions, uv-managed Python versions and environments, and GitHub CLI workflows. Use when Codex needs to inspect project README files, requirements, lockfiles, or setup docs and decide how to apply project dependencies through the team's development environment standards.
metadata:
  version: 0.1.0
  stability: stable
  domain: development-environment
---

# UB Dev Env

Use this skill to turn project setup requirements into the team's standard
developer environment plan.

## Workflow

1. Inspect project setup sources before recommending commands:
   `README*`, `CONTRIBUTING*`, `docs/`, `requirements*.txt`,
   `pyproject.toml`, `uv.lock`, `package.json`, lockfiles, `.nvmrc`,
   `.node-version`, `.python-version`, Docker files, and CI configs.
2. Identify the target environment: macOS, Linux, or Windows via WSL.
3. Check whether Homebrew is available before choosing system package commands.
4. Classify requirements into system tools, Node.js, Python, GitHub, and
   project-local dependencies.
5. Present a read-only diagnosis first. Include proposed commands, but do not
   install, modify shell config, or change project files unless the user
   explicitly requests mutation.

## Tool Policy

- Prefer Homebrew for system-level developer tools such as `git`, `gh`, `jq`,
  `cmake`, `pkg-config`, `openssl`, databases, queues, and native libraries.
- Install `nvm` with Homebrew when Homebrew is available, but manage Node.js
  versions with `nvm`, not Homebrew-managed `node`.
- Use project files such as `.nvmrc`, `.node-version`, `package.json engines`,
  and CI configs to choose the Node.js version. Ask before inventing a version.
- Use `uv` for Python version installation, virtual environments, dependency
  sync, and Python tool execution. Follow `$ub-uv` for Python project details.
- Use GitHub CLI (`gh`) for GitHub authentication, issue, pull request, release,
  and workflow tasks.
- In Windows environments, prefer WSL setup instructions over native Windows
  package management unless the user explicitly asks for native Windows setup.

## Output

When reporting a setup plan, include:

- detected project requirements and source files
- Homebrew-managed tools
- nvm-managed Node.js setup
- uv-managed Python setup
- GitHub CLI setup
- project-local dependency commands
- commands that require explicit user approval before mutation

## Safety

- Treat install, upgrade, shell-profile edits, service startup, login, and
  project file changes as mutation.
- If a command needs network, credentials, or elevated permissions in Codex,
  follow `$ub-codex`.
- Prefer explaining the smallest useful command sequence over running a broad
  bootstrap command.
