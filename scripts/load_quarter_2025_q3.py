#!/usr/bin/env python3
"""Load and verify 2025 Q3 actuals into Quarterly / Weekly Financials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402

QUARTERLY = "Quarterly Financials"
Q3_COL = "B"  # 2025 Q3

# Hardcoded quarterly actuals — Q3 2025 Open House / Form 10-Q (Nov 2025).
# Sources documented in CHANGELOG entry for this run.
Q3_VALUES: dict[int, int | float] = {
    20: 66_000_000,  # GAAP gross profit
    21: 20_000_000,  # Contribution profit (Non-GAAP)
    23: 0.022,  # Contribution margin 2.2%
    34: 31_000_000,  # SBC + market RSUs + IDSW amort (ANL reconciliation)
    35: 741_939_000,  # Basic weighted-average shares (741,939 in thousands)
    40: -33_000_000,  # Adjusted EBITDA
    41: 22_000_000,  # Net interest: property financing 23 + other 11 − interest income 12
    43: 5_000_000,  # D&A excl. intangibles (EBITDA bridge)
    44: 1_000_000,  # Income tax expense
    45: -61_000_000,  # Adjusted net loss
    46: -89_032_680,  # GAAP net loss: -0.12 × 741,939,000 basic shares
    48: -0.12,  # GAAP basic EPS
}

Q3_EOP_SHARES = 771_534_057


def quarterly_row_by_label(client: SheetsClient, label: str) -> int:
    rows = client.worksheet(QUARTERLY).get("A1:A60")
    for idx, row in enumerate(rows, start=1):
        if row and row[0] == label:
            return idx
    raise KeyError(f"Label {label!r} not found on {QUARTERLY!r}")


def write_quarterly_q3(client: SheetsClient) -> None:
    ws = client.worksheet(QUARTERLY)
    eop_row = quarterly_row_by_label(client, "Shares Outstanding (Quarter End)")
    for row, value in Q3_VALUES.items():
        ws.update([[value]], range_name=f"{Q3_COL}{row}", value_input_option="RAW")
    ws.update([[Q3_EOP_SHARES]], range_name=f"{Q3_COL}{eop_row}", value_input_option="RAW")
    label = ws.get(f"A{eop_row}")
    if not label or not label[0] or not label[0][0]:
        ws.update(
            [["Shares Outstanding (Quarter End)"]],
            range_name=f"A{eop_row}",
            value_input_option="RAW",
        )
    print(f"Wrote {len(Q3_VALUES)} quarterly values + EOP shares to {Q3_COL}")


def main() -> None:
    client = SheetsClient()
    write_quarterly_q3(client)
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
