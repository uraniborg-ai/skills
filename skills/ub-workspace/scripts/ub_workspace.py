#!/usr/bin/env python3
"""Bootstrap, inspect, and conservatively synchronize a docs-led workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
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
class Project:
    name: str
    repo: str
    path: str
    branch: str = ""
    required: bool = True


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


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


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
    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and child.name != "proposals" and (child / ".git").exists()
    )


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def docs_path(args: argparse.Namespace, root: Path) -> Path:
    return args.docs_path.expanduser().resolve() if args.docs_path else root / "docs"


def proposals_dir(docs: Path) -> Path:
    return docs / "proposals"


def manifest_path(docs: Path) -> Path:
    return docs / "workspace.toml"


def workspace_proposal_files(proposals: Path) -> list[Path]:
    if not proposals.exists():
        return []
    return sorted(proposals.glob("001-*.md"))


def load_workspace_manifest(docs: Path) -> tuple[Path, list[Project], list[str]]:
    manifest = manifest_path(docs)
    errors: list[str] = []
    if not manifest.exists():
        return manifest, [], [f"missing workspace manifest: {manifest}"]

    try:
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        return manifest, [], [f"{manifest}: invalid TOML: {exc}"]

    version = data.get("version")
    if version != 1:
        errors.append(f"{manifest}: version must be 1")

    projects_data = data.get("projects")
    if not isinstance(projects_data, list):
        errors.append(f"{manifest}: missing [[projects]] entries")
        projects_data = []

    allowed_top_keys = {"version", "workspace", "projects"}
    for key in sorted(set(data) - allowed_top_keys):
        errors.append(f"{manifest}: unknown top-level key `{key}`")

    workspace = data.get("workspace", {})
    if workspace is not None and not isinstance(workspace, dict):
        errors.append(f"{manifest}: [workspace] must be a table")

    projects: list[Project] = []
    allowed_project_keys = {"name", "repo", "path", "branch", "required"}
    for index, item in enumerate(projects_data, start=1):
        label = f"project #{index}"
        if not isinstance(item, dict):
            errors.append(f"{label}: project entry must be a table")
            continue
        name = item.get("name", "")
        repo = item.get("repo", "")
        path = item.get("path", "")
        branch = item.get("branch", "")
        required = item.get("required", True)

        for key in sorted(set(item) - allowed_project_keys):
            errors.append(f"{name or label}: unknown project key `{key}`")
        if not isinstance(name, str):
            errors.append(f"{label}: name must be a string")
            name = ""
        if not isinstance(repo, str):
            errors.append(f"{name or label}: repo must be a string")
            repo = ""
        if not isinstance(path, str):
            errors.append(f"{name or label}: path must be a string")
            path = ""
        if not isinstance(branch, str):
            errors.append(f"{name or label}: branch must be a string")
            branch = ""
        if not isinstance(required, bool):
            errors.append(f"{name or label}: required must be a boolean")
            required = True

        projects.append(
            Project(
                name=name.strip(),
                repo=repo.strip(),
                path=path.strip(),
                branch=branch.strip(),
                required=required,
            )
        )

    errors.extend(validate_projects(projects))
    return manifest, projects, errors


def validate_projects(projects: list[Project]) -> list[str]:
    errors: list[str] = []
    seen_names: set[str] = set()
    seen_paths: set[str] = set()
    if not projects:
        return ["workspace manifest declares no projects"]
    for index, project in enumerate(projects, start=1):
        label = project.name or f"project #{index}"
        if not project.name:
            errors.append(f"{label}: missing name")
        if not project.repo:
            errors.append(f"{label}: missing repo")
        if not project.path:
            errors.append(f"{label}: missing path")
        if project.path.startswith("/") or ".." in Path(project.path).parts:
            errors.append(f"{label}: path must be workspace-relative and must not contain `..`")
        if project.name in seen_names:
            errors.append(f"{label}: duplicate name")
        if project.path in seen_paths:
            errors.append(f"{label}: duplicate path {project.path}")
        seen_names.add(project.name)
        seen_paths.add(project.path)
    return errors


def project_paths(root: Path, projects: list[Project]) -> list[Path]:
    return [root / project.path for project in projects]


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
    if not repo.exists():
        state.relation = "missing"
        state.detail = "declared project is not cloned"
        return state

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
    if state.relation in {"missing", "detached", "no_upstream", "unknown"}:
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
        or state.relation
        in {"missing", "ahead", "behind", "diverged", "no_upstream", "detached", "unknown"}
        or state.recent_commits
        or state.detail
    )


def print_status(states: list[RepoState], include_quiet: bool, report_only: bool = False) -> None:
    dirty = [s for s in states if s.dirty_count]
    attention = [
        s
        for s in states
        if s.relation
        in {"missing", "ahead", "behind", "diverged", "no_upstream", "detached", "unknown"}
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
        "missing",
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


def print_projects(projects: list[Project], root: Path) -> None:
    print("# Workspace Projects\n")
    for project in projects:
        marker = "present" if (root / project.path).exists() else "missing"
        branch = f" branch={project.branch}" if project.branch else ""
        required = "required" if project.required else "optional"
        print(f"- **{project.name}** `{project.path}` {marker}, {required}{branch}")
        print(f"  - {project.repo}")


def clone_project(root: Path, project: Project, dry_run: bool) -> tuple[str, str]:
    target = root / project.path
    if target.exists():
        return "present", f"{project.name}: {project.path} already exists"
    if dry_run:
        return "would_clone", f"{project.name}: would clone {project.repo} -> {project.path}"

    args = ["git", "clone", project.repo, str(target)]
    if project.branch:
        args[2:2] = ["--branch", project.branch]
    proc = run(*args)
    if proc.returncode != 0:
        return "failed", f"{project.name}: {clean_output(proc)}"
    return "cloned", f"{project.name}: cloned to {project.path}"


def ensure_docs_repo(args: argparse.Namespace, root: Path) -> tuple[Path, list[str]]:
    docs = docs_path(args, root)
    messages: list[str] = []
    if (docs / ".git").exists():
        return docs, messages
    if docs.exists():
        messages.append(f"{docs} exists but is not a Git repository")
        return docs, messages
    if not args.docs_repo:
        messages.append("missing docs repo; ask the user for the docs repository URL")
        return docs, messages
    if args.dry_run:
        messages.append(f"would clone docs repo {args.docs_repo} -> {docs}")
        return docs, messages
    proc = run("git", "clone", args.docs_repo, str(docs))
    if proc.returncode != 0:
        messages.append(f"failed to clone docs repo: {clean_output(proc)}")
    else:
        messages.append(f"cloned docs repo: {docs}")
    return docs, messages


def remote_url(repo: Path) -> str:
    proc = git(repo, "remote", "get-url", "origin")
    return proc.stdout.strip() if proc.returncode == 0 else ""


def init_workspace_proposal(root: Path, docs: Path) -> tuple[bool, str]:
    manifest = manifest_path(docs)
    if manifest.exists():
        return False, f"{manifest} already exists"
    if not (docs / ".git").exists():
        return False, f"{docs} is not a Git repository"

    proposals = proposals_dir(docs)
    proposal_files = workspace_proposal_files(proposals)

    rows = []
    for repo in discover_repos(root):
        if repo.resolve() == docs.resolve():
            continue
        origin = remote_url(repo)
        if not origin:
            continue
        rows.append(
            {
                "name": repo.name,
                "repo": origin,
                "path": display_path(repo, root),
                "branch": current_branch(repo) or "main",
            }
        )
    if not rows:
        return False, "no sibling Git repositories with origin remotes found"

    manifest_lines = [
        "version = 1",
        "",
        "[workspace]",
        f"name = {toml_string(root.name)}",
        "",
    ]
    for row in rows:
        manifest_lines.extend(
            [
                "[[projects]]",
                f"name = {toml_string(row['name'])}",
                f"repo = {toml_string(row['repo'])}",
                f"path = {toml_string(row['path'])}",
                f"branch = {toml_string(row['branch'])}",
                "required = true",
                "",
            ]
        )

    proposal_lines = [
        "---",
        "status: draft",
        "---",
        "",
        "# Workspace Projects",
        "",
        "## Decision",
        "",
        "This workspace is governed by `docs/workspace.toml`. The manifest is",
        "the source of truth for child project clone URLs, workspace-relative",
        "paths, preferred branches, and required/optional status.",
        "",
        "The root `docs` repository itself is not listed as a child project.",
        "",
        "## Non-Goals",
        "",
        "- Project-specific decisions stay inside each project's own proposal system.",
        "",
        "## Acceptance Scenarios",
        "",
        "- A new workspace can clone the docs repository and recover the declared projects.",
        "- Workspace status and sync operate on the manifest-declared projects.",
    ]

    manifest.write_text("\n".join(manifest_lines).rstrip() + "\n", encoding="utf-8")

    messages = [f"created {manifest}"]
    if proposal_files:
        messages.append(
            "001 workspace proposal already exists; left unchanged: "
            + ", ".join(p.name for p in proposal_files)
        )
    else:
        proposals.mkdir(parents=True, exist_ok=True)
        target = proposals / "001-workspace-projects.md"
        target.write_text("\n".join(proposal_lines) + "\n", encoding="utf-8")
        messages.append(f"created {target}")
    return True, "; ".join(messages)


def load_repos(args: argparse.Namespace, root: Path) -> tuple[list[Path], list[str]]:
    if args.repo:
        return [repo.expanduser().resolve() for repo in args.repo], []
    if args.discover:
        return discover_repos(root), []

    manifest, projects, errors = load_workspace_manifest(docs_path(args, root))
    if errors:
        return [], errors
    return project_paths(root, projects), [f"using {manifest}"]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--root",
            type=Path,
            default=Path.cwd().parent,
            help="workspace root containing the docs repo and project repos",
        )
        p.add_argument("--docs-path", type=Path, help="docs repo path")

    for name in ("status", "report", "sync"):
        p = sub.add_parser(name)
        add_common(p)
        p.add_argument(
            "--repo", action="append", type=Path, help="explicit repo path; may be repeated"
        )
        p.add_argument(
            "--discover",
            action="store_true",
            help="scan immediate sibling Git repositories instead of using docs/workspace.toml",
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

    p = sub.add_parser("projects")
    add_common(p)
    p.add_argument("--json", action="store_true", help="emit JSON")

    p = sub.add_parser("validate")
    add_common(p)

    p = sub.add_parser("validate-proposals")
    add_common(p)

    p = sub.add_parser("init-proposals")
    add_common(p)

    p = sub.add_parser("bootstrap")
    add_common(p)
    p.add_argument("--docs-repo", help="URL to clone when the docs repo is missing")
    p.add_argument("--dry-run", action="store_true", help="show clone actions without writing")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return parser.parse_args(argv)


def print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"error: {error}", file=sys.stderr)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = args.root.expanduser().resolve()

    if args.command == "init-proposals":
        ok, message = init_workspace_proposal(root, docs_path(args, root))
        print(message)
        return 0 if ok else 1

    if args.command in {"validate", "validate-proposals"}:
        manifest, projects, errors = load_workspace_manifest(docs_path(args, root))
        if errors:
            print_errors(errors)
            return 1
        print(f"ok: {manifest} declares {len(projects)} projects")
        return 0

    if args.command == "projects":
        manifest, projects, errors = load_workspace_manifest(docs_path(args, root))
        if errors:
            print_errors(errors)
            return 1
        if args.json:
            print(json.dumps([asdict(project) for project in projects], indent=2, ensure_ascii=False))
        else:
            print(f"> Source: {manifest}\n")
            print_projects(projects, root)
        return 0

    if args.command == "bootstrap":
        docs, messages = ensure_docs_repo(args, root)
        manifest, projects, errors = load_workspace_manifest(docs)
        actions = []
        if not errors:
            for project in projects:
                status, detail = clone_project(root, project, args.dry_run)
                actions.append({"project": project.name, "status": status, "detail": detail})
        if args.json:
            print(
                json.dumps(
                    {
                        "docs": str(docs),
                        "messages": messages,
                        "manifest": str(manifest),
                        "errors": errors,
                        "actions": actions,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            print("# Workspace Bootstrap\n")
            for message in messages:
                print(f"- {message}")
            if errors:
                print_errors(errors)
            for action in actions:
                print(f"- {action['status']}: {action['detail']}")
        return 1 if errors or any(action["status"] == "failed" for action in actions) else 0

    repos, messages = load_repos(args, root)
    if messages and repos:
        for message in messages:
            print(f"> {message}", file=sys.stderr)
    if not repos:
        print_errors(messages or ["no repositories selected"])
        return 1

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
