"""Canonical Weekly Financials * - Model row formulas (synced from live sheet).

All weekly row references use {Label} placeholders resolved at restore time via
label_to_row — never hardcoded row numbers in templates. Run
scripts/validate_model_formulas.py after layout changes.
"""

from __future__ import annotations

import re

from sheets.formulas import (
    SBC_MODEL_LABEL,
    SHARES_MODEL_LABEL,
    weekly_gaap_below_line_model_formula,
    weekly_sbc_model_formula,
)
from sheets.gaap_below_the_line import (
    ADJ_EBITDA_MODEL_LABEL,
    ADJ_NET_INCOME_MODEL_LABEL,
    CEO_MAKE_WHOLE_LABEL,
    CEO_MAKE_WHOLE_MODEL_LABEL,
    DEBT_EXTINGUISHMENT_LABEL,
    DEBT_EXTINGUISHMENT_MODEL_LABEL,
    INTEREST_EXPENSE_LABEL,
    INTEREST_EXPENSE_MODEL_LABEL,
    INTEREST_EXPENSE_WEEKLY_RUN_RATE,
    INV_VAL_CURRENT_LABEL,
    INV_VAL_CURRENT_MODEL_LABEL,
    INV_VAL_CURRENT_WEEKLY_RUN_RATE,
    INV_VAL_PRIOR_LABEL,
    INV_VAL_PRIOR_MODEL_LABEL,
    INV_VAL_PRIOR_WEEKLY_RUN_RATE,
    OTHER_GAAP_ADJ_LABEL,
    OTHER_GAAP_ADJ_MODEL_LABEL,
    OTHER_INCOME_LABEL,
    OTHER_INCOME_MODEL_LABEL,
    OTHER_INCOME_WEEKLY_RUN_RATE,
    RESTRUCTURING_LABEL,
    RESTRUCTURING_MODEL_LABEL,
)
from sheets.cm_seasonality import (
    CM_SEASONALITY_ADJUSTMENTS_LABEL,
    CM_SEASONALITY_SHEET,
    CM_SEASONALITY_VALUE_RANGE,
)
from sheets.ancillary_products import (
    CM_MORTGAGE_LABEL,
    CM_TITLE_LABEL,
    DOMA_GROWTH_MULTIPLIER_LABEL,
    DOMA_REFI_PROFIT_LABEL,
    OPEN_MORTGAGE_PERCENT_LABEL,
    OPEN_TITLE_PURCHASE_PERCENT_LABEL,
    ASP_LABEL,
    cm_mortgage_formula,
    cm_title_formula,
    open_mortgage_percent_formula,
    open_title_purchase_percent_formula,
)
from sheets.shares_events import (
    SHARES_ADJUSTMENT_LABEL,
    weekly_share_adjustment_formula,
    weekly_shares_model_formula,
)
from sheets.doma_manual_cells import DOMA_GROWTH_MULTIPLIER_CELLS, DOMA_REFI_PROFIT_CELLS
from sheets.open_transition import (
    HOME_SALES_1_0_MODEL_LABEL,
    HOME_SALES_2_0_MODEL_LABEL,
    NEW_LISTINGS_1_0_MODEL_LABEL,
    NEW_LISTINGS_2_0_MODEL_LABEL,
    OPEN_1_0_LISTING_ROW,
    OPEN_1_0_RETENTION_ROW,
    OPEN_1_0_SOLD_ROW,
    OPEN_1_0_SOLD_WEEKS,
    OPEN_2_0_LISTING_ROW,
    OPEN_2_0_RETENTION_ROW,
    OPEN_2_0_SOLD_ROW,
    OPEN_2_0_SOLD_WEEKS,
    REVENUE_1_0_MODEL_LABEL,
    REVENUE_2_0_MODEL_LABEL,
    TRANSITION_COMPLETENESS_LABEL,
    home_sales_model_formula,
    new_listings_model_formula,
    private_home_sales_model_formula,
    revenue_model_formula,
    transition_completeness_formula,
    blend_model_formula,
)

GAAP_NET_INCOME_MODEL_LABEL = (
    "Net Income (Loss) Attributable to Common Shareholders - Model"
)

INVENTORY_MODEL_ANCHOR = 3275

