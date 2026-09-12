"""Senior vs mezzanine warehouse (inventory) financing on Weekly / Quarterly Financials.

Rates and mix are weekly levers (carry forward; overwrite a week to step).
Outstanding balances are quarter-end actuals from 10-Q facility tables, interpolated
like Homes in Inventory. Model debt scales with inventory, CNML capital intensity
(less cash at close on 2P homes), and splits by mezzanine share so a cheaper mix
(less mezz, more senior) cuts Warehouse Interest Expense.
"""

from __future__ import annotations

from .cnml import cnml_intensity_ratio_expr

SENIOR_INTEREST_RATE_LABEL = "Senior Interest Rate"
MEZZ_INTEREST_RATE_LABEL = "Mezzanine Interest Rate"
MEZZ_SHARE_LABEL = "Mezzanine Share of Warehouse Debt - Model"
SENIOR_DEBT_LABEL = "Senior Warehouse Debt"
SENIOR_DEBT_MODEL_LABEL = "Senior Warehouse Debt - Model"
MEZZ_DEBT_LABEL = "Mezzanine Warehouse Debt"
MEZZ_DEBT_MODEL_LABEL = "Mezzanine Warehouse Debt - Model"
WAREHOUSE_INTEREST_MODEL_LABEL = "Warehouse Interest Expense - Model"

ADJ_EBITDA_LABEL = "Adjusted EBITDA"

WAREHOUSE_FINANCING_LABELS: tuple[str, ...] = (
    SENIOR_INTEREST_RATE_LABEL,
    MEZZ_INTEREST_RATE_LABEL,
    MEZZ_SHARE_LABEL,
    SENIOR_DEBT_LABEL,
    SENIOR_DEBT_MODEL_LABEL,
    MEZZ_DEBT_LABEL,
    MEZZ_DEBT_MODEL_LABEL,
    WAREHOUSE_INTEREST_MODEL_LABEL,
)

# Q2 2026 10-Q facility table: outstanding principal, not carrying value.
# Senior = revolvers + senior term; mezzanine is the two term mezz facilities.
SENIOR_DEBT_BY_QUARTER: dict[str, int] = {
    "B": 999_000_000,  # 2025 Q3: $6M revolver + $100M S1 + $268M S2 + $625M S3
    "C": 777_000_000,  # 2025 Q4: $52M revolver + $725M senior term
    "D": 793_000_000,  # 2026 Q1: $68M revolver + $725M senior term
    "E": 1_416_000_000,  # 2026 Q2: $691M revolvers + $725M senior term
}
MEZZ_DEBT_BY_QUARTER: dict[str, int] = {
    "B": 350_000_000,  # $200M 2020-M1 + $150M 2022-M1 (unchanged Q3 2025–Q2 2026)
    "C": 350_000_000,
    "D": 350_000_000,
    "E": 350_000_000,
}

# Q2 2026 drawn-balance weighted senior coupon (~5.30%); mezz 12.50%.
SENIOR_INTEREST_RATE = 0.053
MEZZ_INTEREST_RATE = 0.125
# Q2 mezz $350M / ($1,416M + $350M).
MEZZ_SHARE = 350_000_000 / (1_416_000_000 + 350_000_000)

# Q2 warehouse gross ~$30M vs reported net interest $21M → ~$9M interest income.
INTEREST_INCOME_QUARTERLY = 9_000_000

RATE_LABELS: tuple[str, ...] = (
    SENIOR_INTEREST_RATE_LABEL,
    MEZZ_INTEREST_RATE_LABEL,
    MEZZ_SHARE_LABEL,
)
DEBT_ACTUAL_LABELS: tuple[str, ...] = (SENIOR_DEBT_LABEL, MEZZ_DEBT_LABEL)
DEBT_MODEL_LABELS: tuple[str, ...] = (
    SENIOR_DEBT_MODEL_LABEL,
    MEZZ_DEBT_MODEL_LABEL,
)
MODEL_FORMULA_LABELS: tuple[str, ...] = (
    SENIOR_INTEREST_RATE_LABEL,
    MEZZ_INTEREST_RATE_LABEL,
    MEZZ_SHARE_LABEL,
    SENIOR_DEBT_MODEL_LABEL,
    MEZZ_DEBT_MODEL_LABEL,
    WAREHOUSE_INTEREST_MODEL_LABEL,
)


def rate_seed(label: str) -> float:
    if label == SENIOR_INTEREST_RATE_LABEL:
        return SENIOR_INTEREST_RATE
    if label == MEZZ_INTEREST_RATE_LABEL:
        return MEZZ_INTEREST_RATE
    if label == MEZZ_SHARE_LABEL:
        return MEZZ_SHARE
    raise KeyError(label)


def carry_forward_rate_formula(col: str, prev_col: str, *, rate_row: int) -> str:
    return f"={prev_col}{rate_row}"


def warehouse_debt_model_formula(
    col: str,
    prev_col: str,
    *,
    is_senior: bool,
    label_to_row: dict[str, int],
) -> str:
    """Actual if present; else scale last week's modeled book with inventory, CNML intensity, and mezz share."""
    actual_row = label_to_row[SENIOR_DEBT_LABEL if is_senior else MEZZ_DEBT_LABEL]
    seed = SENIOR_DEBT_BY_QUARTER["B"] if is_senior else MEZZ_DEBT_BY_QUARTER["B"]
    if col == "B":
        return f'=IF(ISNUMBER(B{actual_row}),B{actual_row},{seed})'

    senior_model_row = label_to_row[SENIOR_DEBT_MODEL_LABEL]
    mezz_model_row = label_to_row[MEZZ_DEBT_MODEL_LABEL]
    share_row = label_to_row[MEZZ_SHARE_LABEL]
    inventory_row = label_to_row["Homes in Inventory - Model"]
    mix = f"(1-{col}{share_row})" if is_senior else f"{col}{share_row}"
    total_prev = f"({prev_col}{senior_model_row}+{prev_col}{mezz_model_row})"
    inv_ratio = f"IF({prev_col}{inventory_row}=0,1,{col}{inventory_row}/{prev_col}{inventory_row})"
    intensity_ratio = cnml_intensity_ratio_expr(
        col, prev_col, label_to_row=label_to_row
    )
    return (
        f"=IF(ISNUMBER({col}{actual_row}),{col}{actual_row},"
        f"{total_prev}*{inv_ratio}*({intensity_ratio})*{mix})"
    )


def warehouse_interest_model_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    senior_debt = label_to_row[SENIOR_DEBT_MODEL_LABEL]
    mezz_debt = label_to_row[MEZZ_DEBT_MODEL_LABEL]
    senior_rate = label_to_row[SENIOR_INTEREST_RATE_LABEL]
    mezz_rate = label_to_row[MEZZ_INTEREST_RATE_LABEL]
    return (
        f"={col}{senior_debt}*{col}{senior_rate}/52"
        f"+{col}{mezz_debt}*{col}{mezz_rate}/52"
    )


def net_interest_model_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    """Reported net interest when spread; else warehouse gross minus Q2-calibrated interest income."""
    actual_row = label_to_row["Net Interest Expense"]
    warehouse_row = label_to_row[WAREHOUSE_INTEREST_MODEL_LABEL]
    return (
        f"=IF(ISNUMBER({col}{actual_row}),{col}{actual_row},"
        f"{col}{warehouse_row}-{INTEREST_INCOME_QUARTERLY}/13)"
    )
