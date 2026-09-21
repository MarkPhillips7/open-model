"""Asset Monetization tab: the evidence behind the three non-operating value pillars.

The Levers tab holds the numbers the model actually uses. This tab holds the facts
those numbers came from, so a reader can check whether a lever is defensible without
leaving the workbook. Anything sourced from a filing or a transcript is stated with
its date; anything that is an inference is labelled as one.

Three pillars, in descending order of how solidly they are evidenced:

1. **Legacy mining sale** — signed agreement, specific dollar amounts, one open
   condition. Close to a receivable.
2. **SSOF powered land** — assets owned and power secured, but no transaction yet
   and the value rests on comparable deals rather than a signed price.
3. **Comstock Fuels (Bioleum)** — pre-commercial. The only number with real support
   is Comstock's liquidation preference; the historical valuation marks are stale.
"""

from __future__ import annotations

from models.LODE import levers as lv

ASSET_SHEET = "Asset Monetization"

HEADER = ["Item", "Units", "Value", "Notes"]
COL_WIDTHS_PX: dict[int, int] = {0: 330, 1: 96, 2: 130, 3: 840}

SECTION_MINING = "LEGACY MINING SALE — signed, one condition outstanding"
SECTION_SSOF = "SSOF 'POWERED LAND' — assets secured, no transaction yet"
SECTION_FUELS = "COMSTOCK FUELS / BIOLEUM — pre-commercial"
SECTION_EXCLUDED = "DELIBERATELY EXCLUDED FROM VALUE"

SECTION_LABELS: frozenset[str] = frozenset(
    {SECTION_MINING, SECTION_SSOF, SECTION_FUELS, SECTION_EXCLUDED}
)

_LEVER = "→ lever"


