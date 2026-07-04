#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.32",
# ]
# ///
"""Fetch Korean interest-rate series from the Bank of Korea ECOS API."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests import RequestException


ECOS_BASE_URL = "https://ecos.bok.or.kr/api/StatisticSearch"


@dataclass(frozen=True)
class RateSeries:
    stat_code: str
    item_code: str
    name: str


SERIES = {
    "base-rate": RateSeries("722Y001", "0101000", "한국은행 기준금리"),
    "treasury-3y": RateSeries("817Y002", "010200000", "국고채(3년)"),
    "treasury-10y": RateSeries("817Y002", "010210000", "국고채(10년)"),
    "cd-91d": RateSeries("817Y002", "010502000", "CD(91일)"),
}

FIELDNAMES = [
    "source",
    "fetched_at",
    "timezone",
    "frequency",
    "unit",
    "series_name",
    "series_code",
    "date",
    "value",
]


def compact_date(value: str) -> str:
    return value.replace("-", "")


def format_date(value: str) -> str:
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
    return value


def parse_number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def ecos_url(api_key: str, series: RateSeries, start: str, end: str) -> str:
    count = "10" if api_key == "sample" else "100000"
    return "/".join(
        [
            ECOS_BASE_URL,
            api_key,
            "json",
            "kr",
            "1",
            count,
            series.stat_code,
            "D",
            compact_date(start),
            compact_date(end),
            series.item_code,
        ]
    )


def fetch_series(
    api_key: str,
    slug: str,
    series: RateSeries,
    start: str,
    end: str,
    fetched_at: str,
) -> list[dict[str, Any]]:
    try:
        response = requests.get(ecos_url(api_key, series, start, end), timeout=30)
        response.raise_for_status()
        payload = response.json()
    except RequestException as error:
        raise SystemExit(
            f"ECOS request failed for {slug}. Check network access and the ECOS service status. "
            f"Original error type: {type(error).__name__}"
        ) from None
    except ValueError as error:
        raise SystemExit(
            f"ECOS returned a non-JSON response for {slug}. "
            f"Original error type: {type(error).__name__}"
        ) from None

    if "RESULT" in payload:
        result = payload["RESULT"]
        code = result.get("CODE", "UNKNOWN")
        message = result.get("MESSAGE", "Unknown ECOS response")
        if code == "INFO-200":
            return []
        raise SystemExit(f"ECOS request failed for {slug}: {code} {message}")

    rows = payload.get("StatisticSearch", {}).get("row", [])
    output = []
    for row in rows:
        output.append(
            {
                "source": "Bank of Korea ECOS",
                "fetched_at": fetched_at,
                "timezone": "Asia/Seoul",
                "frequency": "daily",
                "unit": row.get("UNIT_NAME") or "annual percent",
                "series_name": row.get("ITEM_NAME1") or series.name,
                "series_code": slug,
                "date": format_date(row.get("TIME", "")),
                "value": parse_number(row.get("DATA_VALUE")),
            }
        )
    return output


def write_output(rows: list[dict[str, Any]], output_format: str, output: str | None) -> None:
    if output_format == "json":
        text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
        if output:
            Path(output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return

    buffer = sys.stdout if output is None else open(output, "w", encoding="utf-8", newline="")
    try:
        writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output is not None:
            buffer.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="end date, YYYY-MM-DD")
    parser.add_argument(
        "--series",
        nargs="+",
        choices=sorted(SERIES),
        default=sorted(SERIES),
        help="series to fetch; defaults to all supported series",
    )
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("-o", "--output", help="optional output path")
    return parser.parse_args()


def main() -> int:
    api_key = os.environ.get("BOK_ECOS_API_KEY")
    if not api_key:
        raise SystemExit("BOK_ECOS_API_KEY is required to fetch Bank of Korea ECOS data.")

    args = parse_args()
    fetched_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for slug in args.series:
        rows.extend(fetch_series(api_key, slug, SERIES[slug], args.start, args.end, fetched_at))
    write_output(rows, args.format, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
