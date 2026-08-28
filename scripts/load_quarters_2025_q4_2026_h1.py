#!/usr/bin/env python3
"""Load and verify 2025 Q4, 2026 Q1, and 2026 Q2 actuals into Quarterly Financials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.labels import QUARTERLY, label_rows, row_by_label, write_quarterly_by_label  # noqa: E402

EOP_SHARES_LABEL = "Shares Outstanding (Quarter End)"

QUARTER_COLS = {
    "C": "2025 Q4",
    "D": "2026 Q1",
    "E": "2026 Q2",
}

QUARTER_VALUES_BY_LABEL: dict[str, dict[str, int | float]] = {
    "C": {
        "Home Sales": 1_978,
        "Gross Profit": 57_000_000,
        "Contribution Profit": 7_000_000,
        "Contribution Margin": 0.01,
        "Stock Based Compensation": 108_000_000,
        "Basic Shares Outstanding": 869_822_000,
        "Adjusted EBITDA": -43_000_000,
        "Net Interest Expense": 15_000_000,
        "Depreciation and Amortization": 5_000_000,
        "Taxes": 1_000_000,
        "Adjusted Net Income": -62_000_000,
        "Net Income (Loss) Attributable to Common Shareholders": -1_095_975_720,
        "Earnings per Share": -1.26,
    },
    "D": {
        "Home Sales": 1_921,
        "Gross Profit": 72_000_000,
        "Contribution Profit": 32_000_000,
        "Contribution Margin": 0.044,
        "Stock Based Compensation": 123_000_000,
        "Basic Shares Outstanding": 959_332_000,
        "Adjusted EBITDA": -31_000_000,
        "Net Interest Expense": 13_000_000,
        "Depreciation and Amortization": 5_000_000,
        "Taxes": 0,
        "Adjusted Net Income": -49_000_000,
        "Net Income (Loss) Attributable to Common Shareholders": -172_679_760,
        "Earnings per Share": -0.18,
    },
    "E": {
        "Home Sales": 2_339,
        "Gross Profit": 86_000_000,
        "Contribution Margin": 0.058,
        "Stock Based Compensation": 122_000_000,
        "Basic Shares Outstanding": 965_780_000,
        "Adjusted EBITDA": -4_000_000,
        "Net Interest Expense": 21_000_000,
        "Depreciation and Amortization": 5_000_000,
        "Taxes": 0,
        "Adjusted Net Income": -30_000_000,
        "Net Income (Loss) Attributable to Common Shareholders": -164_182_600,
        "Earnings per Share": -0.17,
    },
}

EOP_SHARES_BY_COL: dict[str, int] = {
    "C": 957_245_487,
    "D": 963_283_777,
    "E": 968_626_958,
}


def write_quarters(client: SheetsClient) -> None:
    ws = client.worksheet(QUARTERLY)
    labels = label_rows(client, QUARTERLY)
    eop_row = row_by_label(labels, EOP_SHARES_LABEL, QUARTERLY)
    label = ws.get(f"A{eop_row}")
    if not label or not label[0] or not label[0][0]:
        ws.update([[EOP_SHARES_LABEL]], range_name=f"A{eop_row}", value_input_option="RAW")

    for col, values in QUARTER_VALUES_BY_LABEL.items():
        write_quarterly_by_label(client, col, values)
        if col in EOP_SHARES_BY_COL:
            ws.update(
                [[EOP_SHARES_BY_COL[col]]],
                range_name=f"{col}{eop_row}",
                value_input_option="RAW",
            )
        print(f"Wrote {len(values)} values to {col} ({QUARTER_COLS[col]})")


def main() -> None:
    client = SheetsClient()
    write_quarters(client)
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
