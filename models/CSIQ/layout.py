"""Quarterly Financials row stack for CSIQ (Canadian Solar Inc.).

Same conventions as the Comstock pack this workbook is templated on:

* A bare label is a **reported print**, hardcoded from a filing, blank until reported.
* ``Label - Model`` is **always a formula** and prefers the actual when one exists.
* ``Label - Plan`` is a hand-maintained trajectory, painted yellow. Scalar assumptions
  live on the Levers tab.

Canadian Solar is not one earnings stream. The stack keeps US manufacturing (CS
PowerTech), the rest of manufacturing (mostly CSI Solar), and Recurrent Energy
visible separately so a single multiple is never applied to the mixture.
"""

from __future__ import annotations

from typing import Any

QUARTERLY = "Quarterly Financials"

FIRST_VALUE_COL = "C"
FIRST_VALUE_COL_INDEX = 3
YEARS = (2025, 2026, 2027, 2028, 2029, 2030)
N_QUARTERS = 4 * len(YEARS)
LAST_VALUE_COL = "Z"

LAST_REPORTED_QUARTER = "2026 Q2"
LAST_REPORTED_COL = "H"

# Quarter whose plan is the fully phased Lucas base case (6 GW modules, 5 GWh storage).
BASE_CASE_QUARTER = "2027 Q4"
# Quarter that contains the default As of date (2026-09-25).
CURRENT_QUARTER = "2026 Q3"

UNITS_GW = "GW"
UNITS_GWH = "GWh"
UNITS_M = "$M"
UNITS_PCT = "%"
UNITS_SHARES = "M shares"
UNITS_USD_W = "$/W"
UNITS_USD_KWH = "$/kWh"


YEAR = "Year"
QUARTER = "Quarter"
QUARTER_ENDING = "Quarter ending"
AS_OF_DATE = "As of date"
YEARS_FROM_PRESENT = "Years from present"

US_MODULE_PLAN = "US module shipments - Plan"
EXUS_MODULE_PLAN = "Ex-US module shipments - Plan"
MODULE_GW_ACTUAL = "Module shipments"
MODULE_GW_MODEL = "Module shipments - Model"
US_STORAGE_PLAN = "US storage shipments - Plan"
EXUS_STORAGE_PLAN = "Ex-US storage shipments - Plan"
STORAGE_GWH_ACTUAL = "Storage shipments"
STORAGE_GWH_MODEL = "Storage shipments - Model"
US_MODULE_PHASE = "US module margin phase-in - Plan"
US_STORAGE_PHASE = "US storage margin phase-in - Plan"

MODULE_REV_ACTUAL = "Module revenue"
MODULE_REV_MODEL = "Module revenue - Model"
STORAGE_REV_ACTUAL = "Storage revenue"
STORAGE_REV_MODEL = "Storage revenue - Model"
OTHER_MFG_REV_ACTUAL = "Other manufacturing revenue"
OTHER_MFG_REV_MODEL = "Other manufacturing revenue - Model"
MFG_REV_ACTUAL = "Manufacturing revenue"
MFG_REV_MODEL = "Manufacturing revenue - Model"

US_MODULE_EBITDA = "US module EBITDA - Model"
US_STORAGE_EBITDA = "US storage EBITDA - Model"
MFG_GP_ACTUAL = "Manufacturing gross profit"
MFG_GM_ACTUAL = "Manufacturing gross margin"
MFG_OI_ACTUAL = "Manufacturing operating income"

ASSET_SALES_PLAN = "Asset sales - Plan"
ASSET_SALES_ACTUAL = "Asset sales"
ASSET_SALES_MODEL = "Asset sales - Model"
POWER_PLAN = "Power services - Plan"
POWER_ACTUAL = "Power services"
POWER_MODEL = "Power services - Model"
ELECTRICITY_PLAN = "Electricity revenue - Plan"
ELECTRICITY_ACTUAL = "Electricity revenue"
ELECTRICITY_MODEL = "Electricity revenue - Model"
RECURRENT_REV_ACTUAL = "Recurrent revenue"
RECURRENT_REV_MODEL = "Recurrent revenue - Model"
RECURRENT_GP_ACTUAL = "Recurrent gross profit"
RECURRENT_OI_ACTUAL = "Recurrent operating income"

