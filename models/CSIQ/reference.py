"""Reference tab."""

from __future__ import annotations

REFERENCE_SHEET = "Reference"

HEADER = ["Source", "Link", "What it is used for"]
COL_WIDTHS_PX: dict[int, int] = {0: 380, 1: 460, 2: 700}

SECTION_FILINGS = "FILINGS AND RELEASES"
SECTION_THESIS = "THE 2026-04-28 THESIS"
SECTION_DATA = "MARKET DATA"

SECTION_LABELS: frozenset[str] = frozenset({SECTION_FILINGS, SECTION_THESIS, SECTION_DATA})

ROWS: list[tuple[str, str, str]] = [
    (SECTION_FILINGS, "", ""),
    (
        "Q2 2026 earnings release (2026-08-27)",
        "https://investors.canadiansolar.com/news-releases/news-release-details/canadian-solar-reports-second-quarter-2026-results",
        "Latest actuals: revenue $1.208B, gross margin 13.9%, module 3.1 GW, storage 3.7 GWh, "
        "segment note, pipelines, US guides, Jeffersonville and Mesquite status, cash and debt.",
    ),
    (
        "Q1 2026 earnings release (2026-05-14)",
        "https://investors.canadiansolar.com/news-releases/news-release-details/canadian-solar-reports-first-quarter-2026-results-and-announces",
        "Q1 actuals, the $93M tariff refund, CEO change (Colin Parkin; Shawn Qu to Executive Chairman and CTO), "
        "and the December 2025 CS PowerTech structure.",
    ),
    (
        "CSI Solar ownership 6-K (2026-04-27)",
        "https://www.sec.gov/Archives/edgar/data/1375877/000110465926049421/tm2612799d1_6k.htm",
        "Canadian Solar owns approximately 64% of CSI Solar (Shanghai STAR Market).",
    ),
    (
        "Q2 2026 earnings call (2026-08-27)",
        "https://investors.canadiansolar.com/events",
        "Nearly half of Q2 module volume went to North America. Revenue was recognized on 3.3 GWh "
        "of storage (3.7 GWh shipped, 471 MWh internal). 13 GW of US module bookings through 2029 "
        "discussed at mid-$0.30/W. Spain 426 MW reached COD. Section 232 called accretive, not sized.",
    ),
    (SECTION_THESIS, "", ""),
    (
        "Canadian Solar [Full Investment Thesis], Lucas Sacerdote (2026-04-28, 2h 50m)",
        "https://www.youtube.com/watch?v=egSupfYmkVE",
        "The base-case unit economics and the sum of parts: CSI Solar at a 30% discount to a $7B "
        "Shanghai cap, Recurrent at the BlackRock $2.5B mark, US modules at 7.5¢/W on 6 GW after "
        "a $250M lease and 8×, US storage at 5 GWh / $200/kWh / 15% / 12×, about $9B or $100 a "
        "share on 90M diluted shares. Bear about $11, bull about $323 with a 15% weight. "
        "Recorded before the Q1 and Q2 2026 releases. Notes in models/CSIQ/data/.",
    ),
    (SECTION_DATA, "", ""),
    (
        "GOOGLEFINANCE daily CSIQ",
        "https://www.google.com/finance/quote/CSIQ:NASDAQ",
        "Price History tab. The Stock price row looks up the last close on or before each quarter-end.",
    ),
]


def grid() -> list[list[str]]:
    return [list(HEADER), *([list(row) for row in ROWS])]


def section_rows() -> list[int]:
    return [i + 2 for i, row in enumerate(ROWS) if row[0] in SECTION_LABELS]


NOTE = (
    "The thesis is a source for the levers, not a price target this sheet endorses. "
    "Where a later filing contradicts it, the filing is the actual."
)
