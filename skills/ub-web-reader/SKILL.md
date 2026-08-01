---
name: ub-web-reader
description: Collect public web pages, blog posts, articles, and technical documentation as source-preserving Markdown. Use when the user provides webpage URLs; asks to read, archive, summarize, cite, or compare web content; needs article metadata and raw-HTML provenance; or needs to compare Trafilatura extraction with readability-lxml plus markdownify for code-heavy pages.
---

# UB Web Reader

Collect a page before summarizing or analyzing it. Preserve enough provenance
to reproduce the extraction and inspect the source later.

## Workflow

1. Collect static HTML with Trafilatura by default:

   ```sh
   uv run --script skills/ub-web-reader/scripts/collect_webpage.py URL \
     -o article.md --save-html article.html
   ```

2. Inspect the title, first and last sections, headings, links, images, and code
   blocks. Check for navigation, related-content cards, ads, cookie notices, or
   missing article sections before relying on the Markdown.
3. Rerun code-heavy or structurally damaged pages with the readability engine:

   ```sh
   uv run --script skills/ub-web-reader/scripts/collect_webpage.py URL \
     --engine readability -o article-readability.md
   ```

4. Remove confirmed boilerplate with repeatable CSS selectors. Do not guess at
   selectors without inspecting the page or extracted output:

   ```sh
   uv run --script skills/ub-web-reader/scripts/collect_webpage.py URL \
     --remove-selector ".not-prose" -o article.md
   ```

5. Report the selected engine and any known omissions when summarizing or
   citing the result. Do not silently combine different engine outputs.

## Engine Choice

- Use `trafilatura` for the default article extraction, metadata, and broad
  boilerplate removal.
- Use `readability` when code blocks, their language labels, or fine Markdown
  structure matter more than aggressive article extraction.
- Run both and compare when the page is high-value or either output looks
  incomplete.
- Use a browser-capable workflow when the downloaded HTML lacks content that is
  visibly rendered by JavaScript. Do not treat a sparse static response as a
  complete capture.

## Provenance

The script writes YAML frontmatter with the requested and resolved URLs,
canonical URL when available, retrieval time, extraction engine, content type,
and SHA-256 of the raw response. Use `--save-html` when reproducibility or later
verification matters.

Collect public pages without bypassing authentication, paywalls, access
controls, or site restrictions. Route PDFs to `$ub-pdf-reader` and YouTube URLs
to `$ub-youtube`.
