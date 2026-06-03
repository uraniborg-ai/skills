#!/usr/bin/env python3
"""Smoke-check the skill catalog structure."""

from __future__ import annotations

import sys
from pathlib import Path


EXPECTED = {"ub-codex", "ub-pdf-reader", "ub-youtube-transcript", "ub-uv", "ub-workspace"}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    skills = root / "skills"
    missing = []
    for name in sorted(EXPECTED):
        skill = skills / name / "SKILL.md"
        if not skill.exists():
            missing.append(str(skill.relative_to(root)))
            continue
        text = skill.read_text(encoding="utf-8")
        if f"name: {name}" not in text:
            missing.append(f"{skill.relative_to(root)} missing name: {name}")
        if "description:" not in text:
            missing.append(f"{skill.relative_to(root)} missing description")
    if missing:
        print("\n".join(missing), file=sys.stderr)
        return 1
    print(f"ok: {len(EXPECTED)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
