"""Canonical ``* - Model`` formulas for the LODE Quarterly Financials tab.

Every formula here is the single source of truth for what should be on the live
sheet. ``scripts/validate_model_formulas.py --ticker LODE`` diffs the sheet against
these templates, and ``scripts/restore_weekly_model_formulas.py --ticker LODE``
writes them back. Templates use ``{c}`` for the current column, ``{cp}`` for the
prior column, and ``{Row Label}`` for a row reference resolved against the live
label stack — never a hardcoded row number, so inserting a row cannot silently
break a formula.

Two rules shape the whole file:

1. A Model row always prefers a reported actual when one exists. The projection
   only takes over past the last print, so history is exact by construction.
2. Scalar assumptions come from the Levers tab by absolute reference. No magic
   numbers in formulas — if you find one here, it is a bug.
"""

from __future__ import annotations

import re
from typing import Any

from sheets.formulas import col_letter as _col_letter

from models.LODE import levers as lv
from models.LODE.layout import (
    ADJ_EBITDA_MODEL,
    AS_OF_DATE,
    BREAKEVEN_UTILIZATION_MODEL,
    CAPEX_ACTUAL,
    CAPEX_MODEL,
    CASH_ACTUAL,
    CASH_MODEL,
    CORP_GA_MODEL,
    EQUITY_ISSUED_ACTUAL,
    EQUITY_ISSUED_MODEL,
    FIRST_VALUE_COL,
    FIRST_VALUE_COL_INDEX,
    FUELS_BRIDGE_MODEL,
    LINES_ACTUAL,
    LINES_MODEL,
    LINES_PLAN,
    MARKET_CAP,
    MATERIAL_MODEL,
    METALS_CAPEX_MODEL,
    METALS_CONTRIBUTION_MODEL,
    METALS_COST_MODEL,
    METALS_FIXED_COST_MODEL,
    METALS_MARGIN_MODEL,
    METALS_REVENUE_ACTUAL,
    METALS_REVENUE_MODEL,
    METALS_VARIABLE_COST_MODEL,
    MINING_PROCEEDS_MODEL,
    N_QUARTERS,
    OCF_ACTUAL,
    OCF_MODEL,
    QUARTER,
    QUARTER_ENDING,
    QUARTERLY,
    RATED_CAPACITY,
    REVENUE_PER_TON_MODEL,
    RUNWAY_MODEL,
    SHARES_ACTUAL,
    SHARES_MODEL,
    SHARES_MODEL_QOQ,
    SSOF_PROCEEDS_MODEL,
    STOCK_PRICE,
    TIPPING_MODEL,
    TONS_ACTUAL,
    TONS_MODEL,
    TOTAL_DEBT_ACTUAL,
    TOTAL_DEBT_MODEL,
    TOTAL_REVENUE_ACTUAL,
    TOTAL_REVENUE_MODEL,
    UPLIFT_PHASE_IN,
    UTILIZATION_ACTUAL,
    UTILIZATION_MODEL,
    UTILIZATION_PLAN,
    YEAR,
    YEARS_FROM_PRESENT,
    label_map_from_ab,
    live_quarterly_ab,
    require_live_layout_match,
)

FINANCIALS_TAB = QUARTERLY
FIRST_VALUE_COL = FIRST_VALUE_COL
FIRST_VALUE_COL_INDEX = FIRST_VALUE_COL_INDEX

# Kept for the shared validator's interface; this pack has no column-relative set.
COLUMN_RELATIVE_TEMPLATES: dict[str, str] = {}

_LABEL_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")

PRICE_HISTORY_SHEET = "Price History"

# Ten years. Past this, "quarters of cash remaining" is a divide-by-almost-zero artifact
# rather than information, so the row tops out here.
RUNWAY_CAP_QUARTERS = 40


def col_letter(n: int) -> str:
    return _col_letter(n)


def apply_row_labels(template: str, label_to_row: dict[str, int]) -> str:
    out = template
    for label in sorted(label_to_row, key=len, reverse=True):
        out = out.replace("{" + label + "}", str(label_to_row[label]))
    return out


def sheet_label_map(client: Any) -> dict[str, int]:
    return label_map_from_ab(live_quarterly_ab(client))


def assert_live_layout(client: Any, *, action: str = "restore model formulas") -> None:
    require_live_layout_match(client, action=action)


# --- small builders --------------------------------------------------------


