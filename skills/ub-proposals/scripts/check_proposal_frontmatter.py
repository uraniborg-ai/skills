#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate proposal frontmatter for the UB Proposals skill."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REQUIRED_KEYS = ("title", "description", "author", "status", "created_at", "updated_at")
STANDARD_KEYS = set(REQUIRED_KEYS)
CANONICAL_STATUSES = {"draft", "proposed", "accepted", "implemented", "superseded", "rejected"}
LEGACY_STATUSES = {"active", "shipped"}
LEGACY_KEYS = {
    "date",
    "created",
    "updated",
    "related",
    "tags",
    "features",
    "audience",
    "summary",
    "implemented_by",
    "implemented_commits",
    "decision_note",
    "depends_on",
    "supersedes",
    "superseded_by",
    "follow_up",
    "type",
}
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$")


@dataclass
class Finding:
    path: Path
    severity: str
    message: str


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, object], str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
    if end is None:
        return None

    metadata: dict[str, object] = {}
    frontmatter = lines[1:end]
    index = 0
    while index < len(frontmatter):
        line = frontmatter[index]
        if not line.strip() or line.startswith((" ", "\t")):
            index += 1
            continue

        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", line)
        if not match:
            index += 1
            continue

        key, raw_value = match.group(1), match.group(2) or ""
        if raw_value:
            metadata[key] = strip_quotes(raw_value)
            index += 1
            continue

        values: list[str] = []
        index += 1
        while index < len(frontmatter):
            child = frontmatter[index]
            if not child.startswith((" ", "\t")):
                break
            child_text = child.strip()
            if child_text.startswith("- "):
                values.append(strip_quotes(child_text[2:]))
            index += 1
        metadata[key] = values

    body = "\n".join(lines[end + 1 :])
    return metadata, body


def first_h1(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def is_iso_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not TIMESTAMP_RE.match(value):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def validate_file(path: Path, *, legacy: bool) -> list[Finding]:
    findings: list[Finding] = []
    parsed = parse_frontmatter(path.read_text(encoding="utf-8"))
    if parsed is None:
        return [Finding(path, "error", "missing YAML frontmatter")]

    metadata, body = parsed
    keys = set(metadata)

    for key in REQUIRED_KEYS:
        if key not in metadata:
            severity = "warning" if legacy else "error"
            findings.append(Finding(path, severity, f"missing required field `{key}`"))

    unknown_keys = sorted(keys - STANDARD_KEYS)
    for key in unknown_keys:
        if legacy:
            kind = "legacy" if key in LEGACY_KEYS else "custom"
            findings.append(Finding(path, "warning", f"{kind} metadata field `{key}`"))
        else:
            findings.append(Finding(path, "error", f"non-standard metadata field `{key}`"))

    author = metadata.get("author")
    if "author" in metadata and not (
        isinstance(author, list)
        and author
        and all(isinstance(item, str) and item for item in author)
    ):
        findings.append(Finding(path, "error", "`author` must be a non-empty YAML list"))

    status = metadata.get("status")
    if isinstance(status, str):
        if status not in CANONICAL_STATUSES:
            if legacy and status in LEGACY_STATUSES:
                findings.append(Finding(path, "warning", f"legacy status `{status}`"))
            else:
                allowed = ", ".join(sorted(CANONICAL_STATUSES))
                findings.append(Finding(path, "error", f"`status` must be one of: {allowed}"))
    elif "status" in metadata:
        findings.append(Finding(path, "error", "`status` must be a string"))

    for key in ("created_at", "updated_at"):
        if key in metadata and not is_iso_timestamp(metadata[key]):
            findings.append(Finding(path, "error", f"`{key}` must be an ISO 8601 timestamp"))

    title = metadata.get("title")
    h1 = first_h1(body)
    if isinstance(title, str) and h1 is not None and title != h1:
        findings.append(Finding(path, "error", f"`title` does not match H1 `{h1}`"))

    return findings


def proposal_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.md") if path.name != "README.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "proposal_dir", type=Path, help="Directory containing proposal Markdown files"
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Report legacy metadata/statuses as warnings instead of failures",
    )
    args = parser.parse_args(argv)

    proposal_dir = args.proposal_dir
    if not proposal_dir.is_dir():
        print(f"error: not a directory: {proposal_dir}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for path in proposal_files(proposal_dir):
        findings.extend(validate_file(path, legacy=args.legacy))

    for finding in findings:
        print(f"{finding.severity}: {finding.path}: {finding.message}")

    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        return 1

    print(f"ok: {len(proposal_files(proposal_dir))} proposal file(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