CM_CORE_VALUES: dict[str, float] = {
    "B": 0.034,
    "AA": 0.036,
}
CM_ADJUSTMENTS_VALUES: dict[str, float] = {
    "B": -0.015,
    "C": -0.014,
    "D": -0.014,
    "E": -0.014,
    "F": -0.014,
    "G": -0.013,
    "H": -0.011,
    "I": -0.009,
    "J": -0.007,
    "K": -0.005,
    "L": -0.004,
    "M": -0.004,
    "N": -0.003,
    "O": -0.002,
    "P": 0,
    "Q": 0,
    "R": 0,
    "S": 0,
    "T": 0,
    "U": 0,
    "V": 0,
    "W": 0,
    "X": 0,
    "Y": 0,
    "Z": 0,
    "AA": -0.002,
    "AB": -0.002,
    "AC": -0.003,
    "AD": -0.003,
    "AE": -0.005,
    "AF": -0.005,
    "AG": -0.006,
    "AH": -0.006,
    "AI": -0.006,
    "AJ": -0.007,
    "AK": -0.008,
    "AL": -0.008,
    "AM": -0.008,
    "AN": -0.008,
    "AO": -0.008,
    "AP": -0.007,
    "AQ": -0.007,
    "AR": -0.007,
    "AS": -0.007,
    "AT": -0.007,
    "AU": -0.007,
    "AV": -0.007,
    "AW": -0.007,
    "AX": -0.007,
    "AY": -0.007,
    "AZ": -0.007,
    "BA": 0,
    "BB": 0,
    "BC": 0,
    "BD": 0,
    "BE": 0,
    "BF": 0,
    "BG": 0,
    "BH": 0,
    "BI": 0,
    "BJ": 0,
    "BK": 0,
    "BL": 0,
    "BM": 0,
    "BN": 0,
    "BO": 0,
    "BP": 0,
    "BQ": 0,
    "BR": 0,
    "BS": 0,
    "BT": 0,
    "BU": 0,
    "BV": 0,
    "BW": 0,
    "BX": 0,
    "BY": 0,
    "BZ": 0,
    "CA": 0,
    "CB": 0,
    "CC": 0,
    "CD": 0,
    "CE": 0,
    "CF": 0,
    "CG": 0,
    "CH": 0,
    "CI": 0,
    "CJ": 0,
    "CK": 0,
    "CL": 0,
    "CM": 0,
    "CN": 0,
    "CO": 0,
    "CP": 0,
    "CQ": 0,
    "CR": 0,
    "CS": 0,
    "CT": 0,
    "CU": 0,
    "CV": 0,
    "CW": 0,
    "CX": 0,
    "CY": 0,
    "CZ": 0,
    "DA": 0,
    "DB": 0,
    "DC": 0,
    "DD": 0,
    "DE": 0,
    "DF": 0,
    "DG": 0,
    "DH": 0,
    "DI": 0,
    "DJ": 0,
    "DK": 0,
    "DL": 0,
    "DM": 0,
    "DN": 0,
    "DO": 0,
    "DP": 0,
    "DQ": 0,
    "DR": 0,
    "DS": 0,
    "DT": 0,
    "DU": 0,
    "DV": 0,
    "DW": 0,
    "DX": 0,
    "DY": 0,
}
CM_IMPROVEMENT_ANCHORS: dict[str, float] = {
    "F": 0.0001,
    "U": 0.0002,
    "AP": 0.0003,
    "BC": 0.0004,
    "BE": 0.001,
    "BS": 0,
}
# First column (0-based from B) with seasonality INDEX formula; B onward on live sheet.
CM_SEASONALITY_FORMULA_FROM_COL_IDX = 0
# First column (0-based from B) defaulting adjustments to 0 when not in CM_ADJUSTMENTS_VALUES.
CM_ADJUSTMENTS_ZERO_FROM_COL_IDX = 42  # AR

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
    "New Listings - 2.0 Model": new_listings_model_formula(
        listing_row=OPEN_2_0_LISTING_ROW, include_backlog=False
    ),
    "New Listings - 1.0 Model": new_listings_model_formula(
        listing_row=OPEN_1_0_LISTING_ROW, include_backlog=True
    ),
    "Private Home Sales - Model": private_home_sales_model_formula(),
    "Home Sales - 2.0 Model": home_sales_model_formula(
        sold_row=OPEN_2_0_SOLD_ROW, sold_weeks=OPEN_2_0_SOLD_WEEKS
    ),
    "Home Sales - 1.0 Model": home_sales_model_formula(
        sold_row=OPEN_1_0_SOLD_ROW, sold_weeks=OPEN_1_0_SOLD_WEEKS
    ),
    "Revenue - 2.0 Model": revenue_model_formula(
        sold_row=OPEN_2_0_SOLD_ROW,
        retention_row=OPEN_2_0_RETENTION_ROW,
        sold_weeks=OPEN_2_0_SOLD_WEEKS,
    ),
    "Revenue - 1.0 Model": revenue_model_formula(
        sold_row=OPEN_1_0_SOLD_ROW,
        retention_row=OPEN_1_0_RETENTION_ROW,
        sold_weeks=OPEN_1_0_SOLD_WEEKS,
    ),
    "Fixed Costs - Model": "=35000000/13",
    "Net Interest Expense - Model": "=20000000/13",
}

