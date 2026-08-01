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
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml
from soupsieve.util import SelectorSyntaxError

from collect_webpage import (
    SourceDocument,
    extract_with_readability,
    extract_with_trafilatura,
    prepare_html,
    read_source,
    render_markdown,
)


ARTICLE_HTML = """<!doctype html>
<html lang="en">
  <head>
    <title>Example article</title>
    <link rel="canonical" href="/articles/example">
    <meta name="author" content="Ada Example">
    <meta property="og:image" content="/images/cover.png">
  </head>
  <body>
    <nav class="remove-me">Navigation</nav>
    <article>
      <h1>Example article</h1>
      <p>This paragraph contains enough useful article text for deterministic extraction.</p>
      <p>A second paragraph makes the example representative of a small public article.</p>
      <a href="/references/source">Source reference</a>
      <pre><code class="language-python">print("hello")</code></pre>
    </article>
  </body>
</html>
"""


class CollectWebpageTests(unittest.TestCase):
    def test_prepare_html_removes_selector_and_resolves_urls(self) -> None:
        html, metadata, removed = prepare_html(
            ARTICLE_HTML,
            base_url="https://example.test/start",
            remove_selectors=[".remove-me"],
        )

        self.assertEqual(removed, 1)
        self.assertNotIn("Navigation", html)
        self.assertIn('href="https://example.test/references/source"', html)
        self.assertEqual(metadata["canonical_url"], "https://example.test/articles/example")
        self.assertEqual(metadata["title"], "Example article")
        self.assertEqual(metadata["author"], "Ada Example")

    def test_prepare_html_rejects_invalid_selector(self) -> None:
        with self.assertRaises(SelectorSyntaxError):
            prepare_html(ARTICLE_HTML, base_url=None, remove_selectors=["["])

    def test_both_engines_extract_article_content(self) -> None:
        html, metadata, _ = prepare_html(
            ARTICLE_HTML,
            base_url="https://example.test/start",
            remove_selectors=[".remove-me"],
        )

        trafilatura_body, _ = extract_with_trafilatura(
            html,
            base_url="https://example.test/start",
            generic_metadata=metadata,
        )
        readability_body, _ = extract_with_readability(html, generic_metadata=metadata)

        for body in (trafilatura_body, readability_body):
            self.assertIn("Example article", body)
            self.assertIn("useful article text", body)

    def test_render_markdown_preserves_source_metadata(self) -> None:
        raw = ARTICLE_HTML.encode()
        source = SourceDocument(
            requested_source="https://example.test/start",
            resolved_source="https://example.test/resolved",
            content_type="text/html",
            raw=raw,
            html=ARTICLE_HTML,
        )

        rendered = render_markdown(
            "Article body.",
            source=source,
            engine="trafilatura",
            metadata={"title": "Example article"},
        )
        _, frontmatter_text, body = rendered.split("---", 2)
        frontmatter = yaml.safe_load(frontmatter_text)

        self.assertEqual(frontmatter["source_url"], source.requested_source)
        self.assertEqual(frontmatter["resolved_url"], source.resolved_source)
        self.assertEqual(frontmatter["canonical_url"], source.resolved_source)
        self.assertEqual(frontmatter["content_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(frontmatter["engine"], "trafilatura")
        self.assertRegex(frontmatter["retrieved_at"], r"^\d{4}-\d{2}-\d{2}T.*Z$")
        self.assertIn("# Example article", body)
        self.assertIn("Article body.", body)

    def test_local_source_enforces_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.html"
            path.write_text(ARTICLE_HTML, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "file exceeds"):
                read_source(
                    str(path),
                    timeout=1,
                    max_bytes=10,
                    user_agent="ub-web-reader-test",
                )


if __name__ == "__main__":
    unittest.main()