def _cur(label: str) -> str:
    return f"{{c}}{{{label}}}"


def _prev(label: str) -> str:
    return f"{{cp}}{{{label}}}"


def _prefer_actual(actual: str, model: str) -> str:
    """Reported print wins when present, so a miss shows up instead of being hidden."""
    return f'IF({actual}<>"",{actual},{model})'


def _blank_if_no_quarter(body: str) -> str:
    return f'=IF({_cur(YEAR)}="","",{body})'


def _quarter_index() -> str:
    """Monotonic quarter number, for comparing against a ``"2026 Q3"`` lever."""
    return f"({_cur(YEAR)}*4+{_cur(QUARTER)})"


def _lever_quarter_index(lever_label: str) -> str:
    ref = lv.lever_ref(lever_label)
    return f"(VALUE(LEFT({ref},4))*4+VALUE(RIGHT({ref},1)))"


def _lever(label: str) -> str:
    return lv.lever_ref(label)


# --- formulas --------------------------------------------------------------


def _years_from_present() -> str:
    return (
        f'=IF({_cur(QUARTER_ENDING)}="","",'
        f"({_cur(QUARTER_ENDING)}-{_cur(AS_OF_DATE)})/365)"
    )


def _lines_model() -> str:
    """Line 1 is built, so only the *incremental* lines get the achievement haircut."""
    plan = _cur(LINES_PLAN)
    achieved = _lever(lv.LINE_EXPANSION_ACHIEVED)
    scaled = f"IF({plan}<=0,0,1+({plan}-1)*{achieved}/100)"
    return _blank_if_no_quarter(_prefer_actual(_cur(LINES_ACTUAL), scaled))


def _utilization_model() -> str:
    plan = _cur(UTILIZATION_PLAN)
    achieved = _lever(lv.UTILIZATION_ACHIEVED)
    return _blank_if_no_quarter(
        _prefer_actual(_cur(UTILIZATION_ACTUAL), f"{plan}*{achieved}/100")
    )


def _tons_model() -> str:
    """Quarterly tons = effective lines × (annual rated capacity ÷ 4) × utilization."""
    model = (
        f"{_cur(LINES_MODEL)}*{_cur(RATED_CAPACITY)}/4*{_cur(UTILIZATION_MODEL)}/100"
    )
    return _blank_if_no_quarter(_prefer_actual(_cur(TONS_ACTUAL), model))


def _tipping_model() -> str:
    return _blank_if_no_quarter(
        f"{_lever(lv.TIPPING_FEE_PER_TON)}*{_lever(lv.TIPPING_FEE_ACHIEVED)}/100"
    )


def _material_model() -> str:
    """Today's realised material value, plus the two unproven uplifts once phased in."""
    glass = f"{_lever(lv.GLASS_UPLIFT_PER_TON)}*{_lever(lv.GLASS_UPLIFT_ACHIEVED)}/100"
    metal = f"{_lever(lv.METAL_UPLIFT_PER_TON)}*{_lever(lv.METAL_UPLIFT_ACHIEVED)}/100"
    phase = f"{_cur(UPLIFT_PHASE_IN)}/100"
    return _blank_if_no_quarter(
        f"{_lever(lv.MATERIAL_BASE_PER_TON)}+({glass}+{metal})*{phase}"
    )


def _revenue_per_ton_model() -> str:
    return _blank_if_no_quarter(f"{_cur(TIPPING_MODEL)}+{_cur(MATERIAL_MODEL)}")


def _metals_revenue_model() -> str:
    model = f"{_cur(TONS_MODEL)}*{_cur(REVENUE_PER_TON_MODEL)}/1000000"
    return _blank_if_no_quarter(_prefer_actual(_cur(METALS_REVENUE_ACTUAL), model))


def _metals_fixed_cost_model() -> str:
    """Fixed because the plant is designed to run the ovens continuously."""
    return _blank_if_no_quarter(
        f"{_cur(LINES_MODEL)}*{_lever(lv.FIXED_COST_PER_LINE)}/4"
    )


def _metals_variable_cost_model() -> str:
    return _blank_if_no_quarter(
        f"{_cur(METALS_REVENUE_MODEL)}*{_lever(lv.VARIABLE_COST_PCT)}/100"
    )


def _metals_cost_model() -> str:
    return _blank_if_no_quarter(
        f"{_cur(METALS_FIXED_COST_MODEL)}+{_cur(METALS_VARIABLE_COST_MODEL)}"
    )


