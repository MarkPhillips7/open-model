# Opendoor (OPEN)

Personal research workbook and Python tooling for modeling **Opendoor (OPEN)** financial results and projections—volume funnel, inventory, revenue, contribution margin, and cost structure—to better understand present results, forward estimates, and an investment thesis.

This is the **OPEN** model pack in [open-model](../../README.md). The live model is the Google Sheet **[Opendoor Model](https://docs.google.com/spreadsheets/d/1BhauTzGc9Nyt1J9gQl3NdCnpSSKCpSLbY9H7p5Obvc4)**. Shared OAuth and CLI tooling live at the repo root; issuer-specific formulas and scripts live in this folder.

Sources and citations: **[RESOURCES.md](RESOURCES.md)**. Spreadsheet edits made by agents are logged in **[CHANGELOG.md](CHANGELOG.md)**.

> Not investment advice. The model mixes company-reported Non-GAAP metrics, management guidance, and explicit guesses where Opendoor does not disclose detail.

---

## Goals

- Reconstruct a **weekly operating model** of Opendoor’s home funnel: acquisition contracts → purchases → listings → sales → revenue.
- Separate **reported / stubbed actuals** from **forward model** rows so gaps and surprises are visible.
- Encode **timing and attrition** (likelihood to close by contract week, private closings, days on market, financed vs cash close) as adjustable assumptions.
- Project **contribution margin**, fixed costs, and inventory path under seasonal and growth scenarios.
- Use charts to compare actual vs modeled homes and money over time.

---

## Workbook map

| Tab | Role |
| --- | --- |
| **Welcome** | Starting point for visitors: disclaimer, goals, resources, tab guide with links, and feedback invitation. Canonical copy in `welcome.py`; refresh with `scripts/setup_welcome.py`. |
| **Weekly Financials** | Main time series (week-ending columns). Actuals + model rows for contracts, **likelihood to close**, purchases, listings, **private sales**, listed+private home sales, ASP, revenue, CM stack, opex, SBC, **GAAP net income / EPS**, inventory. Weekly-reported actuals are entered here; quarterly-reported actuals are spread from **Quarterly Financials**. |
| **Quarterly Financials** | Same row layout as Weekly Financials, one column per quarter. Enter quarterly earnings actuals here; they spread across weeks (`÷13`, day-weighted at quarter boundaries). Rows like Acquisition Contracts **sum from weekly** when no quarterly report exists. |
| **Financials Definitions** | Reference tab: column A mirrors Weekly Financials row labels; column B documents each field (Opendoor context, manual vs formula sourcing). Canonical text in `financials_definitions.py`; pull after UI edits with `scripts/pull_financials_definitions_from_sheet.py`. |
| **Transitions** | Lag / probability tables that turn **closing** contracts into purchases (timing only), purchases into listings **or private sales**, and listings into sales (plus private %, **unlisted 1.0 backlog**, cash %, price retention, close timing). |
| **Shares** | Share-count **event table** (buybacks, warrant exercise, convert dilution scenarios) and SBC $/share assumption. Drives **Share Count Adjustment - Model** on Weekly Financials. |
| **Seasonality** | Monthly acquisition seasonality weights; drives the weekly **Acquisition Seasonality Multiplier**. |
| **Price History** | One `GOOGLEFINANCE` spill of OPEN daily OHLCV; **Price (Actual)** on Weekly Financials XLOOKUPs the close column by week-ending date. |
| **Homes Charts** | Two line charts: **Opendoor Homes Funnel** (contracts, purchases, listings, sales) and **Opendoor Homes Inventory** (inventory plus utilization %). |
| **Money Charts** | Two line charts: **Opendoor Weekly Revenue and Shares** (revenue + basic shares) and **Opendoor Weekly Profit and Price** (contribution profit, adjusted/GAAP net income). |

---

## Modeling approach

### Weekly spine

- Columns are **week ending** dates (`Week Ending`, then `+7` across the horizon).
- **Quarterly-reported actuals** (homes purchased, home sales, revenue, opex, SBC, inventory, etc.) live on **Quarterly Financials** as quarter totals. **Weekly Financials** spreads them (`quarterly ÷ 13`, day-weighted at quarter boundaries when a week spans two quarters) when the quarterly cell is a hardcoded value. **One-time GAAP items** (debt extinguishment, inventory valuation timing, restructuring, CEO make-whole) use the **week-ending quarter only**—no cross-quarter blend—so a Q4 debt charge does not leak into Q1 boundary weeks.
- **Weekly-reported actuals** (e.g. acquisition contracts, sparse new-listing counts) are entered on **Weekly Financials**. **Quarterly Financials** sums the matching weeks when the quarterly cell is a formula.
- **Model** rows stay on **Weekly Financials**; formulas fall back between actual and model rows as before.

### Funnel (actuals vs model)

1. **Acquisition contracts** — Observed weekly contracts where available; model = deseasonalized base × **Acquisition Seasonality Multiplier** × weekly operational growth.
2. **Homes purchased** — Model = lagged contracts × that cohort’s **Likelihood to Close** × **Transitions** close-timing weights over ~9 weeks (`SUMPRODUCT` / `MAP` lag). Timing weights sum to 100% of closers; attrition lives on the weekly L2C row.
3. **New listings** — Model = lagged **homes purchased** × **Likelihood to List** × **Transitions** listing-timing weights (row 4 sums to **100% of ultimate listers**). For the first **8 weeks** of the horizon only, add a finite **unlisted 1.0 backlog** (`Transitions!B25`, default 450) draining on row 27. Never-listed share is `(1 − Likelihood to List)` on the weekly row (not a fixed Transitions %).
4. **Home sales** — Model = lagged listings × **Percent Sold by Listing Week** (**25** weeks on 2.0 / **39** on 1.0) **+** private sales. Private sales = lagged purchases × `(1 − Likelihood to List)` on **Percent of Private Completions Sold by Week** (`Transitions!B23:J23`; 9-week purchase→close curve).
5. **Revenue** — Listed path = listings × ASP × sell-through × **price retention**, split by cash vs financed close lags. Private path = that week’s private sales × ASP (close already in the private curve; no DOM decay).
6. **Inventory** — Model rolls forward: prior inventory + **homes purchased** − sales (preferring actuals when present).

### Profitability stack

- **Contribution Margin - Model** = Core + Mortgage + Title/Escrow + Seasonality + Adjustments. Mortgage/title CM rows = attach % × $/unit ÷ ASP (see **Transitions** ancillary assumptions). On-inventory ODL only — applied to home-sale revenue, not off-inventory origination.
- **ODL Off-inventory Revenue / Profit - Model** — loans on homes Opendoor does not hold: (US home-sale TAM / 52) × TAM share, then × $7,500 revenue / $3,000 profit (Transitions B31–B34). Revenue is added to **Revenue - Model**; profit is added to **Adjusted EBITDA - Model**, not to CM or Contribution Profit.
- **Doma Refi Profit - Model** / **Doma Growth Multiplier** — manual weekly rows (stepwise multipliers + compounded profit from **AR**; cells in `doma_manual_cells.py`). Not added to **Contribution Profit - Model**.
- Core CM starts near low single digits and can step up via **Contribution Margin Improvement - Core**.
- Near-term negative adjustments reflect older-cohort / inventory-clearing pressure called out in earnings commentary.
- **Fixed Costs - Model** uses a steady quarterly run-rate (management accountability theme).
- **Adjusted EBITDA - Model** = Contribution Profit + ODL Off-inventory Profit − Adjusted Operating Expenses.
- **Adjusted Net Income - Model** = Adjusted EBITDA − Net Interest − D&A − Taxes (SBC is **not** subtracted again; it sits above EBITDA in the company reconciliation).
- **Net Interest Expense - Model** uses reported net interest when spread; otherwise senior warehouse debt × senior rate / 52 + mezzanine debt × mezzanine rate / 52, minus a $9M/quarter interest-income offset. Lowering **Mezzanine Share of Warehouse Debt - Model** refinances expensive mezz into cheaper senior.
- **Net Income (Loss) Attributable to Common Shareholders - Model** = Adjusted Net Income + debt extinguishment − SBC − inventory valuation (current + prior periods) − restructuring − CEO make-whole − other GAAP adjustments (matches Opendoor’s Adj ↔ GAAP reconciliation in the earnings supplement).
- **Earnings per Share - Model** = GAAP net income ÷ **Basic Shares Outstanding - Model** (actual passthrough when reported; else prior week + **Share Count Adjustment - Model** from the **Shares** event table).

### Charts

- **Homes Charts** — **Opendoor Homes Funnel**: Acquisition Contracts, Homes Purchased, New Listings, Home Sales (each actual + model). **Opendoor Homes Inventory**: Homes in Inventory (actual + model) plus **Inventory Utilization %** and **Inventory Utilization % of Committed** (each actual + model) on the right axis.
- **Money Charts** — **Opendoor Weekly Revenue and Shares**: Revenue, Basic Shares Outstanding (actual + model). **Opendoor Weekly Profit and Price**: Contribution Profit, Adjusted EBITDA, Adjusted Net Income, Net Income Attributable to Common Shareholders (each actual + model), plus **Price (Actual)** and implied prices at **P/S = 2** and **P/S = 3** on the right axis.

**Manual only.** Chart styling (colors, log scale, axes, legend) is set in the Google Sheets UI. Agents and scripts must not edit these charts via the API — automated updates strip settings. After row inserts on Weekly / Quarterly Financials, fix chart series ranges by hand if a line points at the wrong row.

---

## Key assumptions (as encoded)

These are editable levers—mostly on **Transitions** and early columns of **Weekly Financials**. Comments in the sheet explain the rationale; see also [RESOURCES.md](RESOURCES.md).

| Assumption | Approx. value in sheet | Intent |
| --- | --- | --- |
| Likelihood to Close (per contract week) | **78%** in 2025 → **65%** at Q2 2026 (`AE`), dip to **63%**, then **66%** from mid-July | Cohort P(purchase). Includes seller cancel and Opendoor walking deals. Edit the L2C row (B / AE and later waypoints). |
| Close timing (of closers, 9 weeks) | sums to **100%** (mode ~weeks 4–5) | When closers purchase; no longer embeds attrition. |
| OPEN 1.0 → 2.0 transition | **0%** at Feb 2026 → **100%** by Jan 2027 | Blends listing / sales / revenue models between **OPEN 1.0** (pre-Kaz DOM ~51% @ 120d) and **OPEN 2.0** curves on **Transitions**. Edit completeness row or 1.0/2.0 sub-model rows. |
| Purchase → public listing translation | **Likelihood to List** (~**75%** early, higher later) × row 4 timing (**100%** of listers) | **2.0** listing lag: `Transitions` row 4; **1.0**: row 5 (New Listings - 1.0 Model only). |
| Unlisted 1.0 backlog at 2025-09-13 | **450** homes over **8 weeks** | Already-owned, not-yet-listed pipe from the old ~45-day reno wait. Edit `Transitions!B25` / `B27:I27`. Does not add to purchases. |
| Private / non-listed completions | **`1 − Likelihood to List`** on weekly row 10 | Share of purchases that never list. Feeds **Private Home Sales - Model** (not `Transitions!B6`, which is unused). |
| Private sale timing (purchase → close) | 9 weeks (`Transitions!B23:J23`) | Never-listed share lagged on **Percent of Private Completions Sold by Week**; edit row 23. |
| Listing → sale curve | 2.0 **25** weeks. ~**73%** by week 17 / ~120 days, ~**86%** by week 21, ~**99.5%** by week 25 | Shaped to [Open Tracker](https://aubermark.github.io/open-tracker/) cohort sell-through (Sep 2026). The Q2 “~91% over 120 days” stock figure was skewed by recent listings. **1.0** path ~**51%** by week 17, **100%** by week **39** on `Transitions` rows 13–16. |
| Price retention by week on market | 2.0: 100% → ~**93.5%** by week 21 → ~**92.3%** by week 25 | **1.0**: 100% → ~**88.6%** by week 21 (rows 12 vs 16). |
| Offer → close (financed / cash) | **8** / **4** weeks | `Transitions!B18` / `B19`. Help docs cite ~30–45 days financed / ~14 days cash; sheet uses the long end of those windows. |
| Cash purchase share | ~**31.5%** | National U.S. mix; OPEN does not disclose. |
| ASP | **$377,500** | Q2 2026. |
| Seasonality | Monthly acquisition weights summing to **100%** | Peak Nov–Dec (listings lag ~2 months into spring/early summer selling); trough May–Aug. |
| Acquisition growth (ops) | Weekly % ramp then fade | Growth / accountability scenarios. |
| CM path | Core improving; late-Aug/Sep **Adjustments** more negative (price-to-clear) | Q2 2026 ~5.8%; Kaz 9 Sep 2026 Q3 guide **3.2–3.5%** (was 4–4.5%); longer-term ~5–7%. |
| Mortgage attach (ODL) | **0%** before Jan 2026 → smoothstep ramp to **80%** by Oct 2028 | Four-phase smoothstep on **Open Mortgage Percent** (10% Sep 2026 / 40% Dec 2026 / 80% Oct 2028). On-inventory resales only. |
| Mortgage $/attached loan | **$4,000** max net (`Transitions!B29`) | CM add = attach × $/loan ÷ ASP. |
| Off-inventory ODL | **0%** of US existing-home-sale TAM at Sep 2026 GA → **2%** by Jan 1 2030 | `ODL Off-inventory Loans / Revenue / Profit - Model`; TAM **4,000,000**/year (`Transitions!B33`); **$7,500** revenue / **$3,000** profit per loan (`B34` / `B31`). Revenue in **Revenue - Model**; profit in Adj EBITDA, not CM. |
| Title purchase attach | **0%** before Jan 2025 → **100%** by Jun 2027 | Linear ramp on **Open Title Purchase Percent**. |
| Title $/purchase close | **$2,400** max net savings (`Transitions!B30`) | CM add = attach × $/close ÷ ASP. |
| Fixed opex | ~**$35M**/quarter-ish weeklyized | “Hold steady” accountability. |
| Senior warehouse rate | **5.30%** (Q2 2026 drawn-balance blend) | First-in-line inventory loans. Edit **Senior Interest Rate** `B`; later weeks carry forward. |
| Mezzanine warehouse rate | **12.50%** (Q2 2026 10-Q) | Second-priority inventory term debt. Edit **Mezzanine Interest Rate** `B`. |
| Mezzanine share of warehouse debt | **~19.8%** ($350M / $1.766B at Q2) | Mix lever: lower it to refinance mezz into cheaper senior. **Mezzanine Share of Warehouse Debt - Model**. |
| Warehouse facility capacity | **$4.2B** (senior revolvers + term) | Modeled inventory ceiling in dollars. Edit **Warehouse Facility Capacity** `B` ($7.45B headline or $1.5B committed). |
| Warehouse committed capacity | **$1.5B** (Q2 2026 10-Q) | Promised borrowing. **Inventory Utilization % of Committed** > 100% = discretionary draws (Q2 already ~118%). |

Where disclosure is missing, the sheet comments say so explicitly (likelihood to close, cash mix, some conversion totals).

---

## Investment-thesis framing (how to use the model)

Use the workbook to stress-test questions such as:

- Does **volume recovery** (contracts → inventory → sales) support the revenue guide (Q3 2026 **+10–15% YoY** per [Kaz 9 Sep 2026](https://x.com/nejatian/status/2097801756537151649); was ≥20% at Q2 earnings)?
- Is **CM** improving for the right reasons (new cohorts vs one-off), and does it reach the **5–7%** band management ties to adjusted profitability after the Q3 **3.2–3.5%** print?
- Do **fixed costs** stay flat while volume scales (operating leverage)?
- How sensitive are revenue and inventory to **DOM / sell-through**, **likelihood to close**, and **private** rates?

Update after each earnings release using the checklist in [RESOURCES.md](RESOURCES.md).

---

## Python tooling

OAuth, `--ticker`, and shared restore/validate CLIs are documented in the [repo README](../../README.md). OPEN-specific commands:

```bash
python scripts/test_connection.py --ticker OPEN
python scripts/validate_workbook_snapshot.py --ticker OPEN
python scripts/validate_model_formulas.py --ticker OPEN --offline
python scripts/restore_weekly_model_formulas.py --ticker OPEN
python scripts/sync_repo_from_live_sheet.py --ticker OPEN
python models/OPEN/scripts/update_weekly_quarterly_spread.py
```

Canonical model-row formulas live in `weekly_model_formulas.py`. Templates use `{Label}` placeholders resolved at restore time via `sheets/labels.py` — never hardcoded weekly row numbers.

**After inserting or deleting rows** on Weekly / Quarterly Financials:

1. Run `python scripts/validate_model_formulas.py --ticker OPEN` — fails if templates still use numeric row refs or expected labels are missing.
2. Run `python scripts/restore_weekly_model_formulas.py --ticker OPEN` — validates first, then re-applies all `* - Model` formulas.
3. If spread rows moved, run `python models/OPEN/scripts/update_weekly_quarterly_spread.py` (already label-based).

Offline template checks (no Google credentials): `python scripts/validate_model_formulas.py --ticker OPEN --offline`

Workbook layout (tab names, chart series rows) is snapshotted in `snapshot.json`. After intentional chart or tab changes, refresh with `python scripts/validate_workbook_snapshot.py --ticker OPEN --update` and commit the diff.

**After manual edits in the Google Sheet UI**, run `python scripts/sync_repo_from_live_sheet.py --ticker OPEN` (add `--update-snapshot` if chart series rows changed). That pulls acquisition-contract and CM seasonality, CM stack constants when they are hardcoded, **Financials Definitions** notes, and fails if any `* - Model` formula on the live sheet differs from `weekly_model_formulas.py` / `open_transition.py` — so manual formula fixes are not silently lost on the next restore.

After layout changes or accidental clears, run the restore script rather than reconstructing from older CHANGELOG entries.

```python
from sheets import SheetsClient

client = SheetsClient(ticker="OPEN")
print(client.list_worksheets())
```
