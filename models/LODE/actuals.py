"""Reported prints for LODE, mapped from SEC XBRL onto Quarterly Financials rows.

Values are read from ``data/sec_quarterly_actuals.json``, which is pulled straight
from the SEC's companyfacts/companyconcept APIs and checked into git. Mapping here
rather than retyping numbers means a figure on the sheet can always be traced to a
filing, and re-pulling after an earnings release updates everything at once.

Only rows the company actually reports appear here. Operating metrics Comstock does
not disclose — tons processed, capacity utilization — are deliberately absent so
they stay blank on the sheet rather than being back-solved from revenue.

Units: the sheet works in $M and millions of shares; the JSON is in dollars and
whole shares, so the converters below do that division in one place.

Scope note: the spine starts at 2025 Q1, which is after the 1-for-10 reverse split
of 2025-02-24. Every share figure used here is therefore already on today's basis
and needs no split adjustment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from models.LODE import layout as L

DATA_PATH = Path(__file__).resolve().parent / "data" / "sec_quarterly_actuals.json"

# Quarters Comstock has reported, in spine order. Anything later stays blank.
REPORTED_QUARTERS: tuple[str, ...] = (
    "2025 Q1",
    "2025 Q2",
    "2025 Q3",
    "2025 Q4",
    "2026 Q1",
    "2026 Q2",
)


def _millions(value: float) -> float:
    return round(value / 1_000_000, 4)


def _abs_millions(value: float) -> float:
    """Report cost-like lines as positive magnitudes, matching the sheet's convention."""
    return round(abs(value) / 1_000_000, 4)


def _raw(value: float) -> float:
    return round(value, 4)


def _sum_millions(*metric_names: str) -> Callable[[dict[str, Any]], float | None]:
    def getter(metrics: dict[str, Any]) -> float | None:
        parts = [metrics.get(name) for name in metric_names]
        if all(p is None for p in parts):
            return None
        return round(sum(p or 0 for p in parts) / 1_000_000, 4)

    return getter


def _single(
    metric_name: str,
    convert: Callable[[float], float] = _millions,
) -> Callable[[dict[str, Any]], float | None]:
    def getter(metrics: dict[str, Any]) -> float | None:
        value = metrics.get(metric_name)
        return None if value is None else convert(value)

    return getter


# Sheet row label → how to pull it out of the SEC metrics blob.
#
# Sign conventions, chosen so the sheet reads naturally:
#   * Revenue, gross profit, cash, and share counts are as reported.
#   * Operating loss and net loss stay NEGATIVE, because they are losses.
#   * Operating expenses, capex, and impairments are POSITIVE magnitudes.
#   * Operating cash flow stays NEGATIVE when cash is being consumed, so it can be
#     added directly in the Cash - Model roll-forward.
ROW_SOURCES: dict[str, Callable[[dict[str, Any]], float | None]] = {
    L.METALS_REVENUE_ACTUAL: _single("revenue_segment_metals"),
    L.TOTAL_REVENUE_ACTUAL: _single("revenue_total"),
    L.GROSS_PROFIT_ACTUAL: _single("gross_profit"),
    L.OPEX_ACTUAL: _single("opex_total", _abs_millions),
    L.IMPAIRMENTS_ACTUAL: _sum_millions(
        "opex_impairment_goodwill_and_intangibles",
        "opex_impairment_ppe",
    ),
    L.OPERATING_LOSS_ACTUAL: _single("operating_income_loss"),
    L.NET_LOSS_ACTUAL: _single("net_loss_attributable_to_common"),
    L.EPS_ACTUAL: _single("eps_basic", _raw),
    L.CASH_ACTUAL: _single("cash_and_cash_equivalents"),
    L.OCF_ACTUAL: _single("cf_net_cash_used_in_operating"),
    L.CAPEX_ACTUAL: _single(
        "cf_capex_purchases_of_ppe_and_mineral_rights", _abs_millions
    ),
    L.EQUITY_ISSUED_ACTUAL: _single(
        "cf_proceeds_from_issuance_of_common_stock", _abs_millions
    ),
    # Comstock carries no conventional debt. The only debt-like instrument is the
    # Marathon SAFE note, held at fair value in long-term liabilities, so that is
    # what "Total debt" means in this model — and it is what net cash subtracts.
    L.TOTAL_DEBT_ACTUAL: _single("safe_note_convertible_noncurrent"),
    L.SHARES_ACTUAL: _single("common_shares_outstanding_period_end"),
}

