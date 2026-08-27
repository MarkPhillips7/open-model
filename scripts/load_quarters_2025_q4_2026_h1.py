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
EOP_SHARES_ROW = 48

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
        46: -1.26,
        EOP_SHARES_ROW: 957_245_487,
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
        46: -0.18,
        EOP_SHARES_ROW: 963_283_777,
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
        46: -0.17,
        EOP_SHARES_ROW: 968_626_958,
    },
}


def write_quarters(client: SheetsClient) -> None:
    ws = client.worksheet(QUARTERLY)
    label = ws.get(f"A{EOP_SHARES_ROW}")
    if not label or not label[0] or not label[0][0]:
        ws.update(
            [["Shares Outstanding (Quarter End)"]],
            range_name=f"A{EOP_SHARES_ROW}",
            value_input_option="RAW",
        )

    for col, values in QUARTER_VALUES.items():
        for row, value in values.items():
            ws.update([[value]], range_name=f"{col}{row}", value_input_option="RAW")
        print(f"Wrote {len(values)} values to {col} ({QUARTER_COLS[col]})")


def main() -> None:
    client = SheetsClient()
    write_quarters(client)
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