TOTAL_REV_ACTUAL = "Total revenue"
TOTAL_REV_MODEL = "Total revenue - Model"
GP_ACTUAL = "Gross profit"
GM_ACTUAL = "Gross margin"
GP_MODEL = "Gross profit - Model"
OPEX_ACTUAL = "Operating expenses"
OPEX_MODEL = "Operating expenses - Model"
OI_ACTUAL = "Operating income"
OI_MODEL = "Operating income - Model"
NI_ACTUAL = "Net income to CSIQ"
EPS_ACTUAL = "EPS to CSIQ"

CASH_ACTUAL = "Cash and equivalents"
RESTRICTED_ACTUAL = "Restricted cash"
CASH_RESTRICTED_ACTUAL = "Cash and restricted"
OCF_ACTUAL = "Operating cash flow"
CAPEX_ACTUAL = "Capital expenditures"
DEBT_ACTUAL = "Total debt"
CONVERTS_ACTUAL = "Convertible notes"
CONVERTS_MODEL = "Convertible notes - Model"
NONRECOURSE_ACTUAL = "Recurrent non-recourse debt"

SHARES_ACTUAL = "Shares outstanding"
SHARES_MODEL = "Shares outstanding - Model"
STOCK_PRICE = "Stock price"
MARKET_CAP = "Market cap"

CSI_STAKE = "CSI Solar stake - Model"
CSI_CROSSCHECK = "CSI Solar earnings cross-check - Model"
RECURRENT_STAKE = "Recurrent stake - Model"
US_MODULE_EQUITY = "US module equity value - Model"
US_STORAGE_EQUITY = "US storage equity value - Model"
HOLDCO_NET_DEBT = "Holdco net debt - Model"
FLOOR_EQUITY = "Floor equity value - Model"
EQUITY_VALUE = "Equity value - Model"
IMPLIED_PRICE = "Implied stock price - Model"
DILUTED_PRICE = "Implied price on diluted shares - Model"
PRESENT_PRICE = "Present stock price - Model"

SECTION_VOLUME = "MANUFACTURING — VOLUME"
SECTION_REVENUE = "MANUFACTURING — REVENUE"
SECTION_EARNINGS = "MANUFACTURING — EARNINGS"
SECTION_RECURRENT = "RECURRENT ENERGY"
SECTION_CONSOLIDATED = "CONSOLIDATED RESULTS"
SECTION_CASH = "CASH AND DEBT"
SECTION_SHARES = "SHARES AND PRICE"
SECTION_VALUATION = "VALUATION"

SECTION_LABELS: frozenset[str] = frozenset(
    {
        SECTION_VOLUME,
        SECTION_REVENUE,
        SECTION_EARNINGS,
        SECTION_RECURRENT,
        SECTION_CONSOLIDATED,
        SECTION_CASH,
        SECTION_SHARES,
        SECTION_VALUATION,
    }
)

