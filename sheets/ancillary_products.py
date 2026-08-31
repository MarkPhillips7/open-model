"""Mortgage, title/escrow, and Doma refi ancillary product modeling."""

from __future__ import annotations

TRANSITIONS = "Transitions"

# Unit economics on Transitions (spreadsheet is source of truth after setup).
MORTGAGE_NET_PROFIT_PER_LOAN_CELL = f"{TRANSITIONS}!$B$29"
TITLE_NET_SAVINGS_PER_CLOSE_CELL = f"{TRANSITIONS}!$B$30"
DOMA_REFI_NET_PER_CLOSE_CELL = f"{TRANSITIONS}!$B$32"
DOMA_REFI_WEEKLY_CLOSINGS_RAMP_CELL = f"{TRANSITIONS}!$B$33"

MORTGAGE_NET_PROFIT_PER_LOAN = 2000
TITLE_NET_SAVINGS_PER_CLOSE = 1800
DOMA_REFI_NET_PER_CLOSE = 350

OPEN_MORTGAGE_PERCENT_LABEL = "Open Mortgage Percent"
OPEN_TITLE_PURCHASE_PERCENT_LABEL = "Open Title Purchase Percent"
OLD_OPEN_TITLE_LABEL = "Open Title and Escrow (Doma) Percent"

CM_MORTGAGE_LABEL = "Contribution Margin - Mortgage"
CM_TITLE_LABEL = "Contribution Margin - Title and Escrow"
DOMA_REFI_CONTRIBUTION_LABEL = "Doma Refi Contribution - Model"

ASP_LABEL = "Average Sale Price (homes sold by OPEN)"

# ODL resale attach ramp (Florida launch Jul 2026 → multi-state ~Jan 2028).
MORTGAGE_ATTACH_START_DATE = "DATE(2026,7,1)"
MORTGAGE_ATTACH_END_DATE = "DATE(2028,1,1)"
MORTGAGE_ATTACH_START_RATE = 0.15
MORTGAGE_ATTACH_END_RATE = 0.45
MORTGAGE_ATTACH_CAP = 0.50

TITLE_PURCHASE_ATTACH_START_DATE = MORTGAGE_ATTACH_START_DATE
TITLE_PURCHASE_ATTACH_RATE = 0.95

DOMA_REFI_START_DATE = "DATE(2026,4,1)"
DOMA_REFI_WEEKLY_CLOSINGS_RAMP_PER_WEEK = 1.5
DOMA_REFI_WEEKLY_CLOSINGS_CAP = 100

TRANSITIONS_ANCILLARY_ROWS: list[tuple[str, str | int | float]] = [
    ("Mortgage net profit per attached loan ($)", MORTGAGE_NET_PROFIT_PER_LOAN),
    ("Title net savings per purchase close ($)", TITLE_NET_SAVINGS_PER_CLOSE),
    ("", ""),
    ("Doma refi net per close ($)", DOMA_REFI_NET_PER_CLOSE),
    (
        "Doma refi weekly closings ramp (/wk per wk from start)",
        DOMA_REFI_WEEKLY_CLOSINGS_RAMP_PER_WEEK,
    ),
]


def open_mortgage_percent_formula(col: str) -> str:
    return (
        f'=IF({col}$1="","",IF({col}$1<{MORTGAGE_ATTACH_START_DATE},0,'
        f"MIN({MORTGAGE_ATTACH_CAP},{MORTGAGE_ATTACH_START_RATE}+"
        f"({col}$1-{MORTGAGE_ATTACH_START_DATE})/"
        f"({MORTGAGE_ATTACH_END_DATE}-{MORTGAGE_ATTACH_START_DATE})*"
        f"({MORTGAGE_ATTACH_END_RATE}-{MORTGAGE_ATTACH_START_RATE}))))"
    )


def open_title_purchase_percent_formula(col: str) -> str:
    return (
        f'=IF({col}$1="","",IF({col}$1<{TITLE_PURCHASE_ATTACH_START_DATE},0,'
        f"{TITLE_PURCHASE_ATTACH_RATE}))"
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


def doma_refi_contribution_formula(col: str) -> str:
    return (
        f'=IF({col}$1="","",IF({col}$1<{DOMA_REFI_START_DATE},0,'
        f"{DOMA_REFI_NET_PER_CLOSE_CELL}*MIN({DOMA_REFI_WEEKLY_CLOSINGS_CAP},"
        f"MAX(0,({col}$1-{DOMA_REFI_START_DATE})/7*"
        f"{DOMA_REFI_WEEKLY_CLOSINGS_RAMP_CELL}))))"
    )
