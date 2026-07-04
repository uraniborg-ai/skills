#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pykrx>=1.0.51",
# ]
# ///
"""Fetch Korean stock index levels as provenance-preserving JSON or CSV."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INDEXES = {
    "KOSPI": {"ticker": "1001", "name": "KOSPI", "naver_ticker": "KOSPI"},
    "KOSDAQ": {"ticker": "2001", "name": "KOSDAQ", "naver_ticker": "KOSDAQ"},
}

FIELD_MAP = {
    "시가": "open",
    "고가": "high",
    "저가": "low",
    "종가": "close",
    "거래량": "volume",
    "거래대금": "trading_value",
    "상장시가총액": "market_cap",
}

BASE_FIELDS = [
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
EXTRA_FIELDS = ["open", "high", "low", "close", "volume", "trading_value", "market_cap"]


def compact_date(value: str) -> str:
    return value.replace("-", "")


def format_date(value: Any) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    text = str(value)
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return text[:10]


def scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return value


def import_pykrx_modules() -> tuple[Any, Any]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        from pykrx.website import krx
        from pykrx.website.naver import core as naver_core

    return krx, naver_core


def fetch_krx_frame(config: dict[str, str], start: str, end: str) -> Any:
    krx, _ = import_pykrx_modules()
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            return krx.get_index_ohlcv_by_date(
                compact_date(start),
                compact_date(end),
                config["ticker"],
            )
    except Exception as error:
        raise SystemExit(
            "Failed to fetch KRX index data through pykrx. "
            "KRX-derived access can require live network access and can break when "
            f"upstream KRX services change. Original error: {error}"
        ) from error


def fetch_naver_fallback(config: dict[str, str], start: str, end: str) -> list[dict[str, Any]]:
    _, naver_core = import_pykrx_modules()
    start_dt = datetime.strptime(compact_date(start), "%Y%m%d")
    end_dt = datetime.strptime(compact_date(end), "%Y%m%d")
    count = (datetime.now() - start_dt).days + 2
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        xml = naver_core.Sise().fetch(config["naver_ticker"], count)

    rows = []
    for node in ET.fromstring(xml).iter(tag="item"):
        raw = node.get("data")
        if not raw:
            continue
        date_text, open_, high, low, close, volume = raw.split("|")
        row_dt = datetime.strptime(date_text, "%Y%m%d")
        if start_dt <= row_dt <= end_dt:
            rows.append(
                {
                    "date": row_dt.strftime("%Y-%m-%d"),
                    "open": float(open_),
                    "high": float(high),
                    "low": float(low),
                    "close": float(close),
                    "volume": int(volume),
                }
            )
    return sorted(rows, key=lambda row: row["date"])


def frame_to_rows(
    index_code: str,
    frame: Any,
    fetched_at: str,
    source: str,
) -> list[dict[str, Any]]:
    config = INDEXES[index_code]
    rows: list[dict[str, Any]] = []

    for date_value, values in frame.iterrows():
        extra = {
            target: scalar(values[source])
            for source, target in FIELD_MAP.items()
            if source in values
        }
        close = extra.get("close")
        rows.append(
            {
                "source": source,
                "fetched_at": fetched_at,
                "timezone": "Asia/Seoul",
                "frequency": "daily",
                "unit": "index point",
                "series_name": config["name"],
                "series_code": index_code,
                "date": format_date(date_value),
                "value": close,
                **extra,
            }
        )
    return rows


def dicts_to_rows(
    index_code: str,
    raw_rows: list[dict[str, Any]],
    fetched_at: str,
    source: str,
) -> list[dict[str, Any]]:
    config = INDEXES[index_code]
    rows = []
    for raw in raw_rows:
        rows.append(
            {
                "source": source,
                "fetched_at": fetched_at,
                "timezone": "Asia/Seoul",
                "frequency": "daily",
                "unit": "index point",
                "series_name": config["name"],
                "series_code": index_code,
                "date": raw["date"],
                "value": raw["close"],
                **{key: raw[key] for key in EXTRA_FIELDS if key in raw},
            }
        )
    return rows


def fetch_index(index_code: str, start: str, end: str, fetched_at: str) -> list[dict[str, Any]]:
    config = INDEXES[index_code]
    frame = fetch_krx_frame(config, start, end)
    if frame is not None and not frame.empty:
        return frame_to_rows(index_code, frame, fetched_at, "KRX via pykrx")

    fallback_rows = fetch_naver_fallback(config, start, end)
    if fallback_rows:
        return dicts_to_rows(index_code, fallback_rows, fetched_at, "Naver Finance via pykrx")

    raise SystemExit(f"No index rows returned for {index_code} between {start} and {end}.")


def write_output(rows: list[dict[str, Any]], output_format: str, output: str | None) -> None:
    if output_format == "json":
        text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    else:
        fieldnames = BASE_FIELDS + [
            field for field in EXTRA_FIELDS if any(field in row for row in rows)
        ]
        buffer = sys.stdout if output is None else open(output, "w", encoding="utf-8", newline="")
        try:
            writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            return
        finally:
            if output is not None:
                buffer.close()

    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="end date, YYYY-MM-DD")
    parser.add_argument(
        "--index",
        action="append",
        choices=sorted(INDEXES),
        help="index to fetch; repeat for multiple indices; defaults to KOSPI and KOSDAQ",
    )
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("-o", "--output", help="optional output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fetched_at = datetime.now(timezone.utc).isoformat()
    index_codes = args.index or sorted(INDEXES)
    rows: list[dict[str, Any]] = []
    for index_code in index_codes:
        rows.extend(fetch_index(index_code, args.start, args.end, fetched_at))
    write_output(rows, args.format, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