ROWS: list[tuple[str, str]] = [
    ("", "Units"),
    (YEAR, ""),
    (QUARTER, ""),
    (QUARTER_ENDING, "date"),
    (AS_OF_DATE, "date"),
    (YEARS_FROM_PRESENT, "years"),
    ("", ""),
    (SECTION_VOLUME, ""),
    (US_MODULE_PLAN, UNITS_GW),
    (EXUS_MODULE_PLAN, UNITS_GW),
    (MODULE_GW_ACTUAL, UNITS_GW),
    (MODULE_GW_MODEL, UNITS_GW),
    (US_STORAGE_PLAN, UNITS_GWH),
    (EXUS_STORAGE_PLAN, UNITS_GWH),
    (STORAGE_GWH_ACTUAL, UNITS_GWH),
    (STORAGE_GWH_MODEL, UNITS_GWH),
    (US_MODULE_PHASE, UNITS_PCT),
    (US_STORAGE_PHASE, UNITS_PCT),
    ("", ""),
    (SECTION_REVENUE, ""),
    (MODULE_REV_ACTUAL, UNITS_M),
    (MODULE_REV_MODEL, UNITS_M),
    (STORAGE_REV_ACTUAL, UNITS_M),
    (STORAGE_REV_MODEL, UNITS_M),
    (OTHER_MFG_REV_ACTUAL, UNITS_M),
    (OTHER_MFG_REV_MODEL, UNITS_M),
    (MFG_REV_ACTUAL, UNITS_M),
    (MFG_REV_MODEL, UNITS_M),
    ("", ""),
    (SECTION_EARNINGS, ""),
    (US_MODULE_EBITDA, UNITS_M),
    (US_STORAGE_EBITDA, UNITS_M),
    (MFG_GP_ACTUAL, UNITS_M),
    (MFG_GM_ACTUAL, UNITS_PCT),
    (MFG_OI_ACTUAL, UNITS_M),
    ("", ""),
    (SECTION_RECURRENT, ""),
    (ASSET_SALES_PLAN, UNITS_M),
    (ASSET_SALES_ACTUAL, UNITS_M),
    (ASSET_SALES_MODEL, UNITS_M),
    (POWER_PLAN, UNITS_M),
    (POWER_ACTUAL, UNITS_M),
    (POWER_MODEL, UNITS_M),
    (ELECTRICITY_PLAN, UNITS_M),
    (ELECTRICITY_ACTUAL, UNITS_M),
    (ELECTRICITY_MODEL, UNITS_M),
    (RECURRENT_REV_ACTUAL, UNITS_M),
    (RECURRENT_REV_MODEL, UNITS_M),
    (RECURRENT_GP_ACTUAL, UNITS_M),
    (RECURRENT_OI_ACTUAL, UNITS_M),
    ("", ""),
    (SECTION_CONSOLIDATED, ""),
    (TOTAL_REV_ACTUAL, UNITS_M),
    (TOTAL_REV_MODEL, UNITS_M),
    (GP_ACTUAL, UNITS_M),
    (GM_ACTUAL, UNITS_PCT),
    (GP_MODEL, UNITS_M),
    (OPEX_ACTUAL, UNITS_M),
    (OPEX_MODEL, UNITS_M),
    (OI_ACTUAL, UNITS_M),
    (OI_MODEL, UNITS_M),
    (NI_ACTUAL, UNITS_M),
    (EPS_ACTUAL, "$"),
    ("", ""),
    (SECTION_CASH, ""),
    (CASH_ACTUAL, UNITS_M),
    (RESTRICTED_ACTUAL, UNITS_M),
    (CASH_RESTRICTED_ACTUAL, UNITS_M),
    (OCF_ACTUAL, UNITS_M),
    (CAPEX_ACTUAL, UNITS_M),
    (DEBT_ACTUAL, UNITS_M),
    (CONVERTS_ACTUAL, UNITS_M),
    (CONVERTS_MODEL, UNITS_M),
    (NONRECOURSE_ACTUAL, UNITS_M),
    ("", ""),
    (SECTION_SHARES, ""),
    (SHARES_ACTUAL, UNITS_SHARES),
    (SHARES_MODEL, UNITS_SHARES),
    (STOCK_PRICE, "$"),
    (MARKET_CAP, UNITS_M),
    ("", ""),
    (SECTION_VALUATION, ""),
    (CSI_STAKE, UNITS_M),
    (CSI_CROSSCHECK, UNITS_M),
    (RECURRENT_STAKE, UNITS_M),
    (US_MODULE_EQUITY, UNITS_M),
    (US_STORAGE_EQUITY, UNITS_M),
    (HOLDCO_NET_DEBT, UNITS_M),
    (FLOOR_EQUITY, UNITS_M),
    (EQUITY_VALUE, UNITS_M),
    (IMPLIED_PRICE, "$"),
    (DILUTED_PRICE, "$"),
    (PRESENT_PRICE, "$"),
]


# --- Editable trajectories -------------------------------------------------
# 2025 Q1 … 2030 Q4. Written once, then owned by the sheet. 2025 splits and any
# quarter without a filing are a plan, not a print — actual rows stay blank there.

