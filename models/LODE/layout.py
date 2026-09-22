"""Quarterly Financials row stack, units, and time spine for LODE (Comstock Inc.).

Conventions this pack follows everywhere:

* A bare label (``Total revenue``) is a **reported print** — hardcoded from a 10-Q,
  8-K, or earnings release, and left blank until the company has actually reported
  it. Never a formula.
* ``Label - Model`` is **always a formula**, and prefers the actual when one exists
  (``IF(actual<>"", actual, model)``). That way a miss is visible instead of being
  silently overwritten.
* Rows in ``EDITABLE_PATH_LABELS`` are Model rows that hold a hand-maintained
  *trajectory* rather than a derived formula. They are painted yellow on the sheet.
  Scalar assumptions live on the Levers tab instead; see ``levers.py``.

The spine is quarterly only. Comstock reports no weekly or monthly operating
metric, so a weekly sheet would be invented precision.
"""

from __future__ import annotations

from typing import Any

QUARTERLY = "Quarterly Financials"

# A = label, B = units, C = 2025 Q1 … Z = 2030 Q4.
FIRST_VALUE_COL = "C"
FIRST_VALUE_COL_INDEX = 3  # 1-based
YEARS = (2025, 2026, 2027, 2028, 2029, 2030)
N_QUARTERS = 4 * len(YEARS)
LAST_VALUE_COL = "Z"

# Latest quarter Comstock has actually reported as of the As of date.
LAST_REPORTED_QUARTER = "2026 Q2"
LAST_REPORTED_COL = "H"  # 2026 Q2

UNITS_TONS = "tons"
UNITS_USD_TON = "$/ton"
UNITS_M = "$M"
UNITS_PCT = "%"
UNITS_LINES = "lines"
UNITS_SHARES = "M shares"


# --- Label constants -------------------------------------------------------

YEAR = "Year"
QUARTER = "Quarter"
QUARTER_ENDING = "Quarter ending"
AS_OF_DATE = "As of date"
YEARS_FROM_PRESENT = "Years from present"

RATED_CAPACITY = "Rated capacity per production line"
LINES_ACTUAL = "Operating production lines"
LINES_PLAN = "Operating production lines - Plan"
LINES_MODEL = "Operating production lines - Model"
UTILIZATION_ACTUAL = "Capacity utilization"
UTILIZATION_PLAN = "Capacity utilization - Plan"
UTILIZATION_MODEL = "Capacity utilization - Model"
TONS_ACTUAL = "Tons processed"
TONS_MODEL = "Tons processed - Model"

TIPPING_MODEL = "Tipping fee per ton - Model"
MATERIAL_MODEL = "Recovered material per ton - Model"
UPLIFT_PHASE_IN = "Uplift phase-in - Plan"
TAILINGS_STOCKPILE_ADD = "Tailings stockpile add - Model"
TAILINGS_INVENTORY = "Tailings inventory - Model"
TAILINGS_STOCKPILE_DRAW = "Tailings stockpile draw - Model"
STOCKPILE_METAL_REVENUE = "Stockpile metal revenue - Model"
REVENUE_PER_TON_MODEL = "Revenue per ton - Model"

METALS_REVENUE_ACTUAL = "Metals revenue"
METALS_REVENUE_MODEL = "Metals revenue - Model"
METALS_FIXED_COST_MODEL = "Metals fixed cash cost - Model"
METALS_VARIABLE_COST_MODEL = "Metals variable cash cost - Model"
METALS_COST_MODEL = "Metals cash cost - Model"
METALS_CONTRIBUTION_MODEL = "Metals cash contribution - Model"
METALS_MARGIN_MODEL = "Metals contribution margin - Model"
BREAKEVEN_UTILIZATION_MODEL = "Breakeven utilization - Model"
METALS_CAPEX_MODEL = "Metals capex - Model"

TOTAL_REVENUE_ACTUAL = "Total revenue"
TOTAL_REVENUE_MODEL = "Total revenue - Model"
GROSS_PROFIT_ACTUAL = "Gross profit"
OPEX_ACTUAL = "Operating expenses"
OPERATING_LOSS_ACTUAL = "Operating loss"
IMPAIRMENTS_ACTUAL = "Impairments and other non-cash charges"
NET_LOSS_ACTUAL = "Net loss attributable to common"
EPS_ACTUAL = "Net loss per share"
CORP_GA_MODEL = "Corporate cash G&A - Model"
ADJ_EBITDA_MODEL = "Adjusted EBITDA - Model"

