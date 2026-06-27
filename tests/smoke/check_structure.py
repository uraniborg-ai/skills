#!/usr/bin/env python3
"""Smoke-check the skill catalog structure."""

from __future__ import annotations

import sys
from pathlib import Path


EXPECTED = {
    "ub-codex",
    "ub-dev-env",
    "ub-pdf-reader",
    "ub-presentation",
    "ub-proposals",
    "ub-skill-catalog",
    "ub-youtube-transcript",
    "ub-uv",
    "ub-writing",
}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    skills = root / "skills"
    missing = []
    for name in sorted(EXPECTED):
        skill_dir = skills / name
        skill = skill_dir / "SKILL.md"
        if not skill.exists():
            missing.append(str(skill.relative_to(root)))
            continue
        text = skill.read_text(encoding="utf-8")
        if f"name: {name}" not in text:
            missing.append(f"{skill.relative_to(root)} missing name: {name}")
        if "description:" not in text:
            missing.append(f"{skill.relative_to(root)} missing description")
        agent = skill_dir / "agents" / "openai.yaml"
        if not agent.exists():
            missing.append(str(agent.relative_to(root)))
            continue
        agent_text = agent.read_text(encoding="utf-8")
        for field in ("display_name", "short_description", "default_prompt"):
            if f"{field}:" not in agent_text:
                missing.append(f"{agent.relative_to(root)} missing {field}")
        if f"${name}" not in agent_text:
            missing.append(f"{agent.relative_to(root)} default_prompt missing ${name}")
    if missing:
        print("\n".join(missing), file=sys.stderr)
        return 1
    print(f"ok: {len(EXPECTED)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
