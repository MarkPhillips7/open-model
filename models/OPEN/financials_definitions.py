"""Field definitions for the Financials Definitions tab (column B notes)."""

from __future__ import annotations

FINANCIALS_DEFINITIONS_SHEET = "Financials Definitions"

# Label → succinct note (Opendoor context + how the row is updated).
FIELD_NOTES: dict[str, str] = {
    'Week Ending': (
        "Saturday week-ending date for each column on Weekly Financials. Row 1 on both tabs; "
        "columns advance +7 days. Not a metric — defines the time spine."
    ),
    'Acquisition Contracts': (
        "Weekly count of signed home-purchase contracts (seller accepts Opendoor's offer). "
        "Entered manually on Weekly Financials when tracker/company data is available; "
        "Quarterly Financials sums the weeks when the quarterly cell is a formula. Sparse "
        "actuals; model row fills gaps."
    ),
    'Acquisition Contracts - Model': (
        "Forward projection of weekly contracts. Formula: Acquisition Contracts - no "
        "seasonality × Acquisition Seasonality Multiplier. Used when the actual row is blank."
    ),
    'Acquisition Seasonality Multiplier': (
        "Weekly adjustment from the Seasonality tab (monthly acquisition weights ÷ 1/12). "
        "Peaks Nov–Dec (spring/early-summer listing lag); trough May–Aug. Formula on every "
        "week column: INDEX(Seasonality!$B$2:$M$2, MONTH(date)) / (1/12)."
    ),
    'Acquisition Growth - Operational Improvements- weekly': (
        "Weekly % uplift on deseasonalized contracts (accountability / ops-improvement "
        "scenario). Manual inputs on early horizon columns; compounds on Acquisition Contracts "
        "- no seasonality."
    ),
    'Acquisition Contracts - no seasonality': (
        "Base weekly contract run-rate before seasonality. Manual seed + growth ramp; feeds "
        "Acquisition Contracts - Model."
    ),
    'Likelihood to Close': (
        "Share of signed contracts that ultimately close as Opendoor purchases (includes "
        "seller cancel and Opendoor walking away). ~78% in 2025, ~65% at Q2 2026 (AE), a "
        "mid-Q2 dip to ~63%, then ~66% from mid-July (not company-disclosed). Manual weekly "
        "inputs (B / AE and later waypoints); multiplied in Homes Purchased - Model."
    ),
    'Cash Now More Later %': (
        "Share of purchases that are Cash Now, More Later (2P / formerly Cash Plus). Opendoor "
        "still buys, holds, renovates, and resells — capital-light vs 1P, not off-inventory. "
        "Accountable contracts already include CNML. Formula: 0% through Q1 2025 → 19% last "
        "week of Q3 2025 → 35% last week of Q4 2025 → ~40% from Sep 2026 (Kaz 10 Sep 2026) → "
        "Transitions B36 terminal (default 50% by end-2027). Q2 2026 mix was not disclosed; "
        "1P vs 2P CM is not split. Overwrite any week. Feeds warehouse intensity, not the "
        "purchase → inventory unit path."
    ),
    'CNML Purchases - Model': (
        "Homes Purchased - Model × Cash Now More Later %. Informational split of modeled "
        "purchases onto the 2P product. These homes still add to inventory — do not subtract "
        "them from Homes in Inventory - Model."
    ),
    'Homes Purchased': (
        "Non-GAAP homes purchased (inventory adds). Quarterly actual from earnings supplement, "
        "spread to weeks (÷13, day-weighted at quarter boundaries) when Quarterly Financials "
        "has a hardcoded value; otherwise blank and model is used."
    ),
    'Homes Purchased - Model': (
        "Modeled purchases from lagged contracts. SUMPRODUCT over 9 contract-week lags × "
        "Likelihood to Close × Transitions close-timing weights (row 2). Prefers actual "
        "Acquisition Contracts when present, else Acquisition Contracts - Model."
    ),
    'Likelihood to List': (
        "Share of purchased homes that eventually get a public Opendoor listing (~75% early, "
        "higher later). Complement (1 − rate) feeds private sales. Manual weekly inputs; not "
        "on Transitions."
    ),
    'New Listings': (
        "Homes newly listed on Opendoor.com. Weekly manual actuals where available (tracker); "
        "Quarterly Financials may sum weeks. Sparse — model fills forward."
    ),
    'OPEN 1.0-2.0 Transition Completeness': (
        "Blend weight from pre-Kaz OPEN 1.0 ops to OPEN 2.0 (0% Feb 7 2026 → 100% Sep 4 2027). "
        "Formula from week-ending date; weights New Listings / Home Sales model rows between "
        "1.0 and 2.0 sub-models."
    ),
    'New Listings - Model': (
        "Blended listing forecast: Transition Completeness × 2.0 model + (1 − completeness) × "
        "1.0 model. Each sub-model lags Homes Purchased × Likelihood to List × Transitions "
        "listing-timing curve."
    ),
    'New Listings - 2.0 Model': (
        "OPEN 2.0 listing path: lagged purchases × Likelihood to List × Transitions row 4 "
        "(~21-week listing curve). No 1.0 backlog term."
    ),
    'New Listings - 1.0 Model': (
        "Pre-Kaz listing path: slower Transitions row 5 curve plus finite unlisted 1.0 backlog "
        "(Transitions B25, drained over first 8 weeks). Calibrated to ~45-day reno wait."
    ),
    'Average Sale Price (homes sold by OPEN)': (
        "Average resale price on Opendoor-sold homes (~$377.5K at Q2 2026). Quarterly actual "
        "spread to weeks (carries quarter value, day-weighted at boundaries); manual override "
        "on Weekly when needed. Drives revenue and ancillary CM."
    ),
    'Home Sales': (
        "Non-GAAP homes sold (listed + private). Quarterly earnings actual spread ÷13 "
        "(day-weighted). From Sep 2026, weekly sold counts are also published at "
        "accountable.opendoor.com (e.g. week ending 2026-09-05 = 223). Model row when blank."
    ),
    'Private Home Sales - Model': (
        "Never-listed completions: lagged purchases × (1 − Likelihood to List) × Transitions "
        "private-close curve (row 23, 9 weeks). Added to listed sales in Home Sales - Model."
    ),
    'Home Sales - Model': (
        "Blended sales forecast (1.0/2.0 via Transition Completeness). Each sub-model: lagged "
        "listings × sell-through curve + that week's private sales."
    ),
    'Home Sales - 2.0 Model': (
        "OPEN 2.0 sell-through: listing→sale curve on Transitions row 10, shaped to Open "
        "Tracker cohort sell-through (~73% by week 17 / ~120 days; ~86% by week 21; ~99.5% "
        "by week 25). The Q2 2026 “~91% over 120 days” stock figure was skewed by recent "
        "listings. Plus private sales. SUMPRODUCT uses all 25 weeks (`B10:Z10`)."
    ),
    'Home Sales - 1.0 Model': (
        "Pre-Kaz sell-through: ~39-week tail (~51% by week 17) on Transitions row 14, plus "
        "private sales. Slower DOM than 2.0."
    ),
    'Revenue': (
        "Total resale revenue (Non-GAAP). Quarterly actual from supplement, spread ÷13 "
        "(day-weighted). Kaz 9 Sep 2026 Q3 guide +10–15% YoY (~$915M × 1.125 ≈ $1.03B), down "
        "from the Q2 earnings ≥20% YoY guide. Weekly manual possible. Model when blank."
    ),
    'Revenue - Model': (
        "Home-sale revenue: Average Sale Price × Home Sales - Model, plus ODL Off-inventory "
        "Revenue - Model. Home Sales already blends 1.0/2.0 sell-through (closed units that "
        "week), so this does not re-lag cash/financed close or apply a second price-retention "
        "haircut."
    ),
    'Gross Profit': (
        "Revenue minus cost of revenue (Non-GAAP). Quarterly actual spread ÷13; not separately "
        "modeled on the weekly funnel — actuals only unless extended."
    ),
    'Contribution Profit': (
        "Revenue × Contribution Margin (Opendoor's key unit-economics profit measure). "
        "Quarterly actual spread ÷13 (day-weighted). Model row uses home-sale revenue × "
        "home-sale CM only (on-inventory attach included; off-inventory excluded)."
    ),
    'Doma Growth Multiplier': (
        "Stepwise multiplier for Doma refi profit growth (post-acquisition title/refi "
        "business). Manual weekly values from sheets/doma_manual_cells.py — not "
        "formula-driven. Informational; not in Contribution Profit - Model."
    ),
    'Doma Refi Profit - Model': (
        "Modeled weekly profit from Doma mortgage refi / title savings, compounded from column "
        "AR. Manual cell templates in repo; not added to Contribution Profit - Model."
    ),
    'ODL Off-inventory Loans - Model': (
        "Modeled Opendoor Home Loans originated on homes Opendoor does not hold. Formula: (US "
        "existing-home-sale TAM / 52) × TAM share. TAM is Transitions B33 (default 4,000,000 "
        "homes/year). Share smoothsteps 0% at Sep 6 2026 (GA) → Transitions B32 (default 2%) "
        "by Jan 1 2030. Independent of OPEN inventory sales and on-inventory attach. Not "
        "company-disclosed; 2% of national sales is a base-case digital-purchase share (~80k "
        "loans/year)."
    ),
    'ODL Off-inventory Revenue - Model': (
        "Off-inventory ODL loans × $7,500/loan (Transitions B34). Gross origination economics "
        "(gain-on-sale + MSR) on a ~$300k loan. Added to Revenue - Model. Not "
        "company-disclosed."
    ),
    'ODL Off-inventory Profit - Model': (
        "Off-inventory ODL loans × $3,000/loan (Transitions B31). Haircut vs $4,000 "
        "on-inventory. Added to Adjusted EBITDA - Model, not to contribution margin or "
        "Contribution Profit - Model, so reported-style home-sale CM stays clean."
    ),
    'Contribution Profit - Model': (
        "Formula: (Revenue - Model − ODL Off-inventory Revenue - Model) × Contribution Margin "
        "- Model. Home-sale revenue only, including on-inventory mortgage/title CM adds. "
        "Off-inventory origination profit is not in CP."
    ),
    'Contribution Margin': (
        "Contribution profit ÷ revenue (%). Quarterly actual, day-weighted blend across "
        "boundary weeks (no ÷13). Q2 2026 ~5.8%; Kaz 9 Sep 2026 Q3 guide 3.2–3.5% (was 4–4.5% "
        "at Q2 earnings); longer-term target still ~5–7%."
    ),
    'Contribution Margin - Model': (
        "Home-sale CM only: Core + on-inventory Mortgage + Title and Escrow + Seasonality "
        "Adjustments + Adjustments. Applied to home-sale revenue (Revenue - Model minus "
        "off-inventory origination). Off-inventory ODL is not in this stack."
    ),
    'Contribution Margin - Core': (
        "Base home-resale CM excluding ancillary attach. Anchored low single digits, then "
        "ramps via Contribution Margin Improvement - Core. Mix of manual anchors and "
        "prior-week + improvement formula."
    ),
    'Contribution Margin - Mortgage': (
        "CM add from Opendoor Home Loans attach on Opendoor resales: Open Mortgage Percent × "
        "$4,000/loan ÷ ASP (Transitions B29). Formula each week; ramps 0%→80% attach Jan "
        "2026–Oct 2028. Does not include loans on homes Opendoor does not hold — those are ODL "
        "Off-inventory Revenue / Profit - Model (revenue in Revenue - Model; profit in "
        "Adjusted EBITDA - Model)."
    ),
    'Contribution Margin - Title and Escrow': (
        "CM add from Doma title on purchase closes: Open Title Purchase Percent × $2,400/close "
        "÷ ASP (Transitions B30). Linear attach ramp to 100% by Jun 2027."
    ),
    'Contribution Margin - Seasonality Adjustments': (
        "Monthly CM seasonality offset from Seasonality tab (INDEX by month of week-ending "
        "date). Formula from column B onward."
    ),
    'Contribution Margin - Adjustments': (
        "Temporary negative CM offsets (older-cohort / inventory-clearing pressure). Late "
        "Aug–Sep 2026 deepened after Kaz 9 Sep 2026: price-to-clear into a weak housing tape "
        "rather than age inventory. Manual values; defaults to 0 on later columns."
    ),
    'Contribution Margin Improvement - Core': (
        "Weekly incremental step-up to Core CM. Manual anchors at key dates; otherwise prior "
        "week + small improvement (formula)."
    ),
    'Fixed Costs': (
        "Non-GAAP fixed operating costs. Quarterly actual spread ÷13. Management "
        "accountability theme: ~$35–37M/quarter path."
    ),
    'Fixed Costs - Model': (
        "Uses reported Fixed Costs when present; otherwise $35M/quarter ÷ 13 per week."
    ),
    'Adjusted Operating Expenses': "Fixed costs plus variable opex (Non-GAAP). Quarterly actual spread ÷13.",
    'Adjusted Operating Expenses - Model': (
        "Uses reported Adjusted Operating Expenses when present; otherwise Fixed Costs - "
        "Model + $1,269,300/week + $49.30 × Homes in Inventory - Model."
    ),
    'Stock Based Compensation': "SBC expense ($). Quarterly actual spread ÷13; Q3 2026 guide ~$110M/quarter.",
    'Stock Based Compensation - Model': (
        "Forward SBC: uses actual when present, else weekly run-rate derived from quarterly "
        "guidance / prior actuals (see weekly_sbc_model_formula)."
    ),
    'Basic Shares Outstanding': (
        "Reported basic share count. Quarterly EOP interpolation across weeks when quarterly "
        "hard value exists; manual weekly when reported."
    ),
    'Share Count Adjustment - Model': (
        "Weekly Δ shares from Shares tab event table (buybacks, convert dilution, warrant "
        "exercise) plus SBC share issuance. BYROW formula over Shares!A4:I20."
    ),
    'Basic Shares Outstanding - Model': (
        "Forward share count: actual if present, else prior week + Share Count Adjustment - "
        "Model."
    ),
    'Open Mortgage Percent': (
        "Assumed % of Opendoor resale buyers using Opendoor Home Loans (ODL). Four-phase "
        "smoothstep 0%→10% (Sep 6 2026, GA / out of beta) → 40% (Dec 20 2026) → 80% (Oct 1 "
        "2028). Not company-disclosed nationally; Colorado/Texas attach cited in Q2 2026 "
        "earnings. Off-inventory originations are a separate book (see ODL Off-inventory Loans "
        "- Model), not folded into this attach rate."
    ),
    'Open Title Purchase Percent': (
        "Assumed % of purchase closes using Doma title/escrow. Linear ramp 0%→100% (Jan "
        "2025–Jun 2027). Formula each week."
    ),
    'Homes in Inventory': (
        "Homes owned at week end (Non-GAAP). Quarterly actual spread with inventory-specific "
        "formula (delta/13 between quarter points); manual anchor in column B."
    ),
    'Homes in Inventory - Model': (
        "Roll-forward: prior inventory + purchases (actual or model) − sales (actual or "
        "model). Uses actual inventory when populated, else modeled path from anchor."
    ),
    'Warehouse Facility Capacity': (
        "Modeled operating ceiling for warehouse borrowing, in dollars. Seed $4.2B = senior "
        "revolving + senior term capacity (Q2 2026 10-Q). Overwrite B (or a later week) with "
        "$7.45B for headline capacity including uncommitted + mezz, or $1.5B to make ceiling = "
        "committed. Carry-forward weekly. Inventory Utilization % = warehouse debt / this "
        "amount."
    ),
    'Warehouse Committed Capacity': (
        "Amount lenders have contractually promised (Q2 2026 $1.5B: $400M senior revolvers + "
        "$725M senior term + $350M mezz). Q3 2025 10-Q cited $1.8B; step early weeks if you "
        "want that history. Carry-forward. Utilization of Committed > 100% means draws are at "
        "lender discretion — Q2 2026 already was (~$1.76B outstanding / $1.5B committed)."
    ),
    'Inventory Ceiling - Model': (
        "Homes at 100% of Warehouse Facility Capacity at this week's debt per home: facility "
        "capacity × Homes in Inventory - Model / (senior + mezz warehouse debt - Model). "
        "Supporting row for the utilization %; a 15–25k homes line on Opendoor Homes Funnel "
        "would squash the funnel."
    ),
    'Committed Inventory Ceiling - Model': (
        "Homes at 100% of Warehouse Committed Capacity: committed × inventory / warehouse "
        "debt. At Q2 ~4,650 homes vs 5,459 owned — already through the promised book."
    ),
    'Inventory Utilization %': (
        "Reported warehouse debt (senior + mezz actuals) / Warehouse Facility Capacity. Blank "
        "when actual debt is missing. Same ratio as homes / Inventory Ceiling. Intended for "
        "Opendoor Homes Inventory on Homes Charts (right axis, %)."
    ),
    'Inventory Utilization % - Model': "Modeled warehouse debt / Warehouse Facility Capacity. Forward path of the ceiling %.",
    'Inventory Utilization % of Committed': (
        "Reported warehouse debt / Warehouse Committed Capacity. Above 100% = beyond what "
        "lenders promised, still drawing at their discretion. Blank when actual debt is "
        "missing."
    ),
    'Inventory Utilization % of Committed - Model': (
        "Modeled warehouse debt / Warehouse Committed Capacity. The series that shows a "
        "committed-capacity breach as inventory scales."
    ),
    'Senior Interest Rate': (
        "Annual coupon on senior warehouse debt (revolvers + senior term), first-in-line "
        "loans. Q2 2026 seed 5.30% is the drawn-balance blend from the 10-Q facility table. "
        "Column B is the seed; later weeks carry forward so you can type a new rate in any "
        "week to step it."
    ),
    'Mezzanine Interest Rate': (
        "Annual coupon on mezzanine warehouse term debt (second-priority, behind senior). Q2 "
        "2026 seed 12.50% from the 10-Q. Carry-forward weekly; overwrite a week to change it."
    ),
    'Mezzanine Share of Warehouse Debt - Model': (
        "Share of modeled warehouse debt that is mezzanine (the rest is senior). Q2 2026 seed "
        "~19.8% ($350M mezz / $1.766B total). Lowering this refinances mezz into cheaper "
        "senior on the same inventory book and cuts Warehouse Interest Expense. Carry-forward "
        "weekly."
    ),
    'Senior Warehouse Debt': (
        "Quarter-end outstanding principal on senior revolvers + senior term (10-Q facility "
        "table, not carrying value). Interpolated across weeks like Homes in Inventory (Δ/13 "
        "between quarter points)."
    ),
    'Senior Warehouse Debt - Model': (
        "Uses actual senior outstanding when populated; else last week's modeled senior+mezz "
        "book scaled by Homes in Inventory - Model and by CNML capital intensity "
        "((1 − CNML%) + CNML% × Transitions B35 cash-at-close vs 1P), times (1 − mezzanine "
        "share). Rising CNML mix grows debt slower than home count. Cutting mezz share "
        "reallocates the same total into senior (a refi), not a cash paydown."
    ),
    'Mezzanine Warehouse Debt': (
        "Quarter-end outstanding principal on mezzanine term facilities (10-Q). Has sat at "
        "$350M from Q3 2025 through Q2 2026. Weekly interpolation same as senior."
    ),
    'Mezzanine Warehouse Debt - Model': (
        "Uses actual mezz when populated; else inventory- and CNML-intensity-scaled total × "
        "mezzanine share. The mix lever for using less (expensive) mezzanine."
    ),
    'Warehouse Interest Expense - Model': (
        "Gross weekly interest: senior debt × senior rate / 52 + mezz debt × mezz rate / 52. "
        "Not net of interest income. Feeds Net Interest Expense - Model."
    ),
    'Adjusted EBITDA': (
        "Contribution profit minus adjusted opex (Opendoor Non-GAAP EBITDA). Quarterly actual "
        "spread ÷13."
    ),
    'Adjusted EBITDA - Model': (
        "Formula: Contribution Profit - Model + ODL Off-inventory Profit - Model − Adjusted "
        "Operating Expenses - Model. Off-inventory mortgage profit sits here rather than in "
        "contribution margin so home-sale CM stays comparable to reported CM."
    ),
    'Net Interest Expense': (
        "Interest on inventory financing and debt, net (Non-GAAP). Quarterly actual spread "
        "÷13."
    ),
    'Net Interest Expense - Model': (
        "Uses spread Net Interest Expense when present; else Warehouse Interest Expense - "
        "Model minus a $9M/quarter interest-income offset (Q2 2026 warehouse gross ~$30M vs "
        "reported net $21M). Forward net interest now moves with the senior/mezz mix and "
        "inventory-scaled warehouse book."
    ),
    'Depreciation and Amortization': "D&A expense. Quarterly actual spread ÷13.",
    'Taxes': "Income tax provision (Non-GAAP adjusted). Quarterly actual spread ÷13.",
    'Adjusted Net Income': (
        "Adjusted EBITDA − net interest − D&A − taxes. Quarterly actual spread ÷13. SBC is not "
        "subtracted here (sits in GAAP bridge)."
    ),
    '(Loss) Gain on Extinguishment of Debt': (
        "One-time GAAP debt-refinancing gains/losses. Quarterly actual, week-ending quarter "
        "only (÷13, no cross-quarter blend) so Q4 charges don't leak into Q1 boundary weeks."
    ),
    'Interest Expense': "GAAP interest expense (below adjusted NI). Quarterly actual spread ÷13.",
    'Other Income - Net': "GAAP other income/expense net. Quarterly actual spread ÷13.",
    '(Loss) Gain on Extinguishment of Debt - Model': "Uses actual when present; else $0 run-rate (one-time items not projected forward).",
    'Interest Expense - Model': (
        "Uses actual when present; else small weekly run-rate (see "
        "INTEREST_EXPENSE_WEEKLY_RUN_RATE)."
    ),
    'Other Income - Net - Model': "Uses actual when present; else small weekly run-rate.",
    'Adjusted Net Income - Model': "Formula: Adjusted EBITDA - Model − Net Interest Expense - Model − D&A − Taxes.",
    'Inventory Valuation Adjustment - Current Period': (
        "GAAP write-down of inventory at fair value (current period). Quarterly actual, "
        "week-ending quarter only (÷13)."
    ),
    'Inventory Valuation Adjustment - Current Period - Model': "Uses actual when present; else weekly run-rate for ongoing valuation noise.",
    'Inventory Valuation Adjustment - Prior Periods': (
        "GAAP catch-up adjustments on prior-period inventory marks. Quarterly actual, "
        "week-ending quarter only."
    ),
    'Inventory Valuation Adjustment - Prior Periods - Model': "Uses actual when present; else weekly run-rate.",
    'Restructuring': "GAAP restructuring charges. Quarterly actual, week-ending quarter only.",
    'Restructuring - Model': "Uses actual when present; else $0 (not projected).",
    'CEO Make-Whole Provision': (
        "One-time CEO transition make-whole (GAAP). Quarterly actual, week-ending quarter "
        "only."
    ),
    'CEO Make-Whole Provision - Model': "Uses actual when present; else $0.",
    'Other GAAP Adjustments': "Residual GAAP reconciliation items. Quarterly actual, week-ending quarter only.",
    'Other GAAP Adjustments - Model': "Uses actual when present; else $0.",
    'Net Income (Loss) Attributable to Common Shareholders': (
        "GAAP net income to common. Quarterly actual spread ÷13. Full Adj→GAAP bridge in "
        "earnings supplement."
    ),
    'Net Income (Loss) Attributable to Common Shareholders - Model': (
        "Formula: Adjusted Net Income - Model + debt extinguishment − SBC − inventory "
        "valuation (current + prior) − restructuring − CEO make-whole − other GAAP "
        "adjustments."
    ),
    'Earnings per Share': "GAAP EPS (basic). Quarterly actual spread ÷13.",
    'Earnings per Share - Model': "Formula: GAAP NI - Model ÷ Basic Shares Outstanding - Model (blank if shares = 0).",
    'Price (Actual)': (
        "OPEN close on the last trading day on or before the week-ending date. Blank when the "
        "week-ending date is after TODAY() (forward projection columns). XLOOKUP from **Price "
        "History** (single GOOGLEFINANCE daily spill). Shown on Money Charts right axis."
    ),
    'Trailing Twelve Months Revenue': (
        "Rolling 12-month revenue for valuation. Uses reported TTM at quarter ends from "
        "earnings; before 52 weeks of history, day-weighted quarterly revenue proration; after "
        "52 weeks, sum of weekly Revenue (actual or model)."
    ),
    'Price @ P/S = 2': (
        "Implied share price if OPEN traded at 2× TTM revenue ÷ shares (actual or Basic Shares "
        "Outstanding - Model). Formula; scenario line on Money Charts."
    ),
    'Price @ P/S = 3': "Same as P/S = 2 at 3× multiple. Formula; scenario line on Money Charts.",
}
