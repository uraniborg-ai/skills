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
    version: int = 1
    name: str = ""
    root: str = ""
    defaults: dict[str, Any] = field(default_factory=dict)
    discovery: dict[str, Any] = field(default_factory=dict)
    groups: dict[str, dict[str, Any]] = field(default_factory=dict)
    repos: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class RepoStatus:
    repo: str
    path: str
    group: str = "projects"
    branch: str = ""
    upstream: str = ""
    relation: str = "unknown"
    ahead: int | None = None
    behind: int | None = None
    dirty_count: int = 0
    dirty_files: list[str] = field(default_factory=list)
    lfs_files: int = 0
    fetch_policy: str = ""
    pull_policy: str = ""
    dirty_pull_policy: str = ""
    push_policy: str = ""
    labels: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    error: str = ""


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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
        version=int(data.get("version", 1)),
        name=str(data.get("name", "")),
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
    depth = int(config.discovery.get("depth", 1))
    if depth <= 1:
        for child in root.iterdir():
            if child.is_dir() and (child / ".git").exists():
                repos.add(child.resolve())
    else:
        for git_dir in root.glob("*/" * depth + ".git"):
            repos.add(git_dir.parent.resolve())

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


def dirty_files(repo: Path, limit: int) -> tuple[int, list[str]]:
    proc = run_git(repo, "status", "--porcelain=v1")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    return len(lines), lines[:limit]


def ahead_behind(repo: Path, upstream: str) -> tuple[int | None, int | None]:
    proc = run_git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
    if proc.returncode != 0:
        return None, None
    left, right = proc.stdout.strip().split()
    return int(right), int(left)


def relation(ahead: int | None, behind: int | None) -> str:
    if ahead is None or behind is None:
        return "unknown"
    if ahead and behind:
        return "diverged"
    if ahead:
        return "ahead"
    if behind:
        return "behind"
    return "up_to_date"


def lfs_count(repo: Path) -> int:
    proc = run_git(repo, "lfs", "ls-files")
    if proc.returncode != 0:
        return 0
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def summarize_repo(
    repo: Path, root: Path, config: WorkspaceConfig, changed_limit: int
) -> RepoStatus:
    path = rel(repo, root)
    group = group_for(path, config)
    policy = merged_policy(repo.name, path, config)
    status = RepoStatus(
        repo=repo.name,
        path=path,
        group=group,
        fetch_policy=str(policy.get("fetch", "")),
        pull_policy=str(policy.get("pull", "")),
        dirty_pull_policy=str(policy.get("dirty_pull", "")),
        push_policy=str(policy.get("push", "")),
        labels=list(policy.get("labels", [])),
        notes=list(policy.get("notes", [])),
    )

    inside = run_git(repo, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0:
        status.error = output(inside) or "not a Git worktree"
        return status

    status.branch = current_branch(repo)
    status.upstream = upstream_ref(repo)
    status.dirty_count, status.dirty_files = dirty_files(repo, changed_limit)
    status.lfs_files = lfs_count(repo)

    if not status.branch:
        status.relation = "detached"
    elif not status.upstream:
        status.relation = "no_upstream"
    else:
        status.ahead, status.behind = ahead_behind(repo, status.upstream)
        status.relation = relation(status.ahead, status.behind)

    return status


def print_markdown(root: Path, config: WorkspaceConfig, statuses: list[RepoStatus]) -> None:
    dirty = [repo for repo in statuses if repo.dirty_count]
    attention = [
        repo
        for repo in statuses
        if repo.error or repo.relation in {"ahead", "behind", "diverged", "no_upstream", "detached"}
    ]
    lfs = [repo for repo in statuses if repo.lfs_files]
    restricted_push = [
        repo for repo in statuses if repo.push_policy in {"explicit-approval", "never"}
    ]

    print("# UB Workspace Status")
    print()
    print(f"- root: `{root}`")
    print(f"- config: `{config.path or 'none'}`")
    print(f"- repositories scanned: {len(statuses)}")
    print(f"- with local changes: {len(dirty)}")
    print(f"- needing branch attention: {len(attention)}")
    print(f"- with LFS files: {len(lfs)}")
    print(f"- push restricted: {len(restricted_push)}")

    if dirty:
        print("\n## Local Changes")
        for repo in dirty:
            print(f"- **{repo.path}** `{repo.branch}` dirty={repo.dirty_count}")
            for changed in repo.dirty_files:
                print(f"  - `{changed}`")

    if attention:
        print("\n## Branch Attention")
        for repo in attention:
            counts = ""
            if repo.ahead is not None and repo.behind is not None:
                counts = f" ahead={repo.ahead} behind={repo.behind}"
            upstream = f" -> `{repo.upstream}`" if repo.upstream else ""
            detail = f": {repo.error}" if repo.error else ""
            print(
                f"- **{repo.path}** `{repo.branch or 'HEAD'}`{upstream}: {repo.relation}{counts}{detail}"
            )

    if restricted_push:
        print("\n## Push Policy")
        for repo in restricted_push:
            print(f"- **{repo.path}** push={repo.push_policy}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="workspace root")
    parser.add_argument("--config", type=Path, help="explicit .ub-workspace/config.toml path")
    parser.add_argument("--changed-files", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    preliminary_root = args.root.expanduser().resolve() if args.root else Path.cwd().resolve()
    config = load_config(preliminary_root, args.config)
    root = workspace_root(args.root, config)
    if args.root is None and not config.path:
        config = load_config(root, args.config)
        root = workspace_root(args.root, config)

    repos = discover_repos(root, config)
    statuses = [summarize_repo(repo, root, config, args.changed_files) for repo in repos]

    if args.json:
        print(
            json.dumps(
                {
                    "root": str(root),
                    "config": asdict(config),
                    "repositories": [asdict(s) for s in statuses],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print_markdown(root, config, statuses)

    return 1 if any(status.error for status in statuses) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
