#!/usr/bin/env python3
"""Apply day-weighted quarterly spread formulas to Weekly Financials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import (  # noqa: E402
    weekly_asp_formula,
    weekly_from_quarterly_formula,
    weekly_inventory_formula,
    weekly_quarterly_rate_formula,
    weekly_shares_formula,
)
from sheets.labels import QUARTERLY, WEEKLY, label_rows, row_by_label  # noqa: E402

# Dollar amounts: quarterly hard value spread with ÷13 (day-weighted at boundaries).
SPREAD_LABELS = (
    "Homes Purchased",
    "Home Sales",
    "Revenue",
    "Gross Profit",
    "Contribution Profit",
    "Fixed Costs",
    "Adjusted Operating Expenses",
    "Stock Based Compensation",
    "Adjusted EBITDA",
    "Net Interest Expense",
    "Depreciation and Amortization",
    "Taxes",
    "Adjusted Net Income",
    "Net Income (Loss) Attributable to Common Shareholders",
    "Earnings per Share",
)

# Percent / rate rows: day-weighted blend, no ÷13.
RATE_LABELS = ("Contribution Margin",)

SHARES_LABEL = "Basic Shares Outstanding"
EOP_SHARES_LABEL = "Shares Outstanding (Quarter End)"
INVENTORY_LABEL = "Homes in Inventory"
ASP_LABEL = "Average Sale Price (homes sold by OPEN)"


def col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def build_row_map(client: SheetsClient) -> dict[str, tuple[int, int]]:
    """Return label -> (weekly_row, quarterly_row)."""
    weekly_labels = label_rows(client, WEEKLY)
    quarterly_labels = label_rows(client, QUARTERLY)
    mapping: dict[str, tuple[int, int]] = {}
    for label in (*SPREAD_LABELS, *RATE_LABELS, SHARES_LABEL, INVENTORY_LABEL, ASP_LABEL):
        mapping[label] = (
            row_by_label(weekly_labels, label, WEEKLY),
            row_by_label(quarterly_labels, label, QUARTERLY),
        )
    mapping[EOP_SHARES_LABEL] = (
        row_by_label(weekly_labels, EOP_SHARES_LABEL, WEEKLY)
        if EOP_SHARES_LABEL in weekly_labels
        else 0,
        row_by_label(quarterly_labels, EOP_SHARES_LABEL, QUARTERLY),
    )
    return mapping


def update_weekly_formulas(client: SheetsClient) -> None:
    ws = client.worksheet(WEEKLY)
    row_map = build_row_map(client)

    data = ws.get("A1:DY60", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)

    rows_to_update: dict[int, list] = {}

    for label in SPREAD_LABELS:
        weekly_row, quarterly_row = row_map[label]
        existing = list(data[weekly_row - 1][1:]) if len(data[weekly_row - 1]) > 1 else []
        cells = existing + [""] * (n_cols - len(existing))
        changed = len(existing) < n_cols
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            new_val = weekly_from_quarterly_formula(quarterly_row, col)
            if str(cells[col_idx]) != new_val:
                cells[col_idx] = new_val
                changed = True
        if changed:
            rows_to_update[weekly_row] = cells

    for label in RATE_LABELS:
        weekly_row, quarterly_row = row_map[label]
        existing = list(data[weekly_row - 1][1:]) if len(data[weekly_row - 1]) > 1 else []
        cells = existing + [""] * (n_cols - len(existing))
        changed = len(existing) < n_cols
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            new_val = weekly_quarterly_rate_formula(quarterly_row, col)
            if str(cells[col_idx]) != new_val:
                cells[col_idx] = new_val
                changed = True
        if changed:
            rows_to_update[weekly_row] = cells

    shares_weekly_row, _ = row_map[SHARES_LABEL]
    _, quarterly_eop_row = row_map[EOP_SHARES_LABEL]
    existing = list(data[shares_weekly_row - 1][1:]) if len(data[shares_weekly_row - 1]) > 1 else []
    cells = existing + [""] * (n_cols - len(existing))
    changed = len(existing) < n_cols
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        prev_col = col_letter(col_idx + 1)
        new_val = weekly_shares_formula(
            col,
            prev_col,
            weekly_row=shares_weekly_row,
            quarterly_eop_row=quarterly_eop_row,
        )
        if str(cells[col_idx]) != new_val:
            cells[col_idx] = new_val
            changed = True
    if changed:
        rows_to_update[shares_weekly_row] = cells

    inventory_weekly_row, quarterly_inventory_row = row_map[INVENTORY_LABEL]
    existing = list(data[inventory_weekly_row - 1][1:]) if len(data[inventory_weekly_row - 1]) > 1 else []
    cells = existing + [""] * (n_cols - len(existing))
    changed = len(existing) < n_cols
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        prev_col = col_letter(col_idx + 1)
        new_val = weekly_inventory_formula(
            col,
            prev_col,
            weekly_row=inventory_weekly_row,
            quarterly_row=quarterly_inventory_row,
        )
        if str(cells[col_idx]) != new_val:
            cells[col_idx] = new_val
            changed = True
    if changed:
        rows_to_update[inventory_weekly_row] = cells

    asp_weekly_row, quarterly_asp_row = row_map[ASP_LABEL]
    existing = list(data[asp_weekly_row - 1][1:]) if len(data[asp_weekly_row - 1]) > 1 else []
    cells = existing + [""] * (n_cols - len(existing))
    changed = len(existing) < n_cols
    first_col_fallback = existing[0] if existing and existing[0] not in ("", None) else 377_500
    if isinstance(first_col_fallback, str) and first_col_fallback.startswith("="):
        first_col_fallback = 377_500
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        prev_col = col_letter(col_idx + 1)
        new_val = weekly_asp_formula(
            col,
            prev_col,
            weekly_row=asp_weekly_row,
            quarterly_row=quarterly_asp_row,
            first_col_fallback=first_col_fallback,
        )
        if str(cells[col_idx]) != new_val:
            cells[col_idx] = new_val
            changed = True
    if changed:
        rows_to_update[asp_weekly_row] = cells

    for row_num in sorted(rows_to_update):
        ws.update(
            [rows_to_update[row_num]],
            range_name=f"B{row_num}:{end_col}{row_num}",
            value_input_option="USER_ENTERED",
        )

    print(f"Updated weekly formulas on rows: {sorted(rows_to_update)}")


def clear_misplaced_spread_formulas(client: SheetsClient) -> None:
    """Remove quarterly spread formulas that landed on model rows after layout shifts."""
    ws = client.worksheet(WEEKLY)
    data = ws.get("A1:DY60", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)

    cleared: list[int] = []
    for row_idx, row in enumerate(data, start=1):
        label = row[0] if row else ""
        if label.endswith(" - Model"):
            cells = list(row[1:]) if len(row) > 1 else []
            if any("Quarterly Financials'!$B$" in str(c) for c in cells):
                ws.update(
                    [[""] * n_cols],
                    range_name=f"B{row_idx}:{end_col}{row_idx}",
                    value_input_option="RAW",
                )
                cleared.append(row_idx)

    if cleared:
        print(f"Cleared misplaced spread formulas on rows: {cleared}")


def main() -> None:
    client = SheetsClient()
    clear_misplaced_spread_formulas(client)
    update_weekly_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