CASH_ACTUAL = "Cash and equivalents"
OCF_ACTUAL = "Operating cash flow"
OCF_MODEL = "Operating cash flow - Model"
MINING_PROCEEDS_MODEL = "Mining sale proceeds - Model"
SSOF_PROCEEDS_MODEL = "SSOF monetization proceeds - Model"
FUELS_BRIDGE_MODEL = "Comstock Fuels bridge loan - Model"
CAPEX_ACTUAL = "Capital expenditures"
CAPEX_MODEL = "Capital expenditures - Model"
EQUITY_ISSUED_ACTUAL = "Equity issued"
EQUITY_ISSUED_MODEL = "Equity issued - Model"
CASH_MODEL = "Cash - Model"
RUNWAY_MODEL = "Quarters of cash remaining - Model"

TOTAL_DEBT_ACTUAL = "Total debt"
TOTAL_DEBT_MODEL = "Total debt - Model"
SHARES_ACTUAL = "Shares outstanding"
SHARES_MODEL = "Shares outstanding - Model"
STOCK_PRICE = "Stock price"
MARKET_CAP = "Market cap"

ANNUAL_METALS_CONTRIB_MODEL = "Annualized metals cash contribution - Model"
ANNUAL_CORP_GA_MODEL = "Annualized corporate cash G&A - Model"
METALS_EBITDA_PROXY_MODEL = "Metals EBITDA proxy - Model"
METALS_CORE_VALUE_MODEL = "Metals core business value - Model"
METALS_BUSINESS_VALUE_MODEL = "Metals business value - Model"
SSOF_GROSS_MODEL = "SSOF gross asset value - Model"
SSOF_STAKE_VALUE_MODEL = "SSOF stake value - Model"
FUELS_STAKE_VALUE_MODEL = "Comstock Fuels stake value - Model"
NET_CASH_MODEL = "Net cash - Model"
NET_CASH_CREDITED_MODEL = "Net cash credited - Model"
EQUITY_VALUE_MODEL = "Equity value - Model"
IMPLIED_STOCK_PRICE_MODEL = "Implied stock price - Model"
PRESENT_STOCK_PRICE_MODEL = "Present stock price discounted - Model"

SECTION_METALS_VOLUME = "COMSTOCK METALS — VOLUME"
SECTION_METALS_PRICE = "COMSTOCK METALS — REVENUE PER TON"
SECTION_METALS_ECON = "COMSTOCK METALS — UNIT ECONOMICS"
SECTION_CONSOLIDATED = "CONSOLIDATED RESULTS"
SECTION_CASH = "CASH"
SECTION_SHARES = "SHARES AND PRICE"
SECTION_VALUATION = "VALUATION"

SECTION_LABELS: frozenset[str] = frozenset(
    {
        SECTION_METALS_VOLUME,
        SECTION_METALS_PRICE,
        SECTION_METALS_ECON,
        SECTION_CONSOLIDATED,
        SECTION_CASH,
        SECTION_SHARES,
        SECTION_VALUATION,
    }
)


