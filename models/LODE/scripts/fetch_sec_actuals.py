#!/usr/bin/env python3
"""Refresh data/sec_quarterly_actuals.json from the SEC XBRL API.

Comstock tags most income-statement and cash-flow concepts cumulatively (year to
date), so a discrete quarter often has to be derived by subtracting the prior
year-to-date period. This script does that and records how each derived figure was
produced, so nothing on the sheet is untraceable.

    python models/LODE/scripts/fetch_sec_actuals.py
    python models/LODE/scripts/fetch_sec_actuals.py --quarter "2026 Q3"

Values that the filings do not contain are left as null. The script never
interpolates — a gap in the data should look like a gap.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

CIK = "0001120970"
DATA_PATH = ROOT / "models" / "LODE" / "data" / "sec_quarterly_actuals.json"
COMPANY_FACTS = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

# The SEC requires a descriptive User-Agent with contact information.
HEADERS = {"User-Agent": "open-model LODE research (github.com/MarkPhillips7/open-model)"}

# Sheet-facing metric name → candidate us-gaap tags, most preferred first.
# Comstock has changed tags across filings, hence the fallbacks.
TAG_MAP: dict[str, tuple[str, ...]] = {
    "revenue_total": (
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
    ),
    "cost_of_revenue": ("CostOfRevenue", "CostOfGoodsAndServicesSold"),
    "gross_profit": ("GrossProfit",),
    "opex_general_and_administrative": ("GeneralAndAdministrativeExpense",),
    "opex_selling_and_marketing": ("SellingAndMarketingExpense",),
    "opex_research_and_development": ("ResearchAndDevelopmentExpense",),
    "opex_depreciation_and_amortization": (
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
    ),
    "opex_impairment_goodwill_and_intangibles": (
        "ImpairmentOfIntangibleAssetsIncludingGoodwill",
        "GoodwillAndIntangibleAssetImpairment",
    ),
    "opex_impairment_ppe": (
        "ImpairmentOfLongLivedAssetsHeldForUse",
        "TangibleAssetImpairmentCharges",
    ),
    "opex_total": ("OperatingExpenses", "CostsAndExpenses"),
    "operating_income_loss": ("OperatingIncomeLoss",),
    "interest_expense": ("InterestExpense", "InterestExpenseNonoperating"),
    "interest_income": ("InvestmentIncomeInterest",),
    "net_loss_attributable_to_common": (
        "NetIncomeLossAvailableToCommonStockholdersBasic",
        "NetIncomeLoss",
    ),
    "net_loss_including_nci": ("ProfitLoss", "NetIncomeLoss"),
    "eps_basic": ("EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"),
    "eps_diluted": ("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),
    "wavg_shares_basic": (
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
    ),
    # Balance sheet (instant facts — no derivation needed).
    "cash_and_cash_equivalents": ("CashAndCashEquivalentsAtCarryingValue",),
    "total_current_assets": ("AssetsCurrent",),
    "total_assets": ("Assets",),
    "total_current_liabilities": ("LiabilitiesCurrent",),
    "total_liabilities": ("Liabilities",),
    "total_stockholders_equity": ("StockholdersEquity",),
    "investments_equity_method": ("EquityMethodInvestments",),
    "assets_held_for_sale_current": (
        "DisposalGroupIncludingDiscontinuedOperationAssetsCurrent",
    ),
    "liabilities_held_for_sale_current": (
        "DisposalGroupIncludingDiscontinuedOperationLiabilitiesCurrent",
    ),
    "common_shares_outstanding_period_end": ("CommonStockSharesOutstanding",),
    "ppe_net": ("PropertyPlantAndEquipmentNet",),
    "goodwill": ("Goodwill",),
    # Cash flow (cumulative — derived to discrete quarters below).
    "cf_net_cash_used_in_operating": (
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ),
    "cf_net_cash_used_in_investing": ("NetCashProvidedByUsedInInvestingActivities",),
    "cf_net_cash_from_financing": ("NetCashProvidedByUsedInFinancingActivities",),
    "cf_capex_purchases_of_ppe_and_mineral_rights": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ),
    "cf_proceeds_from_issuance_of_common_stock": (
        "ProceedsFromIssuanceOfCommonStock",
        "ProceedsFromIssuanceOrSaleOfEquity",
    ),
    "cf_stock_based_compensation": ("ShareBasedCompensation",),
    "cf_depreciation_and_amortization": ("DepreciationDepletionAndAmortization",),
}

# Facts reported at a point in time rather than over a period.
INSTANT_METRICS = frozenset(
    {
        "cash_and_cash_equivalents",
        "total_current_assets",
        "total_assets",
        "total_current_liabilities",
        "total_liabilities",
        "total_stockholders_equity",
        "investments_equity_method",
        "assets_held_for_sale_current",
        "liabilities_held_for_sale_current",
        "common_shares_outstanding_period_end",
        "ppe_net",
        "goodwill",
    }
)

# Per-share and per-period figures that cannot be derived by subtraction.
NON_ADDITIVE = frozenset({"eps_basic", "eps_diluted", "wavg_shares_basic"})

QUARTER_ENDS = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
QUARTER_STARTS = {1: "01-01", 2: "04-01", 3: "07-01", 4: "10-01"}


def _fetch(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"SEC request failed ({exc.code}) for {url}") from exc


def _quarter_key(year: int, quarter: int) -> str:
    return f"{year} Q{quarter}"


def _units(facts: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    concept = facts.get("us-gaap", {}).get(tag)
    if not concept:
        return []
    for unit_values in concept.get("units", {}).values():
        return unit_values
    return []


def _pick(
    entries: list[dict[str, Any]], *, start: str | None, end: str
) -> float | None:
    """Most recently filed value matching the exact period, preferring 10-K over 10-Q."""
    matches = [
        e
        for e in entries
        if e.get("end") == end and (start is None or e.get("start") == start)
    ]
    if not matches:
        return None
    matches.sort(key=lambda e: (e.get("filed", ""), e.get("form", "")))
    return matches[-1].get("val")


def build(target_quarters: list[tuple[int, int]]) -> dict[str, Any]:
    facts = _fetch(COMPANY_FACTS)["facts"]
    notes: list[str] = []
    quarters: dict[str, Any] = {}

    for year, quarter in target_quarters:
        end = f"{year}-{QUARTER_ENDS[quarter]}"
        start = f"{year}-{QUARTER_STARTS[quarter]}"
        ytd_start = f"{year}-01-01"
        prior_end = (
            f"{year}-{QUARTER_ENDS[quarter - 1]}" if quarter > 1 else None
        )
        key = _quarter_key(year, quarter)
        metrics: dict[str, Any] = {}

        for metric, tags in TAG_MAP.items():
            entries: list[dict[str, Any]] = []
            for tag in tags:
                entries = _units(facts, tag)
                if entries:
                    break
            if not entries:
                metrics[metric] = None
                continue

            if metric in INSTANT_METRICS:
                metrics[metric] = _pick(entries, start=None, end=end)
                continue

            discrete = _pick(entries, start=start, end=end)
            if discrete is not None:
                metrics[metric] = discrete
                continue

            if metric in NON_ADDITIVE:
                metrics[metric] = None
                notes.append(
                    f"{key} {metric}: no discrete-quarter context and the figure is not "
                    "additive across periods, so it was left null rather than derived."
                )
                continue

            ytd = _pick(entries, start=ytd_start, end=end)
            prior_ytd = (
                _pick(entries, start=ytd_start, end=prior_end) if prior_end else None
            )
            if ytd is not None and quarter == 1:
                metrics[metric] = ytd
            elif ytd is not None and prior_ytd is not None:
                metrics[metric] = ytd - prior_ytd
                notes.append(
                    f"{key} {metric}: derived as year-to-date through {end} minus "
                    f"year-to-date through {prior_end}."
                )
            else:
                metrics[metric] = None

        quarters[key] = {
            "period_start": start,
            "period_end": end,
            "metrics": metrics,
        }

    return {
        "cik": CIK,
        "entity": "Comstock Inc.",
        "ticker": "LODE",
        "retrieved": date.today().isoformat(),
        "note": (
            "Discrete quarterly periods, values in USD as reported. Derived figures are "
            "listed in derivation_notes. Nulls mean the filings do not contain the value; "
            "nothing is interpolated."
        ),
        "source": COMPANY_FACTS,
        "quarters": quarters,
        "derivation_notes": sorted(set(notes)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quarter",
        action="append",
        default=None,
        help='Quarter to fetch, e.g. "2026 Q3". Repeatable. Default: 2024 Q1 to now.',
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge into the existing JSON instead of replacing it (keeps hand-checked fields).",
    )
    args = parser.parse_args()

    if args.quarter:
        targets = []
        for item in args.quarter:
            year_text, quarter_text = item.split()
            targets.append((int(year_text), int(quarter_text.lstrip("Qq"))))
    else:
        today = date.today()
        targets = [
            (y, q)
            for y in range(2024, today.year + 1)
            for q in (1, 2, 3, 4)
            if date(y, int(QUARTER_ENDS[q][:2]), int(QUARTER_ENDS[q][3:])) < today
        ]

    payload = build(targets)

    if args.merge and DATA_PATH.exists():
        existing = json.loads(DATA_PATH.read_text())
        existing_quarters = existing.get("quarters", {})
        existing_quarters.update(payload["quarters"])
        existing["quarters"] = existing_quarters
        existing["retrieved"] = payload["retrieved"]
        existing["derivation_notes"] = sorted(
            set(existing.get("derivation_notes", [])) | set(payload["derivation_notes"])
        )
        payload = existing

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"Wrote {DATA_PATH.relative_to(ROOT)} with {len(payload['quarters'])} quarter(s).\n"
        "Next: add the new quarter to REPORTED_QUARTERS in models/LODE/actuals.py, "
        "then run load_quarterly_actuals.py."
    )


if __name__ == "__main__":
    main()