def _metals_contribution_model() -> str:
    return _blank_if_no_quarter(
        f"{_cur(METALS_REVENUE_MODEL)}-{_cur(METALS_COST_MODEL)}"
    )


def _metals_margin_model() -> str:
    return (
        f'=IF(N({_cur(METALS_REVENUE_MODEL)})=0,"",'
        f"{_cur(METALS_CONTRIBUTION_MODEL)}/{_cur(METALS_REVENUE_MODEL)}*100)"
    )


def _breakeven_utilization_model() -> str:
    """Utilization at which one line covers its own fixed cost.

    Solving lines × rated × u × $/ton × (1 − variable%) = lines × fixed gives
    u = fixed ÷ (rated × $/ton × (1 − variable%)), independent of line count.
    With the default levers this lands near 25%, which is the number management
    quotes — so this row doubles as a check that the levers stay internally
    consistent with the company's own claim.
    """
    denom = (
        f"{_cur(RATED_CAPACITY)}*{_cur(REVENUE_PER_TON_MODEL)}"
        f"*(1-{_lever(lv.VARIABLE_COST_PCT)}/100)"
    )
    return (
        f'=IF(N({_cur(REVENUE_PER_TON_MODEL)})=0,"",'
        f"{_lever(lv.FIXED_COST_PER_LINE)}*1000000/({denom})*100)"
    )


def _metals_capex_model() -> str:
    """Charged when the line count steps up. Real spend leads revenue by 2–3 quarters."""
    return _blank_if_no_quarter(
        f"{_lever(lv.CAPEX_PER_LINE)}*MAX(0,{_cur(LINES_MODEL)}-{_prev(LINES_MODEL)})"
    )


def _metals_capex_model_first() -> str:
    return _blank_if_no_quarter(
        f"{_lever(lv.CAPEX_PER_LINE)}*MAX(0,{_cur(LINES_MODEL)})"
    )


def _total_revenue_model() -> str:
    """Past the last print, recycling is the only revenue: mining is sold, fuels is not consolidated."""
    return _blank_if_no_quarter(
        _prefer_actual(_cur(TOTAL_REVENUE_ACTUAL), _cur(METALS_REVENUE_MODEL))
    )


def _corp_ga_model() -> str:
    """Flat cash overhead, less the legacy mining cost that leaves with the sale."""
    saving = (
        f"IF({_quarter_index()}>={_lever_quarter_index(lv.MINING_SALE_QUARTER)},"
        f"{_lever(lv.MINING_COST_SAVINGS)}/4,0)"
    )
    return _blank_if_no_quarter(f"{_lever(lv.CORP_CASH_GA)}-{saving}")


def _adj_ebitda_model() -> str:
    return _blank_if_no_quarter(
        f"{_cur(METALS_CONTRIBUTION_MODEL)}-{_cur(CORP_GA_MODEL)}"
    )


def _ocf_model() -> str:
    """Adjusted EBITDA is the cash proxy: minimal working capital, losses are mostly cash."""
    return _blank_if_no_quarter(
        _prefer_actual(_cur(OCF_ACTUAL), _cur(ADJ_EBITDA_MODEL))
    )


def _capex_model() -> str:
    return _blank_if_no_quarter(
        _prefer_actual(_cur(CAPEX_ACTUAL), _cur(METALS_CAPEX_MODEL))
    )


def _mining_proceeds_model() -> str:
    """Two contractual payments: $20M cash at closing, then the $7M second tranche."""
    initial = (
        f"IF({_quarter_index()}={_lever_quarter_index(lv.MINING_SALE_QUARTER)},"
        f"{_lever(lv.MINING_SALE_CASH)},0)"
    )
    second = (
        f"IF({_quarter_index()}="
        f"{_lever_quarter_index(lv.MINING_SECOND_TRANCHE_QUARTER)},"
        f"{_lever(lv.MINING_SECOND_TRANCHE)},0)"
    )
    return _blank_if_no_quarter(f"{initial}+{second}")


