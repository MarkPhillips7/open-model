"""Levers tab: every adjustable assumption in the LODE model, in one place.

Design rule: a lever is a **scalar** that does not vary by quarter. Anything with a
time shape (the utilization ramp, the production-line count) lives as an editable
``- Model`` row on Quarterly Financials instead, so the trajectory is visible next
to the quarters it applies to.

Each lever carries a *realization* sibling wherever the outcome depends on Comstock
executing something it has not yet done. The plan number stays at management's
stated figure; the realization percentage is where scepticism belongs. That keeps
"what the company said" separate from "what I believe", which is the whole point.

Column layout on the tab: A label, B units, C value (yellow input), D default,
E low, F high, G rationale / source.
"""

from __future__ import annotations

LEVERS_SHEET = "Levers"

VALUE_COL = "C"
DEFAULT_COL = "D"
LOW_COL = "E"
HIGH_COL = "F"

HEADER = ["Lever", "Units", "Value", "Default", "Low", "High", "Rationale / source"]

# Pixel widths captured for the tab (0-based column index).
COL_WIDTHS_PX: dict[int, int] = {0: 330, 1: 86, 2: 96, 3: 84, 4: 74, 5: 74, 6: 860}

SECTION = object()  # sentinel: section heading row, no value


class Lever:
    """One scalar assumption. ``low``/``high`` document a defensible range, not a hard clamp."""

    __slots__ = ("label", "units", "default", "low", "high", "rationale", "number_format")

    def __init__(
        self,
        label: str,
        units: str,
        default: float | str,
        low: float | str | None,
        high: float | str | None,
        rationale: str,
        *,
        number_format: str | None = None,
    ) -> None:
        self.label = label
        self.units = units
        self.default = default
        self.low = low
        self.high = high
        self.rationale = rationale
        self.number_format = number_format


# --- Label constants (import these instead of typing strings) ---------------

AS_OF_DATE = "As of date"
DISCOUNT_RATE = "Discount rate"

RATED_CAPACITY_PER_LINE = "Rated capacity per production line"
UTILIZATION_ACHIEVED = "Utilization ramp achieved"
LINE_EXPANSION_ACHIEVED = "Line expansion achieved"
TIPPING_FEE_PER_TON = "Tipping fee per ton"
TIPPING_FEE_ACHIEVED = "Tipping fee achieved"
MATERIAL_BASE_PER_TON = "Recovered material per ton - base"
TAILINGS_OFFTAKE_PER_TON = "Tailings offtake in material base"
TAILINGS_STOCKPILE_PCT = "Tailings stockpiled"
TAILINGS_STOCKPILE_START = "Tailings stockpile start quarter"
GLASS_UPLIFT_PER_TON = "Glass upgrade uplift per ton"
GLASS_UPLIFT_ACHIEVED = "Glass upgrade achieved"
METAL_UPLIFT_PER_TON = "Metal extraction uplift per ton"
METAL_UPLIFT_ACHIEVED = "Metal extraction achieved"
TAILINGS_BACKLOG_DRAW = "Tailings backlog draw rate"
FIXED_COST_PER_LINE = "Fixed cash cost per line per year"
VARIABLE_COST_PCT = "Variable cash cost"
CAPEX_PER_LINE = "Capex per production line"

CORP_CASH_GA = "Corporate cash G&A per quarter"
MINING_COST_SAVINGS = "Legacy mining cost removed per year"

SSOF_GROSS_VALUE = "SSOF gross asset value"
SSOF_VALUE_GROWTH = "SSOF value quarterly growth rate"
SSOF_OWNERSHIP = "Comstock ownership of SSOF"
SSOF_ACHIEVED = "SSOF value achieved"
SSOF_CASH_SOLD = "SSOF stake sold for cash"
SSOF_PROCEEDS_QUARTER = "SSOF monetization quarter"
FUELS_VALUE = "Comstock Fuels value to Comstock"
FUELS_VALUE_GROWTH = "Comstock Fuels value quarterly growth rate"
FUELS_ACHIEVED = "Comstock Fuels value achieved"
FUELS_BRIDGE_TOTAL = "Comstock Fuels bridge loan"
FUELS_MONTHLY_BURN = "Comstock Fuels monthly burn"
MINING_SALE_CASH = "Mining sale cash at closing"
MINING_SALE_QUARTER = "Mining sale closing quarter"
MINING_SECOND_TRANCHE = "Mining sale second tranche"
MINING_SECOND_TRANCHE_QUARTER = "Mining sale second tranche quarter"
MINING_SALE_TOTAL = "Mining sale total consideration"
NSR_ROYALTY = "Mining NSR royalty retained"

