---
name: ub-pdf-reader
description: Search, inspect, render, and cite PDF documents for scientific and engineering work. Use when the user asks to answer questions from PDFs, inspect tables or figures, cite page-level evidence, compare text extraction with rendered pages, or review technical documents, papers, manuals, forms, reports, and standards in PDF form.
metadata:
  version: 0.1.0
  stability: stable
  domain: evidence
---

# UB PDF Reader

Use text extraction first, then render only the pages where visual layout could
change the answer.

## Workflow

1. Identify candidate PDFs from the user request and local files.
2. Search text before rendering pages.
3. Select a small set of pages with strong hits or layout-sensitive evidence.
4. Render pages when figures, diagrams, forms, merged-cell tables, checkboxes,
   scans, or visual hierarchy matter.
5. Answer with file path, page number, and reading mode: `text`, `image`, or
   `text+image`.

## Script Pattern

If this skill's scripts are present in the installed environment, prefer:

```sh
python3 scripts/pdf_probe.py path/to/file.pdf --pretty
python3 scripts/pdf_search.py --query "keyword phrase" path/to/*.pdf
python3 scripts/pdf_render_pages.py path/to/file.pdf --pages 3,7-8
```

If scripts are unavailable or missing dependencies, use the best local PDF tools
available and keep the same evidence discipline.

## Render Pages When

- The answer depends on a figure, diagram, screenshot, form, table, or layout.
- Extracted text is sparse, garbled, or likely from a scanned page.
- Search hits are near words such as figure, diagram, table, matrix, checklist,
  form, 그림, 도표, 흐름도, 표, 양식, or 체크리스트.
- The conclusion depends on position, grouping, arrows, boxes, or captions.

Do not render an entire PDF unless the user explicitly asks and the document is
small enough to inspect responsibly.

