# Release Checklist

Use this checklist when preparing a `ub-skills` catalog change for sharing or
release.

## Catalog

- Confirm each public skill has `SKILL.md` with matching `name` and
  `description`.
- Confirm each public skill has `agents/openai.yaml` with `display_name`,
  `short_description`, and `default_prompt`.
- Confirm new public skills are listed in `tests/smoke/check_structure.py`.
- Confirm removed public skills are removed from README install examples and
  smoke expectations.
- For renamed or replaced public skills, record the old name, new name, and
  user action in `CHANGELOG.md` before release. Keep the new name in README
  install examples and smoke expectations.
- For new public skills, confirm local `npx skills` discovery shows the skill:

  ```sh
  npx skills add . --list
  ```

## Documentation

- Update `README.md` when the public skill list or install guidance changes.
- Update `CHANGELOG.md` under `Unreleased` with user-visible catalog changes.
- For renames, write the migration note from the user's point of view, such as
  replacing an old skill invocation or install target with the new public skill
  name.
- Keep installation examples aligned with the default public skill set.

## Validation

- Run `npm run smoke`.
- If Python scripts changed, run:

  ```sh
  UV_CACHE_DIR=.uv-cache uv run ruff format .
  UV_CACHE_DIR=.uv-cache uv run ruff format --check .
  ```

- If a bundled script changed, run a representative command for that script.

## Installed Copies

- After a release or shared update, tell users to refresh installed skills with
  `npx skills update --global` for global installs or the project-local update
  command for local installs. Tell users that global updates can affect
  installed skills beyond `ub-*`.
- For supported agent installs, confirm the public catalog is visible with
  `npx skills add uraniborg-ai/skills --list`.
- For new public skills, confirm the public catalog list includes the new skill
  before asking users to install it.
- For renamed or replaced skills, confirm the public catalog list includes the
  new skill and no longer includes the old public skill before asking users to
  refresh installed copies.
- After refreshing, confirm `ub-*` copies in `~/.agents/skills` and
  `~/.claude/skills`. Treat Claude entries as present when they are directories
  or symlinks.
