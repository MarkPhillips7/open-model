"""Field definitions for the Financials Definitions tab (column B notes)."""

from __future__ import annotations

FINANCIALS_DEFINITIONS_SHEET = "Financials Definitions"

# Label → succinct note (Opendoor context + how the row is updated).
FIELD_NOTES: dict[str, str] = {
    "Week Ending": (
        "Saturday week-ending date for each column on Weekly Financials. "
        "Row 1 on both tabs; columns advance +7 days. Not a metric — defines the time spine."
    ),
    "Acquisition Contracts": (
        "Weekly count of signed home-purchase contracts (seller accepts Opendoor's offer). "
        "Entered manually on Weekly Financials when tracker/company data is available; "
        "Quarterly Financials sums the weeks when the quarterly cell is a formula. "
        "Sparse actuals; model row fills gaps."
    ),
    "Acquisition Contracts - Model": (
        "Forward projection of weekly contracts. Formula: "
        "Acquisition Contracts - no seasonality × Seasonality Multiplier. "
        "Used when the actual row is blank."
    ),
    "Seasonality Multiplier": (
        "Weekly adjustment from the Seasonality tab (monthly U.S. home-sales weights ÷ 1/12). "
        "Manual or formula-driven early columns; scales contract volume to mimic national seasonality."
    ),
    "Acquisition Growth - Operational Improvements- weekly": (
        "Weekly % uplift on deseasonalized contracts (accountability / ops-improvement scenario). "
        "Manual inputs on early horizon columns; compounds on Acquisition Contracts - no seasonality."
    ),
    "Acquisition Contracts - no seasonality": (
        "Base weekly contract run-rate before seasonality. "
        "Manual seed + growth ramp; feeds Acquisition Contracts - Model."
    ),
    "Likelihood to Close": (
        "Share of signed contracts that ultimately close as Opendoor purchases (includes seller cancel "
        "and Opendoor walking away). ~78% in 2025 tapering to ~67% by Q2 2026 (not company-disclosed). "
        "Manual weekly inputs (e.g. B8, AE8); multiplied in Homes Purchased - Model."
    ),
    "Homes Purchased": (
        "Non-GAAP homes purchased (inventory adds). Quarterly actual from earnings supplement, "
        "spread to weeks (÷13, day-weighted at quarter boundaries) when Quarterly Financials "
        "has a hardcoded value; otherwise blank and model is used."
    ),
    "Homes Purchased - Model": (
        "Modeled purchases from lagged contracts. SUMPRODUCT over 9 contract-week lags × "
        "Likelihood to Close × Transitions close-timing weights (row 2). "
        "Prefers actual Acquisition Contracts when present, else Acquisition Contracts - Model."
    ),
    "Likelihood to List": (
        "Share of purchased homes that eventually get a public Opendoor listing (~75% early, higher later). "
        "Complement (1 − rate) feeds private sales. Manual weekly inputs; not on Transitions."
    ),
    "New Listings": (
        "Homes newly listed on Opendoor.com. Weekly manual actuals where available (tracker); "
        "Quarterly Financials may sum weeks. Sparse — model fills forward."
    ),
    "OPEN 1.0-2.0 Transition Completeness": (
        "Blend weight from pre-Kaz OPEN 1.0 ops to OPEN 2.0 (0% Feb 2026 → 100% Jan 2027). "
        "Formula from week-ending date; weights New Listings / Home Sales / Revenue model rows "
        "between 1.0 and 2.0 sub-models."
    ),
    "New Listings - Model": (
        "Blended listing forecast: Transition Completeness × 2.0 model + (1 − completeness) × 1.0 model. "
        "Each sub-model lags Homes Purchased × Likelihood to List × Transitions listing-timing curve."
    ),
    "New Listings - 2.0 Model": (
        "OPEN 2.0 listing path: lagged purchases × Likelihood to List × Transitions row 4 "
        "(~21-week listing curve). No 1.0 backlog term."
    ),
    "New Listings - 1.0 Model": (
        "Pre-Kaz listing path: slower Transitions row 5 curve plus finite unlisted 1.0 backlog "
        "(Transitions B25, drained over first 8 weeks). Calibrated to ~45-day reno wait."
    ),
    "Average Sale Price (homes sold by OPEN)": (
        "Average resale price on Opendoor-sold homes (~$377.5K at Q2 2026). "
        "Quarterly actual spread to weeks (carries quarter value, day-weighted at boundaries); "
        "manual override on Weekly when needed. Drives revenue and ancillary CM."
    ),
    "Home Sales": (
        "Non-GAAP homes sold (listed + private). Quarterly earnings actual spread ÷13 "
        "(day-weighted); weekly manual stubs possible. Model row when blank."
    ),
    "Private Home Sales - Model": (
        "Never-listed completions: lagged purchases × (1 − Likelihood to List) × "
        "Transitions private-close curve (row 23, 9 weeks). Added to listed sales in Home Sales - Model."
    ),
    "Home Sales - Model": (
        "Blended sales forecast (1.0/2.0 via Transition Completeness). "
        "Each sub-model: lagged listings × sell-through curve + that week's private sales."
    ),
    "Home Sales - 2.0 Model": (
        "OPEN 2.0 sell-through: ~21-week listing→sale curve on Transitions row 10 "
        "(~91% by ~120 days per Q2 2026 commentary) plus private sales."
    ),
    "Home Sales - 1.0 Model": (
        "Pre-Kaz sell-through: ~39-week tail (~51% by week 17) on Transitions row 14, "
        "plus private sales. Slower DOM than 2.0."
    ),
    "Revenue": (
        "Total resale revenue (Non-GAAP). Quarterly actual from supplement, spread ÷13 "
        "(day-weighted). Weekly manual possible. Model when blank."
    ),
    "Revenue - Model": (
        "Blended revenue (1.0/2.0 via Transition Completeness). "
        "Listed path: listings × ASP × sell-through × price retention, split cash vs financed close lags. "
        "Private path: private sales × ASP."
    ),
    "Revenue - 2.0 Model": (
        "OPEN 2.0 revenue: listings lagged through sell-through and price-retention curves "
        "(Transitions rows 10–12) with cash/financed close timing; plus private sales × ASP."
    ),
    "Revenue - 1.0 Model": (
        "OPEN 1.0 revenue: longer sell-through and lower price retention (row 16); "
        "plus private sales × ASP."
    ),
    "Gross Profit": (
        "Revenue minus cost of revenue (Non-GAAP). Quarterly actual spread ÷13; "
        "not separately modeled on the weekly funnel — actuals only unless extended."
    ),
    "Contribution Profit": (
        "Revenue × Contribution Margin (Opendoor's key unit-economics profit measure). "
        "Quarterly actual spread ÷13 (day-weighted). Model row = Revenue - Model × CM - Model."
    ),
    "Doma Growth Multiplier": (
        "Stepwise multiplier for Doma refi profit growth (post-acquisition title/refi business). "
        "Manual weekly values from sheets/doma_manual_cells.py — not formula-driven. "
        "Informational; not in Contribution Profit - Model."
    ),
    "Doma Refi Profit - Model": (
        "Modeled weekly profit from Doma mortgage refi / title savings, compounded from column AR. "
        "Manual cell templates in repo; not added to Contribution Profit - Model."
    ),
    "Contribution Profit - Model": (
        "Formula: Revenue - Model × Contribution Margin - Model. "
        "Forward P&L starting point below gross profit."
    ),
    "Contribution Margin": (
        "Contribution profit ÷ revenue (%). Quarterly actual, day-weighted blend across "
        "boundary weeks (no ÷13). Q2 2026 ~5.8%; management guides 4–4.5% Q3 and 5–7% longer term."
    ),
    "Contribution Margin - Model": (
        "Sum of CM stack: Core + Mortgage + Title and Escrow + Seasonality Adjustments + Adjustments. "
        "Forward CM path matching earnings narrative."
    ),
    "Contribution Margin - Core": (
        "Base home-resale CM excluding ancillary attach. Anchored low single digits, "
        "then ramps via Contribution Margin Improvement - Core. Mix of manual anchors and "
        "prior-week + improvement formula."
    ),
    "Contribution Margin - Mortgage": (
        "CM add from Opendoor Home Loans attach: Open Mortgage Percent × $4,000/loan ÷ ASP "
        "(Transitions B29). Formula each week; ramps 0%→80% attach Jan 2026–Jan 2029."
    ),
    "Contribution Margin - Title and Escrow": (
        "CM add from Doma title on purchase closes: Open Title Purchase Percent × $2,400/close ÷ ASP "
        "(Transitions B30). Linear attach ramp to 100% by Jun 2027."
    ),
    "Contribution Margin - Seasonality Adjustments": (
        "Monthly CM seasonality offset from Seasonality tab (INDEX by month of week-ending date). "
        "Formula from column B onward."
    ),
    "Contribution Margin - Adjustments": (
        "Temporary negative CM offsets (older-cohort / inventory-clearing pressure per earnings). "
        "Manual values on early columns; defaults to 0 on later columns."
    ),
    "Contribution Margin Improvement - Core": (
        "Weekly incremental step-up to Core CM. Manual anchors at key dates; "
        "otherwise prior week + small improvement (formula)."
    ),
    "Fixed Costs": (
        "Non-GAAP fixed operating costs. Quarterly actual spread ÷13. "
        "Management accountability theme: ~$35–37M/quarter path."
    ),
    "Fixed Costs - Model": (
        "Steady forward run-rate: $35M/quarter ÷ 13 per week. "
        "Holds opex flat while volume scales."
    ),
    "Adjusted Operating Expenses": (
        "Fixed costs plus variable opex (Non-GAAP). Quarterly actual spread ÷13."
    ),
    "Adjusted Operating Expenses - Model": (
        "Formula: Fixed Costs - Model + ($15M/quarter ÷ 13) variable layer."
    ),
    "Stock Based Compensation": (
        "SBC expense ($). Quarterly actual spread ÷13; Q3 2026 guide ~$110M/quarter."
    ),
    "Stock Based Compensation - Model": (
        "Forward SBC: uses actual when present, else weekly run-rate derived from "
        "quarterly guidance / prior actuals (see weekly_sbc_model_formula)."
    ),
    "Basic Shares Outstanding": (
        "Reported basic share count. Quarterly EOP interpolation across weeks when "
        "quarterly hard value exists; manual weekly when reported."
    ),
    "Share Count Adjustment - Model": (
        "Weekly Δ shares from Shares tab event table (buybacks, convert dilution, warrant exercise) "
        "plus SBC share issuance. BYROW formula over Shares!A4:I20."
    ),
    "Basic Shares Outstanding - Model": (
        "Forward share count: actual if present, else prior week + Share Count Adjustment - Model."
    ),
    "Open Mortgage Percent": (
        "Assumed % of Opendoor resale buyers using Opendoor Home Loans (ODL). "
        "Four-phase smoothstep 0%→80% (Jan 2026–Jan 2029). Not company-disclosed nationally; "
        "Colorado/Texas attach cited in Q2 2026 earnings."
    ),
    "Open Title Purchase Percent": (
        "Assumed % of purchase closes using Doma title/escrow. "
        "Linear ramp 0%→100% (Jan 2025–Jun 2027). Formula each week."
    ),
    "Homes in Inventory": (
        "Homes owned at week end (Non-GAAP). Quarterly actual spread with inventory-specific "
        "formula (delta/13 between quarter points); manual anchor in column B."
    ),
    "Homes in Inventory - Model": (
        "Roll-forward: prior inventory + purchases (actual or model) − sales (actual or model). "
        "Uses actual inventory when populated, else modeled path from anchor."
    ),
    "Adjusted EBITDA": (
        "Contribution profit minus adjusted opex (Opendoor Non-GAAP EBITDA). "
        "Quarterly actual spread ÷13."
    ),
    "Adjusted EBITDA - Model": (
        "Formula: Contribution Profit - Model − Adjusted Operating Expenses - Model."
    ),
    "Net Interest Expense": (
        "Interest on inventory financing and debt, net (Non-GAAP). Quarterly actual spread ÷13."
    ),
    "Net Interest Expense - Model": (
        "Forward run-rate: $20M/quarter ÷ 13 per week."
    ),
    "Depreciation and Amortization": (
        "D&A expense. Quarterly actual spread ÷13."
    ),
    "Taxes": (
        "Income tax provision (Non-GAAP adjusted). Quarterly actual spread ÷13."
    ),
    "Adjusted Net Income": (
        "Adjusted EBITDA − net interest − D&A − taxes. Quarterly actual spread ÷13. "
        "SBC is not subtracted here (sits in GAAP bridge)."
    ),
    "(Loss) Gain on Extinguishment of Debt": (
        "One-time GAAP debt-refinancing gains/losses. Quarterly actual, week-ending quarter only "
        "(÷13, no cross-quarter blend) so Q4 charges don't leak into Q1 boundary weeks."
    ),
    "Interest Expense": (
        "GAAP interest expense (below adjusted NI). Quarterly actual spread ÷13."
    ),
    "Other Income - Net": (
        "GAAP other income/expense net. Quarterly actual spread ÷13."
    ),
    "(Loss) Gain on Extinguishment of Debt - Model": (
        "Uses actual when present; else $0 run-rate (one-time items not projected forward)."
    ),
    "Interest Expense - Model": (
        "Uses actual when present; else small weekly run-rate (see INTEREST_EXPENSE_WEEKLY_RUN_RATE)."
    ),
    "Other Income - Net - Model": (
        "Uses actual when present; else small weekly run-rate."
    ),
    "Adjusted Net Income - Model": (
        "Formula: Adjusted EBITDA - Model − Net Interest Expense - Model − D&A − Taxes."
    ),
    "Inventory Valuation Adjustment - Current Period": (
        "GAAP write-down of inventory at fair value (current period). Quarterly actual, "
        "week-ending quarter only (÷13)."
    ),
    "Inventory Valuation Adjustment - Current Period - Model": (
        "Uses actual when present; else weekly run-rate for ongoing valuation noise."
    ),
    "Inventory Valuation Adjustment - Prior Periods": (
        "GAAP catch-up adjustments on prior-period inventory marks. Quarterly actual, "
        "week-ending quarter only."
    ),
    "Inventory Valuation Adjustment - Prior Periods - Model": (
        "Uses actual when present; else weekly run-rate."
    ),
    "Restructuring": (
        "GAAP restructuring charges. Quarterly actual, week-ending quarter only."
    ),
    "Restructuring - Model": (
        "Uses actual when present; else $0 (not projected)."
    ),
    "CEO Make-Whole Provision": (
        "One-time CEO transition make-whole (GAAP). Quarterly actual, week-ending quarter only."
    ),
    "CEO Make-Whole Provision - Model": (
        "Uses actual when present; else $0."
    ),
    "Other GAAP Adjustments": (
        "Residual GAAP reconciliation items. Quarterly actual, week-ending quarter only."
    ),
    "Other GAAP Adjustments - Model": (
        "Uses actual when present; else $0."
    ),
    "Net Income (Loss) Attributable to Common Shareholders": (
        "GAAP net income to common. Quarterly actual spread ÷13. "
        "Full Adj→GAAP bridge in earnings supplement."
    ),
    "Net Income (Loss) Attributable to Common Shareholders - Model": (
        "Formula: Adjusted Net Income - Model + debt extinguishment − SBC − inventory valuation "
        "(current + prior) − restructuring − CEO make-whole − other GAAP adjustments."
    ),
    "Earnings per Share": (
        "GAAP EPS (basic). Quarterly actual spread ÷13."
    ),
    "Earnings per Share - Model": (
        "Formula: GAAP NI - Model ÷ Basic Shares Outstanding - Model (blank if shares = 0)."
    ),
    "Price (at Close)": (
        "OPEN stock price for the week (GOOGLEFINANCE, week-ending Saturday). "
        "Formula only; updates from market data. Shown on Money Charts right axis."
    ),
    "Trailing Twelve Months Revenue": (
        "Rolling 12-month revenue for valuation. Uses reported TTM at quarter ends from earnings; "
        "before 52 weeks of history, day-weighted quarterly revenue proration; "
        "after 52 weeks, sum of weekly Revenue (actual or model)."
    ),
    "Price @ P/S = 2": (
        "Implied share price if OPEN traded at 2× TTM revenue ÷ shares "
        "(actual or Basic Shares Outstanding - Model). Formula; scenario line on Money Charts."
    ),
    "Price @ P/S = 3": (
        "Same as P/S = 2 at 3× multiple. Formula; scenario line on Money Charts."
    ),
}
