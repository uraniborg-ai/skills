#!/usr/bin/env python3
"""Inspect and conservatively synchronize a workspace of Git repositories."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class Commit:
    sha: str
    date: str
    relative: str
    subject: str


@dataclass
class RepoState:
    repo: str
    path: str
    branch: str = ""
    upstream: str = ""
    dirty_count: int = 0
    dirty_files: list[str] | None = None
    ahead: int | None = None
    behind: int | None = None
    relation: str = "unknown"
    last_commit: Commit | None = None
    recent_commits: list[Commit] | None = None
    sync_status: str = ""
    detail: str = ""


def git(repo: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def clean_output(proc: subprocess.CompletedProcess[str] | subprocess.CalledProcessError) -> str:
    return ((getattr(proc, "stdout", "") or "") + (getattr(proc, "stderr", "") or "")).strip()


def discover_repos(root: Path) -> list[Path]:
    return sorted(child for child in root.iterdir() if child.is_dir() and (child / ".git").exists())


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def current_branch(repo: Path) -> str:
    return git(repo, "branch", "--show-current").stdout.strip()


def upstream_ref(repo: Path) -> str:
    proc = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    return proc.stdout.strip() if proc.returncode == 0 else ""


def dirty_files(repo: Path, limit: int) -> tuple[int, list[str]]:
    proc = git(repo, "status", "--porcelain=v1")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    return len(lines), lines[:limit]


def parse_commit_line(line: str) -> Commit | None:
    parts = line.split("\t", 3)
    if len(parts) != 4:
        return None
    return Commit(sha=parts[0], date=parts[1], relative=parts[2], subject=parts[3])


def commits(repo: Path, max_count: int, since_days: int | None = None) -> list[Commit]:
    args = ["log", f"--max-count={max_count}", "--date=short", "--format=%h%x09%ad%x09%cr%x09%s"]
    if since_days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=since_days)
        args.insert(1, f"--since={since.isoformat()}")
    proc = git(repo, *args)
    if proc.returncode != 0:
        return []
    parsed = [parse_commit_line(line) for line in proc.stdout.splitlines()]
    return [commit for commit in parsed if commit is not None]


def ahead_behind(repo: Path, upstream: str) -> tuple[int | None, int | None]:
    proc = git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
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


def summarize_repo(
    repo: Path, root: Path, days: int, commits_limit: int, changed_limit: int
) -> RepoState:
    state = RepoState(
        repo=repo.name, path=display_path(repo, root), dirty_files=[], recent_commits=[]
    )
    inside = git(repo, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0:
        state.detail = clean_output(inside) or "not a Git worktree"
        return state

    state.branch = current_branch(repo)
    state.upstream = upstream_ref(repo)
    state.dirty_count, state.dirty_files = dirty_files(repo, changed_limit)
    state.last_commit = next(iter(commits(repo, 1)), None)
    state.recent_commits = commits(repo, commits_limit, since_days=days)

    if not state.branch:
        state.relation = "detached"
        state.detail = "detached HEAD or no current branch"
    elif not state.upstream:
        state.relation = "no_upstream"
        state.detail = "current branch has no configured upstream"
    else:
        state.ahead, state.behind = ahead_behind(repo, state.upstream)
        state.relation = relation(state.ahead, state.behind)
    return state


def fetch_upstream(repo: Path, upstream: str) -> tuple[bool, str]:
    remote = upstream.split("/", 1)[0] if "/" in upstream else ""
    args = ["fetch", "--prune", remote] if remote else ["fetch", "--all", "--prune"]
    proc = git(repo, *args)
    return proc.returncode == 0, clean_output(proc)


def fast_forward_state(repo: Path, upstream: str) -> str:
    head = git(repo, "rev-parse", "HEAD", check=True).stdout.strip()
    upstream_sha = git(repo, "rev-parse", upstream, check=True).stdout.strip()
    merge_base = git(repo, "merge-base", "HEAD", upstream, check=True).stdout.strip()
    if head == upstream_sha:
        return "up_to_date"
    if merge_base == head:
        return "can_fast_forward"
    if merge_base == upstream_sha:
        return "local_ahead"
    return "diverged"


def sync_repo(repo: Path, root: Path, args: argparse.Namespace) -> RepoState:
    state = summarize_repo(repo, root, args.days, args.commits, args.changed_files)
    if state.relation in {"detached", "no_upstream", "unknown"}:
        state.sync_status = state.relation
        return state

    ok, detail = fetch_upstream(repo, state.upstream)
    if not ok:
        state.sync_status = "failed"
        state.detail = f"fetch failed: {detail}"
        return state

    state.ahead, state.behind = ahead_behind(repo, state.upstream)
    state.relation = relation(state.ahead, state.behind)

    try:
        ff_state = fast_forward_state(repo, state.upstream)
    except subprocess.CalledProcessError as exc:
        state.sync_status = "failed"
        state.detail = f"comparison failed: {clean_output(exc)}"
        return state

    if ff_state == "up_to_date":
        state.sync_status = "up_to_date"
        state.detail = "matches upstream"
    elif ff_state == "local_ahead":
        state.sync_status = "local_ahead"
        state.detail = "local branch has commits not on upstream"
    elif ff_state == "diverged":
        state.sync_status = "diverged"
        state.detail = "local and upstream both have unique commits"
    elif state.dirty_count and not args.include_dirty:
        state.sync_status = "dirty_skipped"
        state.detail = "fast-forward available, but worktree has local changes"
    elif args.dry_run:
        state.sync_status = "would_fast_forward"
        state.detail = "fast-forward available; dry run did not pull"
    else:
        proc = git(repo, "pull", "--ff-only")
        if proc.returncode != 0:
            state.sync_status = "failed"
            state.detail = f"pull --ff-only failed: {clean_output(proc)}"
        else:
            state.sync_status = "fast_forwarded"
            state.detail = clean_output(proc) or "pulled with --ff-only"
            state.ahead, state.behind = ahead_behind(repo, state.upstream)
            state.relation = relation(state.ahead, state.behind)
    return state


def interesting(state: RepoState) -> bool:
    return bool(
        state.dirty_count
        or state.relation in {"ahead", "behind", "diverged", "no_upstream", "detached", "unknown"}
        or state.recent_commits
        or state.detail
    )


def print_status(states: list[RepoState], include_quiet: bool, report_only: bool = False) -> None:
    dirty = [s for s in states if s.dirty_count]
    attention = [
        s
        for s in states
        if s.relation in {"ahead", "behind", "diverged", "no_upstream", "detached", "unknown"}
    ]
    recent = [s for s in states if s.recent_commits]
    quiet = [s for s in states if not interesting(s)]

    title = "Workspace Recent Work" if report_only else "Workspace Status"
    print(f"# {title}\n")
    print(f"- repositories scanned: {len(states)}")
    print(f"- with local changes: {len(dirty)}")
    print(f"- needing branch attention: {len(attention)}")
    print(f"- with recent commits: {len(recent)}")
    print(f"- quiet: {len(quiet)}")
    print(
        "\n> Status uses local remote-tracking refs. Run `sync --dry-run` when fresh remote data matters."
    )

    if dirty and not report_only:
        print("\n## Local Changes")
        for state in dirty:
            print(f"- **{state.repo}** `{state.branch or 'HEAD'}` dirty={state.dirty_count}")
            for path in state.dirty_files or []:
                print(f"  - `{path}`")

    if attention and not report_only:
        print("\n## Branch Attention")
        for state in attention:
            upstream = f" -> `{state.upstream}`" if state.upstream else ""
            counts = ""
            if state.ahead is not None and state.behind is not None:
                counts = f" ahead={state.ahead} behind={state.behind}"
            detail = f": {state.detail}" if state.detail else ""
            print(
                f"- **{state.repo}** `{state.branch or 'HEAD'}`{upstream}: {state.relation}{counts}{detail}"
            )

    if recent:
        print("\n## Recent Work")
        for state in recent:
            print(f"- **{state.repo}**")
            for commit in state.recent_commits or []:
                print(f"  - `{commit.sha}` {commit.relative}: {commit.subject}")

    if include_quiet and quiet and not report_only:
        print("\n## Quiet")
        for state in quiet:
            last = (
                f", last: {state.last_commit.relative} - {state.last_commit.subject}"
                if state.last_commit
                else ""
            )
            print(f"- **{state.repo}** `{state.branch}`{last}")


def print_sync(states: list[RepoState]) -> None:
    order = [
        "fast_forwarded",
        "would_fast_forward",
        "up_to_date",
        "dirty_skipped",
        "local_ahead",
        "diverged",
        "no_upstream",
        "detached",
        "failed",
    ]
    groups: dict[str, list[RepoState]] = {}
    for state in states:
        groups.setdefault(state.sync_status or state.relation, []).append(state)

    print("# Workspace Sync\n")
    for status in order:
        items = groups.get(status, [])
        if not items:
            continue
        print(f"## {status.replace('_', ' ').title()}")
        for item in items:
            counts = ""
            if item.ahead is not None and item.behind is not None:
                counts = f" ahead={item.ahead} behind={item.behind}"
            dirty = f" dirty={item.dirty_count}" if item.dirty_count else ""
            upstream = f" -> {item.upstream}" if item.upstream else ""
            detail = f": {item.detail}" if item.detail else ""
            print(f"- **{item.repo}** `{item.branch or 'HEAD'}{upstream}`{counts}{dirty}{detail}")
        print()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "report", "sync"):
        p = sub.add_parser(name)
        p.add_argument(
            "--root",
            type=Path,
            default=Path.cwd().parent,
            help="workspace whose immediate children are Git repos",
        )
        p.add_argument(
            "--repo", action="append", type=Path, help="explicit repo path; may be repeated"
        )
        p.add_argument("--days", type=int, default=7, help="recent commit window")
        p.add_argument("--commits", type=int, default=3, help="maximum recent commits per repo")
        p.add_argument("--changed-files", type=int, default=8, help="maximum dirty paths per repo")
        p.add_argument(
            "--include-quiet", action="store_true", help="include quiet repos in status output"
        )
        p.add_argument("--json", action="store_true", help="emit JSON")
        if name == "sync":
            p.add_argument(
                "--dry-run", action="store_true", help="fetch and compare, but do not pull"
            )
            p.add_argument(
                "--include-dirty",
                action="store_true",
                help="allow ff-only pull with a dirty worktree",
            )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = args.root.expanduser().resolve()
    repos = (
        [repo.expanduser().resolve() for repo in args.repo] if args.repo else discover_repos(root)
    )

    if args.command == "sync":
        states = [sync_repo(repo, root, args) for repo in repos]
        if args.json:
            print(json.dumps([asdict(state) for state in states], indent=2, ensure_ascii=False))
        else:
            print_sync(states)
        return 1 if any(s.sync_status in {"failed", "diverged"} for s in states) else 0

    states = [
        summarize_repo(repo, root, args.days, args.commits, args.changed_files) for repo in repos
    ]
    if args.json:
        print(json.dumps([asdict(state) for state in states], indent=2, ensure_ascii=False))
    else:
        print_status(states, include_quiet=args.include_quiet, report_only=args.command == "report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
