"""Welcome tab copy for the EOSE Model workbook."""

from __future__ import annotations

WELCOME_SHEET = "Welcome"

REPO_URL = "https://github.com/MarkPhillips7/open-model"
X_PROFILE_URL = "https://x.com/MarkPhillips7"
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing"
)
IR_URL = "https://investors.eose.com/"

TITLE = "EOSE Model — Welcome"

DISCLAIMER = (
    "Nothing in this spreadsheet should be construed as financial advice, an offer to buy or sell "
    "securities, or a recommendation of any kind. The model mixes company-reported metrics, "
    "management commentary, and explicit assumptions where Eos does not disclose detail. Numbers "
    "can be wrong, out of date, or reflect my own interpretation. Do your own research and consult "
    "a qualified professional before making investment decisions."
)

FEEDBACK_X = (
    "Thoughtful feedback and discussion are welcome. If something looks off, if you disagree with an "
    "assumption, or if you have ideas to improve the model, please reach out on X: "
)

THANKS = (
    "Thank you to everyone who comments on this workbook and to Eos management for publishing "
    "backlog, pipeline, and factory commentary alongside GAAP results. This model would be much "
    "thinner without that disclosure."
)

RESOURCES = (
    "This model is built and maintained with help from Cursor (AI-assisted editing in this repository) "
    "and the public tooling at {repo}. Sources include Eos quarterly and annual earnings releases and "
    "10-Q/10-K filings ({ir}), plus notes on the Reference tab. See RESOURCES.md in the repository "
    "for a fuller citation list."
)

GOALS = (
    "Goals: keep reported actuals on their own rows (blank when not yet printed) and a parallel "
    "Model path so misses are visible. The commercial funnel is quarterly — pipeline → booked orders "
    "→ backlog → shipments — with factory capacity as a ceiling. There is no weekly spine: Eos "
    "does not publish a high-frequency unit funnel. 45X / production credits are treated as a COGS "
    "offset, not as revenue. Unit COGS follows the Q2 2026 cost-out waterfall on the COGS tab, "
    "scaled by Percent of Guided Cost Cutting Achieved (default 70%)."
)

TAB_GUIDE_INTRO = (
    "Use the links below to jump to each tab. Cell comments and Financials Definitions explain "
    "sourcing. Charts, if you add them, should overlay Actual (solid) and Model (dotted) — do not "
    "edit chart objects via the Sheets API."
)

TAB_DESCRIPTIONS: list[tuple[str, str]] = [
    (
        "Quarterly Financials",
        "Main time series, one column per quarter (2025 Q1 – 2030 Q4). Actuals from earnings/"
        "10-Q; Model rows for factory, backlog conversion, P&L, cash, and valuation.",
    ),
    (
        "Financials Definitions",
        "Row-by-row notes: what each field means and whether it is reported, a formula, or a guess.",
    ),
    (
        "Shares",
        "Share-count event table (offerings, converts, warrants). Drives Fully diluted shares - Model "
        "after the last reported actual.",
    ),
    (
        "Price History",
        "GOOGLEFINANCE daily EOSE prices. Stock price on Quarterly Financials looks up the last "
        "close on or before quarter-end.",
    ),
    (
        "Reference",
        "Source links for ASP, 45X treatment, and Feltonomics.",
    ),
    (
        "Feltonomics",
        "Placeholder — independent model cited on Reference. Intentionally empty for now.",
    ),
    (
        "COGS",
        "Unit-cost build-up from the Q2 2026 Slide 11 cost-out (materials 25 / conversion 20 / "
        "projects 20 / scrap 8 pts of adj. GM). Haircut defaults to 70%. After the 12-month plan, "
        "remaining gap to terminal $/kWh is absorbed as Lines 3–4 ramp. Feeds Unit COGS - Model.",
    ),
]

CLOSING = (
    "If you spot mistakes, disagree with an assumption or formula, or have suggestions of any kind, "
    "I would genuinely appreciate hearing from you. Thank you for visiting — I hope this workbook "
    "helps you think more clearly about Eos Energy's business and investment case."
)