COLUMN_RELATIVE_TEMPLATES: dict[str, str] = {
    "Acquisition Contracts - Model": (
        "={c}{Acquisition Contracts - no seasonality}*{c}{Acquisition Seasonality Multiplier}"
    ),
    "Contribution Profit - Model": (
        "={c}{Revenue - Model}*{c}{Contribution Margin - Model}"
    ),
    "Contribution Margin - Model": (
        "={c}{Contribution Margin - Core}+{c}{Contribution Margin - Mortgage}"
        "+{c}{Contribution Margin - Title and Escrow}"
        "+{c}{Contribution Margin - Seasonality Adjustments}"
        "+{c}{Contribution Margin - Adjustments}"
    ),
    "Adjusted Operating Expenses - Model": (
        "={c}{Fixed Costs - Model}+(15000000/13)"
    ),
    ADJ_EBITDA_MODEL_LABEL: (
        "={c}{Contribution Profit - Model}-{c}{Adjusted Operating Expenses - Model}"
    ),
    ADJ_NET_INCOME_MODEL_LABEL: (
        "={c}{Adjusted EBITDA - Model}-{c}{Net Interest Expense - Model}"
        "-{c}{Depreciation and Amortization}-{c}{Taxes}"
    ),
    GAAP_NET_INCOME_MODEL_LABEL: (
        "={c}{Adjusted Net Income - Model}+{c}{(Loss) Gain on Extinguishment of Debt - Model}"
        "-{c}{Stock Based Compensation - Model}"
        "-{c}{Inventory Valuation Adjustment - Current Period - Model}"
        "-{c}{Inventory Valuation Adjustment - Prior Periods - Model}"
        "-{c}{Restructuring - Model}-{c}{CEO Make-Whole Provision - Model}"
        "-{c}{Other GAAP Adjustments - Model}"
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
        {
            TRANSITION_COMPLETENESS_LABEL,
            NEW_LISTINGS_2_0_MODEL_LABEL,
            NEW_LISTINGS_1_0_MODEL_LABEL,
        }
    ),
    NEW_LISTINGS_2_0_MODEL_LABEL: frozenset(
        {"Homes Purchased - Model", "Likelihood to List"}
    ),
    NEW_LISTINGS_1_0_MODEL_LABEL: frozenset(
        {"Homes Purchased - Model", "Likelihood to List"}
    ),
    "Private Home Sales - Model": frozenset(
        {"Homes Purchased", "Homes Purchased - Model", "Likelihood to List"}
    ),
    "Home Sales - Model": frozenset(
        {
            TRANSITION_COMPLETENESS_LABEL,
            HOME_SALES_2_0_MODEL_LABEL,
            HOME_SALES_1_0_MODEL_LABEL,
        }
    ),
    HOME_SALES_2_0_MODEL_LABEL: frozenset(
        {
            "New Listings",
            "New Listings - Model",
            "Likelihood to List",
            "Private Home Sales - Model",
        }
    ),
    HOME_SALES_1_0_MODEL_LABEL: frozenset(
        {
            "New Listings",
            "New Listings - Model",
            "Likelihood to List",
            "Private Home Sales - Model",
        }
    ),
    "Revenue - Model": frozenset(
        {
            TRANSITION_COMPLETENESS_LABEL,
            REVENUE_2_0_MODEL_LABEL,
            REVENUE_1_0_MODEL_LABEL,
        }
    ),
    REVENUE_2_0_MODEL_LABEL: frozenset(
        {
            "New Listings",
            "New Listings - Model",
            "Average Sale Price (homes sold by OPEN)",
            "Private Home Sales - Model",
        }
    ),
    REVENUE_1_0_MODEL_LABEL: frozenset(
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
        {"Acquisition Contracts - no seasonality", "Acquisition Seasonality Multiplier"}
    ),
    "Contribution Profit - Model": frozenset(
        {
            "Revenue - Model",
            "Contribution Margin - Model",
        }
    ),
    DOMA_GROWTH_MULTIPLIER_LABEL: frozenset(),
    DOMA_REFI_PROFIT_LABEL: frozenset({DOMA_GROWTH_MULTIPLIER_LABEL}),
    "Contribution Margin - Model": frozenset(
        {
            "Contribution Margin - Core",
            "Contribution Margin - Mortgage",
            "Contribution Margin - Title and Escrow",
            "Contribution Margin - Seasonality Adjustments",
            "Contribution Margin - Adjustments",
        }
    ),
    "Adjusted Operating Expenses - Model": frozenset({"Fixed Costs - Model"}),
    ADJ_EBITDA_MODEL_LABEL: frozenset(
        {
            "Contribution Profit - Model",
            "Adjusted Operating Expenses - Model",
        }
    ),
    ADJ_NET_INCOME_MODEL_LABEL: frozenset(
        {
            ADJ_EBITDA_MODEL_LABEL,
            "Net Interest Expense - Model",
            "Depreciation and Amortization",
            "Taxes",
        }
    ),
    GAAP_NET_INCOME_MODEL_LABEL: frozenset(
        {
            ADJ_NET_INCOME_MODEL_LABEL,
            DEBT_EXTINGUISHMENT_MODEL_LABEL,
            SBC_MODEL_LABEL,
            INV_VAL_CURRENT_MODEL_LABEL,
            INV_VAL_PRIOR_MODEL_LABEL,
            RESTRUCTURING_MODEL_LABEL,
            CEO_MAKE_WHOLE_MODEL_LABEL,
            OTHER_GAAP_ADJ_MODEL_LABEL,
        }
    ),
    DEBT_EXTINGUISHMENT_MODEL_LABEL: frozenset({DEBT_EXTINGUISHMENT_LABEL}),
    INTEREST_EXPENSE_MODEL_LABEL: frozenset({INTEREST_EXPENSE_LABEL}),
    OTHER_INCOME_MODEL_LABEL: frozenset({OTHER_INCOME_LABEL}),
    INV_VAL_CURRENT_MODEL_LABEL: frozenset({INV_VAL_CURRENT_LABEL}),
    INV_VAL_PRIOR_MODEL_LABEL: frozenset({INV_VAL_PRIOR_LABEL}),
    RESTRUCTURING_MODEL_LABEL: frozenset({RESTRUCTURING_LABEL}),
    CEO_MAKE_WHOLE_MODEL_LABEL: frozenset({CEO_MAKE_WHOLE_LABEL}),
    OTHER_GAAP_ADJ_MODEL_LABEL: frozenset({OTHER_GAAP_ADJ_LABEL}),
    "Earnings per Share - Model": frozenset(
        {GAAP_NET_INCOME_MODEL_LABEL, SHARES_MODEL_LABEL}
    ),
    "Homes in Inventory - Model": frozenset(
        {
            "Homes in Inventory",
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
    OPEN_MORTGAGE_PERCENT_LABEL: frozenset(),
    OPEN_TITLE_PURCHASE_PERCENT_LABEL: frozenset(),
    CM_MORTGAGE_LABEL: frozenset({OPEN_MORTGAGE_PERCENT_LABEL, ASP_LABEL}),
    CM_TITLE_LABEL: frozenset({OPEN_TITLE_PURCHASE_PERCENT_LABEL, ASP_LABEL}),
    TRANSITION_COMPLETENESS_LABEL: frozenset(),
}

MODEL_FORMULA_LABELS: tuple[str, ...] = (
    "Acquisition Contracts - Model",
    TRANSITION_COMPLETENESS_LABEL,
    "New Listings - Model",
    NEW_LISTINGS_2_0_MODEL_LABEL,
    NEW_LISTINGS_1_0_MODEL_LABEL,
    *(
        label
        for label in UNIFORM_FORMULA_TEMPLATES.keys()
        if label
        not in {
            NEW_LISTINGS_2_0_MODEL_LABEL,
            NEW_LISTINGS_1_0_MODEL_LABEL,
            HOME_SALES_2_0_MODEL_LABEL,
            HOME_SALES_1_0_MODEL_LABEL,
            REVENUE_2_0_MODEL_LABEL,
            REVENUE_1_0_MODEL_LABEL,
        }
    ),
    "Home Sales - Model",
    HOME_SALES_2_0_MODEL_LABEL,
    HOME_SALES_1_0_MODEL_LABEL,
    "Revenue - Model",
    REVENUE_2_0_MODEL_LABEL,
    REVENUE_1_0_MODEL_LABEL,
    *COLUMN_RELATIVE_TEMPLATES.keys(),
    OPEN_MORTGAGE_PERCENT_LABEL,
    OPEN_TITLE_PURCHASE_PERCENT_LABEL,
    CM_MORTGAGE_LABEL,
    CM_TITLE_LABEL,
    DOMA_GROWTH_MULTIPLIER_LABEL,
    DOMA_REFI_PROFIT_LABEL,
    SBC_MODEL_LABEL,
    DEBT_EXTINGUISHMENT_MODEL_LABEL,
    INTEREST_EXPENSE_MODEL_LABEL,
    OTHER_INCOME_MODEL_LABEL,
    INV_VAL_CURRENT_MODEL_LABEL,
    INV_VAL_PRIOR_MODEL_LABEL,
    RESTRUCTURING_MODEL_LABEL,
    CEO_MAKE_WHOLE_MODEL_LABEL,
    OTHER_GAAP_ADJ_MODEL_LABEL,
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
    return apply_row_labels(template, label_to_row).format(c=col)


def inventory_model_formula(
    col: str,
    prev_col: str,
    *,
    label_to_row: dict[str, int],
    inventory_row: int,
) -> str:
    inventory_actual_row = label_to_row["Homes in Inventory"]
    purchases_row = label_to_row["Homes Purchased"]
    purchases_model_row = label_to_row["Homes Purchased - Model"]
    sales_row = label_to_row["Home Sales"]
    sales_model_row = label_to_row["Home Sales - Model"]
    roll_forward = (
        f"{prev_col}{inventory_row}"
        f"+if({col}{purchases_row}<>\"\",{col}{purchases_row},{col}{purchases_model_row})"
        f"-if({col}{sales_row}<>\"\",{col}{sales_row},{col}{sales_model_row})"
    )
    if col == "B":
        return (
            f"=IF(B{inventory_actual_row}<>\"\",B{inventory_actual_row},"
            f"{INVENTORY_MODEL_ANCHOR})"
        )
    return (
        f"=IF({col}{inventory_actual_row}<>\"\",{col}{inventory_actual_row},"
        f"{roll_forward})"
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


def cm_seasonality_adjustments_formula(col: str) -> str:
    return (
        f"=INDEX('{CM_SEASONALITY_SHEET}'!{CM_SEASONALITY_VALUE_RANGE}, "
        f"MONTH({col}$1))"
    )


def cm_adjustments_cell(col: str) -> float | None:
    return CM_ADJUSTMENTS_VALUES.get(col)


def cm_improvement_cell(
    col: str, col_idx: int, *, imp_row: int
) -> str | float | None:
    if col in CM_IMPROVEMENT_ANCHORS:
        return CM_IMPROVEMENT_ANCHORS[col]
    if col_idx < 4:
        return None
    prev_col = col_letter(col_idx + 1)
    return f"={prev_col}{imp_row}"


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

    if label == TRANSITION_COMPLETENESS_LABEL:
        return [
            transition_completeness_formula(col_letter(col_idx + 2))
            for col_idx in range(n_cols)
        ]

    blend_specs: dict[str, tuple[str, str]] = {
        "New Listings - Model": (NEW_LISTINGS_2_0_MODEL_LABEL, NEW_LISTINGS_1_0_MODEL_LABEL),
        "Home Sales - Model": (HOME_SALES_2_0_MODEL_LABEL, HOME_SALES_1_0_MODEL_LABEL),
        "Revenue - Model": (REVENUE_2_0_MODEL_LABEL, REVENUE_1_0_MODEL_LABEL),
    }
    if label in blend_specs:
        model_2_0, model_1_0 = blend_specs[label]
        return [
            blend_model_formula(
                col_letter(col_idx + 2),
                label_to_row=label_to_row,
                blended_label=label,
                model_2_0_label=model_2_0,
                model_1_0_label=model_1_0,
            )
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

    if label == DEBT_EXTINGUISHMENT_MODEL_LABEL:
        actual_row = label_to_row[DEBT_EXTINGUISHMENT_LABEL]
        return [
            weekly_gaap_below_line_model_formula(
                col_letter(col_idx + 2),
                weekly_actual_row=actual_row,
                weekly_run_rate=0,
            )
            for col_idx in range(n_cols)
        ]

    if label == INTEREST_EXPENSE_MODEL_LABEL:
        actual_row = label_to_row[INTEREST_EXPENSE_LABEL]
        return [
            weekly_gaap_below_line_model_formula(
                col_letter(col_idx + 2),
                weekly_actual_row=actual_row,
                weekly_run_rate=INTEREST_EXPENSE_WEEKLY_RUN_RATE,
            )
            for col_idx in range(n_cols)
        ]

    if label == OTHER_INCOME_MODEL_LABEL:
        actual_row = label_to_row[OTHER_INCOME_LABEL]
        return [
            weekly_gaap_below_line_model_formula(
                col_letter(col_idx + 2),
                weekly_actual_row=actual_row,
                weekly_run_rate=OTHER_INCOME_WEEKLY_RUN_RATE,
            )
            for col_idx in range(n_cols)
        ]

    _adj_to_gaap_model_specs: dict[str, tuple[str, float]] = {
        INV_VAL_CURRENT_MODEL_LABEL: (
            INV_VAL_CURRENT_LABEL,
            INV_VAL_CURRENT_WEEKLY_RUN_RATE,
        ),
        INV_VAL_PRIOR_MODEL_LABEL: (
            INV_VAL_PRIOR_LABEL,
            INV_VAL_PRIOR_WEEKLY_RUN_RATE,
        ),
        RESTRUCTURING_MODEL_LABEL: (RESTRUCTURING_LABEL, 0),
        CEO_MAKE_WHOLE_MODEL_LABEL: (CEO_MAKE_WHOLE_LABEL, 0),
        OTHER_GAAP_ADJ_MODEL_LABEL: (OTHER_GAAP_ADJ_LABEL, 0),
    }
    if label in _adj_to_gaap_model_specs:
        actual_label, run_rate = _adj_to_gaap_model_specs[label]
        actual_row = label_to_row[actual_label]
        return [
            weekly_gaap_below_line_model_formula(
                col_letter(col_idx + 2),
                weekly_actual_row=actual_row,
                weekly_run_rate=run_rate,
            )
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

    if label == OPEN_MORTGAGE_PERCENT_LABEL:
        return [open_mortgage_percent_formula(col_letter(col_idx + 2)) for col_idx in range(n_cols)]

    if label == OPEN_TITLE_PURCHASE_PERCENT_LABEL:
        return [
            open_title_purchase_percent_formula(col_letter(col_idx + 2))
            for col_idx in range(n_cols)
        ]

    if label == CM_MORTGAGE_LABEL:
        return [
            cm_mortgage_formula(col_letter(col_idx + 2), label_to_row=label_to_row)
            for col_idx in range(n_cols)
        ]

    if label == CM_TITLE_LABEL:
        return [
            cm_title_formula(col_letter(col_idx + 2), label_to_row=label_to_row)
            for col_idx in range(n_cols)
        ]

    if label == DOMA_GROWTH_MULTIPLIER_LABEL:
        return list(DOMA_GROWTH_MULTIPLIER_CELLS[:n_cols])

    if label == DOMA_REFI_PROFIT_LABEL:
        return list(DOMA_REFI_PROFIT_CELLS[:n_cols])

    return None


def cm_stack_updates(
    n_cols: int,
    *,
    label_to_row: dict[str, int],
    existing: dict[int, list],
) -> dict[int, list]:
    core_row = label_to_row["Contribution Margin - Core"]
    seas_row = label_to_row[CM_SEASONALITY_ADJUSTMENTS_LABEL]
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

    seas_cells = list(existing.get(seas_row, [""] * n_cols))
    if len(seas_cells) < n_cols:
        seas_cells += [""] * (n_cols - len(seas_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        if col_idx >= CM_SEASONALITY_FORMULA_FROM_COL_IDX:
            seas_cells[col_idx] = cm_seasonality_adjustments_formula(col)

    adj_cells = list(existing.get(adj_row, [""] * n_cols))
    if len(adj_cells) < n_cols:
        adj_cells += [""] * (n_cols - len(adj_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        val = cm_adjustments_cell(col)
        if val is not None:
            adj_cells[col_idx] = val
        elif col_idx >= CM_ADJUSTMENTS_ZERO_FROM_COL_IDX:
            adj_cells[col_idx] = 0

    imp_cells = list(existing.get(imp_row, [""] * n_cols))
    if len(imp_cells) < n_cols:
        imp_cells += [""] * (n_cols - len(imp_cells))
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        val = cm_improvement_cell(col, col_idx, imp_row=imp_row)
        if val is not None:
            imp_cells[col_idx] = val

    return {
        core_row: core_cells,
        seas_row: seas_cells,
        adj_row: adj_cells,
        imp_row: imp_cells,
    }
