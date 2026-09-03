"""Welcome tab copy for the Opendoor Model workbook."""

from __future__ import annotations

WELCOME_SHEET = "Welcome"

REPO_URL = "https://github.com/MarkPhillips7/open-model"
ACCOUNTABLE_URL = "https://accountable.opendoor.com/"
X_PROFILE_URL = "https://x.com/MarkPhillips7"

TITLE = "Opendoor Model — Welcome"

DISCLAIMER = (
    "Nothing in this spreadsheet should be construed as financial advice, an offer to buy or sell securities, or a recommendation of any kind. The model mixes company-reported metrics, management commentary, independent trackers, and explicit assumptions where Opendoor does not disclose detail. Numbers can be wrong, out of date, or reflect my own interpretation. Do your own research and consult a qualified professional before making investment decisions."
)

FEEDBACK_X = (
    "Thoughtful feedback and discussion are welcome. If something looks off, if you disagree with an "
    "assumption, or if you have ideas to improve the model, please reach out on X: "
)

THANKS = (
    "Thank you to the OPEN Army and to Opendoor management for striving to share as much information publicly as possible — through earnings materials, SEC filings, the Accountable site, and ongoing product and leadership updates. This workbook would not exist without that transparency."
)

RESOURCES = (
    "This model is built and maintained with help from Cursor (AI-assisted editing in this repository) "
    "and the public tooling at {repo}. Sources include Opendoor quarterly and annual earnings "
    "reports and supplements, the weekly acquisition tracking on {accountable}, listing and funnel "
    "signals from independent trackers, housing-market seasonality references, and comments and "
    "guidance from earnings calls — especially under CEO Kaz Nejatian's leadership. See "
    "RESOURCES.md in the repository for a fuller citation list."
)

GOALS = (
    "Goals and assumptions: anchor as much as possible in facts — reported actuals, official guidance, and publicly observable data — then model the forward path in a way that is reasonable and, where management has been explicit, primarily follows Kaz's guidance (volume recovery, contribution-margin path, fixed-cost discipline, ancillary attach, and accountability targets). Where disclosure is missing, the sheet states that plainly and uses adjustable levers rather than pretending precision."
)

TAB_GUIDE_INTRO = (
    "Use the links below to jump to each tab. The spreadsheet is also sprinkled with cell comments to explain sourcing, formulas, and judgment calls — hover or right-click cells to read them."
)

TAB_DESCRIPTIONS: list[tuple[str, str]] = [
    (
        "Weekly Financials",
        "Main time series by week ending. Reported actuals, forward model rows, and the full operating funnel from acquisition contracts through revenue, contribution margin, opex, and inventory.",
    ),
    (
        "Quarterly Financials",
        "Same row layout as Weekly Financials, one column per quarter. Enter quarterly earnings actuals here; they spread across weeks on the main tab.",
    ),
    (
        "Financials Definitions",
        "Reference for every row label on Weekly Financials — what the field means and how it is sourced or modeled.",
    ),
    (
        "Homes Chart",
        "Opendoor Homes: line chart of weekly home metrics — contracts, purchases, listings, sales, and inventory (actual vs model).",
    ),
    (
        "Money Charts",
        "Two separate line charts. Opendoor Weekly Revenue and Shares: Revenue and Basic Shares Outstanding (each actual + model). Opendoor Weekly Profit and Price: Contribution Profit, Adjusted EBITDA, Adjusted Net Income, and Net Income Attributable to Common Shareholders (each actual + model), plus Price (Actual) and implied prices at P/S = 2 and P/S = 3 on the right axis.",
    ),
    (
        "Transitions",
        "Lag and probability tables: contract→purchase timing, listing vs private-sale paths, sell-through curves, cash mix, ancillary attach, and OPEN 1.0→2.0 transition weights.",
    ),
    (
        "Shares",
        "Share-count event table (buybacks, converts, warrant scenarios) and SBC assumptions that drive modeled basic shares on Weekly Financials.",
    ),
    (
        "Seasonality",
        "Monthly acquisition seasonality weights (peak Nov–Dec) used to shape the weekly Acquisition Seasonality Multiplier.",
    ),
    (
        "Price History",
        "GOOGLEFINANCE daily OPEN prices; Weekly Financials looks up the close by week-ending date.",
    ),
]

CLOSING = (
    "If you spot mistakes, disagree with an assumption or formula, or have suggestions of any kind, "
    "I would genuinely appreciate hearing from you. Thank you for visiting — I hope this workbook "
    "helps you think more clearly about Opendoor's business and investment case."
)
