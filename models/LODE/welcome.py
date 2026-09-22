"""Welcome tab copy for the LODE Model workbook."""

from __future__ import annotations

WELCOME_SHEET = "Welcome"

COL_WIDTHS_PX: dict[int, int] = {0: 300, 1: 900}

REPO_URL = "https://github.com/MarkPhillips7/open-model"
X_PROFILE_URL = "https://x.com/MarkPhillips7"
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1_2X0QzVWN5XiH4WX2V_outtKgQQYti81T28H22g9xDM/edit"
)
IR_URL = "https://www.comstockinc.com/investors/"

TITLE = "LODE Model — Comstock Inc."

DISCLAIMER = (
    "Nothing here is financial advice, an offer to buy or sell securities, or a recommendation of "
    "any kind. This workbook mixes company-reported figures, management commentary, and explicit "
    "assumptions where Comstock does not disclose detail. Numbers can be wrong, out of date, or "
    "simply my own interpretation. Do your own research and talk to a qualified professional "
    "before making investment decisions."
)

GOALS = (
    "Goal: reflect Comstock's reported financial position accurately up to the latest filing, then "
    "project forward using company guidance — and make every assumption in that projection visible "
    "and adjustable. Reported actuals live on their own rows and stay blank until the company "
    "reports them. Every '- Model' row is a formula that prefers the actual when one exists, so a "
    "miss shows up instead of being quietly overwritten."
)

APPROACH = (
    "Comstock is really three things: a solar-panel recycling business that is just beginning to "
    "ramp, a roughly half-owned 'powered land' position (SSOF), and a pre-commercial fuels venture "
    "— plus a signed sale of the legacy mining assets. Putting one earnings multiple on that "
    "mixture would describe none of it, so the Valuation tab does a sum of parts and gives each "
    "pillar its own realization lever. That way you can believe the recycling plant and still "
    "discount the land, or the reverse."
)

WHY_LEVERS = (
    "Wherever a future outcome is genuinely questionable, the plan number stays at what management "
    "said and a separate 'achieved' percentage carries the scepticism. So the tipping fee stays at "
    "$500/ton and 'Tipping fee achieved' is where you express doubt; the metal-extraction uplift "
    "stays near the 50–60%→>90% recovery gap at current silver and 'Metal extraction achieved' "
    "defaults to 85% under a 'most of the silver by 2030 as higher-purity product' underwrite. "
    "Tailings stockpiling (CEO: prefer to hold once extraction is in sight) is a separate dial: "
    "start quarter, % withheld, and backlog draw rate. Keeping these apart means you can always "
    "see what the company claimed next to what you are willing to underwrite."
)

CALIBRATION = (
    "Sanity check worth knowing about: with the default levers the model independently reproduces "
    "three separate things management has said — roughly $5M of revenue in H2 2026, cash breakeven "
    "at about 25% utilization, and a payback of about one year on a line at 50% utilization. None "
    "of those were fitted; they fall out of the unit economics. The 'Breakeven utilization - Model' "
    "row keeps that check live, so if you change the price or cost levers and it drifts far from "
    "25%, your assumptions have stopped agreeing with the company's own arithmetic."
)

MANUAL_EDITS = (
    "This workbook is edited both by hand and by scripts in the repository, so the tooling always "
    "checks for manual changes before it writes. Yellow cells are yours: lever values in column C "
    "of the Levers tab, and the '- Plan' trajectory rows on Quarterly Financials. Edit them freely "
    "— nothing will overwrite them, and the repo adopts them on the next sync. If a script finds "
    "that a generated formula has been changed by hand, it stops and asks rather than clobbering "
    "your work."
)

FEEDBACK = (
    "Thoughtful feedback is very welcome. If something looks wrong, if you disagree with an "
    "assumption, or if you have a better way to model any of this, please reach out on X: "
)

SOURCES_NOTE = (
    "Built from Comstock's 10-Q and 10-K filings and 8-K earnings releases via SEC XBRL, the Q2 2026 "
    "earnings release and call, and a detailed 2026-08-11 interview with CEO Corrado De Gasperis "
    "that is the source for most of the unit economics. Full citations are on the Reference tab and "
    "in RESOURCES.md in the repository."
)

TAB_DESCRIPTIONS: list[tuple[str, str]] = [
    (
        "Levers",
        "The control panel. Every scalar assumption in one place with its units, default, a "
        "defensible low/high range, and a rationale citing where the number came from. Column C is "
        "yours to edit. Start here.",
    ),
    (
        "Quarterly Financials",
        "The main time series, one column per quarter from 2025 Q1 to 2030 Q4. Recycling volume and "
        "unit economics, reported results, cash, and share count. Yellow '- Plan' rows are the ramp "
        "trajectories you own.",
    ),
    (
        "Financials Definitions",
        "Every row on Quarterly Financials explained: what it is, where it came from, and what has "
        "to be true for it to hold.",
    ),
    (
        "Asset Monetization",
        "The evidence behind the three non-operating pillars — the mining sale, SSOF, and Comstock "
        "Fuels — with sources and dates, plus an explicit list of what is deliberately given no "
        "value.",
    ),
    (
        "Valuation",
        "Sum of parts as at a reference quarter, then discounted back to today. Includes a guard so "
        "an asset sale that already landed in cash is not also counted as a stake.",
    ),
    (
        "Shares",
        "Dated dilution events. Add a planned offering here rather than editing the share-count "
        "formula.",
    ),
    (
        "Price History",
        "One GOOGLEFINANCE spill of daily LODE prices. The Stock price row looks up the last close "
        "on or before each quarter-end.",
    ),
    (
        "Reference",
        "Source links: filings, the earnings release, the CEO interview, and independent work.",
    ),
]

CLOSING = (
    "If you spot a mistake, disagree with an assumption, or think a lever default is wrong, I would "
    "genuinely like to hear it. Thank you for looking — I hope this helps you think more clearly "
    "about Comstock."
)
