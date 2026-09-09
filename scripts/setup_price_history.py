#!/usr/bin/env python3
"""Create Price History tab (one GOOGLEFINANCE spill) and point weekly Price row at it."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.labels import WEEKLY, label_rows, row_by_label  # noqa: E402
from sheets.price_history import (  # noqa: E402
    PRICE_HISTORY_SHEET,
    price_history_spill_formula,
    weekly_price_at_close_formula,
)
from sheets.registry import (  # noqa: E402
    load_pack_module,
    parse_ticker_argv,
    price_symbol_for,
    resolve_ticker,
)

DEFAULT_PRICE_LABEL = "Price (Actual)"


def _price_label(ticker: str) -> str:
    try:
        valuation = load_pack_module(ticker, "valuation")
    except FileNotFoundError:
        return DEFAULT_PRICE_LABEL
    return getattr(valuation, "PRICE_AT_CLOSE_LABEL", DEFAULT_PRICE_LABEL)


def ensure_price_history_sheet(client: SheetsClient) -> None:
    if PRICE_HISTORY_SHEET in client.list_worksheets():
        print(f"{PRICE_HISTORY_SHEET!r} already exists")
        return
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": PRICE_HISTORY_SHEET,
                            "index": 8,
                            "gridProperties": {"rowCount": 500, "columnCount": 8},
                        }
                    }
                }
            ]
        }
    )
    print(f"Added sheet {PRICE_HISTORY_SHEET!r}")


def write_price_history_query(client: SheetsClient, *, price_symbol: str) -> None:
    note = (
        f"Single GOOGLEFINANCE spill for {price_symbol} daily prices. "
        "Weekly Financials → Price (Actual) XLOOKUPs the close column (E) by week-ending date."
    )
    ws = client.worksheet(PRICE_HISTORY_SHEET)
    ws.update(
        [[note]],
        range_name="G1",
        value_input_option="RAW",
    )
    ws.update(
        [[price_history_spill_formula(price_symbol=price_symbol)]],
        range_name="A1",
        value_input_option="USER_ENTERED",
    )
    print(f"Wrote {PRICE_HISTORY_SHEET}!A1 spill formula for {price_symbol}")


def write_weekly_price_formulas(client: SheetsClient, *, ticker: str) -> None:
    labels = label_rows(client, WEEKLY, max_row=100)
    price_row = row_by_label(labels, _price_label(ticker), WEEKLY)
    ws = client.worksheet(WEEKLY)
    data = ws.get("A1:DY90", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)
    cells = [weekly_price_at_close_formula(col_letter(col_idx + 2)) for col_idx in range(n_cols)]
    ws.update(
        [cells],
        range_name=f"B{price_row}:{end_col}{price_row}",
        value_input_option="USER_ENTERED",
    )
    print(f"Wrote {WEEKLY} B{price_row}:{end_col}{price_row} (XLOOKUP → {PRICE_HISTORY_SHEET})")


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    if rest:
        print(f"Unknown arguments: {rest}")
        sys.exit(2)
    ticker = resolve_ticker(ticker_arg)
    price_symbol = price_symbol_for(ticker)
    client = SheetsClient(ticker=ticker)
    ensure_price_history_sheet(client)
    write_price_history_query(client, price_symbol=price_symbol)
    write_weekly_price_formulas(client, ticker=ticker)
    print("Done.")


if __name__ == "__main__":
    main()