def _ssof_proceeds_model() -> str:
    """Only the portion of the SSOF stake actually sold for cash, which defaults to none.

    SSOF is unsigned, so it is deliberately kept out of the base-case cash line and
    credited as option value on the Valuation tab instead. The last factor is the
    switch that lets you move it into cash.
    """
    value = (
        f"{_lever(lv.SSOF_GROSS_VALUE)}*{_lever(lv.SSOF_OWNERSHIP)}/100"
        f"*{_lever(lv.SSOF_ACHIEVED)}/100*{_lever(lv.SSOF_CASH_SOLD)}/100"
    )
    return _blank_if_no_quarter(
        f"IF({_quarter_index()}={_lever_quarter_index(lv.SSOF_PROCEEDS_QUARTER)},"
        f"{value},0)"
    )


def _fuels_bridge_model() -> str:
    """Loan, not equity. Positive magnitude here; subtracted in Cash - Model."""
    quarter = f"{_lever_quarter_index(lv.MINING_SALE_QUARTER)}"
    return _blank_if_no_quarter(
        f"IF({_quarter_index()}={quarter},{_lever(lv.FUELS_BRIDGE_TOTAL)},0)"
    )


def _equity_issued_model() -> str:
    """Deliberately no assumed rescue raise — a negative Cash - Model is the funding gap."""
    return _blank_if_no_quarter(_prefer_actual(_cur(EQUITY_ISSUED_ACTUAL), "0"))


def _cash_model_body(prior: str) -> str:
    flows = (
        f"{_cur(OCF_MODEL)}-{_cur(CAPEX_MODEL)}+{_cur(MINING_PROCEEDS_MODEL)}"
        f"+{_cur(SSOF_PROCEEDS_MODEL)}-{_cur(FUELS_BRIDGE_MODEL)}"
        f"+{_cur(EQUITY_ISSUED_MODEL)}"
    )
    return _prefer_actual(_cur(CASH_ACTUAL), f"{prior}+{flows}")


def _cash_model() -> str:
    return _blank_if_no_quarter(_cash_model_body(_prev(CASH_MODEL)))


def _cash_model_first() -> str:
    """No prior column to roll forward from, so column C must be a reported cash balance."""
    return _blank_if_no_quarter(f'IF({_cur(CASH_ACTUAL)}<>"",{_cur(CASH_ACTUAL)},"")')


def _runway_model() -> str:
    """Quarters of cash left at this quarter's burn. Blank when the quarter self-funds.

    Capped at 40 quarters. Without the cap a quarter that burns almost nothing divides
    by a near-zero denominator and prints thousands of quarters, which looks like a
    number but is noise; 40 should be read as "ten years or more, i.e. not a concern".
    """
    burn = f"({_cur(CAPEX_MODEL)}-{_cur(OCF_MODEL)})"
    return (
        f'=IF(OR({_cur(CASH_MODEL)}="",{burn}<=0),"",'
        f"MIN({RUNWAY_CAP_QUARTERS},{_cur(CASH_MODEL)}/{burn}))"
    )


def _total_debt_model() -> str:
    return _blank_if_no_quarter(
        _prefer_actual(_cur(TOTAL_DEBT_ACTUAL), _prev(TOTAL_DEBT_MODEL))
    )


def _total_debt_model_first() -> str:
    return _blank_if_no_quarter(
        _prefer_actual(_cur(TOTAL_DEBT_ACTUAL), "0")
    )


def _shares_model() -> str:
    """Actual when reported, else a slow drip for vesting stock comp and ATM use."""
    return _blank_if_no_quarter(
        _prefer_actual(_cur(SHARES_ACTUAL), f"{_prev(SHARES_MODEL)}*{SHARES_MODEL_QOQ}")
    )


def _shares_model_first() -> str:
    return _blank_if_no_quarter(_prefer_actual(_cur(SHARES_ACTUAL), '""'))


def _stock_price() -> str:
    """Last daily close on or before quarter end; blank for quarters still in the future.

    The GOOGLEFINANCE spill is bound once with LET and then split into its date and
    close columns. Referencing the tab a single time keeps the formula shorter and
    avoids the shared validator's row-literal heuristic tripping over a second
    ``'Price History'!`` reference.
    """
    qe = _cur(QUARTER_ENDING)
    return (
        f"=LET(d,'{PRICE_HISTORY_SHEET}'!$A$2:$E,"
        f'IF(OR({qe}="",{qe}>TODAY()),"",'
        f'IFERROR(XLOOKUP({qe},INDEX(d,0,1),INDEX(d,0,5),"",-1),"")))'
    )


