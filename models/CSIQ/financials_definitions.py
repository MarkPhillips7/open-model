"""What every Quarterly Financials row means, where it came from, and what it assumes."""

from __future__ import annotations

from models.CSIQ import layout as L

DEFINITIONS_SHEET = "Financials Definitions"

HEADER = ["Field", "Definition, source, and the assumption behind it"]
COL_WIDTHS_PX: dict[int, int] = {0: 340, 1: 920}

_PREFER = (
    "Uses the reported actual in any quarter where one exists. The projection only "
    "takes over after the last print, so a miss stays visible."
)

INTRO: list[tuple[str, str]] = [
    (
        "How to read this sheet",
        "Column A matches Quarterly Financials. A bare label is a filing print. "
        "'- Plan' is a yellow trajectory you own. '- Model' is a formula and prefers "
        "the actual. Every scalar lives on Levers with a range and a source. "
        "This is not one business: CSI Solar (listed in Shanghai), CS PowerTech "
        "(US factories), and Recurrent Energy are valued separately.",
    ),
    (
        "What is not in the equity value",
        "Ex-US module and storage revenue is in the P&L so you can check guidance, "
        "and it is not given a second multiple — those earnings sit inside the CSI "
        "Solar stake. The $3.5B e-STORAGE backlog is not added on top of storage "
        "EBITDA. Early-stage pipeline gigawatts are not added on top of the "
        "BlackRock Recurrent mark. Manufacturing debt and Recurrent project debt "
        "are not subtracted again. Convertible notes are subtracted once, on the "
        "basic-share price, and added back on the diluted-share price.",
    ),
]

SECTION_NOTES: dict[str, str] = {
    L.SECTION_VOLUME: (
        "US versus ex-US is not disclosed as a quarterly split. The yellow rows are "
        "an allocation that hits the reported global total in 2026 Q1–Q2 and the "
        "US and Q3 guides. They are a plan, not a print."
    ),
    L.SECTION_REVENUE: "Product revenue from the earnings-release disaggregation, in $M.",
    L.SECTION_EARNINGS: (
        "US EBITDA is the Lucas Sacerdote base case, phased in. It is the only "
        "manufacturing earnings that enter the sum of parts."
    ),
    L.SECTION_RECURRENT: (
        "Three drivers the company describes: asset sales, power services (O&M), "
        "and electricity from the operating fleet. Lumpy. Not valued on a multiple "
        "of this P&L."
    ),
    L.SECTION_CONSOLIDATED: "GAAP consolidated figures. The forward P&L is a bridge, not the valuation.",
    L.SECTION_CASH: "Reported cash and debt. Project draws dominate, so cash is not projected.",
    L.SECTION_SHARES: "Basic weighted-average shares, and the live price from Price History.",
    L.SECTION_VALUATION: (
        "Sum of parts. Floor (CSI Solar stake + Recurrent stake − holdco net debt) "
        "plus US manufacturing equity. Present price discounts only the US piece."
    ),
}

