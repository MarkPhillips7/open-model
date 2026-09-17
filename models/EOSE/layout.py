"""Quarterly Financials row labels, units, and time spine for EOSE."""

from __future__ import annotations

QUARTERLY = "Quarterly Financials"
OLD_QUARTERLY = "Quarterly Results/Projections"

# A = label, B = units, C = 2025 Q1 … Z = 2030 Q4
FIRST_VALUE_COL = "C"
FIRST_VALUE_COL_INDEX = 3  # 1-based
N_QUARTERS = 24
YEARS = (2025, 2026, 2027, 2028, 2029, 2030)

# Duplicate live column-A label: $M on the first Booked orders row, GWh on the second.
BOOKED_ORDERS_M_KEY = "Booked orders [$M]"
BOOKED_ORDERS_GWH_KEY = "Booked orders [GWh]"
MWH_SHIPPED_DERIVED_LABEL = "MWh shipped - Derived"

# Scalar levers live in column C of these labels (column B is units only).
AS_OF_LABEL = "As of date"
AS_OF_DATE = "2026-09-09"  # sheet DATEVALUE; years-from-present uses this
CYCLE_TIME_FLOOR_LABEL = "Cycle time floor"
CAPEX_PER_LINE_LABEL = "Capex per incremental line"
NET_INTEREST_RUNRATE_LABEL = "Net interest run-rate"
FY2026_GUIDE_LOW_LABEL = "FY 2026 revenue guidance — low"
FY2026_GUIDE_HIGH_LABEL = "FY 2026 revenue guidance — high"
HAIRCUT_LABEL = "Percent of Guided Cost Cutting Achieved"
NONCASH_COGS_LABEL = "Non-cash COGS (D&A + SBC)"
CASH_OPEX_RUNRATE_LABEL = "Cash OpEx run-rate"
PIPELINE_GROWTH_LABEL = "Pipeline quarterly growth rate"
COGS_SHEET = "COGS"

# Cost-out engine rows on Quarterly Financials (levers stay on the COGS tab).
COST_OUT_PROGRESS_LABEL = "Cost-out plan progress - Model"
GUIDED_ADJ_GM_MODEL_LABEL = "Guided adjusted gross margin - Model"
SCALE_BLEND_LABEL = "Scale absorption blend - Model"
EBITDA_200M_GUIDED_LABEL = "Adj. EBITDA at $200M revenue - Guided"
EBITDA_200M_MODEL_LABEL = "Adj. EBITDA at $200M revenue - Model"

# Pixel widths captured from the live workbook (0-based column index).
QUARTERLY_COL_WIDTHS_PX: dict[int, int] = {0: 280, 1: 90, **{i: 60 for i in range(2, 26)}}
WELCOME_COL_WIDTHS_PX: dict[int, int] = {0: 638, 1: 720}
DEFINITIONS_COL_WIDTHS_PX: dict[int, int] = {0: 288, 1: 734}
# COGS: A label, B units, C value (narrow), D notes (wide).
COGS_COL_WIDTHS_PX: dict[int, int] = {0: 287, 1: 58, 2: 100, 3: 720}

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
    (PIPELINE_GROWTH_LABEL, "% / q"),
    ("Pipeline (GWh)", "GWh"),
    ("Pipeline (GWh) - Model", "GWh"),
    ("Booked orders", "$M"),
    ("Booked orders - Model", "$M"),
    ("Booked orders", "GWh"),
    ("Backlog", "$M"),
    ("Backlog - Model", "$M"),
    ("Backlog (GWh)", "GWh"),
    ("Backlog (GWh) - Model", "GWh"),
    ("Backlog conversion lag", "quarters"),
    ("", ""),
    ("Z3 ASP - Derived", "$ / kWh"),
    ("Z3 ASP - Model", "$ / kWh"),
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
    (HAIRCUT_LABEL, "%"),
    (COST_OUT_PROGRESS_LABEL, "0–1"),
    (GUIDED_ADJ_GM_MODEL_LABEL, "%"),
    (SCALE_BLEND_LABEL, "0–1"),
    (EBITDA_200M_GUIDED_LABEL, "$M"),
    (EBITDA_200M_MODEL_LABEL, "$M"),
    ("Unit COGS - Derived", "$ / kWh"),
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
    (MWH_SHIPPED_DERIVED_LABEL, "MWh"),
    ("Revenue - Model", "$M"),
    ("COGS", "$M"),
    ("COGS - Model", "$M"),
    ("Gross profit", "$M"),
    ("Gross profit - Model", "$M"),
    ("Gross margin", "%"),
    ("Gross margin - Model", "%"),
    ("Adjusted gross profit", "$M"),
    ("Adjusted gross profit - Model", "$M"),
    ("Adjusted gross margin", "%"),
    ("Adjusted gross margin - Model", "%"),
    ("SG&A", "$M"),
    ("SG&A - Model", "$M"),
    ("R&D", "$M"),
    ("R&D - Model", "$M"),
    ("OpEx", "$M"),
    ("OpEx - Model", "$M"),
    ("Adjusted EBITDA", "$M"),
    ("Adjusted EBITDA - Model", "$M"),
    ("Operating cash flow - Model", "$M"),
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
    (CASH_OPEX_RUNRATE_LABEL, "$M"),
    (NONCASH_COGS_LABEL, "$M"),
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