# US module GW recognized. 2026 sums to 6.7, inside the reiterated 6.5–7.0 GW
# US guide, back-loaded the way management described H2. From 2027 the plan
# steps to 1.5 GW/quarter (6 GW/year): Lucas Sacerdote's base-case volume, which
# is the cell-constrained figure rather than the 10 GW Texas module nameplate.
US_MODULE_PATH: list[float] = [
    0.4, 0.5, 0.6, 0.8,
    0.9, 1.5, 1.9, 2.4,
    1.5, 1.5, 1.5, 1.5,
    1.5, 1.5, 1.5, 1.5,
    1.5, 1.5, 1.5, 1.5,
    1.5, 1.5, 1.5, 1.5,
]

# Ex-US module GW. 2026 Q1–Q2 are set so US + ex-US equals the reported total.
# Later years hold ~1.5–1.7 GW/quarter: management is managing volume, not
# rebuilding the ~25 GW run-rate.
EXUS_MODULE_PATH: list[float] = [
    6.2, 7.0, 5.0, 3.5,
    1.6, 1.6, 1.7, 1.6,
    1.6, 1.6, 1.6, 1.6,
    1.5, 1.5, 1.5, 1.5,
    1.5, 1.5, 1.5, 1.5,
    1.5, 1.5, 1.5, 1.5,
]

# US storage GWh. 2026 sums to 5.0, the midpoint of the 4.5–5.5 GWh US guide.
# 2027 onward is 1.25 GWh/quarter, Lucas's 5 GWh base, not the 20 GWh bull case.
US_STORAGE_PATH: list[float] = [
    0.3, 0.4, 0.5, 0.6,
    0.7, 1.0, 1.3, 2.0,
    1.25, 1.25, 1.25, 1.25,
    1.25, 1.25, 1.25, 1.25,
    1.25, 1.25, 1.25, 1.25,
    1.25, 1.25, 1.25, 1.25,
]

# Ex-US storage GWh. 2026 Q1–Q2 complete the reported global total; Q3 matches
# the midpoint of 3.4–3.8 GWh guidance once the US plan is subtracted.
EXUS_STORAGE_PATH: list[float] = [
    0.6, 1.7, 2.2, 1.4,
    1.4, 2.7, 2.3, 2.0,
    2.0, 2.0, 2.0, 2.0,
    2.0, 2.0, 2.0, 2.0,
    2.0, 2.0, 2.0, 2.0,
    2.0, 2.0, 2.0, 2.0,
]

# Percent of Lucas's steady US module margin earned this quarter. Jeffersonville
# opened July 2026 and management said ramp costs weigh through the rest of 2026,
# so 2026 stays near half. 100% from 2027 Q4, which is the base-case column.
US_MODULE_PHASE_PATH: list[float] = [
    20, 30, 35, 40,
    40, 45, 50, 55,
    70, 80, 90, 100,
    100, 100, 100, 100,
    100, 100, 100, 100,
    100, 100, 100, 100,
]

# Same idea for US storage margin. Parkin (Q1 2026) said storage competition is
# intensifying, so the 15% steady margin is not credited in full during 2026.
US_STORAGE_PHASE_PATH: list[float] = [
    30, 40, 50, 55,
    40, 55, 70, 85,
    100, 100, 100, 100,
    100, 100, 100, 100,
    100, 100, 100, 100,
    100, 100, 100, 100,
]

# Recurrent $M. 2026 Q3 asset sales step up because management said the Q2
# deferrals close in Q3. Later years are a flat recycle-capital pace, not a guide.
ASSET_SALES_PATH: list[float] = [
    72, 48, 40, 50,
    89, 61, 180, 80,
    70, 70, 70, 70,
    70, 70, 70, 70,
    70, 70, 70, 70,
    70, 70, 70, 70,
]

POWER_PATH: list[float] = [
    16, 19, 20, 21,
    22, 20, 21, 22,
    22, 22, 23, 23,
    23, 23, 24, 24,
    24, 24, 24, 24,
    24, 24, 24, 24,
]

ELECTRICITY_PATH: list[float] = [
    35, 37, 30, 28,
    26, 33, 36, 40,
    44, 48, 52, 56,
    60, 62, 64, 66,
    68, 70, 72, 74,
    76, 78, 80, 80,
]

