"""Repeatable source map for EOSE quarterly actuals.

GAAP P&L, cash, debt, and share counts come from SEC companyfacts / 10-Q / 10-K.
Commercial funnel (pipeline, backlog, booked orders) and adjusted EBITDA come from
the earnings 8-K Exhibit 99.1 (and the earnings-call transcript when GWh is only
spoken, not tabulated).

After each print:

1. ``python models/EOSE/scripts/fetch_sec_gaap.py`` — pull XBRL vs ``actuals.py``
2. Open the earnings 8-K Ex. 99.1 (IR or EDGAR) for adj. EBITDA, pipeline, backlog
3. Patch ``actuals.py`` (native sheet units: $M unless noted)
4. ``python models/EOSE/scripts/load_quarterly_actuals.py``
5. Append ``models/EOSE/CHANGELOG.md``
"""

from __future__ import annotations

CIK = "0001805077"
CIK_INT = 1805077
COMPANYFACTS_URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"
SUBMISSIONS_URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"
IR_EARNINGS = "https://investors.eose.com/news-releases"

# EDGAR index: https://www.sec.gov/Archives/edgar/data/{CIK_INT}/{accession_nodashes}/
FILINGS: dict[tuple[int, int], dict[str, str]] = {
    (2025, 1): {
        "form": "10-Q",
        "period_end": "2025-03-31",
        "accession": "0001805077-25-000051",
        "html": "https://www.sec.gov/Archives/edgar/data/1805077/000180507725000051/eose-20250331.htm",
        "earnings_8k": "https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-records-highest-quarterly-revenue-and",
        "earnings_pdf": "https://investors.eose.com/node/11541/pdf",
        "slides": "https://investors.eose.com/static-files/37bf65c1-0b9f-409a-8a14-4e02c51038cb",
        "transcript": "https://www.roic.ai/quote/EOSEW/transcripts/2025-year/1-quarter",
    },
    (2025, 2): {
        "form": "10-Q",
        "period_end": "2025-06-30",
        "accession": "0001805077-25-000154",
        "html": "https://www.sec.gov/Archives/edgar/data/1805077/000180507725000154/eose-20250630.htm",
        "earnings_8k_html": (
            "https://www.sec.gov/Archives/edgar/data/1805077/"
            "000180507725000152/eoseq22025earningsreleas.htm"
        ),
        "earnings_ir": (
            "https://investors.eose.com/news-releases/news-release-details/"
            "eos-energy-enterprises-delivers-record-quarterly-revenue-nearly"
        ),
        "slides": "https://investors.eose.com/static-files/9f77f7a1-7547-4d12-a596-3ccd63341ec4",
    },
    (2025, 3): {
        "form": "10-Q",
        "period_end": "2025-09-30",
        "accession": "0001628280-25-049588",
        "html": "https://www.sec.gov/Archives/edgar/data/1805077/000162828025049588/eose-20250930.htm",
        "earnings_8k_html": (
            "https://www.sec.gov/Archives/edgar/data/1805077/"
            "000162828025049552/eoseq32025earningsreleas.htm"
        ),
        "earnings_ir": (
            "https://investors.eose.com/news-releases/news-release-details/"
            "eos-energy-enterprises-delivers-highest-company-quarterly"
        ),
    },
    (2025, 4): {
        "form": "10-K",
        "period_end": "2025-12-31",
        "accession": "0001628280-26-011961",
        "html": "https://www.sec.gov/Archives/edgar/data/1805077/000162828026011961/eose-20251231.htm",
        "earnings_8k_html": (
            "https://www.sec.gov/Archives/edgar/data/1805077/"
            "000162828026011958/eoseq4fy25earningsreleas.htm"
        ),
        "earnings_ir": (
            "https://investors.eose.com/news-releases/news-release-details/"
            "eos-energy-enterprises-reports-fourth-quarter-and-full-year-2025"
        ),
        "transcript": (
            "https://earningscalls.dev/transcripts/"
            "eos-energy-enterprises-inc_eose_earnings_call_transcript_2026-02-26"
        ),
    },
    (2026, 1): {
        "form": "10-Q",
        "period_end": "2026-03-31",
        "accession": "0001628280-26-034368",
        "html": "https://www.sec.gov/Archives/edgar/data/1805077/000162828026034368/eose-20260331.htm",
        "earnings_ir": (
            "https://investors.eose.com/news-releases/news-release-details/"
            "eos-energy-enterprises-reports-first-quarter-2026-financial"
        ),
        "transcript": (
            "https://www.theglobeandmail.com/investing/markets/stocks/EOSE/"
            "pressreleases/1912895/eos-energy-eose-q1-2026-earnings-transcript/"
        ),
    },
    (2026, 2): {
        "form": "10-Q",
        "period_end": "2026-06-30",
        "accession": "0001628280-26-052906",
        "html": "https://www.sec.gov/Archives/edgar/data/1805077/000162828026052906/eose-20260630.htm",
        "earnings_8k_html": (
            "https://www.sec.gov/Archives/edgar/data/1805077/"
            "000162828026052903/eoseq2fy26earningsreleas.htm"
        ),
        "earnings_ir": (
            "https://investors.eose.com/news-releases/news-release-details/"
            "eos-energy-enterprises-reports-second-quarter-2026-financial"
        ),
        "transcript": "https://www.roic.ai/quote/EOSEW/transcripts/2026-year/2-quarter",
    },
}

# companyfacts tag → sheet Actual label. Instant tags are period-end; duration tags
# must use the quarter-only frame (CY2025Q1, not YTD).
GAAP_DURATION_TAGS: dict[str, str] = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": "Revenue",
    "CostOfGoodsAndServicesSold": "COGS",
    "GrossProfit": "Gross profit",
    "ResearchAndDevelopmentExpense": "R&D",
    "SellingGeneralAndAdministrativeExpense": "SG&A",
    "NetIncomeLoss": "GAAP net income",
    "WeightedAverageNumberOfSharesOutstandingBasic": "Basic shares",
    "WeightedAverageNumberOfDilutedSharesOutstanding": "Fully diluted shares",
}

GAAP_INSTANT_TAGS: dict[str, str] = {
    # Cash + restricted cash (earnings "total cash")
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": "Cash",
    # 10-Q line "Long-term debt" is named LTD minus related-party notes; derived in fetch
    "LongTermDebt": "Total debt",
    "LongTermDebtNoncurrent": "_ltd_noncurrent",
    "LongTermNotesPayable": "_related_party_notes",
}

# Scale companyfacts native units → sheet units.
SCALE: dict[str, float] = {
    "Revenue": 1e-6,
    "COGS": 1e-6,
    "Gross profit": 1e-6,
    "R&D": 1e-6,
    "SG&A": 1e-6,
    "GAAP net income": 1e-6,
    "Cash": 1e-6,
    "Total debt": 1e-6,
    "Long term debt": 1e-6,
    "Basic shares": 1e-6,
    "Fully diluted shares": 1e-6,
}
