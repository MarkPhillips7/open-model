#!/usr/bin/env python3
"""Load and verify 2025 Q3 actuals into Quarterly / Weekly Financials."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from models.OPEN.gaap_below_the_line import ADJ_TO_GAAP_BY_COL, BELOW_THE_LINE_BY_COL
from sheets.labels import QUARTERLY, label_rows, row_by_label, write_quarterly_by_label  # noqa: E402

Q3_COL = "B"  # 2025 Q3
EOP_SHARES_LABEL = "Shares Outstanding (Quarter End)"

Q3_VALUES_BY_LABEL: dict[str, int | float] = {
    "Gross Profit": 66_000_000,
    "Contribution Profit": 20_000_000,
    "Contribution Margin": 0.022,
    "Stock Based Compensation": 31_000_000,
    "Basic Shares Outstanding": 741_939_000,
    "Adjusted EBITDA": -33_000_000,
    "Net Interest Expense": 22_000_000,
    "Depreciation and Amortization": 5_000_000,
    "Taxes": 1_000_000,
    "Adjusted Net Income": -61_000_000,
    "Net Income (Loss) Attributable to Common Shareholders": -89_032_680,
    "Earnings per Share": -0.12,
}

Q3_EOP_SHARES = 771_534_057


def write_quarterly_q3(client: SheetsClient) -> None:
    write_quarterly_by_label(client, Q3_COL, Q3_VALUES_BY_LABEL)
    write_quarterly_by_label(client, Q3_COL, BELOW_THE_LINE_BY_COL[Q3_COL])
    write_quarterly_by_label(client, Q3_COL, ADJ_TO_GAAP_BY_COL[Q3_COL])
    labels = label_rows(client, QUARTERLY)
    eop_row = row_by_label(labels, EOP_SHARES_LABEL, QUARTERLY)
    client.worksheet(QUARTERLY).update(
        [[Q3_EOP_SHARES]], range_name=f"{Q3_COL}{eop_row}", value_input_option="RAW"
    )
    print(f"Wrote {len(Q3_VALUES_BY_LABEL)} quarterly values + EOP shares to {Q3_COL}")


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    write_quarterly_q3(client)
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
