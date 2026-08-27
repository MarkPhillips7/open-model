#!/usr/bin/env python3
"""Restore Weekly Financials * - Model row formulas cleared by spread cleanup."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402

WEEKLY = "Weekly Financials"

# Funnel / revenue model rows (row refs aligned to current Weekly Financials layout).
HOMES_PURCHASED_MODEL = """=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      contracts, IF(col < 2, 130,
        IF(INDEX($2:$2, 1, col) = "",
          INDEX($3:$3, 1, col),
          INDEX($2:$2, 1, col)
        )
      ),
      l2c, IF(col < 2, $B$7, INDEX($7:$7, 1, col)),
      contracts * l2c
    )
  )),
  Transitions!$B$2:$J$2
))"""

PRIVATE_HOME_SALES_MODEL = """=(Transitions!$B$6*SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 90,
        IF(INDEX($8:$8, 1, col) = "",
          INDEX($9:$9, 1, col),
          INDEX($8:$8, 1, col)
        )
      )
    )
  )),
  Transitions!$B$19:$J$19
))"""

REVENUE_MODEL = """=(SUMPRODUCT(
  MAP(SEQUENCE(1,21), LAMBDA(lag,
    LET(
      col, COLUMN() - lag - Transitions!$B$15,
      IF(col < 2, 220*377500,
        IF(INDEX($11:$11, 1, col) = "",
          INDEX($12:$12, 1, col),
          INDEX($11:$11, 1, col)
        )*INDEX($13:$13, 1, col)
      )
    )
  )),
  Transitions!$B$10:$V$10,
  Transitions!$B$12:$V$12
)*Transitions!$B$16+
 SUMPRODUCT(
  MAP(SEQUENCE(1,21), LAMBDA(lag,
    LET(
      col, COLUMN() - lag - Transitions!$B$14,
      IF(col < 2, 220*377500,
        IF(INDEX($11:$11, 1, col) = "",
          INDEX($12:$12, 1, col),
          INDEX($11:$11, 1, col)
        )*INDEX($13:$13, 1, col)
      )
    )
  )),
  Transitions!$B$10:$V$10,
  Transitions!$B$12:$V$12
)*(1-Transitions!$B$16)+INDEX($15:$15, 1, COLUMN())*INDEX($13:$13, 1, COLUMN()))"""

FIXED_COSTS_MODEL = "=35000000/13"
NET_INTEREST_MODEL = "=20000000/13"

# Same formula in every column (uses COLUMN() or is column-independent).
ROW_FORMULAS: dict[int, str] = {
    9: HOMES_PURCHASED_MODEL,
    15: PRIVATE_HOME_SALES_MODEL,
    18: REVENUE_MODEL,
    30: FIXED_COSTS_MODEL,
    41: NET_INTEREST_MODEL,
}

# Per-column refs — batch API writes do not auto-fill across columns like paste-fill.
COLUMN_RELATIVE_ROWS: dict[int, str] = {
    21: "={c}18*{c}23",
    23: "={c}24+{c}25+{c}26+{c}27",
    32: "={c}30+(15000000/13)",
    46: '=IF({c}34=0,"",({c}21-{c}32-{c}41)/{c}34)',
}


def col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def core_margin_ramp_formula(col: str, prev_col: str) -> str:
    return f"={prev_col}24+{col}28"


def column_relative_formula(row_num: int, col: str) -> str:
    return COLUMN_RELATIVE_ROWS[row_num].format(c=col)


def row_formulas(n_cols: int) -> dict[int, list[str]]:
    updates: dict[int, list[str]] = {}
    for row_num, template in ROW_FORMULAS.items():
        updates[row_num] = [template] * n_cols
    for row_num in COLUMN_RELATIVE_ROWS:
        updates[row_num] = [
            column_relative_formula(row_num, col_letter(col_idx + 2))
            for col_idx in range(n_cols)
        ]
    return updates


def restore_model_formulas(client: SheetsClient) -> None:
    ws = client.worksheet(WEEKLY)
    data = ws.get("A1:DY60", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)

    updates = row_formulas(n_cols)

    # Contribution Margin - Core ramp from col F onward (= prev core + improvement this week).
    core_cells = list(data[23][1:]) if len(data) > 23 else []
    core_cells = core_cells + [""] * (n_cols - len(core_cells))
    changed = False
    for col_idx in range(5, n_cols):  # column F = index 5
        col = col_letter(col_idx + 2)
        prev_col = col_letter(col_idx + 1)
        new_val = core_margin_ramp_formula(col, prev_col)
        if str(core_cells[col_idx]) != new_val:
            core_cells[col_idx] = new_val
            changed = True
    if changed:
        updates[24] = core_cells

    for row_num in sorted(updates):
        ws.update(
            [updates[row_num]],
            range_name=f"B{row_num}:{end_col}{row_num}",
            value_input_option="USER_ENTERED",
        )

    print(f"Restored model formulas on rows: {sorted(updates)}")


def main() -> None:
    client = SheetsClient()
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
