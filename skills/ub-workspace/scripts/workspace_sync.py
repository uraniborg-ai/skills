#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorkspaceConfig:
    path: str = ""
    root: str = ""
    defaults: dict[str, Any] = field(default_factory=dict)
    discovery: dict[str, Any] = field(default_factory=dict)
    groups: dict[str, dict[str, Any]] = field(default_factory=dict)
    repos: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class RepoResult:
    repo: str
    path: str
    group: str = "projects"
    branch: str = ""
    upstream: str = ""
    status: str = ""
    detail: str = ""
    dirty_count: int = 0
    ahead: int | None = None
    behind: int | None = None
    pull_policy: str = ""
    dirty_pull_policy: str = ""
    push_policy: str = ""


def run_git(repo: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def output(proc: subprocess.CompletedProcess[str]) -> str:
    return (proc.stdout or proc.stderr).strip()


def find_config(root: Path) -> Path | None:
    candidate = root / ".ub-workspace" / "config.toml"
    if candidate.exists():
        return candidate
    for parent in [root, *root.parents]:
        candidate = parent / ".ub-workspace" / "config.toml"
        if candidate.exists():
            return candidate
    return None


def load_config(root: Path, config_path: Path | None) -> WorkspaceConfig:
    path = config_path or find_config(root)
    if path is None:
        return WorkspaceConfig(root=str(root))
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return WorkspaceConfig(
        path=str(path),
        root=str(data.get("root", "")),
        defaults=dict(data.get("defaults", {})),
        discovery=dict(data.get("discovery", {})),
        groups=dict(data.get("groups", {})),
        repos=dict(data.get("repos", {})),
    )


def workspace_root(cli_root: Path | None, config: WorkspaceConfig) -> Path:
    if cli_root is not None:
        return cli_root.expanduser().resolve()
    if config.root:
        return Path(config.root).expanduser().resolve()
    return Path.cwd().resolve()


def rel(repo: Path, root: Path) -> str:
    try:
        return repo.relative_to(root).as_posix()
    except ValueError:
        return repo.as_posix()


def discover_repos(root: Path, config: WorkspaceConfig) -> list[Path]:
    repos: set[Path] = set()
    for child in root.iterdir():
        if child.is_dir() and (child / ".git").exists():
            repos.add(child.resolve())

    if config.discovery.get("include_references", True):
        references = root / "references"
        if references.exists():
            for child in references.iterdir():
                if child.is_dir() and (child / ".git").exists():
                    repos.add(child.resolve())

    return sorted(repo for repo in repos if group_for(rel(repo, root), config) != "excluded")


def matches(pattern: str, path: str) -> bool:
    return fnmatch.fnmatch(path, pattern) or path == pattern or path.startswith(f"{pattern}/")


def group_for(path: str, config: WorkspaceConfig) -> str:
    excluded = False
    for name, group in config.groups.items():
        excludes = group.get("exclude", [])
        if any(matches(pattern, path) for pattern in excludes):
            excluded = True
            continue
        if any(matches(pattern, path) for pattern in group.get("paths", [])):
            return name
    if path.startswith("references/"):
        return "references"
    if excluded:
        return "excluded"
    return "projects"


def merged_policy(repo_name: str, path: str, config: WorkspaceConfig) -> dict[str, Any]:
    group_name = group_for(path, config)
    policy = dict(config.defaults)
    policy.update(config.groups.get(group_name, {}))
    policy.update(config.repos.get(repo_name, {}))
    return policy


def current_branch(repo: Path) -> str:
    proc = run_git(repo, "branch", "--show-current")
    return proc.stdout.strip()


def upstream_ref(repo: Path) -> str:
    proc = run_git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    return proc.stdout.strip() if proc.returncode == 0 else ""


def dirty_count(repo: Path) -> int:
    proc = run_git(repo, "status", "--porcelain=v1")
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def fetch_upstream(repo: Path, upstream: str) -> tuple[bool, str]:
    remote = upstream.split("/", 1)[0] if "/" in upstream else ""
    args = ["fetch", "--prune", remote] if remote else ["fetch", "--all", "--prune"]
    proc = run_git(repo, *args)
    return proc.returncode == 0, output(proc)


def ahead_behind(repo: Path, upstream: str) -> tuple[int | None, int | None]:
    proc = run_git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
    if proc.returncode != 0:
        return None, None
    left, right = proc.stdout.strip().split()
    return int(right), int(left)


def classify(repo: Path, upstream: str) -> str:
    head = run_git(repo, "rev-parse", "HEAD", check=True).stdout.strip()
    upstream_sha = run_git(repo, "rev-parse", upstream, check=True).stdout.strip()
    merge_base = run_git(repo, "merge-base", "HEAD", upstream, check=True).stdout.strip()
    if head == upstream_sha:
        return "up_to_date"
    if merge_base == head:
        return "can_fast_forward"
    if merge_base == upstream_sha:
        return "local_ahead"
    return "diverged"


def sync_repo(
    repo: Path, root: Path, config: WorkspaceConfig, dry_run: bool, include_dirty: bool
) -> RepoResult:
    path = rel(repo, root)
    group = group_for(path, config)
    policy = merged_policy(repo.name, path, config)
    result = RepoResult(
        repo=repo.name,
        path=path,
        group=group,
        pull_policy=str(policy.get("pull", "")),
        dirty_pull_policy=str(policy.get("dirty_pull", "")),
        push_policy=str(policy.get("push", "")),
    )
    result.branch = current_branch(repo)
    result.upstream = upstream_ref(repo)
    result.dirty_count = dirty_count(repo)

    if not result.branch:
        result.status = "failed"
        result.detail = "detached HEAD or no current branch"
        return result
    if not result.upstream:
        result.status = "no_upstream"
        result.detail = "current branch has no configured upstream"
        return result
    if result.pull_policy in {"never", "none", "disabled"}:
        result.status = "pull_disabled"
        result.detail = f"pull policy is {result.pull_policy}"
        return result

    ok, fetch_detail = fetch_upstream(repo, result.upstream)
    if not ok:
        result.status = "failed"
        result.detail = f"fetch failed: {fetch_detail}"
        return result

    result.ahead, result.behind = ahead_behind(repo, result.upstream)
    try:
        state = classify(repo, result.upstream)
    except subprocess.CalledProcessError as exc:
        result.status = "failed"
        result.detail = f"comparison failed: {output(exc)}"
        return result

    if state == "up_to_date":
        result.status = "up_to_date"
        result.detail = "matches upstream"
        return result
    if state == "local_ahead":
        result.status = "local_ahead"
        result.detail = "local branch has commits not on upstream"
        return result
    if state == "diverged":
        result.status = "diverged"
        result.detail = "local and upstream both have unique commits"
        return result
    if result.dirty_count and not include_dirty:
        result.status = "dirty_skipped"
        result.detail = "fast-forward available, but worktree has local changes"
        return result
    if dry_run:
        result.status = "would_fast_forward"
        result.detail = "fast-forward available; dry run did not pull"
        return result

    proc = run_git(repo, "pull", "--ff-only")
    if proc.returncode != 0:
        result.status = "failed"
        result.detail = f"pull --ff-only failed: {output(proc)}"
        return result
    result.status = "fast_forwarded"
    result.detail = output(proc) or "pulled with --ff-only"
    result.ahead, result.behind = ahead_behind(repo, result.upstream)
    return result


def print_text(root: Path, config: WorkspaceConfig, results: list[RepoResult]) -> None:
    groups: dict[str, list[RepoResult]] = {}
    for result in results:
        groups.setdefault(result.status, []).append(result)

    order = [
        "fast_forwarded",
        "would_fast_forward",
        "up_to_date",
        "dirty_skipped",
        "local_ahead",
        "diverged",
        "no_upstream",
        "pull_disabled",
        "failed",
    ]
    print("# UB Workspace Sync")
    print()
    print(f"- root: `{root}`")
    print(f"- config: `{config.path or 'none'}`")
    print()
    for status in order:
        items = groups.get(status, [])
        if not items:
            continue
        print(f"## {status} ({len(items)})")
        for item in items:
            counts = ""
            if item.ahead is not None and item.behind is not None:
                counts = f" ahead={item.ahead} behind={item.behind}"
            dirty = f" dirty={item.dirty_count}" if item.dirty_count else ""
            print(
                f"- **{item.path}** `{item.branch}` -> `{item.upstream}`{counts}{dirty}: {item.detail}"
            )
        print()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="workspace root")
    parser.add_argument("--config", type=Path, help="explicit .ub-workspace/config.toml path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-dirty", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    preliminary_root = args.root.expanduser().resolve() if args.root else Path.cwd().resolve()
    config = load_config(preliminary_root, args.config)
    root = workspace_root(args.root, config)

    results = [
        sync_repo(repo, root, config, args.dry_run, args.include_dirty)
        for repo in discover_repos(root, config)
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "root": str(root),
                    "config": asdict(config),
                    "repositories": [asdict(r) for r in results],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print_text(root, config, results)

    return 1 if any(result.status in {"failed", "diverged"} for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
