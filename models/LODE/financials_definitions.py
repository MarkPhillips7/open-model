"""Financials Definitions tab: what every Quarterly Financials row means.

Column A mirrors the Quarterly Financials label stack exactly, so the two tabs can
be read side by side. Column B says three things for each row: what the number is,
where it comes from, and — when it is a projection — what has to be true for it to
hold. The last part matters most. A formula with an unexamined assumption behind it
is worse than no formula, because it looks like knowledge.

Reading the conventions:

* A bare label is a **reported print**, typed from a filing, blank until reported.
* ``- Model`` is **always a formula**, and uses the actual when one exists.
* ``- Plan`` is a **hand-maintained trajectory** — the shape of the ramp. Edit these
  directly on the sheet; nothing overwrites them.
* Every scalar sits on the **Levers** tab with its own range and rationale.
"""

from __future__ import annotations

from models.LODE import layout as L

DEFINITIONS_SHEET = "Financials Definitions"

HEADER = ["Field", "Definition, source, and the assumption behind it"]
COL_WIDTHS_PX: dict[int, int] = {0: 300, 1: 900}

_PREFER = (
    "Uses the reported actual in any quarter where one exists, so history stays exact and "
    "the projection only takes over after the last print."
)


# Label → definition. Keys must match layout.ROWS exactly; section headings and
# spacer rows are handled by the builder.
DEFINITIONS: dict[str, str] = {
    L.YEAR: (
        "Calendar year of the column. Comstock's fiscal year matches the calendar year, so no "
        "fiscal-versus-calendar adjustment is needed anywhere in this model."
    ),
    L.QUARTER: (
        "Calendar quarter number, 1 to 4. Combined with Year it forms the quarter key that the "
        "timing levers ('2026 Q3', '2027 Q2') are matched against."
    ),
    L.QUARTER_ENDING: (
        "Last calendar day of the quarter. Drives the stock-price lookup and the discounting "
        "period on the Valuation tab."
    ),
    L.AS_OF_DATE: (
        "Valuation date, pulled from the Levers tab so there is one place to change it. Everything "
        "time-dependent measures from here."
    ),
    L.YEARS_FROM_PRESENT: (
        "Years between the As of date and this quarter-end, as a decimal, using a 365-day year. "
        "Negative for quarters already past."
    ),
    L.RATED_CAPACITY: (
        "Design throughput of ONE industry-scale production line, in tons of panels per year, from "
        "the Levers tab. Management's figure is ~3.3 million panels a year which at 50–60 lb per "
        "panel is ~100,000 tons. Assumption: the thermal ovens hold design rate running "
        "continuously. The line is built so the ovens are the binding constraint — panels load "
        "every ~7 seconds specifically so the ovens never wait."
    ),
    L.LINES_ACTUAL: (
        "Industry-scale production lines actually in operation, counted from company disclosure. "
        "Zero through 2026 Q2. The ~5,000 ton/year demonstration facility is deliberately NOT "
        "counted: it is about 5% of a line, and including it as a fraction would pull a full line's "
        "$15M/year fixed cost into quarters that never carried it. The demo facility's revenue "
        "still appears in Total revenue, so nothing is hidden — it is just kept out of the "
        "capacity model."
    ),
    L.LINES_PLAN: (
        "EDITABLE TRAJECTORY. The planned number of lines by quarter — your view of the buildout, "
        "not a derived number. Default assumes facility 1 (northern Nevada) from 2026 Q3, facility "
        "2 (central Ohio) in 2028, then roughly one line a year. Assumption: management holds to "
        "its stated discipline of not ordering equipment for the next facility until the first is "
        "'operating and production is effectively ramped up'. Edit this row freely."
    ),
    L.LINES_MODEL: (
        "Effective lines after the 'Line expansion achieved' lever. Line 1 is never scaled down "
        "because it is already built; only the incremental lines are haircut, so a 70% setting "
        "means a plan of 4 lines becomes 3.1. " + _PREFER
    ),
    L.UTILIZATION_ACTUAL: (
        "Percent of rated capacity actually achieved, if Comstock discloses it. Blank in every "
        "historical quarter because the company has never published a utilization figure — it is "
        "left empty rather than reverse-engineered from revenue, which would bake the model's own "
        "price assumptions into what pretends to be an actual."
    ),
    L.UTILIZATION_PLAN: (
        "EDITABLE TRAJECTORY. The planned ramp as a percent of rated capacity. Calibrated so that "
        "2026 Q3 and Q4 reproduce management's H2 2026 guide of roughly $5M of revenue at 'at least "
        "25% of rated capacity from August through year end': 5% for a part-quarter August start, "
        "then 25%. Plateaus at 85%, which allows for maintenance on a plant intended to run 24/7. "
        "This row and the tipping fee are the two things the whole model turns on."
    ),
    L.UTILIZATION_MODEL: (
        "Planned utilization × the 'Utilization ramp achieved' lever — the master scepticism dial on "
        "the ramp. The facility has already slipped from June to August 2026, so a setting below "
        "100% is a reasonable base case rather than a bear case. " + _PREFER
    ),
    L.TONS_ACTUAL: (
        "Tons of panels processed, if disclosed. Blank historically, for the same reason as "
        "utilization. If Comstock starts publishing tonnage, type it here and every downstream "
        "Model row switches to it automatically."
    ),
    L.TONS_MODEL: (
        "Effective lines × (rated capacity ÷ 4) × utilization. The ÷ 4 converts an annual capacity "
        "rating into one quarter. " + _PREFER
    ),
    L.TIPPING_MODEL: (
        "Revenue per ton from the fee customers pay Comstock to take end-of-life panels: the "
        "'Tipping fee per ton' lever × the 'Tipping fee achieved' lever. In Comstock's own revenue "
        "disaggregation this is the 'Decommissioning Services' line. Assumption: the ~$500/ton fee "
        "holds, which it has for about two and a half years. Customers in the southwest generally "
        "pay their own freight, so this is close to a net figure. This is the majority of revenue "
        "per ton, so it is the single most important number in the model — and the reason there is "
        "a separate achievement lever for fee compression."
    ),
    L.UPLIFT_PHASE_IN: (
        "EDITABLE TRAJECTORY. Gates the two UNPROVEN revenue uplifts — upgraded glass and extracted "
        "metals — without touching today's proven economics. Zero through 2026 so the model "
        "reproduces guided H2 2026 revenue on what Comstock actually realises now. Phases in "
        "afterwards because both uplifts are gated on THROUGHPUT and certification rather than on "
        "invention: the high-spec glass buyers want 50,000-ton flows, and metal extraction runs a "
        "1 ton/day pilot before 25 tons/day before industry scale. Set this to zero throughout for "
        "a clean 'today's economics only' case."
    ),
    L.MATERIAL_MODEL: (
        "Revenue per ton from selling recovered materials — Comstock's 'Off-take' revenue line. "
        "Built as the base value realised today, plus (glass uplift × its achieved lever + metal "
        "extraction uplift × its achieved lever) × the phase-in above. The base is ~$160/ton: "
        "aluminium, copper, low-spec glass, and only a PORTION of the silver, because the tailings "
        "are not yet refined. Full theoretical content is ~$1,000/ton, and the gap between $160 and "
        "$1,000 is exactly what the two uplift levers describe."
    ),
    L.REVENUE_PER_TON_MODEL: (
        "Tipping fee + recovered material value. At default levers this is ~$660/ton today, rising "
        "toward ~$716/ton as the uplifts phase in. Worth sanity-checking against the CEO's framing "
        "of '$500 in tipping fees and $250 in material value' — the model is deliberately below the "
        "$250 material figure until extraction is proven."
    ),
    L.METALS_REVENUE_ACTUAL: (
        "Reported Metals segment revenue, from the 10-Q segment note. Comprises Recycling, "
        "Decommissioning Services, and Off-take. Roughly $0.24M in 2026 Q2 — demonstration-facility "
        "scale, which is the point: essentially all of this model's value is in the ramp, not the "
        "history."
    ),
    L.METALS_REVENUE_MODEL: (
        "Tons processed × revenue per ton ÷ 1,000,000. " + _PREFER
    ),
    L.METALS_FIXED_COST_MODEL: (
        "Effective lines × the 'Fixed cash cost per line per year' lever ÷ 4. Modelled as FIXED, "
        "not per-ton, and that is the most consequential structural choice in the model: the plant "
        "is designed to run the ovens continuously with ~30–35 people across two 12-hour shifts, so "
        "the cost is there whether or not panels arrive. It is why profitability swings so violently "
        "on utilization — $15M/year is ~$150/ton at 100,000 tons but ~$300/ton at 50,000 tons."
    ),
    L.METALS_VARIABLE_COST_MODEL: (
        "Metals revenue × the 'Variable cash cost' lever. Genuinely variable cost is essentially "
        "just natural gas and electricity, which management puts at 92–94% of total variable cost "
        "and under 7% of revenue. Kept as a percent of revenue so it scales with the price stack."
    ),
    L.METALS_COST_MODEL: (
        "Fixed + variable cash cost for the recycling segment. Excludes depreciation and stock "
        "compensation, so it is a cash figure, and excludes corporate overhead, which is separate."
    ),
    L.METALS_CONTRIBUTION_MODEL: (
        "Metals revenue less metals cash cost — segment-level cash EBITDA. This is what the "
        "Valuation tab annualises and applies a multiple to."
    ),
    L.METALS_MARGIN_MODEL: (
        "Contribution ÷ revenue, as a percent. Blank when there is no revenue. Rises steeply with "
        "utilization purely because the cost base is fixed."
    ),
    L.BREAKEVEN_UTILIZATION_MODEL: (
        "CONSISTENCY CHECK, not a projection. The utilization at which one line covers its own fixed "
        "cost: fixed cost ÷ (rated capacity × revenue per ton × (1 − variable %)). Independent of "
        "how many lines are running. With default levers it lands at ~24%, against management's "
        "claim of breakeven 'at twenty, twenty five percent utilization'. If you change the price or "
        "cost levers and this drifts far from 25%, your levers have stopped agreeing with the "
        "company's own arithmetic — which is useful to know."
    ),
    L.METALS_CAPEX_MODEL: (
        "'Capex per production line' lever × the increase in effective lines this quarter. "
        "Simplification worth knowing about: real spend LEADS revenue by two to three quarters, so "
        "this charges cash later than it will actually leave. It also means capex is lumpy here and "
        "smooth in reality."
    ),
    L.TOTAL_REVENUE_ACTUAL: (
        "Total reported consolidated revenue, all segments, from the 10-Q. Includes the small mining "
        "and real-estate lease revenue (~$33k/quarter). Because the mining disposal is classified "
        "held for sale and NOT discontinued operations, no prior period is restated and that mining "
        "revenue stays in every historical quarter."
    ),
    L.TOTAL_REVENUE_MODEL: (
        "Past the last print this equals modelled metals revenue, because that is the only revenue "
        "left: mining is being sold, and the fuels business is not consolidated into the forward "
        "view and has never reported revenue. " + _PREFER
    ),
    L.GROSS_PROFIT_ACTUAL: (
        "Reported revenue less reported cost of revenue. Negative in every recent quarter — the "
        "demonstration facility does not cover its own cost, which is expected at that scale."
    ),
    L.OPEX_ACTUAL: (
        "Total reported operating expenses as a positive number: G&A, selling and marketing, R&D, "
        "depreciation and amortisation, and impairments. Shown positive so the sheet reads like a "
        "cost."
    ),
    L.IMPAIRMENTS_ACTUAL: (
        "Goodwill, intangible, and PP&E impairments inside operating expenses, as a positive number. "
        "Broken out because they are large, non-cash, and would otherwise make the opex trend "
        "unreadable — $15.4M in 2026 Q2 for the Flux Photon write-off, whose ~$16.4M total also "
        "includes ~$1.0M of associated investments recorded below the operating line."
    ),
    L.OPERATING_LOSS_ACTUAL: (
        "Reported operating loss, kept NEGATIVE because it is a loss. Revenue less cost of revenue "
        "less total operating expenses."
    ),
    L.NET_LOSS_ACTUAL: (
        "Reported net loss attributable to common shareholders, negative. Includes items the "
        "operating model deliberately ignores: derivative and SAFE-note fair-value marks, equity in "
        "affiliate losses, and gains or losses on investments. Those swing quarter to quarter "
        "without telling you anything about the recycling business, which is why Adjusted EBITDA - "
        "Model does not attempt to reconcile to this line."
    ),
    L.EPS_ACTUAL: (
        "Reported basic loss per share. Comstock states basic and diluted are identical in loss "
        "quarters. Not reported for Q4 in either year, because weighted-average share counts are "
        "not additive and the company publishes no Q4-only figure — left blank rather than "
        "approximated. Note all figures are post the 1-for-10 reverse split of 2025-02-24; the "
        "model's spine starts after it, so no adjustment is needed."
    ),
    L.CORP_GA_MODEL: (
        "Cash cost of running the public company, from the Levers tab, less the legacy mining cost "
        "that leaves with the sale from the closing quarter onward. This is the CORPORATE/OTHER "
        "SEGMENT G&A only — $2,572,589 in Q2 2026 per the 10-Q segment note, ≈$2.25M/quarter net of "
        "share-settled compensation. It is NOT consolidated G&A ($7.00M in Q2 2026), which sums all "
        "five segments and would double-count: Bioleum/Fuels G&A and R&D are covered by the bridge "
        "loan row, Metals cost sits in the metals fixed cost, and Mining G&A leaves with the sale. "
        "Assumption: flat. Corporate/Other G&A has run $2.19M → $2.39M → $2.57M over three quarters "
        "and is rising with no stated reduction programme, so treat flat as optimistic and revisit "
        "it every release."
    ),
    L.ADJ_EBITDA_MODEL: (
        "Metals cash contribution less corporate cash G&A. A cash operating figure: before "
        "depreciation, stock compensation, impairments, and all the fair-value noise below the "
        "operating line. It does NOT tie to reported net loss and is not meant to."
    ),
    L.CASH_ACTUAL: (
        "Reported cash and cash equivalents at quarter end. Comstock presents no restricted cash "
        "line; the reclamation bond deposit is a non-current deposit, not cash."
    ),
    L.OCF_ACTUAL: (
        "Reported net cash used in operating activities, kept NEGATIVE when cash is consumed so it "
        "adds directly into the cash roll-forward. Derived for some quarters by subtracting "
        "year-to-date periods, since Comstock tags cash flow cumulatively."
    ),
    L.OCF_MODEL: (
        "Equals Adjusted EBITDA - Model past the last print. Assumption: working-capital swings are "
        "small and losses are mostly cash, so EBITDA is a fair cash proxy. Reasonable for a company "
        "this size, and it ignores the deferred revenue Comstock collects on panels taken but not "
        "yet processed — which flatters nothing, since deferred revenue is a cash INflow. " + _PREFER
    ),
    L.CAPEX_ACTUAL: (
        "Reported purchases of property, plant, equipment and mineral rights, as a positive number. "
        "$5.68M in 2026 Q1 and $1.33M in 2026 Q2 — this is facility 1 being built."
    ),
    L.CAPEX_MODEL: (
        "Equals modelled metals capex past the last print. Carries no maintenance capex allowance, "
        "which is a known understatement for a plant running two shifts seven days a week. " + _PREFER
    ),
    L.MINING_PROCEEDS_MODEL: (
        "Cash from the legacy mining sale, landing in the quarters the timing levers name: the $20M "
        "Initial Payment at closing, then the $7M Second Tranche due within 18 months. Excludes the "
        "2,000,000 Mackay Parent shares and the $10M contingent payment, both given no value "
        "anywhere in this model."
    ),
    L.SSOF_PROCEEDS_MODEL: (
        "Cash from selling part of the SSOF land stake, in the quarter the timing lever names: gross "
        "asset value × ownership × achieved × 'SSOF stake sold for cash'. That last lever defaults "
        "to ZERO, so this row is zero everywhere until you deliberately turn it on. The reason is "
        "the distinction this model tries hardest to keep: the mining sale has a signed purchase "
        "agreement and belongs in the cash forecast, while SSOF has comps and a management target "
        "and does not. Leaving it at zero is what makes 'Cash - Model' and 'Quarters of cash "
        "remaining' readable as a genuine funding gap rather than a thesis. The stake still gets "
        "full credit as option value on the Valuation tab, which deducts whatever fraction you do "
        "convert to cash so the asset is never counted twice."
    ),
    L.FUELS_BRIDGE_MODEL: (
        "Bridge financing Comstock extends to the fuels subsidiary, as a positive number that is "
        "SUBTRACTED in the cash roll-forward. A loan rather than equity, so it has no P&L effect "
        "here. Modelled as fully drawn in the mining-closing quarter, which is roughly when it was "
        "described. No repayment is assumed, which is the conservative treatment."
    ),
    L.EQUITY_ISSUED_ACTUAL: (
        "Reported gross proceeds from issuing common stock, positive. Large and lumpy: $34.5M in "
        "2025 Q3 and $61.0M in 2026 Q1. This row is the honest record of how the company has funded "
        "itself, and the reason dilution is a first-order concern rather than a footnote."
    ),
    L.EQUITY_ISSUED_MODEL: (
        "Zero past the last print. The model deliberately assumes NO future rescue raise, so that a "
        "negative Cash - Model shows the funding gap instead of papering over it. Read a negative "
        "cash balance as 'this much equity must be raised', not as a prediction of insolvency. "
        "If you want to test a specific raise, add it on the Shares tab. " + _PREFER
    ),
    L.CASH_MODEL: (
        "Prior quarter cash + operating cash flow − capex + mining proceeds + SSOF proceeds − fuels "
        "bridge + equity issued. Uses the reported balance in any quarter where one exists, so the "
        "projection always starts from a real balance sheet rather than compounding its own error. "
        "Column C must be a reported figure since there is no prior quarter to roll from."
    ),
    L.RUNWAY_MODEL: (
        "Cash ÷ (capex − operating cash flow) — quarters of cash left if this quarter's burn "
        "repeated. Blank when the quarter generates cash, and capped at 40 quarters because a "
        "quarter that burns almost nothing otherwise divides by a near-zero denominator and prints "
        "a meaningless four-digit number; read 40 as 'ten years or more'. A rough dial, not a "
        "financing plan: it assumes the current quarter's burn repeats and ignores asset sales "
        "still to come."
    ),
    L.TOTAL_DEBT_ACTUAL: (
        "Comstock carries no conventional debt. The only debt-like instrument is the Marathon SAFE "
        "note, held at fair value in long-term liabilities (~$10.9M at 2026-06-30), and that is what "
        "this row means. Net cash on the Valuation tab subtracts it."
    ),
    L.TOTAL_DEBT_MODEL: (
        "Held flat at the last reported level. Assumption: no new borrowing and no conversion. " + _PREFER
    ),
    L.SHARES_ACTUAL: (
        "Common shares issued and outstanding at period end, in millions — NOT the weighted average, "
        "which understates the count that matters for valuation. 75.95M at 2026-06-30. All figures "
        "are post the 1-for-10 reverse split of 2025-02-24."
    ),
    L.SHARES_MODEL: (
        "Prior quarter × a ~1%/quarter drip past the last print, covering vesting stock compensation "
        "and routine at-the-market use. Assumption: no large offering. Given that Comstock has "
        "raised $34.5M and $61.0M in single quarters, this is the model's most obviously optimistic "
        "assumption — override it with dated events on the Shares tab. " + _PREFER
    ),
    L.STOCK_PRICE: (
        "Last daily close on or before quarter end, looked up from the Price History tab. Blank for "
        "quarters still in the future, by design — the model should not pretend to know a price it "
        "cannot observe."
    ),
    L.MARKET_CAP: (
        "Modelled shares outstanding × stock price, in $M. Blank whenever either input is missing, "
        "so it is only populated for quarters that have actually traded."
    ),
}