def _market_cap() -> str:
    return (
        f'=IF(OR(N({_cur(SHARES_MODEL)})=0,N({_cur(STOCK_PRICE)})=0),"",'
        f"{_cur(SHARES_MODEL)}*{_cur(STOCK_PRICE)})"
    )


# --- template registry ----------------------------------------------------

UNIFORM_FORMULA_TEMPLATES: dict[str, str] = {
    AS_OF_DATE: f"={_lever(lv.AS_OF_DATE)}",
    YEARS_FROM_PRESENT: _years_from_present(),
    RATED_CAPACITY: f"={_lever(lv.RATED_CAPACITY_PER_LINE)}",
    LINES_MODEL: _lines_model(),
    UTILIZATION_MODEL: _utilization_model(),
    TONS_MODEL: _tons_model(),
    TIPPING_MODEL: _tipping_model(),
    MATERIAL_MODEL: _material_model(),
    REVENUE_PER_TON_MODEL: _revenue_per_ton_model(),
    METALS_REVENUE_MODEL: _metals_revenue_model(),
    METALS_FIXED_COST_MODEL: _metals_fixed_cost_model(),
    METALS_VARIABLE_COST_MODEL: _metals_variable_cost_model(),
    METALS_COST_MODEL: _metals_cost_model(),
    METALS_CONTRIBUTION_MODEL: _metals_contribution_model(),
    METALS_MARGIN_MODEL: _metals_margin_model(),
    BREAKEVEN_UTILIZATION_MODEL: _breakeven_utilization_model(),
    METALS_CAPEX_MODEL: _metals_capex_model(),
    TOTAL_REVENUE_MODEL: _total_revenue_model(),
    CORP_GA_MODEL: _corp_ga_model(),
    ADJ_EBITDA_MODEL: _adj_ebitda_model(),
    OCF_MODEL: _ocf_model(),
    CAPEX_MODEL: _capex_model(),
    MINING_PROCEEDS_MODEL: _mining_proceeds_model(),
    SSOF_PROCEEDS_MODEL: _ssof_proceeds_model(),
    FUELS_BRIDGE_MODEL: _fuels_bridge_model(),
    EQUITY_ISSUED_MODEL: _equity_issued_model(),
    CASH_MODEL: _cash_model(),
    RUNWAY_MODEL: _runway_model(),
    TOTAL_DEBT_MODEL: _total_debt_model(),
    SHARES_MODEL: _shares_model(),
    STOCK_PRICE: _stock_price(),
    MARKET_CAP: _market_cap(),
}

# Column C has no prior column, so rows that roll forward need their own opener.
FIRST_COL_TEMPLATES: dict[str, str] = {
    METALS_CAPEX_MODEL: _metals_capex_model_first(),
    CASH_MODEL: _cash_model_first(),
    TOTAL_DEBT_MODEL: _total_debt_model_first(),
    SHARES_MODEL: _shares_model_first(),
}

MODEL_FORMULA_LABELS: tuple[str, ...] = tuple(UNIFORM_FORMULA_TEMPLATES)


def formula_row_dependencies(label: str) -> frozenset[str]:
    tmpl = UNIFORM_FORMULA_TEMPLATES.get(label, "") + FIRST_COL_TEMPLATES.get(label, "")
    return frozenset(
        m.group(1)
        for m in _LABEL_PLACEHOLDER_RE.finditer(tmpl)
        if m.group(1) not in {"c", "cp"}
    )


def uniform_formula_template(label: str) -> str:
    return UNIFORM_FORMULA_TEMPLATES[label]


def row_cells_for_label(
    label: str,
    n_cols: int,
    *,
    label_to_row: dict[str, int] | None = None,
) -> list[Any] | None:
    if label not in UNIFORM_FORMULA_TEMPLATES:
        return None
    label_to_row = label_to_row or {}
    general = apply_row_labels(UNIFORM_FORMULA_TEMPLATES[label], label_to_row)
    first = (
        apply_row_labels(FIRST_COL_TEMPLATES[label], label_to_row)
        if label in FIRST_COL_TEMPLATES
        else general
    )
    cells: list[Any] = []
    for i in range(n_cols):
        col = col_letter(FIRST_VALUE_COL_INDEX + i)
        prior = col_letter(FIRST_VALUE_COL_INDEX + i - 1)
        tmpl = first if i == 0 else general
        cells.append(tmpl.replace("{c}", col).replace("{cp}", prior))
    return cells


assert N_QUARTERS == 24
