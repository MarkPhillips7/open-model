"""Levers tab: every scalar assumption in the CSIQ model.

A lever does not vary by quarter. Time shapes (the US ramp, Recurrent project
sales) are yellow ``- Plan`` rows on Quarterly Financials.

Where the video states a figure, that figure is the default. Scepticism has its
own dial (an "achieved" percent, a holdco discount, or an ownership stake) so
"what was claimed" stays readable next to "what this sheet underwrites."
"""

from __future__ import annotations

LEVERS_SHEET = "Levers"

VALUE_COL = "C"

HEADER = ["Lever", "Units", "Value", "Default", "Low", "High", "Rationale / source"]

COL_WIDTHS_PX: dict[int, int] = {0: 360, 1: 90, 2: 100, 3: 90, 4: 80, 5: 80, 6: 920}

SECTION = object()


class Lever:
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


AS_OF_DATE = "As of date"
DISCOUNT_RATE = "Discount rate"

US_MODULE_VOL_ACH = "US module volume achieved"
EXUS_MODULE_VOL_ACH = "Ex-US module volume achieved"
US_STORAGE_VOL_ACH = "US storage volume achieved"
EXUS_STORAGE_VOL_ACH = "Ex-US storage volume achieved"

US_MODULE_ASP = "US module ASP"
EXUS_MODULE_ASP = "Ex-US module ASP"
US_STORAGE_ASP = "US storage ASP"
EXUS_STORAGE_ASP = "Ex-US storage ASP"
OTHER_MFG_REV = "Other manufacturing revenue per quarter"

US_MODULE_MARGIN = "US module cash margin"
US_MODULE_MARGIN_ACH = "US module margin achieved"
US_LEASE = "US factory lease per year"
US_LEASE_GW = "Lease sized at annual GW"
US_MODULE_MULTIPLE = "US module EV / EBITDA"

US_STORAGE_MARGIN = "US storage EBITDA margin"
US_STORAGE_MARGIN_ACH = "US storage margin achieved"
US_STORAGE_MULTIPLE = "US storage EV / EBITDA"
US_STORAGE_DEBT = "US storage net debt"
POWERTECH_OWNED = "CSIQ direct ownership of CS PowerTech"
US_VALUE_ACH = "US manufacturing value achieved"

CSI_MKTCAP = "CSI Solar Shanghai market cap"
CSI_OWNED = "CSIQ ownership of CSI Solar"
CSI_DISCOUNT = "CSI Solar holdco discount"
CSI_ACH = "CSI Solar value achieved"
CSI_EBITDA = "CSI Solar normalized EBITDA"
CSI_MULTIPLE = "CSI Solar EV / EBITDA"
CSI_NET_DEBT = "CSI Solar net debt"

RECURRENT_EQUITY = "Recurrent equity value"
RECURRENT_OWNED = "CSIQ ownership of Recurrent"
RECURRENT_ACH = "Recurrent value achieved"

CONVERTS = "Convertible notes"
HOLDCO_CASH = "Holdco cash"
HOLDCO_CASH_CREDIT = "Holdco cash credited"
GROSS_MARGIN = "Consolidated gross margin"
OPEX_Q = "Operating expenses per quarter"
SHARE_DRIP = "Share count quarterly growth"
DILUTED_SHARES = "Fully diluted shares"

PCT = "%"
USD_M = "$M"
USD_W = "$/W"
USD_KWH = "$/kWh"
GW = "GW"
SHARES = "M shares"


