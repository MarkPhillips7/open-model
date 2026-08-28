#!/usr/bin/env python3
"""Load and verify 2025 Q4, 2026 Q1, and 2026 Q2 actuals into Quarterly Financials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402

QUARTERLY = "Quarterly Financials"
EOP_SHARES_LABEL = "Shares Outstanding (Quarter End)"

# Column → quarter key
QUARTER_COLS = {
    "C": "2025 Q4",
    "D": "2026 Q1",
    "E": "2026 Q2",
}

# Sources: Q4 2025 Open House (Ex. 99.1/99.2, Feb 2026); Q1/Q2 2026 8-K + 10-Q.
# SBC row = stock-based comp + market-condition RSUs + IDSW amort (same as Q3 load).
QUARTER_VALUES: dict[str, dict[int, int | float]] = {
    "C": {
        15: 1_978,
        20: 57_000_000,
        21: 7_000_000,
        23: 0.01,
        34: 108_000_000,  # 16 + 89 + 3
        35: 869_822_000,
        40: -43_000_000,
        41: 15_000_000,  # property financing 21 + other 7 − interest income 13
        43: 5_000_000,
        44: 1_000_000,
        45: -62_000_000,
        46: -1_095_975_720,  # GAAP net loss: -1.26 × 869,822,000
        48: -1.26,
    },
    "D": {
        15: 1_921,
        20: 72_000_000,
        21: 32_000_000,
        23: 0.044,
        34: 123_000_000,  # 15 + 105 + 3
        35: 959_332_000,
        40: -31_000_000,
        41: 13_000_000,  # 19 + 4 − 10
        43: 5_000_000,
        44: 0,
        45: -49_000_000,
        46: -172_679_760,  # GAAP net loss: -0.18 × 959,332,000
        48: -0.18,
    },
    "E": {
        15: 2_339,
        20: 86_000_000,
        23: 0.058,
        34: 122_000_000,  # 19 + 100 + 3
        35: 965_780_000,
        40: -4_000_000,
        41: 21_000_000,  # 24 + 5 − 8
        43: 5_000_000,
        44: 0,
        45: -30_000_000,
        46: -164_182_600,  # GAAP net loss: -0.17 × 965,780,000
        48: -0.17,
    },
}

EOP_SHARES_BY_COL: dict[str, int] = {
    "C": 957_245_487,
    "D": 963_283_777,
    "E": 968_626_958,
}


def quarterly_row_by_label(client: SheetsClient, label: str) -> int:
    rows = client.worksheet(QUARTERLY).get("A1:A60")
    for idx, row in enumerate(rows, start=1):
        if row and row[0] == label:
            return idx
    raise KeyError(f"Label {label!r} not found on {QUARTERLY!r}")


def write_quarters(client: SheetsClient) -> None:
    ws = client.worksheet(QUARTERLY)
    eop_row = quarterly_row_by_label(client, EOP_SHARES_LABEL)
    label = ws.get(f"A{eop_row}")
    if not label or not label[0] or not label[0][0]:
        ws.update(
            [[EOP_SHARES_LABEL]],
            range_name=f"A{eop_row}",
            value_input_option="RAW",
        )

    for col, values in QUARTER_VALUES.items():
        for row, value in values.items():
            ws.update([[value]], range_name=f"{col}{row}", value_input_option="RAW")
        if col in EOP_SHARES_BY_COL:
            ws.update([[EOP_SHARES_BY_COL[col]]], range_name=f"{col}{eop_row}", value_input_option="RAW")
        print(f"Wrote {len(values)} values to {col} ({QUARTER_COLS[col]})")


def main() -> None:
    client = SheetsClient()
    write_quarters(client)
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
