"""Reference tab: where every number in this workbook came from."""

from __future__ import annotations

REFERENCE_SHEET = "Reference"

HEADER = ["Source", "Link", "What it is used for"]
COL_WIDTHS_PX: dict[int, int] = {0: 380, 1: 420, 2: 700}

SECTION_FILINGS = "SEC FILINGS AND COMPANY DISCLOSURE"
SECTION_COMMENTARY = "MANAGEMENT COMMENTARY"
SECTION_DATA = "MARKET AND PRICE DATA"
SECTION_INDEPENDENT = "INDEPENDENT AND COMMUNITY WORK"

SECTION_LABELS: frozenset[str] = frozenset(
    {SECTION_FILINGS, SECTION_COMMENTARY, SECTION_DATA, SECTION_INDEPENDENT}
)

# (source, link, used_for)
ROWS: list[tuple[str, str, str]] = [
    (SECTION_FILINGS, "", ""),
    (
        "Q2 2026 Form 10-Q (period ended 2026-06-30)",
        "https://www.sec.gov/Archives/edgar/data/1120970/000143774926024304/lode20260630_10q.htm",
        "Every reported actual in the model's most recent quarter, the Metals segment revenue "
        "breakdown (Recycling / Decommissioning Services / Off-take), the Marathon SAFE note used as "
        "'Total debt', held-for-sale balances, and the exact Mackay purchase-agreement terms — "
        "including the '$20,000,000 in cash (the Initial Payment)' language.",
    ),
    (
        "Q2 2026 earnings release (8-K Exhibit 99.1, 2026-07-23)",
        "https://www.sec.gov/Archives/edgar/data/1120970/000143774926024415/ex_992178.htm",
        "The H2 2026 guide: solar recycling facility running in August at 'at least 25% of rated "
        "capacity' through year end, generating about $5M of revenue. This is what the default "
        "utilization ramp is calibrated to reproduce.",
    ),
    (
        "SEC XBRL company facts, CIK 0001120970",
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0001120970.json",
        "Machine-readable source for all historical quarterly actuals. Pulled into "
        "data/sec_quarterly_actuals.json so every figure on the sheet traces back to a filing.",
    ),
    (
        "All Comstock SEC filings",
        "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001120970&type=10-Q",
        "Filing index, for checking whether a newer quarter has been reported.",
    ),
    (
        "Comstock investor relations",
        "https://www.comstockinc.com/investors/",
        "Press releases, earnings webcasts, and presentations.",
    ),
    (SECTION_COMMENTARY, "", ""),
    (
        "CEO interview — Corrado De Gasperis with Lucas Sacerdote (2026-08-11, 95 min)",
        "https://www.youtube.com/watch?v=QGzT-ExtP0k",
        "The primary source for the recycling unit economics: ~100,000 tons/year and ~3.3M panels "
        "per line, $12–15M capex and ~$15M/year opex per line, $500/ton tipping fee, $125–200/ton "
        "material value today against a ~$1,000/ton theoretical, glass uplift of $30–60/ton, 1.5–2 "
        "lb of metal per ton of tailings, gas and electricity under 7% of revenue, breakeven at "
        "~25% utilization, and roughly one-year payback at 50%. Also the SSOF facts (2,500 acres "
        "owned, ~2,000 acre-feet of water, 300 MW secured with a November 2028 pipeline, $400–600M "
        "comps) and the fuels position (bridge loan not equity, ~$650k/month burn, $65M liquidation "
        "preference). Full transcript in data/youtube_interview_2026-08-11.md.",
    ),
    (
        "Q2 2026 earnings call transcript (2026-07-23)",
        "https://seekingalpha.com/article/4925054-comstock-inc-lode-q2-2026-earnings-call-transcript",
        "Management's own framing of the quarter, the Flux Photon impairment, and the fuels funding "
        "position.",
    ),
    (SECTION_DATA, "", ""),
    (
        "GOOGLEFINANCE daily LODE prices",
        "",
        "One spill formula on the Price History tab. The Stock price row on Quarterly Financials "
        "looks up the last close on or before each quarter-end.",
    ),
    (SECTION_INDEPENDENT, "", ""),
    (
        "Lucas Sacerdote / Valora Investment Group",
        "https://www.youtube.com/watch?v=QGzT-ExtP0k",
        "Registered investment adviser and disclosed Comstock shareholder who interviewed the CEO "
        "and maintains his own model. The framing of tipping fee plus material value per ton, and "
        "the per-factory capex and opex comparison, follows the ground he covered in that interview.",
    ),
    (
        "open-model repository",
        "https://github.com/MarkPhillips7/open-model",
        "The Python tooling that builds and validates this workbook, plus RESOURCES.md with a fuller "
        "citation list and CHANGELOG.md recording every write to this sheet.",
    ),
]

NOTE = (
    "Not investment advice. Where Comstock has not disclosed something, this model uses an explicit "
    "assumption with a lever attached rather than a silent estimate — see the Levers tab for the "
    "rationale and source behind each one."
)


def grid() -> list[list[object]]:
    out: list[list[object]] = [list(HEADER)]
    for source, link, used_for in ROWS:
        out.append([source, link, used_for])
    return out


def section_rows() -> list[int]:
    return [i for i, (s, _l, _u) in enumerate(ROWS, start=2) if s in SECTION_LABELS]
