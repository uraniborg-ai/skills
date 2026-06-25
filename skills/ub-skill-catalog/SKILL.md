---
name: ub-skill-catalog
description: Maintain the Uraniborg public skill catalog by adding, updating, validating, releasing, and sharing `ub-*` skills from the source `ub-skills` repository. Use when an installed `ub-*` skill needs improvement, when Codex must distinguish installed skill copies from the source catalog, or when Uraniborg team members need to update SKILL.md, OpenAI metadata, references, scripts, tests, README, changelog, or release guidance.
---

# UB Skill Catalog

Use this skill to maintain the Uraniborg public skill catalog from the source
repository. Treat installed `ub-*` skills as distribution copies, not as the
durable source of truth.

## Source Policy

- Use `https://github.com/uraniborg-ai/skills.git` as the canonical public
  repository URL.
- Assume permanent `ub-*` source edits are made by Uraniborg team members.
- Treat `~/.agents/skills/ub-*` and `./.agents/skills/ub-*` as installed
  copies. Inspect them to understand observed behavior, but do not make durable
  fixes there.
- If the user is not acting as a Uraniborg team member, help them capture the
  reproduction, expected behavior, installed skill path, project context, and
  relevant logs for a team request.

## Improve Installed UB Skills

1. Identify the observed problem in the installed skill copy or project where
   the skill was used.
2. Ask the user whether they already have the `ub-skills` repository cloned and,
   if so, for its path. Do this before cloning or assuming a source location.
3. If the user provides a path, verify that it is the source repository before
   editing it.
4. If the user does not have a clone, use HTTPS by default:

   ```sh
   git clone https://github.com/uraniborg-ai/skills.git ub-skills
   ```

5. Use SSH only when the user explicitly requests it.
6. Make durable fixes in the source repository, not in the installed copy.
7. Update `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`,
   `templates/`, README, changelog, and smoke expectations as needed.
8. Validate the source repository before reporting the work as complete.

## Add Or Update Public Skills

1. Read `AGENTS.md` and `docs/development.md` before changing public skills.
2. Keep public skill names prefixed with `ub-`.
3. Keep `SKILL.md` concise. Move optional details into `references/` only when
   progressive disclosure helps.
4. Add or update `agents/openai.yaml` with `display_name`, `short_description`,
   and `default_prompt`.
5. Add new public skills to `tests/smoke/check_structure.py`.
6. Update `README.md` and `CHANGELOG.md` when the public catalog changes.
7. For release preparation, read `references/release-checklist.md`.

## Validation

- Run `npm run smoke` after adding, removing, or changing a public skill.
- If Python scripts changed, run Ruff format and format check using the repo
  commands from `docs/development.md`.
- If a skill includes a deterministic script, run a representative command for
  that script before sharing the change.