METALS_MULTIPLE = "Metals EV / annualized cash contribution"
METALS_CORE_VALUE = "Metals core business value"
METALS_ACHIEVED = "Metals business value achieved"
NET_CASH_CREDIT = "Net cash credited to equity value"

PCT = "%"
USD_TON = "$/ton"
USD_M = "$M"
TONS_YR = "tons/yr"


LEVERS: list[object] = [
    (SECTION, "Timing and discount"),
    Lever(
        AS_OF_DATE,
        "date",
        "2026-09-18",
        None,
        None,
        "Valuation date. 'Years from present' on Quarterly Financials measures each quarter-end "
        "from here, and the Valuation tab discounts the implied share price back to this date. "
        "Latest reported quarter as of this date is Q2 2026 (10-Q filed 2026-07-23).",
    ),
    Lever(
        DISCOUNT_RATE,
        "% / yr",
        15,
        10,
        30,
        "Annual rate used to present-value the implied future share price. Comstock is a "
        "pre-profit micro-cap that has funded itself with equity, so its cost of equity is high; "
        "15% is a deliberately plain choice rather than a derived CAPM number. Raise it if you "
        "want to penalise execution risk through the discount rate instead of the achieved levers.",
    ),
    (SECTION, "Comstock Metals — solar panel recycling"),
    Lever(
        RATED_CAPACITY_PER_LINE,
        TONS_YR,
        100_000,
        80_000,
        110_000,
        "One production line is designed for ~3.3 million panels/year, which at 50–60 lb/panel is "
        "~100,000 tons/year (CEO, 2026-08-11 interview 00:07:06). The line loads a panel every "
        "~7 seconds and the thermal ovens are the intended constraint, running 24/7. Low end "
        "allows for the ovens not holding design throughput once running continuously.",
    ),
    Lever(
        UTILIZATION_ACHIEVED,
        PCT,
        100,
        40,
        120,
        "Master scepticism dial on the ramp. Scales the entire 'Capacity utilization - Model' row "
        "on Quarterly Financials. The row itself is seeded to hit management's guide (≥25% of rated "
        "capacity from August through year-end 2026, ~$5M H2 2026 revenue) and then ramps. Set this "
        "below 100 if you think the ramp slips — the facility has already moved from June to August "
        "2026. Above 100 only if you think they beat the stated ramp.",
    ),
    Lever(
        LINE_EXPANSION_ACHIEVED,
        PCT,
        75,
        0,
        100,
        "Scepticism dial on production lines beyond the first. Scales only the *incremental* lines "
        "in 'Operating production lines - Model'; line 1 is never scaled because it is built. "
        "Management is explicit that it will not order equipment for facility 2 until facility 1 is "
        "'operating and production is effectively ramped up' (Q2 2026 release), and sites 2–5 are at "
        "site-selection/permitting stage. 75% reflects real intent plus real funding and timing risk.",
    ),
    Lever(
        TIPPING_FEE_PER_TON,
        USD_TON,
        500,
        350,
        600,
        "Fee customers pay Comstock to take end-of-life panels. CEO: '$500 a ton is sort of our "
        "target. It's held up over the last two and a half years' (2026-08-11, 00:17:52). Customers "
        "in the southwest generally also pay freight, so this is close to a net figure. This is the "
        "majority of revenue per ton today, which is why the next lever matters.",
    ),
    Lever(
        TIPPING_FEE_ACHIEVED,
        PCT,
        100,
        60,
        100,
        "Durability of the tipping fee. Held at 100 because the fee has been stable for 2.5 years "
        "and 85–90% of panels still go to landfill, so supply of paying customers is not the "
        "binding issue. The bear case is that competition (SolarCycle et al.) or a shift in "
        "hazardous-waste rules compresses the fee as capacity is added — drop this to 60–80 to "
        "test that. Every point here flows straight to contribution because the cost base is fixed.",
    ),
    Lever(
        MATERIAL_BASE_PER_TON,
        USD_TON,
        200,
        125,
        450,
        "Value of recovered materials while selling all three offtake streams (Al, glass, "
        "tailings): CEO band today '$125 to $200' (2026-08-11, 00:20:10). Default at the top of "
        "that band with silver ~$66/oz. The tailings slice inside this number is broken out in "
        "the next lever so a stockpile policy can withhold it. High (~$450) is full MTM offtake "
        "if commercial sales mark to spot. Keep the default near realised so H2 2026 still "
        "tracks the ~$5M guide.",
    ),
    Lever(
        TAILINGS_OFFTAKE_PER_TON,
        USD_TON,
        100,
        50,
        375,
        "Portion of the material-base $/ton that comes from SELLING silver-rich tailings to a "
        "third-party refiner (~50–60% of silver value). Midpoint of the CEO's $125–200 band "
        "attributed to the 'portion of the silver content' (2026-08-11). High 375 is management's "
        "stated silver-offtake line at ~$60/oz (FY2025 call). When 'Tailings stockpiled' is on, "
        "this amount is removed from near-term revenue and only returns as in-house metal is "
        "phased in (plus any backlog draw).",
    ),
    Lever(
        TAILINGS_STOCKPILE_PCT,
        PCT,
        100,
        0,
        100,
        "Share of current-period tailings withheld from sale once the stockpile start quarter "
        "hits. CEO (2026-08-11, 00:26:22): once they 'feel that we can extract the silver "
        "economically… we prefer not to sell those tailings' and 'preserve the higher value for "
        "ourselves,' even while the pilot is only 1 t/d. Default 100 = stop selling and store. "
        "Set to 0 to keep today's sell-as-you-go offtake.",
    ),
    Lever(
        TAILINGS_STOCKPILE_START,
        "quarter",
        "2027 Q1",
        None,
        None,
        "First quarter the stockpile policy applies. Default 2027 Q1: after the end-2026 1 t/d "
        "pilot is supposed to 'prove and demonstrate' silver recovery (Q1 2026 call), which is "
        "when the CEO's 'clear line of sight' test is most likely to flip. Move earlier only if "
        "they announce they are already holding tailings; keep at 2026 Q4 or later so H2 2026 "
        "guided revenue is not stripped of offtake.",
    ),
    Lever(
        GLASS_UPLIFT_PER_TON,
        USD_TON,
        45,
        30,
        60,
        "Incremental $/ton from selling upgraded glass into ceramics/fibre-optic specs rather than "
        "as a cement additive. Glass is ~70% of a panel's mass. Baseline additive glass fetches "
        "$10–20/ton; cleaned glass 'could be selling for 30, 40, 50, 60 more per ton' after the "
        "$1.5M upgrading investment, which is already installed (CEO 2026-08-11, 00:24:46).",
    ),
    Lever(
        GLASS_UPLIFT_ACHIEVED,
        PCT,
        70,
        0,
        100,
        "Share of the glass uplift actually captured. Equipment is built and running; the binding "
        "gate is certification plus buyer demand for ~50,000-ton flows, not invention. Default 70 "
        "is an expected-value mid-ramp: most likely they sell a majority of upgraded glass once "
        "facility #1 is through its utilization ramp (the uplift phase-in row still times it), "
        "not a full offtake on day one and not a zero.",
    ),
    Lever(
        METAL_UPLIFT_PER_TON,
        USD_TON,
        350,
        0,
        400,
        "Incremental $/ton from in-house extraction vs selling tailings at ~50–60% silver-value "
        "capture — moving toward the >90% recovery target and Doré-type product (Q1 2026 call). "
        "Default 350 underwrites 'most of the silver by 2030' at ~$66/oz: the 50–60%→>90% gap "
        "plus other metals, approaching management's framing that metal recoveries can look "
        "'just as good, if not better, than our tipping fees.' High 400 is tipping-fee parity. "
        "With stockpiling on, forgone offtake is returned through the material formula as "
        "phase-in × achieved rises, so do not also inflate this to include the base offtake.",
    ),
    Lever(
        METAL_UPLIFT_ACHIEVED,
        PCT,
        85,
        0,
        100,
        "Share of the metal-extraction uplift underwritten by 2030. Default 85 reflects the view "
        "that the funded 1→25→250 t/d path largely works and they sell mostly higher-purity "
        "silver product rather than tailings — short of 100% only for residual scale/ops risk. "
        "The uplift phase-in row still times WHEN capacity arrives; this dial is HOW MUCH of "
        "the >90% recovery prize you believe. Drop toward 50 if the end-2026 pilot slips or "
        "publishes weak recoveries.",
    ),
    Lever(
        TAILINGS_BACKLOG_DRAW,
        "× current tons",
        1.0,
        0,
        3,
        "When metal phase-in is running, how fast the stockpile is worked off relative to "
        "current-quarter panel tons. 1.0 = leftover extraction capacity equal to current "
        "throughput can also chew backlog (so inventory clears over a few quarters once phase-in "
        "is high). Raise toward 2–3 if you think the 25→250 t/d metal plants outrun panel "
        "recycling and flush the pile quickly; 0 disables backlog revenue (stockpile is then "
        "only a near-term offtake haircut).",
    ),
    Lever(
        FIXED_COST_PER_LINE,
        USD_M,
        15,
        12,
        18,
        "Annual cash operating cost to run one production line at full rate — labour (~30–35 people "
        "across two 12-hour shifts), maintenance, site, logistics. CEO: '$15 million of recurring "
        "operating expense' per line (2026-08-11, 00:07:06). Modelled as FIXED because the plant is "
        "designed to run the ovens continuously, which is exactly why utilization drives "
        "profitability so violently. At 100k tons this is ~$150/ton; at 50k tons ~$300/ton.",
    ),
    Lever(
        VARIABLE_COST_PCT,
        "% of revenue",
        7,
        5,
        12,
        "Truly variable cost, which is essentially just natural gas and electricity: CEO says gas "
        "and electricity are '92 to 94%' of totally variable cost and that total is 'less than "
        "seven percent of our revenue' (2026-08-11, 00:40:15). Kept as a percent of revenue rather "
        "than $/ton so it scales with the revenue-per-ton stack.",
    ),
    Lever(
        CAPEX_PER_LINE,
        USD_M,
        13.5,
        12,
        16,
        "One-time capital to build one production line. CEO quotes $12M for the line itself "
        "(2026-08-11, 00:39:29) and $15M in the fuller facility framing including storage and "
        "site work; 13.5 is the midpoint. A line takes 30–40k sq ft. Charged in the model when the "
        "line count steps up, which is a simplification — real spend leads revenue by 2–3 quarters.",
    ),
    (SECTION, "Corporate"),
    Lever(
        CORP_CASH_GA,
        USD_M,
        2.25,
        2.10,
        2.60,
        "Cash cost of running the public company, per quarter. This is the CORPORATE/OTHER SEGMENT "
        "G&A only — $2,572,589 in Q2 2026 per the 10-Q segment note — less roughly $324K/quarter of "
        "share-settled compensation (director $531,765 + employee $116,566 for H1, halved). Low is "
        "the H1 2026 average net of that comp; high is the Q2 gross figure. It deliberately "
        "EXCLUDES three things, each of which the model carries elsewhere, so putting them here "
        "would double-count. (1) Bioleum/Fuels G&A ($2,376,255 in Q2 2026): third parties fund "
        "Bioleum and Comstock's own exposure is the bridge loan, sized separately by the fuels "
        "burn and bridge levers. (2) Metals plant operating cost, which lives in the fixed cash "
        "cost per line above. (3) Mining G&A, which the legacy-mining-cost lever below strips out "
        "from the sale quarter. Do NOT reset this to consolidated G&A ($7.00M in Q2 2026): that "
        "figure is the sum of all five segments and double-counts Bioleum against the bridge loan. "
        "Sanity check: $2.25M/qtr ($9M/yr) plus Bioleum ~$14.5M/yr plus Metals fixed cost lands "
        "near the $25–30M/yr total cost structure implied by management's claim that one facility at "
        "40–50% utilization covers all company-wide cost. Watch it anyway — Corporate/Other G&A has "
        "run $2.19M → $2.39M → $2.57M over three quarters and is RISING, with no stated reduction "
        "programme, so a flat run-rate is an assumption, not an observation.",
    ),
    Lever(
        MINING_COST_SAVINGS,
        USD_M,
        1.5,
        1,
        2,
        "Annual cost that disappears with the legacy mining sale: permits, environmental and "
        "holding costs. CEO: 'the annual cost, not so dramatic, but a million and a half gone' "
        "(2026-08-11, 01:20:55). Applied to corporate G&A from the sale quarter forward.",
    ),
    (SECTION, "Asset monetization — SSOF 'powered land'"),
    Lever(
        SSOF_GROSS_VALUE,
        USD_M,
        500,
        76,
        900,
        "Whole-asset value of Sierra Springs Opportunity Fund as of the As of date: 2,500 owned "
        "acres plus ~2,000 acre-feet of water rights in Silver Springs NV, with 300 MW of gas "
        "equivalent secured (pipeline delivery November 2028) and a further 900–1,200 MW targeted "
        "for 2030. CEO on comps: 'four hundred, five hundred, six hundred million for the powered "
        "land thesis is out there' (2026-08-11, 00:47:54). Buyers increasingly price by the "
        "megawatt, not the acre. TREAT THE DEFAULT AS A COMPARABLE, NOT A VALUATION: Comstock has "
        "never disclosed a gross asset value, NAV or appraisal for this land, and an EDGAR "
        "full-text search finds no use of the phrase in any recent filing. The $76M low is the only "
        "market-tested anchor available — it back-solves from SSOF's own $0.65/share primary issue "
        "price, and at that level Comstock's 47.63% is worth about $36M, i.e. BELOW the $49.0M "
        "equity-method carrying value, which is the genuine bear case. Also note Comstock took "
        "actual title to the land only weeks before 2026-08-11, by exercising a 2019 option. "
        "Quarterly Financials compounds this at 'SSOF value quarterly growth rate' from the As of "
        "date — set that growth to zero to freeze the comparable.",
    ),
    Lever(
        SSOF_VALUE_GROWTH,
        "% / q",
        2.0,
        -5,
        5,
        "QoQ % applied to 'SSOF gross asset value' on Quarterly Financials, measured from the As of "
        "date (exponent zero in that quarter). Default 2%/q (~8%/yr) is a modest path toward the "
        "powered-land comps as the Nov 2028 gas delivery and further MW allocations land — not a "
        "fitted NAV. Set to 0 to hold the comparable flat; use a negative rate if you think comps "
        "compress or the thesis slips.",
    ),
    Lever(
        SSOF_OWNERSHIP,
        PCT,
        47.63,
        40,
        50,
        "Comstock's equity interest in SSOF, 47.63% as of Q2 2026 (Q2 2026 release). Comstock "
        "increased this materially during 2026 and describes it as 'almost fifty percent'. SSOF is "
        "an equity-method investment, so its carrying value on the balance sheet is far below this "
        "share of the figures above — that gap is the option value the model is trying to show.",
    ),
    Lever(
        SSOF_ACHIEVED,
        PCT,
        85,
        0,
        100,
        "Share of the gross SSOF value that converts into cash for Comstock shareholders. Haircuts "
        "three separate things at once: whether comps hold, minority-stake and structuring "
        "friction, and timing. As of Aug 2026 nothing is signed — management's own year-end test "
        "is only 'some defined transaction with some derivable value', explicitly not a close. "
        "Land ownership and the power source are secured, which is why this is not lower.",
    ),
    Lever(
        SSOF_CASH_SOLD,
        PCT,
        0,
        0,
        100,
        "PERCENTAGE of Comstock's haircut SSOF value sold for cash inside the forecast — not a "
        "dollar proceeds cell. Defaults to ZERO on purpose: nothing is signed, and every SSOF "
        "transaction to date is Comstock paying in (~$37M cumulative). At 0 the cash line shows "
        "the real unrescued funding gap and the stake still gets full credit as option value on "
        "the Valuation tab. Leave the high at 100 so you can still test 'what if they sell half "
        "the fund' — the Valuation tab nets out whatever converts to cash, so there is no "
        "double-count at any setting. Do not lock the high to zero just because cash realised "
        "to date is $0.",
    ),
    Lever(
        SSOF_PROCEEDS_QUARTER,
        "quarter",
        "2027 Q2",
        None,
        None,
        "Quarter in which SSOF cash proceeds land, matched against the 'Quarter' header row. Only "
        "bites when 'SSOF stake sold for cash' is above zero. Default 2027 Q2: management wants a "
        "defined transaction by end of 2026 but concedes it 'probably' will not have closed, and "
        "these processes involve entitlement and delivery diligence with sophisticated "
        "counterparties. Together with the lever above this is the largest swing factor in the cash "
        "line.",
    ),
    (SECTION, "Asset monetization — Comstock Fuels (Bioleum)"),
    Lever(
        FUELS_VALUE,
        USD_M,
        150,
        0,
        200,
        "Value attributed to Comstock's stake in the fuels business as of the As of date. Default 65 "
        "is management's own FLOOR, not its hope: Comstock sits at the top of the capital stack with "
        "a liquidation preference and 'would expect to recover our sixty-five million dollars for "
        "sure' (2026-08-11, 01:17:47). For reference only, the upside marks are a Marathon Petroleum "
        "$325M term sheet at ~$700M valuation (2024) and ~$1B from third-party investors. Those "
        "are stale and pre-date the founder departures, so they are not the default. Quarterly "
        "Financials compounds this at 'Comstock Fuels value quarterly growth rate' from the As of "
        "date.",
    ),
    Lever(
        FUELS_VALUE_GROWTH,
        "% / q",
        0,
        -5,
        5,
        "QoQ % applied to 'Comstock Fuels value to Comstock' on Quarterly Financials, measured from "
        "the As of date. Default 0 keeps the liquidation-preference floor flat — the conservative "
        "read of a pre-revenue TRL-6 business. Raise it if you underwrite Hexas materials revenue "
        "or a path toward the stale Marathon / third-party marks; use a negative rate if you think "
        "the preference is at risk.",
    ),
    Lever(
        FUELS_ACHIEVED,
        PCT,
        100,
        0,
        100,
        "Share of the value above that is realised. Held at 100 *because the default value is "
        "already the liquidation floor* — double-discounting a floor would understate it. If you "
        "raise the value lever toward the Marathon or third-party marks, cut this hard: the "
        "business is at TRL 6, needs $200–250M for commercial demonstration, is being funded by "
        "third parties rather than Comstock, and has founder departures plus related litigation.",
    ),
    Lever(
        FUELS_BRIDGE_TOTAL,
        USD_M,
        4,
        3,
        6,
        "Bridge financing Comstock extends to the fuels business while it raises third-party "
        "capital. Structured as a LOAN, not equity: 'we're gonna do it as a loan. We're not "
        "putting more equity in' (2026-08-11, 01:00:57). Sized at $3–4M to cover 3–4 months. "
        "Modelled as a cash outflow with no P&L effect, spread over the bridge period.",
    ),
    Lever(
        FUELS_MONTHLY_BURN,
        USD_M,
        0.65,
        0.5,
        0.9,
        "Monthly cash burn of the downsized fuels team, '$600 or $700 thousand' per month "
        "(2026-08-11, 01:02:28). Only used to size and pace the bridge loan — it is not a Comstock "
        "operating expense, because the subsidiary is separately funded.",
    ),
    (SECTION, "Asset monetization — legacy mining"),
    Lever(
        MINING_SALE_CASH,
        USD_M,
        20,
        20,
        20,
        "The 'Initial Payment' — cash at closing for the legacy mining subsidiaries and the Gold "
        "Hill Hotel. The Q2 2026 10-Q Securities Purchase Agreement (dated 2026-06-21) states "
        "'$20,000,000 in cash (the Initial Payment)' explicitly, against which a $150,000 "
        "non-refundable buyer deposit is credited. NO RANGE: the sale CLOSED on 2026-08-24 and the "
        "cash is received, so this is a fact rather than an estimate. Contrast the second tranche "
        "and the contingent payment below, which are still open.",
    ),
    Lever(
        MINING_SALE_QUARTER,
        "quarter",
        "2026 Q3",
        None,
        None,
        "Quarter the Initial Payment lands, matched against the 'Quarter' header row. Default "
        "2026 Q3: cash was expected in August 2026 and the CEO called the close 'imminent' on "
        "2026-08-11. Closing needs TSX-V clearance. Move this if it slips past September — it "
        "shifts $20M, the single biggest near-term item in the cash line.",
    ),
    Lever(
        MINING_SECOND_TRANCHE,
        USD_M,
        7,
        5,
        7,
        "The 'Second Tranche Payment': $7.0M due within 18 months of the effective date, secured by "
        "a Deed of Trust on the sold properties and bearing 12% interest after its due date. Up to "
        "$2M of it may be settled in Mackay Parent stock instead of cash depending on Mackay's "
        "volume-weighted average price, which is why the low end is $5M.",
    ),
    Lever(
        MINING_SECOND_TRANCHE_QUARTER,
        "quarter",
        "2027 Q4",
        None,
        None,
        "Quarter the Second Tranche lands. Eighteen months from the 2026-06-21 effective date is "
        "December 2027, so 2027 Q4 is the contractual outside date rather than an optimistic guess.",
    ),
    Lever(
        MINING_SALE_TOTAL,
        USD_M,
        45,
        45,
        50,
        "Total headline consideration, reconciled from the 10-Q: $20M cash Initial Payment + "
        "2,000,000 Mackay Parent shares + $7M Second Tranche + $10M contingent payment (only if "
        "Mackay makes a Construction Decision or is acquired within 7 years) + assumption of all "
        "reclamation obligations + the 1.5% NSR royalty. Recorded here for reference only — the "
        "cash line uses the two payment levers above, so nothing is double-counted. The $10M "
        "contingent payment and the Mackay shares are deliberately given no value anywhere in the "
        "model. The reclamation assumption is worth something too: $6.7M of reclamation liability "
        "sits in Liabilities Held for Sale and leaves with the buyer.",
    ),
    Lever(
        NSR_ROYALTY,
        PCT,
        1.5,
        1.5,
        1.5,
        "Net smelter return royalty retained on the transferred properties, fixed by contract. "
        "Carried at ZERO in the sum of parts, which is conservative rather than lazy: the agreement "
        "gives Mackay a right to repurchase 100% of it for $3,500,000, rising to $7,000,000 if the "
        "7-year contingent-payment window lapses unpaid. That buyout is a defensible floor — credit "
        "it on the Valuation tab equity note / another dollar line if you want it, never by editing "
        "this cell, which only records the royalty RATE.",
    ),
    (SECTION, "Valuation"),
    Lever(
        METALS_MULTIPLE,
        "x",
        15,
        6,
        16,
        "Multiple applied to annualised metals cash contribution less corporate overhead to value "
        "the recycling *operations*. Default 15 underwrites expected high growth through the ramp; "
        "~10x is a mid-range industrial/waste-services multiple if you want a steadier comps read. "
        "Note this is applied to a *cash contribution* figure, so it already sits above the EBIT "
        "line — it does not need a separate capex deduction, but it also is not a free-cash-flow "
        "multiple. Plant assets, process IP and R&D are valued separately via 'Metals core "
        "business value'.",
    ),
    Lever(
        METALS_CORE_VALUE,
        USD_M,
        50,
        0,
        60,
        "Fixed add-on to Metals business value for assets, process IP, and R&D already in place as "
        "of the start of the spine (2025 Q1) — the demonstration plant, know-how, customer MSAs, and "
        "early metal-recovery work that a cash-contribution multiple alone would miss while the "
        "ramp is still loss-making. ASSUMPTION — Comstock has never published a Metals NAV or IP "
        "appraisal. $50M is a soft package (demo-scale plant plus IP/R&D credit), not a fitted "
        "number; set to 0 to value operations only. Held flat through the forecast: incremental "
        "industry-scale lines are already in Cash - Model (capex) and in the contribution multiple "
        "once they earn.",
    ),
    Lever(
        METALS_ACHIEVED,
        PCT,
        100,
        50,
        100,
        "Final haircut on the *operating* metals EV (proxy × multiple) in the sum of parts — not "
        "on the core asset/IP add-on, which you size directly. Held at 100 by default because the "
        "operating levers above already carry the execution risk, and discounting twice would be "
        "double-counting. Use this only if you want a single overall margin of safety on the "
        "operating business while leaving the unit economics at management's numbers.",
    ),
    Lever(
        NET_CASH_CREDIT,
        PCT,
        100,
        0,
        100,
        "PERCENTAGE of modelled net cash credited to equity value — not a dollar amount. 100 "
        "treats cash as cash. Reduce it if you think the cash will be consumed by losses before it "
        "can benefit shareholders — an honest concern for a company at this stage, and a cleaner "
        "way to express it than manipulating the operating levers. A near-term cash sanity check "
        "(~$35–51M after the Mackay Initial Payment, depending on burn) belongs on the Valuation "
        "tab notes, not in this cell.",
    ),
]