EDITABLE_PATHS: dict[str, list[float]] = {
    US_MODULE_PLAN: US_MODULE_PATH,
    EXUS_MODULE_PLAN: EXUS_MODULE_PATH,
    US_STORAGE_PLAN: US_STORAGE_PATH,
    EXUS_STORAGE_PLAN: EXUS_STORAGE_PATH,
    US_MODULE_PHASE: US_MODULE_PHASE_PATH,
    US_STORAGE_PHASE: US_STORAGE_PHASE_PATH,
    ASSET_SALES_PLAN: ASSET_SALES_PATH,
    POWER_PLAN: POWER_PATH,
    ELECTRICITY_PLAN: ELECTRICITY_PATH,
}
EDITABLE_PATH_LABELS: tuple[str, ...] = tuple(EDITABLE_PATHS)

for _label, _path in EDITABLE_PATHS.items():
    if len(_path) != N_QUARTERS:
        raise ValueError(f"{_label} path has {len(_path)} values, expected {N_QUARTERS}")


NUMBER_FORMAT_1DP = "0.0"
NUMBER_FORMAT_2DP = "#,##0.00"
NUMBER_FORMAT_3DP = "0.000"

NUMBER_FORMAT_BY_LABEL: dict[str, str] = {
    YEARS_FROM_PRESENT: NUMBER_FORMAT_2DP,
    US_MODULE_PLAN: NUMBER_FORMAT_2DP,
    EXUS_MODULE_PLAN: NUMBER_FORMAT_2DP,
    MODULE_GW_ACTUAL: NUMBER_FORMAT_2DP,
    MODULE_GW_MODEL: NUMBER_FORMAT_2DP,
    US_STORAGE_PLAN: NUMBER_FORMAT_2DP,
    EXUS_STORAGE_PLAN: NUMBER_FORMAT_2DP,
    STORAGE_GWH_ACTUAL: NUMBER_FORMAT_2DP,
    STORAGE_GWH_MODEL: NUMBER_FORMAT_2DP,
    US_MODULE_PHASE: NUMBER_FORMAT_1DP,
    US_STORAGE_PHASE: NUMBER_FORMAT_1DP,
    MODULE_REV_ACTUAL: NUMBER_FORMAT_2DP,
    MODULE_REV_MODEL: NUMBER_FORMAT_2DP,
    STORAGE_REV_ACTUAL: NUMBER_FORMAT_2DP,
    STORAGE_REV_MODEL: NUMBER_FORMAT_2DP,
    OTHER_MFG_REV_ACTUAL: NUMBER_FORMAT_2DP,
    OTHER_MFG_REV_MODEL: NUMBER_FORMAT_2DP,
    MFG_REV_ACTUAL: NUMBER_FORMAT_2DP,
    MFG_REV_MODEL: NUMBER_FORMAT_2DP,
    US_MODULE_EBITDA: NUMBER_FORMAT_2DP,
    US_STORAGE_EBITDA: NUMBER_FORMAT_2DP,
    MFG_GP_ACTUAL: NUMBER_FORMAT_2DP,
    MFG_GM_ACTUAL: NUMBER_FORMAT_1DP,
    MFG_OI_ACTUAL: NUMBER_FORMAT_2DP,
    ASSET_SALES_PLAN: NUMBER_FORMAT_2DP,
    ASSET_SALES_ACTUAL: NUMBER_FORMAT_2DP,
    ASSET_SALES_MODEL: NUMBER_FORMAT_2DP,
    POWER_PLAN: NUMBER_FORMAT_2DP,
    POWER_ACTUAL: NUMBER_FORMAT_2DP,
    POWER_MODEL: NUMBER_FORMAT_2DP,
    ELECTRICITY_PLAN: NUMBER_FORMAT_2DP,
    ELECTRICITY_ACTUAL: NUMBER_FORMAT_2DP,
    ELECTRICITY_MODEL: NUMBER_FORMAT_2DP,
    RECURRENT_REV_ACTUAL: NUMBER_FORMAT_2DP,
    RECURRENT_REV_MODEL: NUMBER_FORMAT_2DP,
    RECURRENT_GP_ACTUAL: NUMBER_FORMAT_2DP,
    RECURRENT_OI_ACTUAL: NUMBER_FORMAT_2DP,
    TOTAL_REV_ACTUAL: NUMBER_FORMAT_2DP,
    TOTAL_REV_MODEL: NUMBER_FORMAT_2DP,
    GP_ACTUAL: NUMBER_FORMAT_2DP,
    GM_ACTUAL: NUMBER_FORMAT_1DP,
    GP_MODEL: NUMBER_FORMAT_2DP,
    OPEX_ACTUAL: NUMBER_FORMAT_2DP,
    OPEX_MODEL: NUMBER_FORMAT_2DP,
    OI_ACTUAL: NUMBER_FORMAT_2DP,
    OI_MODEL: NUMBER_FORMAT_2DP,
    NI_ACTUAL: NUMBER_FORMAT_2DP,
    EPS_ACTUAL: NUMBER_FORMAT_2DP,
    CASH_ACTUAL: NUMBER_FORMAT_2DP,
    RESTRICTED_ACTUAL: NUMBER_FORMAT_2DP,
    CASH_RESTRICTED_ACTUAL: NUMBER_FORMAT_2DP,
    OCF_ACTUAL: NUMBER_FORMAT_2DP,
    CAPEX_ACTUAL: NUMBER_FORMAT_2DP,
    DEBT_ACTUAL: NUMBER_FORMAT_2DP,
    CONVERTS_ACTUAL: NUMBER_FORMAT_2DP,
    CONVERTS_MODEL: NUMBER_FORMAT_2DP,
    NONRECOURSE_ACTUAL: NUMBER_FORMAT_2DP,
    SHARES_ACTUAL: NUMBER_FORMAT_3DP,
    SHARES_MODEL: NUMBER_FORMAT_3DP,
    STOCK_PRICE: NUMBER_FORMAT_2DP,
    MARKET_CAP: NUMBER_FORMAT_2DP,
    CSI_STAKE: NUMBER_FORMAT_2DP,
    CSI_CROSSCHECK: NUMBER_FORMAT_2DP,
    RECURRENT_STAKE: NUMBER_FORMAT_2DP,
    US_MODULE_EQUITY: NUMBER_FORMAT_2DP,
    US_STORAGE_EQUITY: NUMBER_FORMAT_2DP,
    HOLDCO_NET_DEBT: NUMBER_FORMAT_2DP,
    FLOOR_EQUITY: NUMBER_FORMAT_2DP,
    EQUITY_VALUE: NUMBER_FORMAT_2DP,
    IMPLIED_PRICE: NUMBER_FORMAT_2DP,
    DILUTED_PRICE: NUMBER_FORMAT_2DP,
    PRESENT_PRICE: NUMBER_FORMAT_2DP,
}