DEFINITIONS: dict[str, str] = {
    L.YEAR: "Calendar year. Canadian Solar's fiscal year is the calendar year.",
    L.QUARTER: "Calendar quarter, 1 to 4.",
    L.QUARTER_ENDING: "Last calendar day of the quarter. Drives the stock-price lookup and the discount clock.",
    L.AS_OF_DATE: "Valuation date, from the Levers tab.",
    L.YEARS_FROM_PRESENT: "Years from the As of date to this quarter-end, on a 365-day year. Negative for quarters already over.",
    L.US_MODULE_PLAN: (
        "EDITABLE. US module GW recognized as revenue. 2026 sums to 6.7 GW, inside the "
        "reiterated 6.5–7.0 GW US guide, and is back-loaded because management said each "
        "quarter of 2026 would be larger. From 2027 the plan is 1.5 GW/quarter (6 GW/year): "
        "the cell-constrained base case in the 2026-04-28 thesis, not the 10 GW Texas module "
        "nameplate. 2025 is a sketch, not a disclosure. Raise 2027+ toward 2.5 GW/quarter "
        "for the 10 GW bull case."
    ),
    L.EXUS_MODULE_PLAN: (
        "EDITABLE. Module GW outside the US, mostly CSI Solar. 2026 Q1–Q2 are set so this "
        "plus the US plan equals the reported global total (2.5 GW and 3.1 GW). Held near "
        "1.5–1.7 GW/quarter after that: management is managing volume against feedstock "
        "costs, not rebuilding a 25 GW run-rate. Does not get its own valuation."
    ),
    L.MODULE_GW_ACTUAL: (
        "Module GW recognized as revenue, from the earnings release. 2.5 GW in 2026 Q1 "
        "(above 2.2–2.4 guidance) and 3.1 GW in 2026 Q2. Blank where the release did not "
        "state the number. The US/ex-US split is not in this row."
    ),
    L.MODULE_GW_MODEL: (
        "US plan × US volume achieved, plus ex-US plan × ex-US volume achieved. " + _PREFER
    ),
    L.US_STORAGE_PLAN: (
        "EDITABLE. US storage GWh. 2026 sums to 5.0, the midpoint of the reiterated "
        "4.5–5.5 GWh US guide, back-loaded. From 2027, 1.25 GWh/quarter, which is the "
        "thesis base case of 5 GWh/year. The bull case of 20 GWh is an edit to this row, "
        "not a hidden assumption. 2025 is a sketch."
    ),
    L.EXUS_STORAGE_PLAN: (
        "EDITABLE. Storage GWh outside the US. 2026 Q1–Q2 complete the reported global "
        "total (2.1 and 3.7 GWh). 2026 Q3 is the rest of the 3.6 GWh midpoint of "
        "3.4–3.8 guidance. Revenue bridge only."
    ),
    L.STORAGE_GWH_ACTUAL: (
        "Storage GWh recognized as revenue. 2.1 GWh in 2026 Q1 (guide was 1.7–1.9) and "
        "3.7 GWh in 2026 Q2 (guide was 2.8–3.2). On the Q2 call, revenue was recognized on 3.3 GWh; 471 MWh of the 3.7 was internal "
        "and that revenue is deferred. Blank elsewhere."
    ),
    L.STORAGE_GWH_MODEL: "US plan plus ex-US plan, each times its achieved lever. " + _PREFER,
    L.US_MODULE_PHASE: (
        "EDITABLE. Percent of the steady US module cash margin earned this quarter. "
        "Jeffersonville Phase I (2.1 GWp of HJT cells) opened in July 2026, and Colin Parkin "
        "said ramp costs weigh on profitability for the rest of 2026, so 2026 stays near "
        "half. Hits 100% in 2027 Q4, which is the base-case column. Set the whole row to "
        "100 if you want the steady margin immediately."
    ),
    L.US_STORAGE_PHASE: (
        "EDITABLE. Percent of the steady 15% US storage margin earned this quarter. "
        "Full from 2027. 2026 is partial because Parkin said storage competition is "
        "intensifying and because the $200/kWh price is a US price, not the ~$115/kWh "
        "blended print."
    ),
    L.MODULE_REV_ACTUAL: (
        "Solar module revenue, $M, from the product table. Q2 2026 was $589M, down from "
        "$1,022M in Q2 2025. Q1 2025 is first-half 2025 minus Q2 2025."
    ),
    L.MODULE_REV_MODEL: (
        "US GW × US ASP × 1,000 plus ex-US GW × ex-US ASP × 1,000, in $M. The ASPs are "
        "revenue-bridge prices, not the valuation margin. " + _PREFER
    ),
    L.STORAGE_REV_ACTUAL: (
        "Battery energy storage revenue, $M. Q2 2026 was $426M on 3.7 GWh. Q1 2025 is "
        "first-half minus Q2."
    ),
    L.STORAGE_REV_MODEL: (
        "US GWh × US ASP plus ex-US GWh × ex-US ASP. GWh times $/kWh is $M. " + _PREFER
    ),
    L.OTHER_MFG_REV_ACTUAL: (
        "Solar system kits plus EPC and others, $M. Q2 2026 was $79M. Q1 2025 is "
        "first-half minus Q2."
    ),
    L.OTHER_MFG_REV_MODEL: "The 'other manufacturing revenue' lever when no actual is typed. " + _PREFER,
    L.MFG_REV_ACTUAL: (
        "Manufacturing segment net revenue from the segment note. Q2 2026 was $1,098M "
        "(gross profit $131M, operating loss $49M). Q1 2026 is first-half segment revenue "
        "minus Q2. Slightly different from the product-table subtotal because of eliminations."
    ),
    L.MFG_REV_MODEL: "Module + storage + other revenue. " + _PREFER,
    L.US_MODULE_EBITDA: (
        "Quarterly US module cash EBITDA. Gross profit is US GW × 7.5¢/W × phase-in × "
        "margin achieved, times 1,000 to land in $M. Lease is $250M/year times the share "
        "of a 6 GW year this quarter's volume represents, capped at a full quarter. "
        "At 1.5 GW, 100% phase-in, and default levers this is $50M in the quarter, "
        "$200M annualized — Lucas's base case — before the 75.1% ownership haircut. "
        "Can print negative while the lease is ahead of the ramp. That negative is shown "
        "here and floored at zero only when it becomes equity value."
    ),
    L.US_STORAGE_EBITDA: (
        "Quarterly US storage EBITDA: GWh × $200/kWh × 15% × phase-in × margin achieved. "
        "At 1.25 GWh and full phase-in this is $37.5M in the quarter, $150M annualized, "
        "which is the thesis base case before ownership."
    ),
    L.MFG_GP_ACTUAL: (
        "Manufacturing segment gross profit. Q2 2026 was $131M (about 12% margin). "
        "Q1 2026 was $276M and includes the IEEPA tariff refund that also inflated "
        "consolidated margin. Q1 is first-half minus Q2."
    ),
    L.MFG_GM_ACTUAL: (
        "Manufacturing gross margin, percent, if you type it. Not back-solved here, "
        "because Q1's margin is a refund, not a run-rate."
    ),
    L.MFG_OI_ACTUAL: (
        "Manufacturing segment operating income. Q1 2026 profit $127M, Q2 2026 loss $49M. "
        "Q1 is first-half segment operating income minus Q2."
    ),
    L.ASSET_SALES_PLAN: (
        "EDITABLE. Recurrent project and operating-asset sales, $M. 2026 Q3 steps up to "
        "$180M because management said sales deferred from Q2 would close in the second "
        "half and make Q3 sequentially stronger. After 2026 the row is a flat "
        "$70M/quarter recycle-capital pace, not guidance."
    ),
    L.ASSET_SALES_ACTUAL: (
        "Solar and storage asset-sale revenue. Q2 2026 was $61M, Q1 2026 was $89M "
        "(Fort Duncan). Q1 2025 is first-half minus Q2."
    ),
    L.ASSET_SALES_MODEL: "The plan, unless an actual is typed. " + _PREFER,
    L.POWER_PLAN: (
        "EDITABLE. O&M / power-services revenue, $M. The company has about 15 GW under "
        "long-term O&M contracts. Recent quarters are about $20M. This row drifts toward "
        "$24M. It is a stable annuity, not the swing factor."
    ),
    L.POWER_ACTUAL: "Power services revenue. About $20M a quarter through the first half of 2026.",
    L.POWER_MODEL: "The plan, unless an actual is typed. " + _PREFER,
    L.ELECTRICITY_PLAN: (
        "EDITABLE. Electricity, storage operations, and similar revenue from the fleet "
        "Recurrent keeps. Q2 2026 rose to $33M after a utility-scale project in Spain "
        "reached COD. The path keeps rising slowly as more assets are held rather than sold. "
        "That is the strategy Ismael Guerrero described in May 2026: own and operate more, "
        "sell selectively to delever."
    ),
    L.ELECTRICITY_ACTUAL: "Electricity and storage-operations revenue from the product table.",
    L.ELECTRICITY_MODEL: "The plan, unless an actual is typed. " + _PREFER,
    L.RECURRENT_REV_ACTUAL: (
        "Recurrent Energy segment net revenue. Q2 2026 was $117M and was light because "
        "project sales slipped to the second half. Gross profit was $36M and the operating "
        "loss was $19M, including a Latin America impairment. Q1 is first-half minus Q2."
    ),
    L.RECURRENT_REV_MODEL: "Asset sales + power services + electricity. Ignores a few million of eliminations. " + _PREFER,
    L.RECURRENT_GP_ACTUAL: "Recurrent segment gross profit. Q1 2026 was negative; Q2 was $36M. Q1 is first-half minus Q2.",
    L.RECURRENT_OI_ACTUAL: "Recurrent segment operating income. A loss in both quarters of 2026. Not the basis of the valuation.",
    L.TOTAL_REV_ACTUAL: (
        "Consolidated net revenue. Q2 2026 was $1,208M, the top of $1.0–1.2B guidance, "
        "down 29% year over year. Q1 2025 is first-half 2025 revenue minus Q2 2025."
    ),
    L.TOTAL_REV_MODEL: (
        "Manufacturing revenue plus Recurrent revenue. " + _PREFER + " "
        "2026 Q3 should land near the $1.3–1.5B guide if the default prices and the "
        "Q3 volume plans hold. If it doesn't, the miss is the point."
    ),
    L.GP_ACTUAL: (
        "Consolidated gross profit. Q2 2026 was $168M. Q1 2026 was $271M including a "
        "$93M tariff refund. Q4 2025's $124M is the rounded figure from the Q1 release."
    ),
    L.GM_ACTUAL: (
        "Consolidated gross margin, percent. Q2 2026 was 13.9% (guide 13–15). Q1 2026 "
        "was 25.1% because of the tariff refund. Q2 2025 was 29.8% and included a "
        "sales-type lease profit release. None of those peaks is the run-rate."
    ),
    L.GP_MODEL: "Total revenue × the gross-margin lever (default 14.5%, the Q3 guide midpoint). " + _PREFER,
    L.OPEX_ACTUAL: (
        "Consolidated operating expenses. Q2 2026 was $240M, up from $198M in Q1 on ramp "
        "and logistics costs, and 19.8% of revenue. Q4 2025's $188M is the rounded figure "
        "from the Q1 release."
    ),
    L.OPEX_MODEL: "The quarterly opex lever, default $220M. " + _PREFER,
    L.OI_ACTUAL: (
        "Consolidated operating income. Q2 2026 was a $71M loss. Q1 2026 was a $73M profit, "
        "mostly the tariff refund. Q1 2025 is that quarter's gross profit minus opex."
    ),
    L.OI_MODEL: "Gross profit minus operating expenses. " + _PREFER + " Not used in the sum of parts.",
    L.NI_ACTUAL: (
        "Net income attributable to Canadian Solar, not to non-controlling interests. "
        "Q2 2026 was a $77M loss ($1.40 a share). Q2 2025 was a $7M profit but still a "
        "loss per share, because preferred dividends and converts sit in the per-share math. "
        "Q4 2025's $86M loss is the rounded figure. Not projected: interest, FX, tax, and "
        "the minority share move too much to invent a quarterly path."
    ),
    L.EPS_ACTUAL: (
        "Basic EPS as reported. Q2 2026 was −$1.40 on 67.9M shares. Do not divide net income "
        "by the share count and expect to match EPS — the release says per-share results "
        "include convert dilution when it applies and paid-in-kind dividends on Recurrent's "
        "redeemable preferred shares."
    ),
    L.CASH_ACTUAL: (
        "Cash and equivalents. $1,461M at June 30, 2026 and $1,370M at December 31, 2025. "
        "Manufacturing held $1,344M of the June cash; Recurrent held $75M; $42M was unallocated."
    ),
    L.RESTRICTED_ACTUAL: (
        "Current plus non-current restricted cash. $389M at June 30, 2026 and $570M at "
        "December 31, 2025. Mostly project cash, not holdco cash."
    ),
    L.CASH_RESTRICTED_ACTUAL: (
        "Cash, equivalents, and restricted cash, the total the cash-flow statement rolls. "
        "$1,850M at June 30, 2026, down from $2,264M a year earlier. The company describes "
        "the cash position as about $1.9B."
    ),
    L.OCF_ACTUAL: (
        "Operating cash flow, signed. Q2 2026 used $181M and Q1 used $209M, both on working "
        "capital (inventories in Q1). Q1 and Q4 2025 are the rounded figures from the releases "
        "(−$264M and −$65M). Not projected."
    ),
    L.CAPEX_ACTUAL: (
        "Cash paid for property, plant, and equipment, as a positive spend. About $172M in "
        "each of the first two quarters of 2026. The Indiana and Texas buildout is in here. "
        "Not projected; the US lease lever is the thesis's stand-in for the ongoing cost of "
        "those factories."
    ),
    L.DEBT_ACTUAL: (
        "Total debt including financing liabilities, the rounded total from the release: "
        "$6.5B at December 31, 2025, $6.8B at March 31, 2026, $7.1B at June 30, 2026. "
        "Of the June figure, about $4.1B is Recurrent, $2.5B manufacturing, $0.4B converts. "
        "Not subtracted in full in the valuation — see Holdco net debt."
    ),
    L.CONVERTS_ACTUAL: (
        "Convertible notes. $195M at December 31, 2025 and $420M at June 30, 2026. "
        "Q1 2026 is left blank: the company said 'about $0.4B' and disclosed $223M of "
        "issuance proceeds, which is not the same as a quarter-end carrying value."
    ),
    L.CONVERTS_MODEL: (
        "The actual when one exists. After the As of date, the convertible-notes lever "
        "(default $420M), so a refinance is one cell. Before the first print, blank, "
        "so 2025 is not loaded with the 2026 balance. " + _PREFER
    ),
    L.NONRECOURSE_ACTUAL: (
        "Recurrent non-recourse project debt. $2.3B at March 31, 2026 and $2.62B at "
        "June 30, 2026. Stays inside the Recurrent equity mark. Not subtracted again."
    ),
    L.SHARES_ACTUAL: (
        "Basic weighted-average shares, millions. 67.167M in Q2 2025, 67.818M in Q1 2026, "
        "67.908M in Q2 2026. Not the 90M fully diluted count Lucas used."
    ),
    L.SHARES_MODEL: (
        "The actual, otherwise the prior quarter grown by the share-drip lever (default 0). "
        "Blank until the first print. " + _PREFER
    ),
    L.STOCK_PRICE: (
        "Last daily CSIQ close on or before quarter-end, from the Price History spill. "
        "Blank if the quarter has not ended yet."
    ),
    L.MARKET_CAP: "Stock price times basic shares, in $M. This is what the model price is compared with.",
    L.CSI_STAKE: (
        "CSI Solar market cap × CSIQ ownership × (1 − holdco discount) × value achieved. "
        "Defaults: $7,000M × 64% × 70% = about $3,136M. Lucas called this $3.6B; the gap is "
        "rounding in the video ($7B and 30% do not multiply to $3.6B exactly). Update the "
        "market-cap lever — the $7B is the April 2026 video, not a live Shanghai quote. "
        "This is equity value. Do not subtract CSI Solar debt again."
    ),
    L.CSI_CROSSCHECK: (
        "NOT in the equity total. (Normalized EBITDA × multiple − net debt) × ownership. "
        "Defaults: ($825M × 8 − $1,400M) × 64% = about $3,328M, close to the listed stake. "
        "If you update the Shanghai price and this row is far away, the earnings anchor or "
        "the quote is stale."
    ),
    L.RECURRENT_STAKE: (
        "Recurrent equity value × CSIQ ownership × achieved. Defaults: $2,500M × 80% = $2,000M, "
        "the BlackRock early-2024 post-money mark. Debt inside Recurrent is already net of "
        "that equity price. Q2 2026 operations do not, by themselves, rewrite the mark — "
        "the achieved lever is where that scepticism goes."
    ),
    L.US_MODULE_EQUITY: (
        "MAX(0, annualized US module EBITDA) × the module multiple × CSIQ's direct "
        "PowerTech stake × US value achieved. Annualized means this quarter × 4, so a "
        "half-ramped quarter is not credited with the steady state. Default ownership is "
        "75.1%, not 100%, so the 24.9% CSI Solar owns is not counted twice. At the 2027 Q4 "
        "plan this is about $1.2B, versus $1.6B if you set ownership to 100%."
    ),
    L.US_STORAGE_EQUITY: (
        "MAX(0, annualized US storage EBITDA × multiple − storage net debt) × PowerTech "
        "ownership × US value achieved. Default debt is zero, matching Lucas's base case. "
        "At full phase-in and 75.1% ownership this is about $1.35B, versus $1.8B at 100%."
    ),
    L.HOLDCO_NET_DEBT: (
        "Convertible notes minus holdco cash × the credit percent. The only debt subtracted "
        "in the equity value. Manufacturing borrowings and Recurrent project debt are left "
        "inside those stakes."
    ),
    L.FLOOR_EQUITY: (
        "CSI Solar stake + Recurrent stake − holdco net debt. The part of the value that "
        "does not depend on the US ramp. This is what gets no time discount."
    ),
    L.EQUITY_VALUE: "Floor plus US module equity plus US storage equity. Undiscounted.",
    L.IMPLIED_PRICE: (
        "Equity value divided by basic shares. This is the primary price. It treats converts "
        "as debt (they were subtracted) and does not use the 90M diluted count."
    ),
    L.DILUTED_PRICE: (
        "Same equity, converts added back, divided by the fully diluted shares lever "
        "(default 90M). This is the Lucas share-count convention. His $100 was $9B / 90M "
        "at 100% US ownership and full steady-state margins. This row will be lower than "
        "that until the phase-in is done, and lower still at 75.1% ownership."
    ),
    L.PRESENT_PRICE: (
        "Floor, plus the US equity values discounted at the discount-rate lever for quarters "
        "that have not ended. Quarters already over are not discounted. Set the discount "
        "rate to 0 to mark the whole ramp as present value, which is the video's stance "
        "that the base case is 'worth that today.'"
    ),
}


def _check() -> None:
    labels = {label for label, _units in L.ROWS if label and label not in L.SECTION_LABELS}
    missing = labels - set(DEFINITIONS)
    extra = set(DEFINITIONS) - labels
    if missing or extra:
        raise ValueError(f"definition mismatch missing={sorted(missing)} extra={sorted(extra)}")


_check()
