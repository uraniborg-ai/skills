#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4>=4.13,<5",
#   "markdownify>=1.2,<2",
#   "pyyaml>=6,<7",
#   "readability-lxml>=0.8.4.1,<0.9",
#   "trafilatura>=2.1,<3",
# ]
# ///
"""Collect a public HTML page as source-preserving Markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import yaml
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify
from readability import Document
from soupsieve.util import SelectorSyntaxError
from trafilatura import extract, extract_metadata


DEFAULT_USER_AGENT = "ub-web-reader/0.1 (+https://github.com/uraniborg-ai/skills)"


@dataclass(frozen=True)
class SourceDocument:
    requested_source: str
    resolved_source: str
    content_type: str
    raw: bytes
    html: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect a URL or local HTML file as source-preserving Markdown."
    )
    parser.add_argument("source", help="HTTP(S) URL or local HTML file")
    parser.add_argument(
        "--engine",
        choices=("trafilatura", "readability"),
        default="trafilatura",
        help="Article extraction engine (default: trafilatura)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Markdown output path, or - for stdout (default: -)",
    )
    parser.add_argument(
        "--save-html",
        metavar="PATH",
        help="Save the unmodified response body for provenance",
    )
    parser.add_argument(
        "--base-url",
        help="Base URL for resolving relative links, especially with local HTML",
    )
    parser.add_argument(
        "--remove-selector",
        action="append",
        default=[],
        metavar="CSS",
        help="Remove a confirmed boilerplate CSS selector; repeat as needed",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Network timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=20_000_000,
        help="Maximum response size (default: 20000000)",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="HTTP User-Agent header",
    )
    return parser


def read_source(
    source: str,
    *,
    timeout: float,
    max_bytes: int,
    user_agent: str,
) -> SourceDocument:
    parsed = urlparse(source)
    local_path = Path(source).expanduser()
    if parsed.scheme not in {"http", "https"} and local_path.exists():
        path = local_path.resolve()
        raw = path.read_bytes()
        if len(raw) > max_bytes:
            raise ValueError(f"file exceeds --max-bytes={max_bytes}")
        html = raw.decode("utf-8-sig", errors="replace")
        return SourceDocument(source, str(path), "text/html", raw, html)

    if parsed.scheme in {"http", "https"}:
        request = Request(
            source,
            headers={
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
                "User-Agent": user_agent,
            },
        )
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError(f"response exceeds --max-bytes={max_bytes}")
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            resolved = response.geturl()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            prefix = html[:1000].lower()
            if "<html" not in prefix and "<!doctype html" not in prefix:
                raise ValueError(f"unsupported content type: {content_type}")
        return SourceDocument(source, resolved, content_type, raw, html)

    if parsed.scheme:
        raise ValueError(f"unsupported source scheme: {parsed.scheme}")

    path = local_path.resolve()
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"file exceeds --max-bytes={max_bytes}")
    html = raw.decode("utf-8-sig", errors="replace")
    return SourceDocument(source, str(path), "text/html", raw, html)


def normalize_space(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def first_value(*values: Any) -> str | None:
    for value in values:
        normalized = normalize_space(value)
        if normalized:
            return normalized
    return None


def json_ld_articles(soup: BeautifulSoup) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        if not script.string:
            continue
        try:
            payload = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue
        candidates: list[Any] = []
        if isinstance(payload, dict):
            candidates.append(payload)
            graph = payload.get("@graph")
            if isinstance(graph, list):
                candidates.extend(graph)
        elif isinstance(payload, list):
            candidates.extend(payload)
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            kinds = candidate.get("@type", [])
            if isinstance(kinds, str):
                kinds = [kinds]
            if any(kind in {"Article", "BlogPosting", "NewsArticle"} for kind in kinds):
                articles.append(candidate)
    return articles


def author_name(value: Any) -> str | None:
    if isinstance(value, str):
        return normalize_space(value)
    if isinstance(value, dict):
        return normalize_space(value.get("name"))
    if isinstance(value, list):
        names = [author_name(item) for item in value]
        return ", ".join(name for name in names if name) or None
    return None


def page_metadata(soup: BeautifulSoup, base_url: str | None) -> dict[str, Any]:
    meta: dict[str, list[str]] = {}
    for element in soup.find_all("meta"):
        key = element.get("property") or element.get("name")
        value = element.get("content")
        if key and value:
            meta.setdefault(str(key).lower(), []).append(str(value))

    articles = json_ld_articles(soup)
    article = articles[0] if articles else {}
    canonical_element = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical = canonical_element.get("href") if isinstance(canonical_element, Tag) else None
    title_element = soup.find("title")
    tags = [normalize_space(value) for value in meta.get("article:tag", [])]
    keywords = article.get("keywords")
    if not tags and isinstance(keywords, str):
        tags = [normalize_space(value) for value in keywords.split(",")]
    tags = [tag for tag in tags if tag]

    result: dict[str, Any] = {
        "title": first_value(
            meta.get("og:title", [None])[0],
            meta.get("twitter:title", [None])[0],
            article.get("headline"),
            title_element.get_text(" ", strip=True) if title_element else None,
        ),
        "author": first_value(
            meta.get("article:author", [None])[0],
            meta.get("author", [None])[0],
            author_name(article.get("author")),
        ),
        "date": first_value(
            meta.get("article:published_time", [None])[0],
            meta.get("date", [None])[0],
            article.get("datePublished"),
        ),
        "description": first_value(
            meta.get("og:description", [None])[0],
            meta.get("description", [None])[0],
            article.get("description"),
        ),
        "canonical_url": urljoin(base_url, str(canonical)) if canonical and base_url else canonical,
        "image": first_value(
            meta.get("og:image", [None])[0],
            article.get("image", {}).get("url")
            if isinstance(article.get("image"), dict)
            else article.get("image"),
        ),
        "language": normalize_space(soup.html.get("lang")) if soup.html else None,
        "tags": tags,
    }
    return {key: value for key, value in result.items() if value not in (None, [], "")}


def prepare_html(
    html: str,
    *,
    base_url: str | None,
    remove_selectors: list[str],
) -> tuple[str, dict[str, Any], int]:
    soup = BeautifulSoup(html, "html.parser")
    removed = 0
    for selector in remove_selectors:
        matches = soup.select(selector)
        removed += len(matches)
        for element in matches:
            element.decompose()

    if base_url:
        for element in soup.find_all(href=True):
            element["href"] = urljoin(base_url, str(element["href"]))
        for element in soup.find_all(src=True):
            element["src"] = urljoin(base_url, str(element["src"]))

    return str(soup), page_metadata(soup, base_url), removed


def code_language(element: Tag) -> str | None:
    candidates: list[str] = []
    for node in (element, element.find("code")):
        if not isinstance(node, Tag):
            continue
        value = node.get("data-language")
        if value:
            candidates.append(str(value))
        candidates.extend(str(item) for item in node.get("class", []))
    for candidate in candidates:
        match = re.search(r"(?:language-|lang-|highlight-source-)?([A-Za-z0-9_+.#-]+)$", candidate)
        if match:
            language = match.group(1)
            if language not in {"astro-code", "github-light", "line"}:
                return language
    return None


def extract_with_trafilatura(
    html: str,
    *,
    base_url: str | None,
    generic_metadata: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    body = extract(
        html,
        url=base_url,
        output_format="markdown",
        with_metadata=False,
        include_comments=False,
        include_links=True,
        include_images=True,
        include_formatting=True,
    )
    if not body:
        raise ValueError("Trafilatura did not find article content")

    metadata = dict(generic_metadata)
    extracted = extract_metadata(html, default_url=base_url)
    if extracted:
        values = extracted.as_dict()
        mapping = {
            "title": "title",
            "author": "author",
            "date": "date",
            "description": "description",
            "url": "canonical_url",
            "image": "image",
            "language": "language",
            "tags": "tags",
        }
        for source_key, target_key in mapping.items():
            value = values.get(source_key)
            if value not in (None, [], "") and metadata.get(target_key) in (None, [], ""):
                metadata[target_key] = value
    return body, metadata


def extract_with_readability(
    html: str,
    *,
    generic_metadata: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    document = Document(html)
    summary = document.summary(html_partial=True, keep_all_images=True)
    body = markdownify(
        summary,
        heading_style="ATX",
        bullets="-",
        code_language_callback=code_language,
    ).strip()
    if not body:
        raise ValueError("readability-lxml did not find article content")
    metadata = dict(generic_metadata)
    metadata["title"] = first_value(metadata.get("title"), document.short_title())
    author = normalize_space(document.author())
    if author and author != "[no-author]":
        metadata["author"] = author
    return body, metadata


def ensure_h1(body: str, title: str | None) -> str:
    if not title or re.search(r"(?m)^#\s+\S", body):
        return body.strip()
    return f"# {title}\n\n{body.strip()}"


def render_markdown(
    body: str,
    *,
    source: SourceDocument,
    engine: str,
    metadata: dict[str, Any],
) -> str:
    title = normalize_space(metadata.get("title"))
    body = ensure_h1(body, title)
    frontmatter: dict[str, Any] = {}
    for key in ("title", "author", "date", "description", "tags", "language", "image"):
        value = metadata.get(key)
        if value not in (None, [], ""):
            frontmatter[key] = value
    frontmatter.update(
        {
            "source_url": source.requested_source,
            "resolved_url": source.resolved_source,
            "canonical_url": metadata.get("canonical_url") or source.resolved_source,
            "retrieved_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "engine": engine,
            "content_type": source.content_type,
            "content_sha256": hashlib.sha256(source.raw).hexdigest(),
        }
    )
    yaml_text = yaml.safe_dump(
        frontmatter,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    ).strip()
    return f"---\n{yaml_text}\n---\n\n{body.strip()}\n"


def write_file(path_value: str, data: str | bytes) -> None:
    path = Path(path_value).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")

    try:
        source = read_source(
            args.source,
            timeout=args.timeout,
            max_bytes=args.max_bytes,
            user_agent=args.user_agent,
        )
        base_url = args.base_url or (
            source.resolved_source
            if urlparse(source.resolved_source).scheme in {"http", "https"}
            else None
        )
        prepared_html, generic_metadata, removed = prepare_html(
            source.html,
            base_url=base_url,
            remove_selectors=args.remove_selector,
        )
        if args.engine == "trafilatura":
            body, metadata = extract_with_trafilatura(
                prepared_html,
                base_url=base_url,
                generic_metadata=generic_metadata,
            )
        else:
            body, metadata = extract_with_readability(
                prepared_html,
                generic_metadata=generic_metadata,
            )
        output = render_markdown(
            body,
            source=source,
            engine=args.engine,
            metadata=metadata,
        )
        if args.save_html:
            write_file(args.save_html, source.raw)
        if args.output == "-":
            sys.stdout.write(output)
        else:
            write_file(args.output, output)
        headings = len(re.findall(r"(?m)^#{1,6}\s+", output))
        code_blocks = len(re.findall(r"(?m)^```", body)) // 2
        print(
            f"ok: engine={args.engine} chars={len(body)} headings={headings} "
            f"code_blocks={code_blocks} removed={removed}",
            file=sys.stderr,
        )
        return 0
    except (HTTPError, URLError, OSError, ValueError, SelectorSyntaxError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