# (item, units, value, notes). ``value`` of ``_LEVER`` becomes a live reference to
# the matching lever so this tab cannot drift from the numbers the model uses.
ROWS: list[tuple[str, str, object, str]] = [
    (SECTION_MINING, "", "", ""),
    (
        "Counterparty",
        "",
        "Mackay",
        "Mackay Precious Metals Inc. and Mackay Gold & Silver Corp. ('Mackay Parent', a British "
        "Columbia corporation). Securities Purchase Agreement dated 2026-06-21.",
    ),
    (
        "Entities sold",
        "count",
        4,
        "Comstock Mining LLC, Comstock Processing LLC, Comstock Exploration and Development LLC, and "
        "Comstock Real Estate Inc. (whose main asset is the Gold Hill Hotel). Properties sit in Lyon "
        "and Storey Counties, Nevada. The Silver Springs real estate is expressly NOT included — "
        "that is SSOF, which is the whole point of the next section.",
    ),
    (
        "Cash at closing",
        "$M",
        _LEVER,
        "The 'Initial Payment'. The 10-Q states '$20,000,000 in cash' outright. A $150,000 "
        "non-refundable buyer deposit is credited against it at closing.",
    ),
    (
        "Second tranche",
        "$M",
        _LEVER,
        "Due within 18 months of the effective date, secured by a Deed of Trust on the sold "
        "properties, and bearing 12% interest after the due date. Up to $2M may be settled in "
        "Mackay Parent stock depending on its volume-weighted average price.",
    ),
    (
        "Mackay Parent shares received",
        "shares",
        2_000_000,
        "Equity consideration. Given NO value in this model: Mackay Parent is a small TSX-V issuer, "
        "so the position is illiquid and the model would rather understate than guess.",
    ),
    (
        "Contingent payment",
        "$M",
        10,
        "Payable in cash only if, within 7 years of closing, Mackay makes a Construction Decision or "
        "a Change of Control occurs. Given NO value here — a seven-year conditional call on somebody "
        "else's capital-allocation decision is not something to capitalise.",
    ),
    (
        "NSR royalty retained",
        "%",
        _LEVER,
        "1.5% net smelter return on minerals produced from the transferred properties. Mackay may "
        "repurchase 100% of it for $3,500,000, rising to $7,000,000 if the 7-year contingent window "
        "lapses unpaid. That repurchase right is a defensible floor if you want to credit it; the "
        "model carries it at zero.",
    ),
    (
        "Reclamation liability transferred",
        "$M",
        6.71,
        "Reclamation obligation sitting in Liabilities Held for Sale at 2026-06-30 that leaves with "
        "the buyer, along with the associated surety bonds and collateral. Real economic relief, but "
        "not modelled as cash because it was never going to be paid in one quarter.",
    ),
    (
        "Assets held for sale",
        "$M",
        22.99,
        "Carrying value at 2026-06-30: mineral properties and water rights $11.25M, buildings, land "
        "and equipment $7.43M, reclamation bond deposit $4.29M, other $0.02M. Because the disposal is "
        "classified held for sale and NOT discontinued operations, no prior period is restated and "
        "mining revenue stays inside reported revenue in every historical quarter.",
    ),
    (
        "Closing status",
        "",
        "CLOSED 2026-08-24",
        "The sale completed on 2026-08-24 and the $20.0M Initial Payment is received, so the closing "
        "quarter (2026 Q3) and the cash amount are now facts rather than estimates. What remains "
        "open is the $7.0M second tranche, the $10.0M contingent payment, and the NSR buyout.",
    ),
    (SECTION_SSOF, "", "", ""),
    (
        "Comstock ownership",
        "%",
        _LEVER,
        "47.63% as of Q2 2026, up materially during 2026. Accounted for under the equity method, so "
        "the balance-sheet carrying value is far below this share of the values below — that gap is "
        "the option value this section exists to surface.",
    ),
    (
        "Land owned",
        "acres",
        2_500,
        "Silver Springs, Nevada. Crucially, Comstock only took OWNERSHIP roughly three to four weeks "
        "before 2026-08-11, by exercising a purchase option entered in 2019 at 2019 prices. Before "
        "that it held an option, not the land — which is why nothing was marketed earlier.",
    ),
    (
        "Water rights",
        "acre-feet",
        2_000,
        "Roughly 2,000 acre-feet. For a data-centre buyer, water for cooling is a gating item, not a "
        "nice-to-have, so this is part of what makes the site sellable rather than just large.",
    ),
    (
        "Power secured",
        "MW",
        300,
        "300 MW of gas equivalent won through a Southwest Gas open-bid development project, with "
        "pipeline delivery in November 2028. This is the single most important fact in the section: "
        "buyers in this market increasingly price by the megawatt rather than by the acre, and "
        "unpowered land near a tapped-out grid is worth a fraction of powered land.",
    ),
    (
        "Additional power targeted",
        "MW",
        900,
        "A further 900 MW, possibly 1,200 MW, targeted for 2030, with Comstock positioned in the "
        "front line for the next allocation. Not included in the valuation comps — treat it as "
        "upside that is not yet in the number.",
    ),
    (
        "Gross asset value",
        "$M",
        _LEVER,
        "Management's comparable range for the powered-land thesis is '$400, $500, $600 million' "
        "(CEO, 2026-08-11). Northern Nevada sits next to the Tahoe Reno Industrial Center, and the "
        "CEO names Switch, Apple, Microsoft and Google as present in the region. This is a comp, not "
        "a bid — hence the achievement lever.",
    ),
    (
        "Value achieved",
        "%",
        _LEVER,
        "The haircut. Covers whether the comps hold, minority-stake and structuring friction, and "
        "timing all at once.",
    ),
    (
        "Monetization quarter",
        "quarter",
        _LEVER,
        "When proceeds are assumed to land. Management's own year-end 2026 test is only 'some defined "
        "transaction with some derivable value', and the CEO said a close by then is 'probably not'. "
        "Comstock is explicit it wants to pull capital out of SSOF, not put more in.",
    ),
    (SECTION_FUELS, "", "", ""),
    (
        "Comstock value attributed",
        "$M",
        _LEVER,
        "Default is the liquidation-preference floor, not a growth valuation. Comstock sits at the "
        "top of the capital stack and the CEO expects to recover '$65 million for sure' in a wind-up "
        "(2026-08-11).",
    ),
    (
        "Marathon Petroleum term sheet",
        "$M",
        325,
        "At roughly a $700M valuation, in 2024. Reference only. Marathon's interest was driven by the "
        "feedstock breakthrough. Stale, and it predates the founder departures.",
    ),
    (
        "Third-party investor valuation",
        "$M",
        1_000,
        "Approximately $1B from third-party investors. Reference only, and for the same reasons not "
        "used as a default.",
    ),
    (
        "Bridge loan from Comstock",
        "$M",
        _LEVER,
        "A LOAN, not equity: 'we're not putting more equity in' (CEO, 2026-08-11). Sized to carry a "
        "downsized team three to four months while third-party capital is raised.",
    ),
    (
        "Monthly burn",
        "$M",
        _LEVER,
        "About $600–700k per month for the downsized team. Used only to size and pace the bridge — "
        "it is not a Comstock operating expense, because the subsidiary is separately funded.",
    ),
    (
        "Technology readiness level",
        "TRL",
        6,
        "Building an integrated TRL 6 pilot. TRL 7 commercial demonstration needs $200–250M; a "
        "million-ton-per-year industry-scale biorefinery is $1.0–1.2B for $700M–$1B of revenue. "
        "Oklahoma has allocated ~$160–170M of private activity bonds toward the TRL 7 facility, but "
        "management says it is 'not ready yet' to build it. This is why fuels is an option, not a "
        "business line, in this model.",
    ),
    (
        "Core technology retained",
        "",
        "Organosolv",
        "Solvent digestion that fractionates woody biomass into cellulosic and lignin paths, plus "
        "RenFuel (lignin to oil) and Hexas Biomass (a purpose-grown feedstock at 60–100 barrels of "
        "oil equivalent per acre per year versus 10 for corn). The $16.4M Flux Photon write-off in "
        "Q2 2026 was peripheral IP the company decided it would never fund, not this core.",
    ),
    (
        "Known risks",
        "",
        "See notes",
        "Founder departures with related litigation; a $200–250M funding requirement Comstock will "
        "not meet itself; and the fact that a bridge loan was needed at all, which says the "
        "third-party raise is taking longer than planned.",
    ),
    (SECTION_EXCLUDED, "", "", ""),
    (
        "Green Li-ion investment",
        "$M",
        0,
        "Held in the Strategic Investments segment alongside SSOF. Carried at zero here because "
        "Comstock does not disclose a separable value for it. Understatement, not an oversight.",
    ),
    (
        "Mining contingent and equity consideration",
        "$M",
        0,
        "The $10M contingent payment and the 2,000,000 Mackay Parent shares, both excluded above.",
    ),
    (
        "NSR royalty buyout value",
        "$M",
        0,
        "The $3.5M Mackay repurchase right, excluded. Listed here so the exclusions are explicit "
        "rather than invisible — together these lines are roughly $15M of value the model refuses "
        "to count.",
    ),
]


