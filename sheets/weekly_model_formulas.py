"""Canonical Weekly Financials * - Model row formulas (synced from live sheet).

Row numbers below match the current Weekly Financials layout after the row-1 delete
(Week Ending on R1). The restore script resolves rows by label so future inserts
do not break restores.

Weekly row map (reference):
  R2/R3   Acquisition Contracts / - Model
  R8/R9   Homes Purchased / - Model
  R10     Likelihood to List
  R11/R12 New Listings / - Model
  R14/R16 Home Sales / - Model
  R15     Private Home Sales - Model
  R17/R18 Revenue / - Model
  R21     Contribution Profit - Model
  R23     Contribution Margin - Model
  R24–28  CM stack (Core, Mortgage, Title, Adjustments, Improvement)
  R30     Fixed Costs - Model
  R32     Adjusted Operating Expenses - Model
  R38     Homes in Inventory - Model
  R34     Basic Shares Outstanding
  R35     Share Count Adjustment - Model
  R36     Basic Shares Outstanding - Model
  R43     Net Interest Expense - Model
  R47     Net Income (Loss) Attributable to Common Shareholders - Model
  R50     Earnings per Share - Model
"""

from __future__ import annotations

from sheets.formulas import SHARES_MODEL_LABEL
from sheets.shares_events import (
    SHARES_ADJUSTMENT_LABEL,
    weekly_share_adjustment_formula,
    weekly_shares_model_formula,
)

GAAP_NET_INCOME_MODEL_LABEL = (
    "Net Income (Loss) Attributable to Common Shareholders - Model"
)

# B-column anchor for Homes in Inventory - Model (prior to first weekly roll-forward).
INVENTORY_MODEL_ANCHOR = 3275

# Hardcoded CM stack inputs (cols B–E and ramp/improvement cols F+ where not formula-driven).
CM_CORE_VALUES: dict[str, float] = {"B": 0.026, "C": 0.026, "D": 0.026, "E": 0.027}
CM_ADJUSTMENTS_VALUES: dict[str, float] = {
    "B": -0.03,
    "C": -0.03,
    "D": -0.03,
    "E": -0.03,
    "F": -0.03,
    "G": -0.03,
    "H": -0.02,
    "I": -0.02,
    "J": -0.02,
    "K": -0.02,
}
CM_IMPROVEMENT_FROM_COL_F = 0.0005

