"""Mortgage and title/escrow ancillary product modeling."""

from __future__ import annotations

TRANSITIONS = "Transitions"

# Unit economics on Transitions (spreadsheet is source of truth after setup).
MORTGAGE_NET_PROFIT_PER_LOAN_CELL = f"{TRANSITIONS}!$B$29"
TITLE_NET_SAVINGS_PER_CLOSE_CELL = f"{TRANSITIONS}!$B$30"
# Legacy weekly Doma formulas still reference these cells; inputs removed from Transitions.
DOMA_REFI_NET_PER_CLOSE_CELL = f"{TRANSITIONS}!$B$32"
DOMA_REFI_WEEKLY_CLOSINGS_RAMP_CELL = f"{TRANSITIONS}!$B$33"

MORTGAGE_NET_PROFIT_PER_LOAN = 4000
TITLE_NET_SAVINGS_PER_CLOSE = 2400

DOMA_GROWTH_MULTIPLIER_LABEL = "Doma Growth Multiplier"
DOMA_REFI_PROFIT_LABEL = "Doma Refi Profit - Model"

OPEN_MORTGAGE_PERCENT_LABEL = "Open Mortgage Percent"
OPEN_TITLE_PURCHASE_PERCENT_LABEL = "Open Title Purchase Percent"
OLD_OPEN_TITLE_LABEL = "Open Title and Escrow (Doma) Percent"

CM_MORTGAGE_LABEL = "Contribution Margin - Mortgage"
CM_TITLE_LABEL = "Contribution Margin - Title and Escrow"

ASP_LABEL = "Average Sale Price (homes sold by OPEN)"

# ODL attach ramp — smoothstep phases on Weekly Financials (Open Mortgage Percent).
MORTGAGE_ATTACH_PHASE1_END = "DATE(2026,1,4)"
MORTGAGE_ATTACH_PHASE2_END = "DATE(2026,9,6)"
MORTGAGE_ATTACH_PHASE3_END = "DATE(2027,1,3)"
MORTGAGE_ATTACH_PHASE4_END = "DATE(2029,1,2)"

TITLE_PURCHASE_ATTACH_START_DATE = "DATE(2025,1,1)"
TITLE_PURCHASE_ATTACH_END_DATE = "DATE(2027,6,1)"

DOMA_REFI_START_DATE = "DATE(2026,4,1)"
DOMA_REFI_WEEKLY_CLOSINGS_CAP = 100

DOMA_GROWTH_MULTIPLIER_SEED = 0

TRANSITIONS_ANCILLARY_ROWS: list[tuple[str, str | int | float]] = [
    ("Max Mortgage net contribution profit per attached loan ($)", MORTGAGE_NET_PROFIT_PER_LOAN),
    ("Max Title/ESCROW net contribution profit per purchase close ($)", TITLE_NET_SAVINGS_PER_CLOSE),
]


def _smoothstep(col: str, start: str, end: str) -> str:
    t = f"(({col}$1-{start})/({end}-{start}))"
    return f"(3*{t}^2-2*{t}^3)"


def open_mortgage_percent_formula(col: str) -> str:
    s1 = MORTGAGE_ATTACH_PHASE1_END
    s2 = MORTGAGE_ATTACH_PHASE2_END
    s3 = MORTGAGE_ATTACH_PHASE3_END
    s4 = MORTGAGE_ATTACH_PHASE4_END
    return (
        f"=IFS({col}$1<={s1},0%,"
        f"{col}$1<={s2},10%*{_smoothstep(col, s1, s2)},"
        f"{col}$1<={s3},10%+30%*{_smoothstep(col, s2, s3)},"
        f"{col}$1<={s4},40%+40%*{_smoothstep(col, s3, s4)},"
        f"TRUE,80%)"
    )


def open_title_purchase_percent_formula(col: str) -> str:
    return (
        f'=IF({col}$1="","",IF({col}$1<{TITLE_PURCHASE_ATTACH_START_DATE},0,'
        f"MIN(1,({col}$1-{TITLE_PURCHASE_ATTACH_START_DATE})/"
        f"({TITLE_PURCHASE_ATTACH_END_DATE}-{TITLE_PURCHASE_ATTACH_START_DATE}))))"
    )


def cm_mortgage_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    asp = label_to_row[ASP_LABEL]
    attach = label_to_row[OPEN_MORTGAGE_PERCENT_LABEL]
    return (
        f'=IF(OR(N({col}{asp})=0,N({col}{attach})=0),"",'
        f"{col}{attach}*{MORTGAGE_NET_PROFIT_PER_LOAN_CELL}/{col}{asp})"
    )


def cm_title_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    asp = label_to_row[ASP_LABEL]
    attach = label_to_row[OPEN_TITLE_PURCHASE_PERCENT_LABEL]
    return (
        f'=IF(OR(N({col}{asp})=0,N({col}{attach})=0),"",'
        f"{col}{attach}*{TITLE_NET_SAVINGS_PER_CLOSE_CELL}/{col}{asp})"
    )


def doma_refi_base_formula(col: str) -> str:
    return (
        f'=IF({col}$1="","",IF({col}$1<{DOMA_REFI_START_DATE},0,'
        f"{DOMA_REFI_NET_PER_CLOSE_CELL}*MIN({DOMA_REFI_WEEKLY_CLOSINGS_CAP},"
        f"MAX(0,({col}$1-{DOMA_REFI_START_DATE})/7*"
        f"{DOMA_REFI_WEEKLY_CLOSINGS_RAMP_CELL}))))"
    )


def doma_growth_multiplier_cell(col: str, prev_col: str, *, label_to_row: dict[str, int]) -> str | float:
    if col == "B":
        return DOMA_GROWTH_MULTIPLIER_SEED
    mult_row = label_to_row[DOMA_GROWTH_MULTIPLIER_LABEL]
    return f"={prev_col}{mult_row}"


def doma_refi_profit_formula(col: str, prev_col: str, *, label_to_row: dict[str, int]) -> str:
    if col == "B":
        return doma_refi_base_formula(col)
    profit_row = label_to_row[DOMA_REFI_PROFIT_LABEL]
    mult_row = label_to_row[DOMA_GROWTH_MULTIPLIER_LABEL]
    return f"={prev_col}{profit_row}*{col}{mult_row}"