def _rows() -> list[object]:
    return LEVERS


def lever_rows() -> dict[str, int]:
    """Label → 1-based row on the Levers tab (row 1 is the header)."""
    out: dict[str, int] = {}
    row = 1
    for item in LEVERS:
        row += 1
        if isinstance(item, Lever):
            out[item.label] = row
    return out


def lever(label: str) -> Lever:
    for item in LEVERS:
        if isinstance(item, Lever) and item.label == label:
            return item
    raise KeyError(f"No lever named {label!r}")


def lever_ref(label: str) -> str:
    """Absolute A1 reference to a lever's value cell, for use inside sheet formulas."""
    rows = lever_rows()
    if label not in rows:
        raise KeyError(f"No lever named {label!r}")
    # No quotes: sheet name has no spaces; Sheets also strips them on read, which
    # would otherwise make validate_model_formulas report false drift.
    return f"{LEVERS_SHEET}!${VALUE_COL}${rows[label]}"


def grid() -> list[list[object]]:
    """Full A1:G{n} value grid for the tab."""
    out: list[list[object]] = [list(HEADER)]
    for item in LEVERS:
        if isinstance(item, Lever):
            out.append(
                [
                    item.label,
                    item.units,
                    item.default,
                    item.default,
                    "" if item.low is None else item.low,
                    "" if item.high is None else item.high,
                    item.rationale,
                ]
            )
        else:
            _, heading = item  # type: ignore[misc]
            out.append([heading, "", "", "", "", "", ""])
    return out


def section_rows() -> list[int]:
    """1-based rows that are section headings (for bold formatting)."""
    out: list[int] = []
    row = 1
    for item in LEVERS:
        row += 1
        if not isinstance(item, Lever):
            out.append(row)
    return out


def value_rows() -> list[int]:
    """1-based rows that hold an editable value in column C (for yellow fill)."""
    return sorted(lever_rows().values())


def date_rows() -> list[int]:
    """Rows whose value cell should be formatted as a date."""
    rows = lever_rows()
    return [rows[AS_OF_DATE]]


# Levers whose value is a quarter key ("2026 Q3") matched against the Quarter header.
QUARTER_LEVERS: tuple[str, ...] = (
    SSOF_PROCEEDS_QUARTER,
    MINING_SALE_QUARTER,
    MINING_SECOND_TRANCHE_QUARTER,
    TAILINGS_STOCKPILE_START,
)