# (label, units) in sheet order. Row 1 is the units header. "" = spacer row.
ROWS: list[tuple[str, str]] = [
    ("", "Units"),
    (YEAR, ""),
    (QUARTER, ""),
    (QUARTER_ENDING, "date"),
    (AS_OF_DATE, "date"),
    (YEARS_FROM_PRESENT, "years"),
    ("", ""),
    (SECTION_METALS_VOLUME, ""),
    (RATED_CAPACITY, UNITS_TONS + "/yr"),
    (LINES_ACTUAL, UNITS_LINES),
    (LINES_PLAN, UNITS_LINES),
    (LINES_MODEL, UNITS_LINES),
    (UTILIZATION_ACTUAL, UNITS_PCT),
    (UTILIZATION_PLAN, UNITS_PCT),
    (UTILIZATION_MODEL, UNITS_PCT),
    (TONS_ACTUAL, UNITS_TONS),
    (TONS_MODEL, UNITS_TONS),
    ("", ""),
    (SECTION_METALS_PRICE, ""),
    (TIPPING_MODEL, UNITS_USD_TON),
    (UPLIFT_PHASE_IN, UNITS_PCT),
    (MATERIAL_MODEL, UNITS_USD_TON),
    (REVENUE_PER_TON_MODEL, UNITS_USD_TON),
    (TAILINGS_STOCKPILE_ADD, UNITS_TONS),
    (TAILINGS_INVENTORY, UNITS_TONS),
    (TAILINGS_STOCKPILE_DRAW, UNITS_TONS),
    (STOCKPILE_METAL_REVENUE, UNITS_M),
    ("", ""),
    (SECTION_METALS_ECON, ""),
    (METALS_REVENUE_ACTUAL, UNITS_M),
    (METALS_REVENUE_MODEL, UNITS_M),
    (METALS_FIXED_COST_MODEL, UNITS_M),
    (METALS_VARIABLE_COST_MODEL, UNITS_M),
    (METALS_COST_MODEL, UNITS_M),
    (METALS_CONTRIBUTION_MODEL, UNITS_M),
    (METALS_MARGIN_MODEL, UNITS_PCT),
    (BREAKEVEN_UTILIZATION_MODEL, UNITS_PCT),
    (METALS_CAPEX_MODEL, UNITS_M),
    ("", ""),
    (SECTION_CONSOLIDATED, ""),
    (TOTAL_REVENUE_ACTUAL, UNITS_M),
    (TOTAL_REVENUE_MODEL, UNITS_M),
    (GROSS_PROFIT_ACTUAL, UNITS_M),
    (OPEX_ACTUAL, UNITS_M),
    (IMPAIRMENTS_ACTUAL, UNITS_M),
    (OPERATING_LOSS_ACTUAL, UNITS_M),
    (NET_LOSS_ACTUAL, UNITS_M),
    (EPS_ACTUAL, "$"),
    (CORP_GA_MODEL, UNITS_M),
    (ADJ_EBITDA_MODEL, UNITS_M),
    ("", ""),
    (SECTION_CASH, ""),
    (CASH_ACTUAL, UNITS_M),
    (OCF_ACTUAL, UNITS_M),
    (OCF_MODEL, UNITS_M),
    (CAPEX_ACTUAL, UNITS_M),
    (CAPEX_MODEL, UNITS_M),
    (MINING_PROCEEDS_MODEL, UNITS_M),
    (SSOF_PROCEEDS_MODEL, UNITS_M),
    (FUELS_BRIDGE_MODEL, UNITS_M),
    (EQUITY_ISSUED_ACTUAL, UNITS_M),
    (EQUITY_ISSUED_MODEL, UNITS_M),
    (CASH_MODEL, UNITS_M),
    (RUNWAY_MODEL, "quarters"),
    ("", ""),
    (SECTION_SHARES, ""),
    (TOTAL_DEBT_ACTUAL, UNITS_M),
    (TOTAL_DEBT_MODEL, UNITS_M),
    (SHARES_ACTUAL, UNITS_SHARES),
    (SHARES_MODEL, UNITS_SHARES),
    (STOCK_PRICE, "$"),
    (MARKET_CAP, UNITS_M),
    ("", ""),
    (SECTION_VALUATION, ""),
    (ANNUAL_METALS_CONTRIB_MODEL, UNITS_M),
    (ANNUAL_CORP_GA_MODEL, UNITS_M),
    (METALS_EBITDA_PROXY_MODEL, UNITS_M),
    (METALS_CORE_VALUE_MODEL, UNITS_M),
    (METALS_BUSINESS_VALUE_MODEL, UNITS_M),
    (SSOF_GROSS_MODEL, UNITS_M),
    (SSOF_STAKE_VALUE_MODEL, UNITS_M),
    (FUELS_STAKE_VALUE_MODEL, UNITS_M),
    (NET_CASH_MODEL, UNITS_M),
    (NET_CASH_CREDITED_MODEL, UNITS_M),
    (EQUITY_VALUE_MODEL, UNITS_M),
    (IMPLIED_STOCK_PRICE_MODEL, "$"),
    (PRESENT_STOCK_PRICE_MODEL, "$"),
]