LEVERS: list[object] = [
    (SECTION, "Timing and discount"),
    Lever(
        AS_OF_DATE,
        "date",
        "2026-09-25",
        None,
        None,
        "Valuation date. Years-from-present and the discount on the US ramp both measure from here. "
        "Reported actuals run through 2026 Q2 (released 2026-08-27).",
        number_format="yyyy-mm-dd",
    ),
    Lever(
        DISCOUNT_RATE,
        PCT,
        12,
        0,
        20,
        "Applied only to the US manufacturing equity value, and only for quarters after this date. "
        "CSI Solar's listed stake and the BlackRock Recurrent mark are already present-value claims, "
        "so they are not discounted again. Set this to 0 to treat the future US run-rate as worth "
        "that amount today — the stance in the 2026-04-28 thesis.",
    ),
    (SECTION, "Volume — scepticism on the yellow plan"),
    Lever(
        US_MODULE_VOL_ACH,
        PCT,
        100,
        50,
        110,
        "Scales the US module GW plan. Default 100% leaves the plan alone: 6.7 GW in 2026 (inside "
        "the reiterated 6.5–7.0 GW US guide) and 6.0 GW/year from 2027. Cut this if Jeffersonville "
        "or Mesquite slips. The plan row is where you change the shape.",
    ),
    Lever(
        EXUS_MODULE_VOL_ACH,
        PCT,
        100,
        50,
        130,
        "Scales ex-US module GW. Does not enter the sum-of-parts: ex-US earnings sit inside the CSI "
        "Solar stake. It only affects the revenue bridge, so you can see whether the volume path "
        "still lands inside quarterly guidance.",
    ),
    Lever(
        US_STORAGE_VOL_ACH,
        PCT,
        100,
        40,
        160,
        "Scales the US storage GWh plan. 100% is 5.0 GWh in 2026 (midpoint of 4.5–5.5) and 5 GWh/year "
        "after that. Lucas Sacerdote's bull case is 20 GWh — that is a plan-row edit, not this dial. "
        "The high end here is headroom, not the bull case.",
    ),
    Lever(
        EXUS_STORAGE_VOL_ACH,
        PCT,
        100,
        50,
        150,
        "Scales ex-US storage GWh for the revenue bridge only. Same double-count rule as ex-US modules: "
        "this volume is inside CSI Solar, not a second storage equity value.",
    ),
    (SECTION, "Prices — revenue bridge, not the valuation margin"),
    Lever(
        US_MODULE_ASP,
        USD_W,
        0.30,
        0.22,
        0.40,
        "Used only to turn US module GW into revenue dollars. On the Q2 2026 call an analyst "
        "put the 13 GW of US bookings through 2029 at mid-$0.30/W, and Colin Parkin did not "
        "dispute the level. He would not quantify how much Section 232 might add on top. "
        "Q2 blended module ASP was still about $0.19/W because nearly half the volume was "
        "ex-US. The valuation does not use this price; it uses the cash-margin lever.",
        number_format="0.00",
    ),
    Lever(
        EXUS_MODULE_ASP,
        USD_W,
        0.10,
        0.07,
        0.16,
        "Ex-US module price in the downturn. Revenue bridge only. Management has been restricting "
        "volume rather than chasing price while silver and other feedstock costs are elevated "
        "(Q1 2026 call, Colin Parkin).",
        number_format="0.00",
    ),
    Lever(
        US_STORAGE_ASP,
        USD_KWH,
        200,
        120,
        250,
        "Lucas's base-case US storage price: 5 GWh × $200/kWh × 15% margin = $150M EBITDA. "
        "Q2 2026 blended recognized storage ASP was about $115/kWh ($426M / 3.7 GWh), so $200 is a "
        "US price, not the global blend. It drives both US storage revenue and US storage EBITDA.",
        number_format="#,##0",
    ),
    Lever(
        EXUS_STORAGE_ASP,
        USD_KWH,
        80,
        50,
        140,
        "Chosen so US $200 and ex-US $80 land the 2026 Q3 storage revenue bridge near the recent "
        "blended print. Revenue bridge only.",
        number_format="#,##0",
    ),
    Lever(
        OTHER_MFG_REV,
        USD_M,
        70,
        40,
        120,
        "Solar system kits plus EPC and other, per quarter, when no actual is typed. Q1 2026 was "
        "$103M and Q2 2026 was $79M. Inside manufacturing revenue; not given its own multiple.",
    ),
    (SECTION, "US modules — CS PowerTech"),
    Lever(
        US_MODULE_MARGIN,
        USD_W,
        0.075,
        0.03,
        0.13,
        "Lucas base case: 7.5¢/W cash margin on 6 GW, which he described as about half the margin "
        "T1 Energy is marketing. Bull case in the same video is 13¢/W on 10 GW. Gross module EBITDA "
        "before lease = GW × this margin × the phase-in row. Q2 2026 did not disclose a US ¢/W.",
        number_format="0.000",
    ),
    Lever(
        US_MODULE_MARGIN_ACH,
        PCT,
        100,
        0,
        100,
        "Extra haircut on the 7.5¢ itself. Left at 100% because the yellow phase-in row is already "
        "the ramp scepticism (Jeffersonville ramp costs through 2026). Turn this down if you think "
        "7.5¢ is too high even at full phase-in.",
    ),
    Lever(
        US_LEASE,
        USD_M,
        250,
        150,
        350,
        "Lucas: about $250M/year of lease cost on the US factories, subtracted from gross module "
        "EBITDA. He flagged this as conservative because some of that lease is interest and "
        "depreciation a buyer might add back. Charged in proportion to US GW, capped once volume "
        "reaches 'Lease sized at annual GW'.",
    ),
    Lever(
        US_LEASE_GW,
        GW,
        6,
        4,
        10,
        "Annual GW at which the full lease is on. Lucas sized $250M against his 6 GW base case. "
        "A quarter shipping 1.5 GW (6/4) bears the full quarterly lease.",
    ),
    Lever(
        US_MODULE_MULTIPLE,
        "x",
        8,
        5,
        10,
        "Lucas base: 8× EBITDA → $200M × 8 = $1.6B at 100% of the US solar subsidiary. Bull case "
        "in the video is 10× on a $1B EBITDA. Applied to annualized quarterly EBITDA.",
        number_format="0.0",
    ),
    (SECTION, "US storage — CS PowerTech"),
    Lever(
        US_STORAGE_MARGIN,
        PCT,
        15,
        8,
        25,
        "Lucas base: 15% EBITDA margin on US storage revenue. Bull case in the video switches the "
        "stack to a $45/kWh production-tax-credit margin on 20 GWh, which is a different model — "
        "edit the plan and this margin if you want that case, and do not also add the credit on top.",
    ),
    Lever(
        US_STORAGE_MARGIN_ACH,
        PCT,
        100,
        0,
        100,
        "Extra haircut on the 15% margin. Default 100%; the phase-in row carries 2026 scepticism. "
        "Parkin said in May 2026 that storage competition is intensifying.",
    ),
    Lever(
        US_STORAGE_MULTIPLE,
        "x",
        12,
        6,
        14,
        "Lucas: 12× because storage is the growth engine. $150M × 12 = $1.8B at 100% ownership. "
        "He contrasted that with Eos Energy reaching a similar headline value on a few hundred MWh.",
        number_format="0.0",
    ),
    Lever(
        US_STORAGE_DEBT,
        USD_M,
        0,
        0,
        800,
        "Subtracted from US storage enterprise value. Lucas's base case does not subtract factory "
        "debt; his bull case subtracts about $800M of buildout financing. Default 0 matches the base "
        "case. Do not also subtract manufacturing segment debt — that sits inside the CSI Solar mark "
        "and the PowerTech equity value.",
    ),
    (SECTION, "Ownership — the double-count guard"),
    Lever(
        POWERTECH_OWNED,
        PCT,
        75.1,
        50,
        100,
        "On 2025-12-01 Canadian Solar took a 75.1% controlling stake in CS PowerTech, the US "
        "manufacturing JV, with CSI Solar holding the other 24.9%. US equity value is multiplied by "
        "this stake. 100% reproduces Lucas's $1.6B + $1.8B and also counts the 24.9% that, if the "
        "Shanghai price reflects it, is already inside the CSI Solar stake. Default is the direct stake.",
        number_format="0.0",
    ),
    Lever(
        US_VALUE_ACH,
        PCT,
        100,
        0,
        100,
        "Scales both US equity values after the multiple. The bear case in the video sets US solar "
        "and US storage to zero (factories written off). This is that dial. Volume, margin, and "
        "phase-in are separate.",
    ),
    (SECTION, "CSI Solar — listed stake"),
    Lever(
        CSI_MKTCAP,
        USD_M,
        7000,
        3000,
        12000,
        "Shanghai-listed CSI Solar market cap used in the 2026-04-28 thesis ($7B). That figure is "
        "the video's, not a live quote — update this cell. CSI Solar (STAR Market, 688472) is the "
        "global-ex-US manufacturer. Canadian Solar owned about 64% as of the April 2026 6-K.",
    ),
    Lever(
        CSI_OWNED,
        PCT,
        64,
        50,
        75,
        "Canadian Solar's ownership of CSI Solar, 'approximately 64%' in the 2026-04-27 6-K. The "
        "stake, not the whole market cap, is what CSIQ shareholders own.",
        number_format="0.0",
    ),
    Lever(
        CSI_DISCOUNT,
        PCT,
        30,
        0,
        90,
        "Lucas applies 30% for the stake being a Chinese listed company inside a Canadian holdco. "
        "UBS, in his telling, was using something near a 90% holdco discount and putting nothing on "
        "US operations. 0% is his bull case (mark the Shanghai price with no discount).",
    ),
    Lever(
        CSI_ACH,
        PCT,
        100,
        0,
        100,
        "Scales the listed stake. Bear case in the video is a distress value of about $500M to CSIQ "
        "(roughly 20% of book). Get there by cutting this, or by cutting the market cap and raising "
        "the discount — this dial is the single scepticism switch.",
    ),
    Lever(
        CSI_EBITDA,
        USD_M,
        825,
        200,
        1200,
        "Cross-check only, not added to equity. Lucas: normalized EBITDA of $800–850M. Midpoint $825M. "
        "8× minus $1.4B net debt, times 64% ownership, lands near the discounted Shanghai stake. "
        "If this cross-check and the listed stake diverge a lot, one of them is stale.",
    ),
    Lever(
        CSI_MULTIPLE,
        "x",
        8,
        4,
        12,
        "Cross-check only. Lucas uses 8× on CSI Solar, the same multiple as US modules, not the 12× "
        "he uses for storage.",
        number_format="0.0",
    ),
    Lever(
        CSI_NET_DEBT,
        USD_M,
        1400,
        800,
        2500,
        "Cross-check only. Lucas subtracts $1.4B of CSI Solar net debt from the earnings value. "
        "Manufacturing borrowings were $2.4B at 2026-06-30 against manufacturing cash of $1.3B, so "
        "$1.4B net is in the neighborhood but is his figure, not a line we re-derived this quarter. "
        "Not subtracted again in the equity value — the listed stake is already equity.",
    ),
    (SECTION, "Recurrent Energy"),
    Lever(
        RECURRENT_EQUITY,
        USD_M,
        2500,
        800,
        5000,
        "100% equity value. BlackRock invested $500M for 20% in early 2024, $2.5B post-money. "
        "Lucas's base case holds that mark: $5.5B asset base, about $3B net debt, low-to-mid-teens "
        "levered IRR, about 2× book. His bull case is $5B of 100% equity (operating assets plus a "
        "pipeline). Q2 2026 net project debt is higher than $3B (Recurrent borrowings were $4.1B). "
        "The mark is an equity price, so that debt is not subtracted again.",
    ),
    Lever(
        RECURRENT_OWNED,
        PCT,
        80,
        60,
        90,
        "Canadian Solar's share after BlackRock's 20%. There is also a redeemable non-controlling "
        "interest on the balance sheet ($318M at 2026-06-30); this lever is the video's 80%, not a "
        "re-cut of that carrying value.",
        number_format="0.0",
    ),
    Lever(
        RECURRENT_ACH,
        PCT,
        100,
        40,
        120,
        "Scepticism on the 2024 mark. Left at 100% so the default shows what BlackRock paid. Turn it "
        "down if a two-year-old round plus 2026's deferred project sales, Latin America impairment, "
        "and pipeline prune (about 24 GWp to 21.7 GWp) deserve a haircut. The video's bear case "
        "recovers less than half the US and European equity.",
    ),
    (SECTION, "Holdco, margin, shares"),
    Lever(
        CONVERTS,
        USD_M,
        420,
        0,
        600,
        "Convertible notes when a quarter has no reported print. June 30, 2026 carrying value was "
        "$420M (up from $195M at December 31, 2025 after a Q1 issuance). Subtracted in the primary "
        "equity value because the share count used there is basic, not diluted. The diluted-price "
        "row adds this back so it is not counted twice.",
    ),
    Lever(
        HOLDCO_CASH,
        USD_M,
        42,
        0,
        200,
        "Unallocated cash at June 30, 2026 ($42M), the cash that is not already inside CSI Solar or "
        "Recurrent. Manufacturing cash ($1.34B) and Recurrent cash ($75M) stay inside those equity "
        "values and are not added here.",
    ),
    Lever(
        HOLDCO_CASH_CREDIT,
        PCT,
        100,
        0,
        100,
        "How much of holdco cash to count. 100% is the default; cut it if you think the cash is "
        "trapped.",
    ),
    Lever(
        GROSS_MARGIN,
        PCT,
        14.5,
        10,
        20,
        "Forward consolidated gross margin when no actual is typed. Q3 2026 guide is 13.5–15.5%; "
        "14.5% is the midpoint. Q2 printed 13.9%. Q1's 25.1% included a $93M IEEPA tariff refund and "
        "is not the run-rate. This builds gross profit for the P&L bridge. It is not an input to "
        "the sum of parts.",
        number_format="0.0",
    ),
    Lever(
        OPEX_Q,
        USD_M,
        220,
        160,
        320,
        "Forward quarterly operating expenses when no actual is typed. Q1 2026 was $198M and Q2 was "
        "$240M, the latter lifted by ramp and logistics. Not a valuation input.",
    ),
    Lever(
        SHARE_DRIP,
        PCT,
        0,
        0,
        3,
        "Quarterly growth in basic shares after the last print. Default 0: the share count has been "
        "roughly flat (67.2M in Q2 2025 to 67.9M in Q2 2026). Dilution that matters is the converts, "
        "handled on the diluted-price row rather than by inventing a share drip.",
        number_format="0.00",
    ),
    Lever(
        DILUTED_SHARES,
        SHARES,
        90,
        68,
        110,
        "Lucas's fully diluted share count, about 90M, used only on 'Implied price on diluted shares'. "
        "Basic shares in Q2 2026 were 67.9M. His $100/share is $9B / 90M. This row does not subtract "
        "the converts, because they are presumed to be in the 90M.",
        number_format="0.0",
    ),
]


def lever_rows() -> dict[str, int]:
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
    raise KeyError(label)


def lever_ref(label: str) -> str:
    rows = lever_rows()
    if label not in rows:
        raise KeyError(label)
    return f"{LEVERS_SHEET}!${VALUE_COL}${rows[label]}"


def grid() -> list[list[object]]:
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
    out: list[int] = []
    row = 1
    for item in LEVERS:
        row += 1
        if not isinstance(item, Lever):
            out.append(row)
    return out


def value_rows() -> list[int]:
    return sorted(lever_rows().values())


def date_rows() -> list[int]:
    return [lever_rows()[AS_OF_DATE]]


def percent_rows() -> list[int]:
    rows = lever_rows()
    return [rows[item.label] for item in LEVERS if isinstance(item, Lever) and item.units == PCT]