# Rows that are reported but not in XBRL, or that need a hand-set value.
#
# Industry-scale production lines: zero through 2026 Q2. Comstock's revenue in
# these quarters comes from the ~5,000 t/yr demonstration facility, which is about
# 5% of one industry-scale line. Counting it as a fraction of a line would drag a
# full line's $15M/yr fixed cost into quarters that never carried it, so the demo
# is left out of the capacity model and shows up only in reported revenue.
MANUAL_ROW_VALUES: dict[str, dict[str, Any]] = {
    L.LINES_ACTUAL: {q: 0 for q in REPORTED_QUARTERS},
}


def _load() -> dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing {DATA_PATH}. Run models/LODE/scripts/fetch_sec_actuals.py first."
        )
    return json.loads(DATA_PATH.read_text())


def quarterly_actuals() -> dict[str, dict[str, Any]]:
    """``{row label: {quarter key: value}}`` for every reported figure."""
    payload = _load()
    quarters = payload.get("quarters", {})
    out: dict[str, dict[str, Any]] = {}

    for label, getter in ROW_SOURCES.items():
        series: dict[str, Any] = {}
        for quarter in REPORTED_QUARTERS:
            metrics = quarters.get(quarter, {}).get("metrics", {})
            if not metrics:
                continue
            value = getter(metrics)
            if value is not None:
                series[quarter] = value
        if series:
            out[label] = series

    for label, series in MANUAL_ROW_VALUES.items():
        out.setdefault(label, {}).update(series)

    # Share counts are reported in whole shares but displayed in millions.
    if L.SHARES_ACTUAL in out:
        out[L.SHARES_ACTUAL] = {
            q: round(v, 4) for q, v in out[L.SHARES_ACTUAL].items()
        }

    return out


def latest_reported_quarter() -> str:
    return REPORTED_QUARTERS[-1]


def consolidated_cash_ga_run_rate() -> float:
    """CONSOLIDATED cash G&A, in $M per quarter, from the last print.

    This is a CEILING, not the ``Corporate cash G&A per quarter`` lever default.
    Do not paste it into the Levers tab.

    Built as reported G&A + selling & marketing, less stock compensation, it sums
    ALL FIVE segments. That makes it roughly 3x the lever, which carries only the
    Corporate/Other segment ($2,572,589 in 2026 Q2 per the 10-Q segment note, or
    ~$2.25M net of share-settled comp). The difference is cost the model already
    carries elsewhere, so including it here would double-count:

    * **Bioleum/Fuels G&A** (~$2.4M in 2026 Q2) plus Fuels **R&D** (~$2.3M).
      Bioleum is funded by third parties and management is explicit that Comstock
      is not putting more equity in — Comstock's own cash exposure is the bridge
      loan, sized separately by the fuels burn and bridge levers.
    * **Metals** cost, which belongs to the $15M/line/year fixed cost in the
      metals engine.
    * **Mining** G&A, which the legacy-mining-cost lever strips out from the
      closing quarter (the sale closed 2026-08-24).

    The dataset in ``data/sec_quarterly_actuals.json`` carries revenue by segment
    but NOT G&A by segment, so the lever basis cannot be recomputed here — read
    the segment note in the filing. Useful as a trend check: consolidated G&A has
    gone $3.02M -> $7.00M in six quarters.
    """
    metrics = _load()["quarters"][latest_reported_quarter()]["metrics"]
    cash_ga = (
        (metrics.get("opex_general_and_administrative") or 0)
        + (metrics.get("opex_selling_and_marketing") or 0)
        - (metrics.get("cf_stock_based_compensation") or 0)
    )
    return round(cash_ga / 1_000_000, 2)
