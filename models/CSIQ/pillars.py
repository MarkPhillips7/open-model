"""Pillars tab: the three stakes, the buildout, and what is given no separate value."""

from __future__ import annotations

PILLARS_SHEET = "Pillars"

HEADER = ["Item", "Figure", "As of", "What it means here"]
COL_WIDTHS_PX: dict[int, int] = {0: 340, 1: 220, 2: 140, 3: 780}

SECTION_CSI = "CSI SOLAR"
SECTION_POWER = "CS POWERTECH — US MANUFACTURING"
SECTION_STORAGE = "E-STORAGE"
SECTION_RECURRENT = "RECURRENT ENERGY"
SECTION_NOT = "GIVEN NO SEPARATE VALUE"

SECTION_LABELS: frozenset[str] = frozenset(
    {SECTION_CSI, SECTION_POWER, SECTION_STORAGE, SECTION_RECURRENT, SECTION_NOT}
)

# (item, figure, as of, note)
ROWS: list[tuple[str, str, str, str]] = [
    (SECTION_CSI, "", "", ""),
    (
        "CSIQ ownership",
        "about 64%",
        "2026-04-27",
        "6-K: Canadian Solar owns approximately 64% of CSI Solar, listed on the Shanghai STAR Market.",
    ),
    (
        "Shanghai market cap used",
        "$7B",
        "2026-04-28",
        "Lucas Sacerdote's figure in the thesis. A lever, not a live quote. Update it.",
    ),
    (
        "Holdco discount",
        "30%",
        "2026-04-28",
        "Thesis base case. He said UBS was closer to a 90% discount and put zero on the US.",
    ),
    (
        "Earnings cross-check",
        "$800–850M EBITDA, 8×, $1.4B net debt",
        "2026-04-28",
        "Lands near the discounted stake. Shown beside the listed value and not added to it.",
    ),
    (SECTION_POWER, "", "", ""),
    (
        "CSIQ direct stake",
        "75.1%",
        "2025-12-01",
        "Canadian Solar formed CS PowerTech with CSI Solar and took a 75.1% controlling stake. CSI Solar holds the rest.",
    ),
    (
        "Mesquite, Texas modules",
        "5 GWp, expanding to 10 GWp",
        "H2 2026",
        "Q2 2026 release. Nameplate, not recognized shipments. The 10 GW figure is the bull-case volume, not the default plan.",
    ),
    (
        "Jeffersonville HJT cells, Phase I",
        "2.1 GWp",
        "Opened July 2026",
        "First commercial HJT cell factory in the US, per the company. Ribbon cutting in July; trial production had started in April.",
    ),
    (
        "Jeffersonville Phase II",
        "+4.2 GWp, total 6.3 GWp",
        "Trial Q1 2027; nameplate H1 2027",
        "Why the default underwritten volume is ~6 GW/year and not the 10 GW module nameplate. Cells are the constraint on domestic content.",
    ),
    (
        "Thesis base margin",
        "7.5¢/W after a $250M lease, 8×",
        "2026-04-28",
        "Lucas: about half the margin T1 Energy markets. Bull case in the same video is 13¢/W, 10 GW, 10×, about $10B.",
    ),
    (
        "2026 US module guide",
        "6.5–7.0 GW",
        "Reiterated 2026-08-27",
        "The 2026 yellow plan sums to 6.7 GW. This is shipments into the US, not all of it on domestic cells yet.",
    ),
    (
        "US module bookings",
        "13 GW through 2029, mid-$0.30/W",
        "Q2 2026 call",
        "Contracted visibility, not a volume cap. The 2026 shipment guide is larger than this backlog alone. Price is the revenue-bridge ASP. Parkin said Section 232 should be accretive and would not size it.",
    ),
    (SECTION_STORAGE, "", "", ""),
    (
        "Contracted backlog",
        "$3.5B",
        "2026-06-30",
        "e-STORAGE backlog including long-term service agreements. Was $3.6B in the April thesis. Visibility, not a separate NAV.",
    ),
    (
        "Q2 2026 shipments",
        "3.7 GWh",
        "2026-06-30",
        "Above 2.8–3.2 GWh guidance. 471 MWh was internal, revenue deferred. Q1 was 2.1 GWh, also above guide.",
    ),
    (
        "2026 US storage guide",
        "4.5–5.5 GWh",
        "Reiterated 2026-08-27",
        "The yellow US plan sums to 5.0 GWh. The thesis had talked about 14–17 GWh global for 2026; the company did not reiterate that in the Q2 release.",
    ),
    (
        "Thesis base economics",
        "5 GWh, $200/kWh, 15% margin, 12×",
        "2026-04-28",
        "$150M EBITDA and $1.8B at 100% ownership. Bull case: 20 GWh at a $45/kWh credit-like margin, minus ~$800M of factory debt.",
    ),
    (SECTION_RECURRENT, "", "", ""),
    (
        "BlackRock mark",
        "$500M for 20%, $2.5B post-money",
        "Early 2024",
        "The equity value the model holds unless you move the achieved lever. CSIQ's 80% is $2.0B.",
    ),
    (
        "Solar pipeline",
        "21.7 GWp",
        "2026-06-30",
        "1.7 under construction, 2.2 backlog, 2.2 advanced, 15.5 early-stage. Down from 23.7 GWp at March 31. The company is pruning.",
    ),
    (
        "Storage pipeline",
        "84.1 GWh",
        "2026-06-30",
        "0.6 under construction, 4.4 backlog, the rest earlier stage. Includes projects that may be sold rather than kept.",
    ),
    (
        "Operating fleet book",
        "$2.0B net PP&E-equivalent",
        "2026-06-30",
        "Solar power and battery systems, net, on the balance sheet. Not added on top of the $2.5B equity mark.",
    ),
    (
        "O&M",
        "15 GW contracted",
        "2026-06-30",
        "Power services, about $20M a quarter. Inside Recurrent revenue, not a third multiple.",
    ),
    (
        "Q2 segment result",
        "Revenue $117M, operating loss $19M",
        "2026-06-30",
        "Light because project sales moved to H2. Electricity rose after a Spanish project reached COD. A $24M-class Latin America impairment is in the quarter's expenses discussion.",
    ),
    (
        "Non-recourse debt",
        "$2.62B",
        "2026-06-30",
        "Project debt. Recurrent borrowings in total were about $4.1B. Left inside the equity mark.",
    ),
    (SECTION_NOT, "", "", ""),
    (
        "Early-stage pipeline",
        "15.5 GWp solar, ~71 GWh storage",
        "2026-06-30",
        "The company itself says pipeline magnitude is not a forecast of owned assets or revenue. Not given a $/W on top of BlackRock's price.",
    ),
    (
        "e-STORAGE backlog as NAV",
        "$3.5B of orders",
        "2026-06-30",
        "Those orders are the volume path. Adding the backlog as a lump of value on top of storage EBITDA would count the same watts twice.",
    ),
    (
        "45X / domestic-content credits",
        "Inside the ¢/W, or not at all",
        "2026-04-28",
        "Lucas's 7.5¢ is already his net margin. His bull case switches to an explicit $45/kWh credit. Do not add credits on top of either.",
    ),
    (
        "CSI Solar's 24.9% of PowerTech",
        "Inside the Shanghai stake if the market prices it",
        "2025-12-01",
        "Default ownership on the US equity value is the 75.1% Canadian Solar holds directly. Set it to 100% only if you believe Shanghai gives this nothing.",
    ),
    (
        "Full $7.1B of debt",
        "Not a holdco obligation in one piece",
        "2026-06-30",
        "Only converts, net of the $42M unallocated cash, are subtracted. The rest is inside the stakes.",
    ),
]


def grid() -> list[list[str]]:
    return [list(HEADER), *([list(row) for row in ROWS])]


def section_rows() -> list[int]:
    return [i + 2 for i, row in enumerate(ROWS) if row[0] in SECTION_LABELS]
