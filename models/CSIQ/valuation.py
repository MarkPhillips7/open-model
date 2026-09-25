"""Valuation tab: the sum of parts at the current quarter and at the phased-in base case.

Values are formulas pointed at Quarterly Financials, so a lever edit shows up here.
"""

from __future__ import annotations

from sheets.formulas import col_letter

from models.CSIQ import layout as L

VALUATION_SHEET = "Valuation"

NOW_COL = col_letter(L.col_index_for_quarter(L.CURRENT_QUARTER))
BASE_COL = col_letter(L.col_index_for_quarter(L.BASE_CASE_QUARTER))

HEADER = [
    "Line",
    f"{L.CURRENT_QUARTER} (this quarter)",
    f"{L.BASE_CASE_QUARTER} (base case phased in)",
    "How to read it",
]

COL_WIDTHS_PX: dict[int, int] = {0: 340, 1: 180, 2: 200, 3: 720}

Q = L.QUARTERLY

# (label on quarterly, note) — pulled live. Blank label = spacer.
LINES: list[tuple[str, str]] = [
    (L.TOTAL_REV_MODEL, "Revenue bridge. 2026 Q3 should sit in the $1.3–1.5B guide."),
    (L.GP_MODEL, "Consolidated gross profit. Not an input to the price."),
    (L.OI_MODEL, "Operating income. The consolidated loss is not what is being valued."),
    ("", ""),
    (L.US_MODULE_EBITDA, "Quarterly. Multiply by 4 in your head for the annualized run-rate. ~$50M at full phase-in is $200M a year."),
    (L.US_STORAGE_EBITDA, "Quarterly. ~$37.5M at full phase-in is $150M a year."),
    (L.US_MODULE_EQUITY, "Annualized EBITDA × 8 × 75.1% ownership, floored at zero."),
    (L.US_STORAGE_EQUITY, "Annualized EBITDA × 12 × 75.1%, minus storage debt (default zero)."),
    ("", ""),
    (L.CSI_STAKE, "Discounted Shanghai stake. Update the market-cap lever; $7B is the April 2026 video."),
    (L.CSI_CROSSCHECK, "Earnings cross-check. Not included in equity value."),
    (L.RECURRENT_STAKE, "80% of the $2.5B BlackRock mark, times the achieved lever."),
    (L.HOLDCO_NET_DEBT, "Converts minus credited holdco cash. The only debt subtracted."),
    (L.FLOOR_EQUITY, "CSI Solar + Recurrent − holdco net debt. Not discounted."),
    (L.EQUITY_VALUE, "Floor plus the two US equity values. Undiscounted."),
    ("", ""),
    (L.SHARES_MODEL, "Basic shares, millions."),
    (L.IMPLIED_PRICE, "Equity value / basic shares. Primary price. Converts treated as debt."),
    (L.DILUTED_PRICE, "Converts added back, divided by the 90M diluted-share lever. The thesis convention."),
    (L.PRESENT_PRICE, "Floor in full, US ramp discounted. This is the number to compare with the stock."),
    (L.STOCK_PRICE, "Last close on or before quarter-end. Blank if the quarter has not ended."),
    (L.MARKET_CAP, "Price times basic shares, $M."),
]


def _pull(col: str, label: str) -> str:
    if not label:
        return ""
    row = L.row_number_for(label)
    return f"=IF('{Q}'!{col}{row}=\"\",\"\",'{Q}'!{col}{row})"


def grid() -> list[list[str]]:
    out: list[list[str]] = [list(HEADER)]
    for label, note in LINES:
        out.append([label, _pull(NOW_COL, label), _pull(BASE_COL, label), note])
    return out


NOTE = (
    "2027 Q4 is the base-case column because that is where the default phase-in hits 100% "
    "and US volume is 6 GW/year of modules and 5 GWh/year of storage. 2026 Q3 is the quarter "
    "that contains the default As of date. Neither column is a target price from a bank."
)