# Uses COLUMN() — same string in every column.
UNIFORM_FORMULAS: dict[str, str] = {
    "Homes Purchased - Model": """=(SUMPRODUCT(
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
))""",
    "New Listings - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      purchases, IF(col < 2, 90, INDEX($9:$9, 1, col)*INDEX($10:$10, 1, col)),
      purchases
    )
  )),
  Transitions!$B$4:$J$4
)+IF(COLUMN()-1<=8, Transitions!$B$21*INDEX(Transitions!$B$23:$I$23, 1, COLUMN()-1), 0))""",
    # Private share via (1 − Likelihood to List), not Transitions!B6.
    "Private Home Sales - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 15,
        IF(INDEX($8:$8, 1, col) = "",
          INDEX($9:$9, 1, col),
          INDEX($8:$8, 1, col)
        )*(1-INDEX($10:$10, 1, col))
      )
    )
  )),
  Transitions!$B$19:$J$19
))""",
    "Home Sales - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,21), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 140,
        IF(INDEX($11:$11, 1, col) = "",
          INDEX($12:$12, 1, col),
          INDEX($11:$11, 1, col)
        )*INDEX($10:$10, 1, col)
      )
    )
  )),
  Transitions!$B$10:$V$10
)+INDEX($15:$15, 1, COLUMN()))""",
    "Revenue - Model": """=(SUMPRODUCT(
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
)*(1-Transitions!$B$16)+INDEX($15:$15, 1, COLUMN())*INDEX($13:$13, 1, COLUMN()))""",
    "Fixed Costs - Model": "=35000000/13",
    "Net Interest Expense - Model": "=20000000/13",
}

# Per-column refs — batch API writes do not auto-fill like paste-down.
COLUMN_RELATIVE: dict[str, str] = {
    "Acquisition Contracts - Model": "={c}6*{c}4",
    "Contribution Profit - Model": "={c}18*{c}23",
    "Contribution Margin - Model": "={c}24+{c}25+{c}26+{c}27",
    "Adjusted Operating Expenses - Model": "={c}30+(15000000/13)",
    GAAP_NET_INCOME_MODEL_LABEL: (
        "={c}21-{c}32-{c}33-{c}41-{c}42-{c}43"
    ),
    "Earnings per Share - Model": '=IF(N({c}{shares_row})=0,"",{c}{gaap_row}/{c}{shares_row})',
}

# Row labels included in a full model-formula restore (excluding CM stack value rows).
MODEL_FORMULA_LABELS: tuple[str, ...] = (
    "Acquisition Contracts - Model",
    *UNIFORM_FORMULAS.keys(),
    *COLUMN_RELATIVE.keys(),
    SHARES_ADJUSTMENT_LABEL,
    SHARES_MODEL_LABEL,
    "Homes in Inventory - Model",
)


def col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def column_relative_formula(
    label: str,
    col: str,
    *,
    label_to_row: dict[str, int] | None = None,
) -> str:
    template = COLUMN_RELATIVE[label]
    if label == "Earnings per Share - Model":
        if label_to_row is None:
            raise ValueError("label_to_row required for Earnings per Share - Model")
        gaap_row = label_to_row[GAAP_NET_INCOME_MODEL_LABEL]
        shares_row = label_to_row[SHARES_MODEL_LABEL]
        return template.format(c=col, gaap_row=gaap_row, shares_row=shares_row)
    return template.format(c=col)


def inventory_model_formula(
    col: str,
    prev_col: str,
    *,
    inventory_row: int,
    purchases_row: int = 8,
    purchases_model_row: int = 9,
    sales_row: int = 14,
    sales_model_row: int = 16,
) -> str:
    """Roll inventory: prior + purchases (actual else model) − sales (actual else model)."""
    if col == "B":
        return str(INVENTORY_MODEL_ANCHOR)
    return (
        f"={prev_col}{inventory_row}"
        f"+if({col}{purchases_row}<>\"\",{col}{purchases_row},{col}{purchases_model_row})"
        f"-if({col}{sales_row}<>\"\",{col}{sales_row},{col}{sales_model_row})"
    )


def core_margin_ramp_formula(col: str, prev_col: str, *, core_row: int = 24, improvement_row: int = 28) -> str:
    return f"={prev_col}{core_row}+{col}{improvement_row}"


def cm_core_cell(col: str, prev_col: str | None, *, core_row: int = 24) -> str | float:
    if col in CM_CORE_VALUES:
        return CM_CORE_VALUES[col]
    if prev_col is None:
        raise ValueError(f"No prior column for CM core ramp at {col}")
    return core_margin_ramp_formula(col, prev_col, core_row=core_row)


def cm_adjustments_cell(col: str) -> float | None:
    return CM_ADJUSTMENTS_VALUES.get(col)


def cm_improvement_cell(col: str, col_idx: int) -> float | None:
    """Return improvement rate from col F (index 5) onward."""
    if col_idx >= 5:
        return CM_IMPROVEMENT_FROM_COL_F
    return None


def row_cells_for_label(
    label: str,
    n_cols: int,
    *,
    label_to_row: dict[str, int],
) -> list[str | float] | None:
    """Build a full B:… row of formulas/values for one model label."""
    if label in UNIFORM_FORMULAS:
        return [UNIFORM_FORMULAS[label]] * n_cols

    if label in COLUMN_RELATIVE:
        return [
            column_relative_formula(label, col_letter(col_idx + 2), label_to_row=label_to_row)
            for col_idx in range(n_cols)
        ]

    if label == "Homes in Inventory - Model":
        inventory_row = label_to_row[label]
        cells: list[str | float] = []
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            prev_col = col_letter(col_idx + 1) if col_idx > 0 else "A"
            cells.append(
                inventory_model_formula(col, prev_col, inventory_row=inventory_row)
            )
        return cells

    if label == SHARES_ADJUSTMENT_LABEL:
        sbc_row = label_to_row["Stock Based Compensation"]
        cells: list[str | float] = []
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            prev_col = col_letter(col_idx + 1) if col_idx > 0 else "A"
            cells.append(
                weekly_share_adjustment_formula(
                    col,
                    prev_col,
                    weekly_sbc_row=sbc_row,
                )
            )
        return cells

    if label == SHARES_MODEL_LABEL:
        actual_row = label_to_row["Basic Shares Outstanding"]
        model_row = label_to_row[SHARES_MODEL_LABEL]
        adj_row = label_to_row[SHARES_ADJUSTMENT_LABEL]
        cells = []
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            prev_col = col_letter(col_idx + 1) if col_idx > 0 else "A"
            cells.append(
                weekly_shares_model_formula(
                    col,
                    prev_col,
                    weekly_actual_shares_row=actual_row,
                    weekly_model_shares_row=model_row,
                    weekly_adjustment_row=adj_row,
                )
            )
        return cells

    return None


def cm_stack_updates(
    n_cols: int,
    *,
    label_to_row: dict[str, int],
    existing: dict[int, list],
) -> dict[int, list]:
    """Merge CM core ramp, adjustments, and improvement values into update dict."""
    core_row = label_to_row["Contribution Margin - Core"]
    adj_row = label_to_row["Contribution Margin - Adjustments"]
    imp_row = label_to_row["Contribution Margin Improvement - Core"]

    core_cells = list(existing.get(core_row, [""] * n_cols))
    if len(core_cells) < n_cols:
        core_cells += [""] * (n_cols - len(core_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        prev_col = col_letter(col_idx + 1) if col_idx > 0 else None
        core_cells[col_idx] = cm_core_cell(col, prev_col, core_row=core_row)

    adj_cells = list(existing.get(adj_row, [""] * n_cols))
    if len(adj_cells) < n_cols:
        adj_cells += [""] * (n_cols - len(adj_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        val = cm_adjustments_cell(col)
        if val is not None:
            adj_cells[col_idx] = val
        elif col_idx >= 7:  # extend −2% pattern from col H onward if sheet widens
            adj_cells[col_idx] = -0.02

    imp_cells = list(existing.get(imp_row, [""] * n_cols))
    if len(imp_cells) < n_cols:
        imp_cells += [""] * (n_cols - len(imp_cells))
    for col_idx in range(n_cols):
        val = cm_improvement_cell(col_letter(col_idx + 2), col_idx)
        if val is not None:
            imp_cells[col_idx] = val
        elif col_idx >= 5:
            imp_cells[col_idx] = CM_IMPROVEMENT_FROM_COL_F

    return {core_row: core_cells, adj_row: adj_cells, imp_row: imp_cells}
