#!/usr/bin/env python3
"""Apply day-weighted quarterly spread formulas to Weekly Financials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import (  # noqa: E402
    weekly_from_quarterly_formula,
    weekly_quarterly_rate_formula,
    weekly_shares_formula,
)

WEEKLY = "Weekly Financials"

# Dollar amounts: quarterly hard value spread with ÷13 (day-weighted at boundaries).
SPREAD_ROWS = {9, 15, 18, 20, 21, 30, 32, 34, 40, 41, 43, 44, 45, 46}

# Percent / rate rows: day-weighted blend, no ÷13.
RATE_ROWS = {23}

SHARES_ROW = 35


def col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def update_weekly_formulas(client: SheetsClient) -> None:
    ws = client.worksheet(WEEKLY)
    data = ws.get("A2:DY47", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)

    rows_to_update: dict[int, list] = {}

    for row_idx, row in enumerate(data):
        row_num = row_idx + 2
        existing = list(row[1:]) if len(row) > 1 else []
        cells = existing + [""] * (n_cols - len(existing))

        needs_spread = row_num in SPREAD_ROWS
        needs_rate = row_num in RATE_ROWS
        needs_shares = row_num == SHARES_ROW

        if not (needs_spread or needs_rate or needs_shares):
            continue

        changed = len(existing) < n_cols
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            prev_col = col_letter(col_idx + 1)
            cell = cells[col_idx]

            if needs_shares:
                new_val = weekly_shares_formula(col, prev_col)
            elif needs_rate:
                new_val = weekly_quarterly_rate_formula(row_num, col)
            else:
                new_val = weekly_from_quarterly_formula(row_num, col)

            if str(cell) != new_val:
                cells[col_idx] = new_val
                changed = True

        if changed:
            rows_to_update[row_num] = cells

    for row_num in sorted(rows_to_update):
        ws.update(
            [rows_to_update[row_num]],
            range_name=f"B{row_num}:{end_col}{row_num}",
            value_input_option="USER_ENTERED",
        )

    print(f"Updated weekly formulas on rows: {sorted(rows_to_update)}")


def main() -> None:
    client = SheetsClient()
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
