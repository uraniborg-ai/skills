---
name: ub-finance-data
description: Collect source-preserving Korean finance data for market analysis. Use when Codex needs Korean stock index levels, Korean stock OHLCV rows, Bank of Korea ECOS interest-rate series, CSV or JSON finance data exports, provenance-aware market data collection, or early-stage workflows for Korean financial indicators.
---

# UB Finance Data

Use this skill to collect Korean finance data with source, timestamp, unit, and
series identifiers preserved. Keep the first version focused on Korean stock
indices, Korean stock OHLCV, and Korean interest rates.

## Workflow

1. Collect KOSPI or KOSDAQ index levels with the bundled KRX-derived script:

   ```sh
   uv run --script skills/ub-finance-data/scripts/fetch_kr_indices.py --start 2024-01-02 --end 2024-01-05 --format json
   uv run --script skills/ub-finance-data/scripts/fetch_kr_indices.py --start 2024-01-02 --end 2024-01-05 --index KOSPI --format csv -o kr_indices.csv
   ```

2. Collect Korean interest rates with a Bank of Korea ECOS API key:

   ```sh
   BOK_ECOS_API_KEY=... uv run --script skills/ub-finance-data/scripts/fetch_kr_rates.py --start 2024-01-01 --end 2024-01-31 --format json
   BOK_ECOS_API_KEY=... uv run --script skills/ub-finance-data/scripts/fetch_kr_rates.py --series base-rate treasury-3y --start 2024-01-01 --end 2024-01-31 --format csv -o kr_rates.csv
   ```

3. Collect Korean stock OHLCV by six-digit ticker:

   ```sh
   uv run --script skills/ub-finance-data/scripts/fetch_kr_stocks.py --ticker 035420 --name NAVER --start 2026-01-01 --end 2026-07-04 --format json
   uv run --script skills/ub-finance-data/scripts/fetch_kr_stocks.py --ticker 035420 --name NAVER --start 2026-01-01 --end 2026-07-04 --format csv -o naver.csv
   ```

4. Prefer JSON when the next step is analysis by an agent or notebook. Use CSV
   for spreadsheet import or quick inspection.
5. Treat the output as data collection, not investment advice. Check units,
   dates, holidays, and source freshness before drawing conclusions.
6. Mention that KRX-derived access uses `pykrx` and can be affected by upstream
   KRX website or data-service changes. If the KRX path returns no rows, the
   index script may fall back to `pykrx`'s Naver Finance backend and will mark
   that source in each row. The stock script uses `pykrx`'s Naver Finance
   backend and marks that source in each row.

## Data Contract

All rows include:

- `source`
- `fetched_at`
- `timezone`
- `frequency`
- `unit`
- `series_name`
- `series_code`
- `date`
- `value`

Index rows may also include open, high, low, close, volume, trading value, and
market capitalization fields when the upstream data provides them.

Stock rows may also include ticker, open, high, low, close, volume, and change
rate fields. The stock row `value` is the closing price.

## Current Scope

- Korean stock indices: `KOSPI`, `KOSDAQ`
- Korean stocks by six-digit ticker, such as `035420` for NAVER
- Korean rates: `base-rate`, `treasury-3y`, `treasury-10y`, `cd-91d`

Leave stock-name lookup, watchlist files, commodities, foreign exchange, and
overseas market indicators for later extensions.