# Rows whose value cell is a live reference to a lever, in tab order.
LEVER_BY_ITEM: dict[str, str] = {
    "Cash at closing": lv.MINING_SALE_CASH,
    "Second tranche": lv.MINING_SECOND_TRANCHE,
    "NSR royalty retained": lv.NSR_ROYALTY,
    "Comstock ownership": lv.SSOF_OWNERSHIP,
    "Gross asset value": lv.SSOF_GROSS_VALUE,
    "Value achieved": lv.SSOF_ACHIEVED,
    "Monetization quarter": lv.SSOF_PROCEEDS_QUARTER,
    "Comstock value attributed": lv.FUELS_VALUE,
    "Bridge loan from Comstock": lv.FUELS_BRIDGE_TOTAL,
    "Monthly burn": lv.FUELS_MONTHLY_BURN,
}


def label_rows() -> dict[str, int]:
    out: dict[str, int] = {}
    for i, (item, _u, _v, _n) in enumerate(ROWS, start=2):
        out.setdefault(item, i)
    return out


def grid() -> list[list[object]]:
    """Full A1:D{n} grid. Lever-backed rows become formulas so they cannot drift."""
    out: list[list[object]] = [list(HEADER)]
    for item, units, value, notes in ROWS:
        if item in SECTION_LABELS:
            out.append([item, "", "", ""])
            continue
        if value == _LEVER:
            value = f"={lv.lever_ref(LEVER_BY_ITEM[item])}"
        out.append([item, units, value, notes])
    return out


def section_rows() -> list[int]:
    return [i for i, (item, _u, _v, _n) in enumerate(ROWS, start=2) if item in SECTION_LABELS]