def column_width_requests(sheet_id: int, widths: dict[int, int]) -> list[dict]:
    """Sheets API requests to set pixel widths. *widths* is 0-based column index → px."""
    requests: list[dict] = []
    keys = sorted(widths)
    i = 0
    while i < len(keys):
        start = keys[i]
        px = widths[start]
        j = i + 1
        while j < len(keys) and keys[j] == keys[j - 1] + 1 and widths[keys[j]] == px:
            j += 1
        requests.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": start,
                        "endIndex": keys[j - 1] + 1,
                    },
                    "properties": {"pixelSize": px},
                    "fields": "pixelSize",
                }
            }
        )
        i = j
    return requests


def label_map_from_ab(rows: list[list]) -> dict[str, int]:
    """Map labels to 1-based rows from A:B grids.

    Bare ``label`` is the first match (so ``Booked orders`` is the $M row).
    ``label [units]`` is always unique (covers the duplicate GWh Booked orders row).
    """
    found: dict[str, int] = {}
    for i, row in enumerate(rows, start=1):
        label = row[0] if row else ""
        if not label:
            continue
        units = row[1] if len(row) > 1 else ""
        found.setdefault(label, i)
        found[f"{label} [{units}]"] = i
    return found


def label_row_numbers() -> dict[str, int]:
    """1-based row index for each non-empty label (first match + units key)."""
    return label_map_from_ab([[label, units] for label, units in ROWS])


def live_quarterly_ab(client) -> list[list]:
    rows = client.batch_get([f"{QUARTERLY}!A1:B160"])[0]
    # Pad so a trailing empty row on the sheet still compares to ROWS.
    while rows and (not rows[-1] or not any(rows[-1])):
        rows.pop()
    return rows


def live_layout_mismatches(client) -> list[str]:
    """Diff live Quarterly Financials A:B against ROWS. Empty if they match."""
    live = live_quarterly_ab(client)
    issues: list[str] = []
    n = max(len(live), len(ROWS))
    for i in range(n):
        live_row = live[i] if i < len(live) else []
        live_label = live_row[0] if live_row else ""
        live_units = live_row[1] if len(live_row) > 1 else ""
        repo_label, repo_units = ROWS[i] if i < len(ROWS) else ("", "")
        if (live_label, live_units) != (repo_label, repo_units):
            issues.append(
                f"R{i + 1}: live {live_label!r}/{live_units!r} != "
                f"repo {repo_label!r}/{repo_units!r}"
            )
    return issues


def require_live_layout_match(client, *, action: str) -> None:
    """Abort sheet writes if the live label stack drifted from git."""
    issues = live_layout_mismatches(client)
    if not issues:
        return
    preview = "\n".join(f"  {line}" for line in issues[:25])
    extra = f"\n  … {len(issues) - 25} more" if len(issues) > 25 else ""
    raise SystemExit(
        f"Refusing to {action}: live Quarterly Financials labels differ from "
        f"models/EOSE/layout.py.\n{preview}{extra}\n"
        "Update the repo from the sheet first, or pass --force-rebuild if you "
        "intentionally want to replace the live workbook."
    )


def row_number_for(label: str, units: str | None = None) -> int:
    """1-based row in ROWS. Bare label is first match; pass units to disambiguate."""
    first: int | None = None
    for i, (lab, un) in enumerate(ROWS, start=1):
        if lab != label:
            continue
        if first is None:
            first = i
        if units is not None and un == units:
            return i
    if first is None or units is not None:
        raise KeyError(f"Label {label!r} units {units!r} not in layout.ROWS")
    return first


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

# Z3 ASP - Model is a formula on the live sheet (260 in C, prior × 0.97).
ASP_MODEL_START = 260
ASP_MODEL_QOQ = 0.97
