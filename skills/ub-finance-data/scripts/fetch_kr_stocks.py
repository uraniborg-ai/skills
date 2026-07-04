#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pykrx>=1.0.51",
# ]
# ///
"""Fetch Korean stock OHLCV rows as provenance-preserving JSON or CSV."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
EXTRA_FIELDS = ["ticker", "open", "high", "low", "close", "volume", "change_rate"]
FIELD_MAP = {
    "시가": "open",
    "고가": "high",
    "저가": "low",
    "종가": "close",
    "거래량": "volume",
    "등락률": "change_rate",
}


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


def normalize_field(field: str, value: Any) -> Any:
    value = scalar(value)
    if field in {"open", "high", "low", "close", "volume"} and value is not None:
        return int(value)
    return value


def import_naver_module() -> Any:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        from pykrx.website import naver

    return naver


def fetch_stock_frame(ticker: str, start: str, end: str) -> Any:
    naver = import_naver_module()
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            return naver.get_market_ohlcv_by_date(
                compact_date(start),
                compact_date(end),
                ticker,
            )
    except Exception as error:
        raise SystemExit(
            "Failed to fetch stock data through pykrx's Naver Finance backend. "
            "Check the ticker, network access, and upstream service status. "
            f"Original error type: {type(error).__name__}"
        ) from None


def frame_to_rows(
    ticker: str,
    name: str,
    frame: Any,
    fetched_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for date_value, values in frame.iterrows():
        extra = {
            target: normalize_field(target, values[source])
            for source, target in FIELD_MAP.items()
            if source in values
        }
        close = extra.get("close")
        rows.append(
            {
                "source": "Naver Finance via pykrx",
                "fetched_at": fetched_at,
                "timezone": "Asia/Seoul",
                "frequency": "daily",
                "unit": "KRW",
                "series_name": name,
                "series_code": ticker,
                "date": format_date(date_value),
                "value": close,
                "ticker": ticker,
                **extra,
            }
        )
    return rows


def write_output(rows: list[dict[str, Any]], output_format: str, output: str | None) -> None:
    if output_format == "json":
        text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
        if output:
            Path(output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return

    fieldnames = BASE_FIELDS + [
        field for field in EXTRA_FIELDS if any(field in row for row in rows)
    ]
    buffer = sys.stdout if output is None else open(output, "w", encoding="utf-8", newline="")
    try:
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output is not None:
            buffer.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="six-digit Korean stock ticker")
    parser.add_argument("--name", help="optional display name; defaults to ticker")
    parser.add_argument("--start", required=True, help="start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="end date, YYYY-MM-DD")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("-o", "--output", help="optional output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    name = args.name or args.ticker
    fetched_at = datetime.now(timezone.utc).isoformat()
    frame = fetch_stock_frame(args.ticker, args.start, args.end)
    if frame is None or frame.empty:
        raise SystemExit(
            f"No stock rows returned for {args.ticker} between {args.start} and {args.end}."
        )
    rows = frame_to_rows(args.ticker, name, frame, fetched_at)
    write_output(rows, args.format, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