SECTION_NOTES: dict[str, str] = {
    L.SECTION_METALS_VOLUME: (
        "How much material goes through the plant. Capacity × utilization, nothing more — the whole "
        "business is a throughput machine."
    ),
    L.SECTION_METALS_PRICE: (
        "What a ton is worth. Two streams: a fee for taking the panel, and the value of what comes "
        "out. Comstock gets paid at both ends, which is unusual and is the core of the thesis."
    ),
    L.SECTION_METALS_ECON: (
        "Throughput × price, less a mostly FIXED cost base. The fixed cost is why utilization "
        "dominates everything and why the breakeven check row is worth watching."
    ),
    L.SECTION_CONSOLIDATED: (
        "Reported results as filed, plus the two Model rows that carry the operating view forward. "
        "The Model rows do not reconcile to reported net loss, and are not meant to."
    ),
    L.SECTION_CASH: (
        "The survival section. Operating burn against asset sales, and the point of the model that "
        "most deserves your scepticism."
    ),
    L.SECTION_SHARES: (
        "Denominator and market price. Dilution has been the main destroyer of per-share value at "
        "this company, so this section is not an afterthought."
    ),
}


INTRO: list[tuple[str, str]] = [
    (
        "How to read this workbook",
        "A bare label is a REPORTED PRINT, typed from a filing and left blank until the company "
        "reports it. A '- Model' row is ALWAYS a formula and always prefers the actual when one "
        "exists, so a miss is visible rather than overwritten. A '- Plan' row is a hand-maintained "
        "trajectory that you own — edit it directly and nothing will overwrite it. Every scalar "
        "assumption lives on the Levers tab with a range and a rationale; if you find a magic number "
        "inside a formula, that is a bug worth reporting.",
    ),
    (
        "Where the value comes from",
        "Comstock is one ramping operating business (solar panel recycling) plus two lumpy asset "
        "stakes (SSOF powered land, Comstock Fuels) plus a signed legacy mining sale. The Valuation "
        "tab therefore does a sum of parts rather than putting one multiple on consolidated "
        "earnings, and each pillar carries its own 'achieved' lever so you can believe one and doubt "
        "another.",
    ),
    (
        "What is deliberately left blank",
        "Tons processed and capacity utilization have no historical actuals, because Comstock has "
        "never published them. They are left empty rather than reverse-engineered from revenue — "
        "doing that would smuggle the model's own price assumptions into cells labelled 'actual'.",
    ),
]