# --- Editable trajectories -------------------------------------------------
# One value per quarter, 2025 Q1 … 2030 Q4. These are written once by setup and
# then owned by whoever edits the sheet; the restore flow treats them as data,
# not as formulas, so manual edits survive. Scaled by a Levers "achieved" dial.

# Industry-scale production lines. The 5,000 t/yr demo facility is deliberately
# NOT counted here — its revenue shows up in Total revenue actuals only, because
# counting it as a fraction of a 100,000 t/yr line would distort the cost model.
# Facility 1 (northern Nevada) commissions August 2026. Management will not order
# equipment for facility 2 until facility 1 is ramped, so line 2 is not assumed
# until 2028, with roughly one additional line a year after that.
LINE_PATH: list[float] = [
    0, 0, 0, 0,              # 2025: demo facility only
    0, 0, 1, 1,              # 2026: facility 1 live from Q3
    1, 1, 1, 1,              # 2027: prove and ramp facility 1
    1, 2, 2, 2,              # 2028: facility 2 (central Ohio)
    2, 3, 3, 3,              # 2029: facility 3
    3, 4, 4, 4,              # 2030: facility 4
]

# Percent of rated capacity. 2026 Q3/Q4 are set to reproduce the company's H2 2026
# guide (~$5M of revenue at "at least 25% of rated capacity from August through
# year end"): 5% of a quarter in Q3 for a part-quarter August start, 25% in Q4.
# Terminal 85% allows for maintenance on a plant designed to run 24/7.
UTILIZATION_PATH: list[float] = [
    0, 0, 0, 0,              # 2025
    0, 0, 5, 25,             # 2026: August start, ≥25% exiting the year
    35, 45, 55, 65,          # 2027
    70, 75, 80, 85,          # 2028
    85, 85, 85, 85,          # 2029
    85, 85, 85, 85,          # 2030
]

# Gate on the two unproven revenue uplifts (upgraded glass, extracted metals).
# Zero through 2026 so the model reproduces guided H2 2026 revenue on today's
# realised economics ($500 tipping + ~$200 material). Phases in as throughput
# rises, because both uplifts are gated on volume and certification, not on
# invention: the glass buyers want 50,000-ton flows, and metal extraction runs
# 1 t/day pilot → 25 t/day → industry scale.
UPLIFT_PHASE_IN_PATH: list[float] = [
    0, 0, 0, 0,              # 2025
    0, 0, 0, 0,              # 2026: 1 t/d pilot only — not commercial offtake
    15, 25, 40, 55,          # 2027: 25 t/d demo year (TARGET)
    65, 75, 85, 90,          # 2028: scale toward industry
    95, 100, 100, 100,       # 2029
    100, 100, 100, 100,      # 2030
]

EDITABLE_PATHS: dict[str, list[float]] = {
    LINES_PLAN: LINE_PATH,
    UTILIZATION_PLAN: UTILIZATION_PATH,
    UPLIFT_PHASE_IN: UPLIFT_PHASE_IN_PATH,
}
EDITABLE_PATH_LABELS: tuple[str, ...] = tuple(EDITABLE_PATHS)

# Quarterly crawl applied after the last reported actual.
SHARES_MODEL_QOQ = 1.01  # ~1%/quarter drip; override with dated events on Shares
EQUITY_RAISE_DEFAULT = 0.0  # no speculative raise baked in; see Shares tab


for _label, _path in EDITABLE_PATHS.items():
    if len(_path) != N_QUARTERS:
        raise ValueError(f"{_label} path has {len(_path)} values, expected {N_QUARTERS}")


# --- Formatting ------------------------------------------------------------

QUARTERLY_COL_WIDTHS_PX: dict[int, int] = {
    0: 300,
    1: 78,
    **{i: 72 for i in range(2, 2 + N_QUARTERS)},
}

NUMBER_FORMAT_1DP = "0.0"
NUMBER_FORMAT_2DP = "#,##0.00"
NUMBER_FORMAT_INT = "#,##0"
NUMBER_FORMAT_MONEY = "#,##0.00"

