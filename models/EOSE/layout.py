"""Quarterly Financials row labels, units, and time spine for EOSE."""

from __future__ import annotations

QUARTERLY = "Quarterly Financials"
OLD_QUARTERLY = "Quarterly Results/Projections"

# A = label, B = units, C = 2025 Q1 … Z = 2030 Q4
FIRST_VALUE_COL = "C"
FIRST_VALUE_COL_INDEX = 3  # 1-based
N_QUARTERS = 24
YEARS = (2025, 2026, 2027, 2028, 2029, 2030)

# Scalar levers live in column C of these labels (column B is units only).
AS_OF_LABEL = "As of date"
AS_OF_DATE = "2026-09-09"  # sheet DATEVALUE; years-from-present uses this
CYCLE_TIME_FLOOR_LABEL = "Cycle time floor"
CAPEX_PER_LINE_LABEL = "Capex per incremental line"
NET_INTEREST_RUNRATE_LABEL = "Net interest run-rate"
FY2026_GUIDE_LOW_LABEL = "FY 2026 revenue guidance — low"
FY2026_GUIDE_HIGH_LABEL = "FY 2026 revenue guidance — high"

# (label, units) in sheet order. Row 1 is the Units header (A blank, B "Units").
# Empty label = spacer / section break.
ROWS: list[tuple[str, str]] = [
    ("", "Units"),
    ("Year", ""),
    ("Quarter", ""),
    ("Quarter ending", "date"),
    (AS_OF_LABEL, "date"),
    ("Years from present", "years"),
    ("", ""),
    ("Pipeline", "$B"),
    ("Pipeline - Model", "$B"),
    ("Pipeline (GWh)", "GWh"),
    ("Pipeline (GWh) - Model", "GWh"),
    ("Booked orders", "$M"),
    ("Booked orders - Model", "$M"),
    ("Backlog", "$M"),
    ("Backlog - Model", "$M"),
    ("Backlog (GWh)", "GWh"),
    ("Backlog (GWh) - Model", "GWh"),
    ("Backlog conversion lag", "quarters"),
    ("GWh shipped", "GWh"),
    ("GWh shipped - Model", "GWh"),
    ("", ""),
    ("Z3 ASP", "$"),
    ("Z3 ASP - Model", "$"),
    ("Z3 Module Energy Capacity", "kWh / module"),
    ("Z3 module cycle time", "seconds"),
    ("Z3 module cycle time - Model", "seconds"),
    ("Quarterly module cycle time reduction rate", "%"),
    (CYCLE_TIME_FLOOR_LABEL, "seconds"),
    ("Z3 modules per cube", "count"),
    ("Z3 manufacturing lines", "count"),
    ("Z3 manufacturing lines - Model", "count"),
    ("Capacity utilization", "%"),
    ("Z3 manufacturing lines utilized - Model", "count"),
    ("Full utilization weeks per year", "wks /yr"),
    ("Full utilization days per week", "days / wk"),
    ("Full utilization hours per day", "hrs / day"),
    ("Module production count per line - Model", "millions / yr"),
    ("Capacity per line - Model", "GWh / yr"),
    ("Annualized module energy capacity - Model", "GWh"),
    ("Factory capacity - Model", "GWh"),
    ("", ""),
    ("Unit COGS - Model", "$ / kWh"),
    ("45x & active electrode credits", "$ / kWh"),
    ("45x transfer rate", "%"),
    ("Effective 45x credit - Model", "$ / kWh"),
    ("Government credits - Model", "$M"),
    ("Unit COGS w/ 45x - Model", "$ / kWh"),
    ("", ""),
    (FY2026_GUIDE_LOW_LABEL, "$M"),
    (FY2026_GUIDE_HIGH_LABEL, "$M"),
    ("Revenue", "$M"),
    ("Revenue - Model", "$M"),
    ("COGS", "$M"),
    ("COGS - Model", "$M"),
    ("Gross profit", "$M"),
    ("Gross profit - Model", "$M"),
    ("Gross margin", "%"),
    ("Gross margin - Model", "%"),
    ("SG&A", "$M"),
    ("SG&A - Model", "$M"),
    ("R&D", "$M"),
    ("R&D - Model", "$M"),
    ("OpEx", "$M"),
    ("OpEx - Model", "$M"),
    ("Adjusted EBITDA", "$M"),
    ("Adjusted EBITDA - Model", "$M"),
    ("Adjusted EBITDA margin", "%"),
    ("Adjusted EBITDA margin - Model", "%"),
    ("Annualized EBITDA - Model", "$M"),
    ("GAAP net income", "$M"),
    ("GAAP net income - Model", "$M"),
    ("", ""),
    ("Cash", "$M"),
    ("Cash - Model", "$M"),
    ("Capex - Model", "$M"),
    (CAPEX_PER_LINE_LABEL, "$M"),
    (NET_INTEREST_RUNRATE_LABEL, "$M"),
    ("Long term debt", "$M"),
    ("Total debt", "$M"),
    ("Total debt - Model", "$M"),
    ("Net debt - Model", "$M"),
    ("", ""),
    ("Basic shares", "million"),
    ("Fully diluted shares", "million"),
    ("Fully diluted shares - Model", "million"),
    ("Stock price", "$"),
    ("Market cap", "$B"),
    ("EV / EBITDA", "x"),
    ("Discount rate", "%"),
    ("Enterprise value - Model", "$B"),
    ("Market cap - Model", "$B"),
    ("Implied future stock price - Model", "$"),
    ("Present stock price discounted - Model", "$"),
]


def label_row_numbers() -> dict[str, int]:
    """1-based row index for each non-empty label."""
    found: dict[str, int] = {}
    for i, (label, _units) in enumerate(ROWS, start=1):
        if label:
            found[label] = i
    return found


def quarters() -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for year in YEARS:
        for q in (1, 2, 3, 4):
            out.append((year, q))
    return out


# Factory line-count path (editable Model assumptions). 2025 stays at 1 line;
# ramp starts 2026 Q1. Last two 2030 quarters hold at 12.
LINE_RAMP: list[float] = [
    1, 1, 1, 1,
    1.25, 1.5, 1.75, 2,
    2.5, 3, 3.5, 4,
    4.5, 5, 5.5, 6,
    6.75, 7.5, 8.5, 9.5,
    10.75, 12, 12, 12,
]

# ASP Model: 250 in 2025 Q1–Q3 (early production), 256 thereafter.
def asp_model_values() -> list[float]:
    vals: list[float] = []
    for year, q in quarters():
        vals.append(250.0 if year == 2025 and q <= 3 else 256.0)
    return vals
