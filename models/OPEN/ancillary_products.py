"""Mortgage and title/escrow ancillary product modeling."""

from __future__ import annotations

TRANSITIONS = "Transitions"

# Unit economics on Transitions (spreadsheet is source of truth after setup).
MORTGAGE_NET_PROFIT_PER_LOAN_CELL = f"{TRANSITIONS}!$B$29"
TITLE_NET_SAVINGS_PER_CLOSE_CELL = f"{TRANSITIONS}!$B$30"
OFF_INVENTORY_PROFIT_PER_LOAN_CELL = f"{TRANSITIONS}!$B$31"
OFF_INVENTORY_TAM_SHARE_CELL = f"{TRANSITIONS}!$B$32"
US_HOME_SALES_TAM_CELL = f"{TRANSITIONS}!$B$33"
OFF_INVENTORY_REVENUE_PER_LOAN_CELL = f"{TRANSITIONS}!$B$34"
# Manual Doma row cells live in models/OPEN/doma_manual_cells.py (not Transitions-driven).

MORTGAGE_NET_PROFIT_PER_LOAN = 4000
TITLE_NET_SAVINGS_PER_CLOSE = 2400
OFF_INVENTORY_PROFIT_PER_LOAN = 3000
OFF_INVENTORY_REVENUE_PER_LOAN = 7500
OFF_INVENTORY_TAM_SHARE_TERMINAL = 0.02
US_HOME_SALES_TAM_ANNUAL = 4_000_000

DOMA_GROWTH_MULTIPLIER_LABEL = "Doma Growth Multiplier"
DOMA_REFI_PROFIT_LABEL = "Doma Refi Profit - Model"

OPEN_MORTGAGE_PERCENT_LABEL = "Open Mortgage Percent"
OPEN_TITLE_PURCHASE_PERCENT_LABEL = "Open Title Purchase Percent"
OLD_OPEN_TITLE_LABEL = "Open Title and Escrow (Doma) Percent"

CM_MORTGAGE_LABEL = "Contribution Margin - Mortgage"
CM_TITLE_LABEL = "Contribution Margin - Title and Escrow"

ODL_OFF_INVENTORY_LOANS_LABEL = "ODL Off-inventory Loans - Model"
ODL_OFF_INVENTORY_REVENUE_LABEL = "ODL Off-inventory Revenue - Model"
ODL_OFF_INVENTORY_PROFIT_LABEL = "ODL Off-inventory Profit - Model"
ODL_OFF_INVENTORY_LABELS: tuple[str, ...] = (
    ODL_OFF_INVENTORY_LOANS_LABEL,
    ODL_OFF_INVENTORY_REVENUE_LABEL,
    ODL_OFF_INVENTORY_PROFIT_LABEL,
)

ASP_LABEL = "Average Sale Price (homes sold by OPEN)"

# ODL attach ramp — smoothstep phases on Weekly Financials (Open Mortgage Percent).
# 10% waypoint is GA / out-of-beta (Sep 2026). 40% pulled ~2 weeks vs prior Jan 3 2027;
# 80% pulled ~3 months vs prior Jan 2 2029.
MORTGAGE_ATTACH_PHASE1_END = "DATE(2026,1,4)"
MORTGAGE_ATTACH_PHASE2_END = "DATE(2026,9,6)"
MORTGAGE_ATTACH_PHASE3_END = "DATE(2026,12,20)"
MORTGAGE_ATTACH_PHASE4_END = "DATE(2028,10,1)"

# Off-inventory originations as a % of US existing-home-sale TAM (not a CM add).
# Start = ODL GA / out of beta. End = Jan 1 2030 (base-case ~2% share, ~3.3 years).
OFF_INVENTORY_RATIO_START = "DATE(2026,9,6)"
OFF_INVENTORY_RATIO_END = "DATE(2030,1,1)"

TITLE_PURCHASE_ATTACH_START_DATE = "DATE(2025,1,1)"
TITLE_PURCHASE_ATTACH_END_DATE = "DATE(2027,6,1)"

TRANSITIONS_ANCILLARY_ROWS: list[tuple[str, str | int | float]] = [
    ("Max Mortgage net contribution profit per attached loan ($)", MORTGAGE_NET_PROFIT_PER_LOAN),
    ("Max Title/ESCROW net contribution profit per purchase close ($)", TITLE_NET_SAVINGS_PER_CLOSE),
    (
        "Max Mortgage net contribution profit per off-inventory loan ($)",
        OFF_INVENTORY_PROFIT_PER_LOAN,
    ),
    (
        "Terminal off-inventory ODL loans as % of US home-sale TAM",
        OFF_INVENTORY_TAM_SHARE_TERMINAL,
    ),
    (
        "US existing home sales TAM (homes/year)",
        US_HOME_SALES_TAM_ANNUAL,
    ),
    (
        "Max Mortgage revenue per off-inventory loan ($)",
        OFF_INVENTORY_REVENUE_PER_LOAN,
    ),
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


def _off_inventory_tam_share_expr(col: str) -> str:
    start = OFF_INVENTORY_RATIO_START
    end = OFF_INVENTORY_RATIO_END
    terminal = OFF_INVENTORY_TAM_SHARE_CELL
    return (
        f"IFS({col}$1<={start},0,"
        f"{col}$1<={end},{terminal}*{_smoothstep(col, start, end)},"
        f"TRUE,{terminal})"
    )


def odl_off_inventory_loans_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    """Weekly US home-sale TAM × off-inventory TAM share. Independent of OPEN inventory."""
    del label_to_row
    return (
        f"=({US_HOME_SALES_TAM_CELL}/52)*({_off_inventory_tam_share_expr(col)})"
    )


def odl_off_inventory_revenue_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    loans = label_to_row[ODL_OFF_INVENTORY_LOANS_LABEL]
    return f"={col}{loans}*{OFF_INVENTORY_REVENUE_PER_LOAN_CELL}"


def odl_off_inventory_profit_formula(col: str, *, label_to_row: dict[str, int]) -> str:
    loans = label_to_row[ODL_OFF_INVENTORY_LOANS_LABEL]
    return f"={col}{loans}*{OFF_INVENTORY_PROFIT_PER_LOAN_CELL}"
