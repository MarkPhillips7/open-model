"""Canonical Weekly Financials * - Model row formulas (synced from live sheet).

All weekly row references use {Label} placeholders resolved at restore time via
label_to_row — never hardcoded row numbers in templates. Run
scripts/validate_model_formulas.py after layout changes.
"""

from __future__ import annotations

import re

from sheets.formulas import SBC_MODEL_LABEL, SHARES_MODEL_LABEL, weekly_sbc_model_formula
from sheets.shares_events import (
    SHARES_ADJUSTMENT_LABEL,
    weekly_share_adjustment_formula,
    weekly_shares_model_formula,
)

GAAP_NET_INCOME_MODEL_LABEL = (
    "Net Income (Loss) Attributable to Common Shareholders - Model"
)

INVENTORY_MODEL_ANCHOR = 3275

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

# {Label} → row number at restore time. Uses COLUMN() — same string in every column.
UNIFORM_FORMULA_TEMPLATES: dict[str, str] = {
    "Homes Purchased - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      contracts, IF(col < 2, 130,
        IF(INDEX(${Acquisition Contracts}:${Acquisition Contracts}, 1, col) = "",
          INDEX(${Acquisition Contracts - Model}:${Acquisition Contracts - Model}, 1, col),
          INDEX(${Acquisition Contracts}:${Acquisition Contracts}, 1, col)
        )
      ),
      l2c, IF(col < 2, $B${Likelihood to Close}, INDEX(${Likelihood to Close}:${Likelihood to Close}, 1, col)),
      contracts * l2c
    )
  )),
  Transitions!$B$2:$J$2
))""",
    "New Listings - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      purchases, IF(col < 2, 90, INDEX(${Homes Purchased}:${Homes Purchased}, 1, col)*INDEX(${Likelihood to List}:${Likelihood to List}, 1, col)),
      purchases
    )
  )),
  Transitions!$B$4:$J$4
)+IF(COLUMN()-1<=8, Transitions!$B$21*INDEX(Transitions!$B$23:$I$23, 1, COLUMN()-1), 0))""",
    "Private Home Sales - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 15,
        IF(INDEX(${Homes Purchased}:${Homes Purchased}, 1, col) = "",
          INDEX(${Homes Purchased - Model}:${Homes Purchased - Model}, 1, col),
          INDEX(${Homes Purchased}:${Homes Purchased}, 1, col)
        )*(1-INDEX(${Likelihood to List}:${Likelihood to List}, 1, col))
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
        IF(INDEX(${New Listings}:${New Listings}, 1, col) = "",
          INDEX(${New Listings - Model}:${New Listings - Model}, 1, col),
          INDEX(${New Listings}:${New Listings}, 1, col)
        )*INDEX(${Likelihood to List}:${Likelihood to List}, 1, col)
      )
    )
  )),
  Transitions!$B$10:$V$10
)+INDEX(${Private Home Sales - Model}:${Private Home Sales - Model}, 1, COLUMN()))""",
    "Revenue - Model": """=(SUMPRODUCT(
  MAP(SEQUENCE(1,21), LAMBDA(lag,
    LET(
      col, COLUMN() - lag - Transitions!$B$15,
      IF(col < 2, 220*377500,
        IF(INDEX(${New Listings}:${New Listings}, 1, col) = "",
          INDEX(${New Listings - Model}:${New Listings - Model}, 1, col),
          INDEX(${New Listings}:${New Listings}, 1, col)
        )*INDEX(${Average Sale Price (homes sold by OPEN)}:${Average Sale Price (homes sold by OPEN)}, 1, col)
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
        IF(INDEX(${New Listings}:${New Listings}, 1, col) = "",
          INDEX(${New Listings - Model}:${New Listings - Model}, 1, col),
          INDEX(${New Listings}:${New Listings}, 1, col)
        )*INDEX(${Average Sale Price (homes sold by OPEN)}:${Average Sale Price (homes sold by OPEN)}, 1, col)
      )
    )
  )),
  Transitions!$B$10:$V$10,
  Transitions!$B$12:$V$12
)*(1-Transitions!$B$16)+INDEX(${Private Home Sales - Model}:${Private Home Sales - Model}, 1, COLUMN())*INDEX(${Average Sale Price (homes sold by OPEN)}:${Average Sale Price (homes sold by OPEN)}, 1, COLUMN()))""",
    "Fixed Costs - Model": "=35000000/13",
    "Net Interest Expense - Model": "=20000000/13",
}

COLUMN_RELATIVE_TEMPLATES: dict[str, str] = {
    "Acquisition Contracts - Model": (
        "={c}{Acquisition Contracts - no seasonality}*{c}{Seasonality Multiplier}"
    ),
    "Contribution Profit - Model": (
        "={c}{Revenue - Model}*{c}{Contribution Margin - Model}"
    ),
    "Contribution Margin - Model": (
        "={c}{Contribution Margin - Core}+{c}{Contribution Margin - Mortgage}"
        "+{c}{Contribution Margin - Title and Escrow}+{c}{Contribution Margin - Adjustments}"
    ),
    "Adjusted Operating Expenses - Model": (
        "={c}{Fixed Costs - Model}+(15000000/13)"
    ),
    GAAP_NET_INCOME_MODEL_LABEL: (
        "={c}{cp}-{c}{opex}-{c}{sbc}-{c}{interest}-{c}{da}-{c}{tax}"
    ),
    "Earnings per Share - Model": (
        '=IF(N({c}{shares_row})=0,"",{c}{gaap_row}/{c}{shares_row})'
    ),
}

# Labels each model formula must read from (for validation).
FORMULA_ROW_DEPENDENCIES: dict[str, frozenset[str]] = {
    "Homes Purchased - Model": frozenset(
        {"Acquisition Contracts", "Acquisition Contracts - Model", "Likelihood to Close"}
    ),
    "New Listings - Model": frozenset(
        {"Homes Purchased", "Likelihood to List"}
    ),
    "Private Home Sales - Model": frozenset(
        {"Homes Purchased", "Homes Purchased - Model", "Likelihood to List"}
    ),
    "Home Sales - Model": frozenset(
        {"New Listings", "New Listings - Model", "Likelihood to List", "Private Home Sales - Model"}
    ),
    "Revenue - Model": frozenset(
        {
            "New Listings",
            "New Listings - Model",
            "Average Sale Price (homes sold by OPEN)",
            "Private Home Sales - Model",
        }
    ),
    "Fixed Costs - Model": frozenset(),
    "Net Interest Expense - Model": frozenset(),
    "Acquisition Contracts - Model": frozenset(
        {"Acquisition Contracts - no seasonality", "Seasonality Multiplier"}
    ),
    "Contribution Profit - Model": frozenset(
        {"Revenue - Model", "Contribution Margin - Model"}
    ),
    "Contribution Margin - Model": frozenset(
        {
            "Contribution Margin - Core",
            "Contribution Margin - Mortgage",
            "Contribution Margin - Title and Escrow",
            "Contribution Margin - Adjustments",
        }
    ),
    "Adjusted Operating Expenses - Model": frozenset({"Fixed Costs - Model"}),
    GAAP_NET_INCOME_MODEL_LABEL: frozenset(
        {
            "Contribution Profit - Model",
            "Adjusted Operating Expenses - Model",
            SBC_MODEL_LABEL,
            "Net Interest Expense - Model",
            "Depreciation and Amortization",
            "Taxes",
        }
    ),
    "Earnings per Share - Model": frozenset(
        {GAAP_NET_INCOME_MODEL_LABEL, SHARES_MODEL_LABEL}
    ),
    "Homes in Inventory - Model": frozenset(
        {
            "Homes Purchased",
            "Homes Purchased - Model",
            "Home Sales",
            "Home Sales - Model",
        }
    ),
    SBC_MODEL_LABEL: frozenset({"Stock Based Compensation"}),
    SHARES_ADJUSTMENT_LABEL: frozenset({SBC_MODEL_LABEL}),
    SHARES_MODEL_LABEL: frozenset(
        {
            "Basic Shares Outstanding",
            SHARES_ADJUSTMENT_LABEL,
        }
    ),
}

MODEL_FORMULA_LABELS: tuple[str, ...] = (
    "Acquisition Contracts - Model",
    *UNIFORM_FORMULA_TEMPLATES.keys(),
    *COLUMN_RELATIVE_TEMPLATES.keys(),
    SBC_MODEL_LABEL,
    SHARES_ADJUSTMENT_LABEL,
    SHARES_MODEL_LABEL,
    "Homes in Inventory - Model",
)

_LABEL_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")


def apply_row_labels(template: str, label_to_row: dict[str, int]) -> str:
    """Replace {Label Name} placeholders with current row numbers (longest labels first)."""
    out = template
    for label in sorted(label_to_row, key=len, reverse=True):
        out = out.replace("{" + label + "}", str(label_to_row[label]))
    return out


def uniform_formula_template(label: str) -> str:
    return UNIFORM_FORMULA_TEMPLATES[label]


def formula_row_dependencies(label: str) -> frozenset[str]:
    return FORMULA_ROW_DEPENDENCIES[label]


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
    if label_to_row is None:
        raise ValueError(f"label_to_row required for {label!r}")

    template = COLUMN_RELATIVE_TEMPLATES[label]
    if label == "Earnings per Share - Model":
        return template.format(
            c=col,
            gaap_row=label_to_row[GAAP_NET_INCOME_MODEL_LABEL],
            shares_row=label_to_row[SHARES_MODEL_LABEL],
        )
    if label == GAAP_NET_INCOME_MODEL_LABEL:
        return template.format(
            c=col,
            cp=label_to_row["Contribution Profit - Model"],
            opex=label_to_row["Adjusted Operating Expenses - Model"],
            sbc=label_to_row[SBC_MODEL_LABEL],
            interest=label_to_row["Net Interest Expense - Model"],
            da=label_to_row["Depreciation and Amortization"],
            tax=label_to_row["Taxes"],
        )
    return apply_row_labels(template, label_to_row).format(c=col)


def inventory_model_formula(
    col: str,
    prev_col: str,
    *,
    label_to_row: dict[str, int],
    inventory_row: int,
) -> str:
    purchases_row = label_to_row["Homes Purchased"]
    purchases_model_row = label_to_row["Homes Purchased - Model"]
    sales_row = label_to_row["Home Sales"]
    sales_model_row = label_to_row["Home Sales - Model"]
    if col == "B":
        return str(INVENTORY_MODEL_ANCHOR)
    return (
        f"={prev_col}{inventory_row}"
        f"+if({col}{purchases_row}<>\"\",{col}{purchases_row},{col}{purchases_model_row})"
        f"-if({col}{sales_row}<>\"\",{col}{sales_row},{col}{sales_model_row})"
    )


def core_margin_ramp_formula(col: str, prev_col: str, *, core_row: int, improvement_row: int) -> str:
    return f"={prev_col}{core_row}+{col}{improvement_row}"


def cm_core_cell(
    col: str,
    prev_col: str | None,
    *,
    core_row: int,
    improvement_row: int,
) -> str | float:
    if col in CM_CORE_VALUES:
        return CM_CORE_VALUES[col]
    if prev_col is None:
        raise ValueError(f"No prior column for CM core ramp at {col}")
    return core_margin_ramp_formula(
        col, prev_col, core_row=core_row, improvement_row=improvement_row
    )


def cm_adjustments_cell(col: str) -> float | None:
    return CM_ADJUSTMENTS_VALUES.get(col)


def cm_improvement_cell(col: str, col_idx: int) -> float | None:
    if col_idx >= 5:
        return CM_IMPROVEMENT_FROM_COL_F
    return None


def row_cells_for_label(
    label: str,
    n_cols: int,
    *,
    label_to_row: dict[str, int],
) -> list[str | float] | None:
    if label in UNIFORM_FORMULA_TEMPLATES:
        formula = apply_row_labels(UNIFORM_FORMULA_TEMPLATES[label], label_to_row)
        return [formula] * n_cols

    if label in COLUMN_RELATIVE_TEMPLATES:
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
                inventory_model_formula(
                    col, prev_col, label_to_row=label_to_row, inventory_row=inventory_row
                )
            )
        return cells

    if label == SBC_MODEL_LABEL:
        actual_row = label_to_row["Stock Based Compensation"]
        return [
            weekly_sbc_model_formula(col_letter(col_idx + 2), weekly_actual_sbc_row=actual_row)
            for col_idx in range(n_cols)
        ]

    if label == SHARES_ADJUSTMENT_LABEL:
        sbc_row = label_to_row[SBC_MODEL_LABEL]
        cells: list[str | float] = []
        for col_idx in range(n_cols):
            col = col_letter(col_idx + 2)
            prev_col = col_letter(col_idx + 1) if col_idx > 0 else "A"
            cells.append(
                weekly_share_adjustment_formula(col, prev_col, weekly_sbc_row=sbc_row)
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
    core_row = label_to_row["Contribution Margin - Core"]
    adj_row = label_to_row["Contribution Margin - Adjustments"]
    imp_row = label_to_row["Contribution Margin Improvement - Core"]

    core_cells = list(existing.get(core_row, [""] * n_cols))
    if len(core_cells) < n_cols:
        core_cells += [""] * (n_cols - len(core_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        prev_col = col_letter(col_idx + 1) if col_idx > 0 else None
        core_cells[col_idx] = cm_core_cell(
            col, prev_col, core_row=core_row, improvement_row=imp_row
        )

    adj_cells = list(existing.get(adj_row, [""] * n_cols))
    if len(adj_cells) < n_cols:
        adj_cells += [""] * (n_cols - len(adj_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        val = cm_adjustments_cell(col)
        if val is not None:
            adj_cells[col_idx] = val
        elif col_idx >= 7:
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