YELLOW = {"red": 1, "green": 0.95, "blue": 0.8}

QUARTERLY_COL_WIDTHS_PX: dict[int, int] = {
    0: 340,
    1: 78,
    **{i: 78 for i in range(2, 2 + N_QUARTERS)},
}


def quarters() -> list[tuple[int, int]]:
    return [(year, q) for year in YEARS for q in (1, 2, 3, 4)]


def quarter_keys() -> list[str]:
    return [f"{year} Q{q}" for year, q in quarters()]


def quarter_end_dates() -> list[str]:
    ends = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
    return [f"{year}-{ends[q]}" for year, q in quarters()]


def col_index_for_quarter(key: str) -> int:
    try:
        return FIRST_VALUE_COL_INDEX + quarter_keys().index(key)
    except ValueError as exc:
        raise KeyError(f"Quarter {key!r} not on the spine") from exc


def label_map_from_ab(rows: list[list]) -> dict[str, int]:
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
        raise KeyError(label)
    return rows[label]


def live_quarterly_ab(client: Any) -> list[list]:
    rows = client.batch_get([f"{QUARTERLY}!A1:B220"])[0]
    while rows and (not rows[-1] or not any(rows[-1])):
        rows.pop()
    return rows


def live_layout_mismatches(client: Any) -> list[str]:
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
    issues = live_layout_mismatches(client)
    if not issues:
        return
    preview = "\n".join(f"  {line}" for line in issues[:25])
    extra = f"\n  … {len(issues) - 25} more" if len(issues) > 25 else ""
    raise SystemExit(
        f"Refusing to {action}: live {QUARTERLY} labels differ from "
        f"models/CSIQ/layout.py.\n{preview}{extra}\n"
        "Reconcile the repo, or pass --force-rebuild to replace the live layout."
    )
