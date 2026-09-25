"""Welcome tab copy for the CSIQ workbook."""

from __future__ import annotations

WELCOME_SHEET = "Welcome"

COL_WIDTHS_PX: dict[int, int] = {0: 280, 1: 920}

REPO_URL = "https://github.com/MarkPhillips7/open-model"
X_PROFILE_URL = "https://x.com/MarkPhillips7"
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1kCYZnwJyOKNRnyDPlyQyGCYOwkelu944fJ7yEEKyEeo/edit"
)
IR_URL = "https://investors.canadiansolar.com/"

TITLE = "CSIQ Model — Canadian Solar Inc."

DISCLAIMER = (
    "Nothing here is financial advice, an offer to buy or sell securities, or a recommendation. "
    "The workbook mixes filings, management guidance, and explicit assumptions, including a "
    "long public investment thesis that is one person's view. Numbers can be wrong, stale, or "
    "simply my reading of them. Do your own work."
)

GOALS = (
    "Goal: show Canadian Solar's reported results through the latest quarter, then project "
    "forward with every assumption visible. Reported rows stay blank until the company prints "
    "them. Every '- Model' row prefers that print, so a miss shows up instead of being overwritten."
)

APPROACH = (
    "Canadian Solar is three claims sitting in one ticker. CSI Solar is a Shanghai-listed "
    "manufacturer Canadian Solar owns about 64% of. CS PowerTech is the US cell and module "
    "buildout, 75.1% owned directly since December 2025. Recurrent Energy is the project "
    "platform BlackRock bought 20% of in early 2024 at a $2.5B post-money value. One earnings "
    "multiple on the consolidated loss describes none of those. Quarterly Financials values "
    "them separately. The US ramp is phased, because Jeffersonville opened in July 2026 and "
    "management said those ramp costs weigh on the rest of the year. The Shanghai stake and "
    "the Recurrent mark are not phased: they are present-value claims, and only the US piece "
    "is discounted."
)

WHY_LEVERS = (
    "The 2026-04-28 thesis (Lucas Sacerdote) is the source of the base-case unit economics: "
    "7.5¢/W on 6 GW of US modules after a $250M lease, 8× that EBITDA; 5 GWh of US storage "
    "at $200/kWh and a 15% margin, 12× that EBITDA; CSI Solar at a 30% discount to a $7B "
    "Shanghai cap; Recurrent at the BlackRock mark. Those numbers stay on the Levers tab as "
    "the claim. Scepticism is a different cell: ownership (75.1% so the slice CSI Solar "
    "already holds is not counted twice), the yellow phase-in rows, the holdco discount, "
    "and the 'achieved' dials. Set PowerTech ownership to 100% and the discount rate to 0 "
    "if you want the video's arithmetic rather than the guarded one."
)

CALIBRATION = (
    "Two checks worth doing before you trust a price. At 2027 Q4, with default levers, US "
    "module EBITDA annualizes to about $200M and US storage EBITDA to about $150M — the "
    "thesis base case, before the 75.1% stake. And 2026 Q3 total revenue should fall inside "
    "the $1.3–1.5B guide. The $7B Shanghai cap is the video's April 2026 figure, not a live "
    "quote; if you do nothing else, update that lever. Charts are not built by the scripts. "
    "If you want the Comstock-style picture, chart Present stock price and Stock price on the "
    "left and US module EBITDA on the right, by hand."
)

MANUAL_EDITS = (
    "Yellow cells are yours: column C on Levers, and every '- Plan' row on Quarterly "
    "Financials. Formulas are regenerated from the repository. If you change a generated "
    "formula by hand, the next restore will put it back — change the lever or the plan instead."
)

FEEDBACK = (
    "If a number is wrong or a lever default is foolish, I want to hear it. X: "
)

SOURCES_NOTE = (
    "Built from the Q1 and Q2 2026 earnings releases, the Q2 2026 segment note, the April 2026 "
    "6-K on CSI Solar's ownership, and Lucas Sacerdote's 2026-04-28 investment thesis "
    "(https://www.youtube.com/watch?v=egSupfYmkVE). The thesis predates both 2026 earnings "
    "prints. Where they disagree, the filing is the actual and the thesis is the lever. "
    "Citations are on the Reference tab."
)

TAB_DESCRIPTIONS: list[tuple[str, str]] = [
    (
        "Levers",
        "Every scalar, with units, a default, a range, and a source. Column C is the live value. "
        "Start here. The Shanghai market cap in particular goes stale.",
    ),
    (
        "Quarterly Financials",
        "2025 Q1 through 2030 Q4. Volume, revenue, reported results, and the sum-of-parts price. "
        "Yellow rows are the ramp and the Recurrent sales path.",
    ),
    (
        "Financials Definitions",
        "Each row: what it is, where it came from, and what has to be true. Read the note at "
        "the top on what is deliberately not added twice.",
    ),
    (
        "Pillars",
        "The evidence behind the three stakes — CSI Solar, Recurrent, CS PowerTech — and the "
        "list of things given no separate value.",
    ),
    (
        "Valuation",
        "The same sum of parts, shown for 2026 Q3 (where we are) and 2027 Q4 (base case fully "
        "phased). Linked to Quarterly Financials, so editing a lever changes both.",
    ),
    (
        "Shares",
        "Dilution events worth remembering. The model does not invent a common-share drip.",
    ),
    (
        "Price History",
        "One GOOGLEFINANCE spill of daily CSIQ prices. Stock price looks up the last close on "
        "or before each quarter-end.",
    ),
    (
        "Reference",
        "Filings, the thesis, and the guidance the plans are tied to.",
    ),
]

CLOSING = (
    "The useful argument is not whether the consolidated P&L is a loss. It is whether the "
    "Shanghai stake, the BlackRock mark, and a still-ramping US factory are worth more than "
    "the market cap, after you refuse to count any of them twice. Thank you for looking."
)