NUMBER_FORMAT_BY_LABEL: dict[str, str] = {
    YEARS_FROM_PRESENT: NUMBER_FORMAT_2DP,
    RATED_CAPACITY: NUMBER_FORMAT_INT,
    LINES_ACTUAL: NUMBER_FORMAT_2DP,
    LINES_PLAN: NUMBER_FORMAT_2DP,
    LINES_MODEL: NUMBER_FORMAT_2DP,
    UTILIZATION_ACTUAL: NUMBER_FORMAT_1DP,
    UTILIZATION_PLAN: NUMBER_FORMAT_1DP,
    UTILIZATION_MODEL: NUMBER_FORMAT_1DP,
    TONS_ACTUAL: NUMBER_FORMAT_INT,
    TONS_MODEL: NUMBER_FORMAT_INT,
    TIPPING_MODEL: NUMBER_FORMAT_MONEY,
    MATERIAL_MODEL: NUMBER_FORMAT_MONEY,
    UPLIFT_PHASE_IN: NUMBER_FORMAT_1DP,
    REVENUE_PER_TON_MODEL: NUMBER_FORMAT_MONEY,
    TAILINGS_STOCKPILE_ADD: NUMBER_FORMAT_INT,
    TAILINGS_INVENTORY: NUMBER_FORMAT_INT,
    TAILINGS_STOCKPILE_DRAW: NUMBER_FORMAT_INT,
    STOCKPILE_METAL_REVENUE: NUMBER_FORMAT_2DP,
    METALS_REVENUE_ACTUAL: NUMBER_FORMAT_2DP,
    METALS_REVENUE_MODEL: NUMBER_FORMAT_2DP,
    METALS_FIXED_COST_MODEL: NUMBER_FORMAT_2DP,
    METALS_VARIABLE_COST_MODEL: NUMBER_FORMAT_2DP,
    METALS_COST_MODEL: NUMBER_FORMAT_2DP,
    METALS_CONTRIBUTION_MODEL: NUMBER_FORMAT_2DP,
    METALS_MARGIN_MODEL: NUMBER_FORMAT_1DP,
    BREAKEVEN_UTILIZATION_MODEL: NUMBER_FORMAT_1DP,
    METALS_CAPEX_MODEL: NUMBER_FORMAT_2DP,
    TOTAL_REVENUE_ACTUAL: NUMBER_FORMAT_2DP,
    TOTAL_REVENUE_MODEL: NUMBER_FORMAT_2DP,
    GROSS_PROFIT_ACTUAL: NUMBER_FORMAT_2DP,
    OPEX_ACTUAL: NUMBER_FORMAT_2DP,
    IMPAIRMENTS_ACTUAL: NUMBER_FORMAT_2DP,
    OPERATING_LOSS_ACTUAL: NUMBER_FORMAT_2DP,
    NET_LOSS_ACTUAL: NUMBER_FORMAT_2DP,
    EPS_ACTUAL: NUMBER_FORMAT_2DP,
    CORP_GA_MODEL: NUMBER_FORMAT_2DP,
    ADJ_EBITDA_MODEL: NUMBER_FORMAT_2DP,
    CASH_ACTUAL: NUMBER_FORMAT_2DP,
    OCF_ACTUAL: NUMBER_FORMAT_2DP,
    OCF_MODEL: NUMBER_FORMAT_2DP,
    CAPEX_ACTUAL: NUMBER_FORMAT_2DP,
    CAPEX_MODEL: NUMBER_FORMAT_2DP,
    MINING_PROCEEDS_MODEL: NUMBER_FORMAT_2DP,
    SSOF_PROCEEDS_MODEL: NUMBER_FORMAT_2DP,
    FUELS_BRIDGE_MODEL: NUMBER_FORMAT_2DP,
    EQUITY_ISSUED_ACTUAL: NUMBER_FORMAT_2DP,
    EQUITY_ISSUED_MODEL: NUMBER_FORMAT_2DP,
    CASH_MODEL: NUMBER_FORMAT_2DP,
    RUNWAY_MODEL: NUMBER_FORMAT_1DP,
    TOTAL_DEBT_ACTUAL: NUMBER_FORMAT_2DP,
    TOTAL_DEBT_MODEL: NUMBER_FORMAT_2DP,
    SHARES_ACTUAL: NUMBER_FORMAT_2DP,
    SHARES_MODEL: NUMBER_FORMAT_2DP,
    STOCK_PRICE: NUMBER_FORMAT_MONEY,
    MARKET_CAP: NUMBER_FORMAT_2DP,
    ANNUAL_METALS_CONTRIB_MODEL: NUMBER_FORMAT_2DP,
    ANNUAL_CORP_GA_MODEL: NUMBER_FORMAT_2DP,
    METALS_EBITDA_PROXY_MODEL: NUMBER_FORMAT_2DP,
    METALS_CORE_VALUE_MODEL: NUMBER_FORMAT_2DP,
    METALS_BUSINESS_VALUE_MODEL: NUMBER_FORMAT_2DP,
    SSOF_GROSS_MODEL: NUMBER_FORMAT_2DP,
    SSOF_STAKE_VALUE_MODEL: NUMBER_FORMAT_2DP,
    FUELS_STAKE_VALUE_MODEL: NUMBER_FORMAT_2DP,
    NET_CASH_MODEL: NUMBER_FORMAT_2DP,
    NET_CASH_CREDITED_MODEL: NUMBER_FORMAT_2DP,
    EQUITY_VALUE_MODEL: NUMBER_FORMAT_2DP,
    IMPLIED_STOCK_PRICE_MODEL: NUMBER_FORMAT_MONEY,
    PRESENT_STOCK_PRICE_MODEL: NUMBER_FORMAT_MONEY,
}

YELLOW = {"red": 1, "green": 0.95, "blue": 0.8}
GREY = {"red": 0.91, "green": 0.91, "blue": 0.91}


# --- Spine helpers ---------------------------------------------------------


def quarters() -> list[tuple[int, int]]:
    return [(year, q) for year in YEARS for q in (1, 2, 3, 4)]


def quarter_keys() -> list[str]:
    return [f"{year} Q{q}" for year, q in quarters()]


def quarter_end_dates() -> list[str]:
    ends = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
    return [f"{year}-{ends[q]}" for year, q in quarters()]


def col_index_for_quarter(key: str) -> int:
    """1-based sheet column for a ``"2026 Q3"`` key."""
    try:
        return FIRST_VALUE_COL_INDEX + quarter_keys().index(key)
    except ValueError as exc:
        raise KeyError(f"Quarter {key!r} not in the {YEARS[0]}–{YEARS[-1]} spine") from exc


def label_map_from_ab(rows: list[list]) -> dict[str, int]:
    """Map label → 1-based row from an A:B grid. First match wins; adds ``label [units]``."""
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
    return label_map_from_ab([[label, units] for label, units in ROWS])


def row_number_for(label: str) -> int:
    rows = label_row_numbers()
    if label not in rows:
        raise KeyError(f"Label {label!r} not in layout.ROWS")
    return rows[label]


def live_quarterly_ab(client: Any) -> list[list]:
    rows = client.batch_get([f"{QUARTERLY}!A1:B160"])[0]
    while rows and (not rows[-1] or not any(rows[-1])):
        rows.pop()
    return rows


def live_layout_mismatches(client: Any) -> list[str]:
    """Diff the live A:B label stack against ROWS. Empty list means they match."""
    live = live_quarterly_ab(client)
    issues: list[str] = []
    for i in range(max(len(live), len(ROWS))):
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


def require_live_layout_match(client: Any, *, action: str) -> None:
    """Refuse to write if the live label stack has drifted from git."""
    issues = live_layout_mismatches(client)
    if not issues:
        return
    preview = "\n".join(f"  {line}" for line in issues[:25])
    extra = f"\n  … {len(issues) - 25} more" if len(issues) > 25 else ""
    raise SystemExit(
        f"Refusing to {action}: live {QUARTERLY} labels differ from "
        f"models/LODE/layout.py.\n{preview}{extra}\n"
        "Someone edited the row stack by hand. Run\n"
        "  python models/LODE/scripts/check_manual_changes.py\n"
        "to see what changed, reconcile the repo, then retry. Pass --force-rebuild "
        "only if you intend to replace the live layout from git."
    )
