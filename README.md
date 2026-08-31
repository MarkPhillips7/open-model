# Open Model

Personal research workbook and Python tooling for modeling **Opendoor (OPEN)** financial results and projections—volume funnel, inventory, revenue, contribution margin, and cost structure—to better understand present results, forward estimates, and an investment thesis.

The live model is the Google Sheet **[Opendoor Model](https://docs.google.com/spreadsheets/d/1BhauTzGc9Nyt1J9gQl3NdCnpSSKCpSLbY9H7p5Obvc4)**. This repo connects to that sheet via OAuth and documents the approach.

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
| **Weekly Financials** | Main time series (week-ending columns). Actuals + model rows for contracts, **likelihood to close**, purchases, listings, **private sales**, listed+private home sales, ASP, revenue, CM stack, opex, SBC, **GAAP net income / EPS**, inventory. Weekly-reported actuals are entered here; quarterly-reported actuals are spread from **Quarterly Financials**. |
| **Quarterly Financials** | Same row layout as Weekly Financials, one column per quarter. Enter quarterly earnings actuals here; they spread across weeks (`÷13`, day-weighted at quarter boundaries). Rows like Acquisition Contracts **sum from weekly** when no quarterly report exists. |
| **Transitions** | Lag / probability tables that turn **closing** contracts into purchases (timing only), purchases into listings **or private sales**, and listings into sales (plus private %, **unlisted 1.0 backlog**, cash %, price retention, close timing). |
| **Shares** | Share-count **event table** (buybacks, warrant exercise, convert dilution scenarios) and SBC $/share assumption. Drives **Share Count Adjustment - Model** on Weekly Financials. |
| **Seasonality** | Monthly home-sales seasonality weights; drives weekly seasonality multipliers. |
| **Homes Chart** | Line chart of weekly home metrics (actual vs model for contracts, purchases, listings, sales, inventory). |
| **Money Charts** | Two line charts: **Revenue and Shares** (revenue + basic shares) and **Profit and Price** (contribution profit, adjusted/GAAP net income). |

---

## Modeling approach

### Weekly spine

- Columns are **week ending** dates (`Week Ending`, then `+7` across the horizon).
- **Quarterly-reported actuals** (homes purchased, home sales, revenue, opex, SBC, inventory, etc.) live on **Quarterly Financials** as quarter totals. **Weekly Financials** spreads them (`quarterly ÷ 13`, weighted by days when a week spans two quarters) when the quarterly cell is a hardcoded value.
- **Weekly-reported actuals** (e.g. acquisition contracts, sparse new-listing counts) are entered on **Weekly Financials**. **Quarterly Financials** sums the matching weeks when the quarterly cell is a formula.
- **Model** rows stay on **Weekly Financials**; formulas fall back between actual and model rows as before.

### Funnel (actuals vs model)

1. **Acquisition contracts** — Observed weekly contracts where available; model = deseasonalized base × seasonality × weekly operational growth.
2. **Homes purchased** — Model = lagged contracts × that cohort’s **Likelihood to Close** × **Transitions** close-timing weights over ~9 weeks (`SUMPRODUCT` / `MAP` lag). Timing weights sum to 100% of closers; attrition lives on the weekly L2C row.
3. **New listings** — Model = lagged **homes purchased** × **Likelihood to List** × **Transitions** listing-timing weights (row 4 sums to **100% of ultimate listers**). For the first **8 weeks** of the horizon only, add a finite **unlisted 1.0 backlog** (`Transitions!B21`, default 450) draining on row 23. Complements private sales via Likelihood to List / `B6`.
4. **Home sales** — Model = lagged listings × **Percent Sold by Listing Week** (~21 weeks) **+** private sales. Private sales = lagged purchases × `B6` × **Percent of Private Completions Sold by Week** (9-week purchase→close curve).
5. **Revenue** — Listed path = listings × ASP × sell-through × **price retention**, split by cash vs financed close lags. Private path = that week’s private sales × ASP (close already in the private curve; no DOM decay).
6. **Inventory** — Model rolls forward: prior inventory + **homes purchased** − sales (preferring actuals when present).

### Profitability stack

- **Contribution Margin - Model** = Core + Mortgage + Title/Escrow + Seasonality + Adjustments. Mortgage/title CM rows = attach % × $/unit ÷ ASP (see **Transitions** ancillary assumptions).
- **Doma Refi Profit - Model** / **Doma Growth Multiplier** — legacy weekly rows (zeroed; Transitions inputs removed).
- Core CM starts near low single digits and can step up via **Contribution Margin Improvement - Core**.
- Near-term negative adjustments reflect older-cohort / inventory-clearing pressure called out in earnings commentary.
- **Fixed Costs - Model** uses a steady quarterly run-rate (management accountability theme).
- **Adjusted EBITDA - Model** = Contribution Profit − Adjusted Operating Expenses (matches Opendoor Non-GAAP EBITDA).
- **Adjusted Net Income - Model** = Adjusted EBITDA − Net Interest − D&A − Taxes (SBC is **not** subtracted again; it sits above EBITDA in the company reconciliation).
- **Earnings per Share - Model** = GAAP net income ÷ **Basic Shares Outstanding - Model** (actual passthrough when reported; else prior week + **Share Count Adjustment - Model** from the **Shares** event table).

### Charts

- **Homes Chart**: Acquisition Contracts, Homes Purchased, New Listings, Home Sales, Homes in Inventory (each actual + model).
- **Money Charts** — **Revenue and Shares**: Revenue, Basic Shares Outstanding (actual + model). **Profit and Price**: Contribution Profit, Adjusted Net Income, Net Income Attributable to Common Shareholders (actual + model).

**Manual only.** Chart styling (colors, log scale, axes, legend) is set in the Google Sheets UI. Agents and scripts must not edit these charts via the API — automated updates strip settings. After row inserts on Weekly / Quarterly Financials, fix chart series ranges by hand if a line points at the wrong row.

---

## Key assumptions (as encoded)

These are editable levers—mostly on **Transitions** and early columns of **Weekly Financials**. Comments in the sheet explain the rationale; see also [RESOURCES.md](RESOURCES.md).

| Assumption | Approx. value in sheet | Intent |
| --- | --- | --- |
| Likelihood to Close (per contract week) | **78%** in 2025 → **67%** from Q2 2026 (Q1 2026 interpolates) | Cohort P(purchase). Includes seller cancel and Opendoor walking deals. Edit `B8` / `AE8`. |
| Close timing (of closers, 9 weeks) | sums to **100%** (mode ~weeks 4–5) | When closers purchase; no longer embeds attrition. |
| OPEN 1.0 → 2.0 transition | **0%** at Feb 2026 → **100%** by Jan 2027 | Blends listing / sales / revenue models between **OPEN 1.0** (pre-Kaz DOM ~51% @ 120d) and **OPEN 2.0** curves on **Transitions**. Edit completeness row or 1.0/2.0 sub-model rows. |
| Purchase → public listing translation | **Likelihood to List** (~**75%** early, higher later) × row 4 timing (**100%** of listers) | Complements private %; `B6` is still the private-sales share. **2.0** listing lag: `Transitions` row 4; **1.0**: row 5. |
| Unlisted 1.0 backlog at 2025-09-13 | **450** homes over **8 weeks** | Already-owned, not-yet-listed pipe from the old ~45-day reno wait. Edit `Transitions!B21` / `B23:I23`. Does not add to purchases. |
| Private / non-listed completions | ~**25%** (`Transitions!B6`; model uses **1 − Likelihood to List** on row 10) | Share of purchases that never list. Feeds **Private Home Sales - Model**. |
| Private sale timing (purchase → close) | 9 weeks on **2.0 listing lag** (`Transitions!B4:J4`) | Non-listed share uses the same purchase→listing curve as public listings; edit row 4. |
| Listing → sale curve | ~21 weeks; ~**91%** by ~120 days (2.0) | Calibrated to Q2 2026 DOM commentary. **1.0** path ~**51%** by week 17, **100%** by week **39** (~9 months) on `Transitions` rows 13–16. |
| Price retention by week on market | 2.0: 100% → ~**93.5%** by week 21 | **1.0**: 100% → ~**88.6%** by week 21 (rows 12 vs 16). |
| Offer → close (financed / cash) | **6** / **3** weeks | From Opendoor help docs. |
| Cash purchase share | ~**31.5%** | National U.S. mix; OPEN does not disclose. |
| ASP | **$377,500** | Q2 2026. |
| Seasonality | Monthly weights summing via helper **73%** | Mimics national monthly sales seasonality. |
| Acquisition growth (ops) | Weekly % ramp then fade | Growth / accountability scenarios. |
| CM path | Core improving; temporary negative adjustments; guided mid-single digits | Matches earnings CM narrative (bottom Sept 2025, Q3 guide 4–4.5%, longer-term ~5–7%). |
| Mortgage attach (ODL) | **0%** before Jan 2026 → smoothstep ramp to **80%** by Jan 2029 | Four-phase smoothstep on **Open Mortgage Percent** (10% / 40% / 80% phase targets). |
| Mortgage $/attached loan | **$4,000** max net (`Transitions!B29`) | CM add = attach × $/loan ÷ ASP. |
| Title purchase attach | **0%** before Jan 2025 → **100%** by Jun 2027 | Linear ramp on **Open Title Purchase Percent**. |
| Title $/purchase close | **$2,400** max net savings (`Transitions!B30`) | CM add = attach × $/close ÷ ASP. |
| Fixed opex | ~**$35M**/quarter-ish weeklyized | “Hold steady” accountability. |

Where disclosure is missing, the sheet comments say so explicitly (likelihood to close, cash mix, some conversion totals).

---

## Investment-thesis framing (how to use the model)

Use the workbook to stress-test questions such as:

- Does **volume recovery** (contracts → inventory → sales) support the revenue guide (e.g. ≥20% YoY)?
- Is **CM** improving for the right reasons (new cohorts vs one-off), and does it reach the **5–7%** band management ties to adjusted profitability?
- Do **fixed costs** stay flat while volume scales (operating leverage)?
- How sensitive are revenue and inventory to **DOM / sell-through**, **likelihood to close**, and **private** rates?

Update after each earnings release using the checklist in [RESOURCES.md](RESOURCES.md).

---

## Python tooling

Read/write the sheet from this repo (formulas, values, multiple tabs).

### Quick start

```bash
cd ~/open-model
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then complete the [Google Cloud setup](#one-time-google-cloud-setup) below, save credentials, and run:

```bash
python scripts/auth_setup.py      # first-time sign-in
python scripts/test_connection.py # verify access to your spreadsheet
python scripts/validate_workbook_snapshot.py  # compare live tabs/charts to config/workbook_snapshot.json
python scripts/validate_model_formulas.py        # check templates + live label alignment
python scripts/restore_weekly_model_formulas.py  # restore * - Model row formulas
```

Canonical model-row formulas live in `sheets/weekly_model_formulas.py`. Templates use `{Label}` placeholders resolved at restore time via `sheets/labels.py` — never hardcoded weekly row numbers.

**After inserting or deleting rows** on Weekly / Quarterly Financials:

1. Run `python scripts/validate_model_formulas.py` — fails if templates still use numeric row refs or expected labels are missing.
2. Run `python scripts/restore_weekly_model_formulas.py` — validates first, then re-applies all `* - Model` formulas.
3. If spread rows moved, run `python scripts/update_weekly_quarterly_spread.py` (already label-based).

Offline template checks (no Google credentials): `python scripts/validate_model_formulas.py --offline`

Workbook layout (tab names, chart series rows) is snapshotted in `config/workbook_snapshot.json`. After intentional chart or tab changes, refresh with `python scripts/validate_workbook_snapshot.py --update` and commit the diff.

After layout changes or accidental clears, run the restore script rather than reconstructing from older CHANGELOG entries.

### One-time Google Cloud setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project (e.g. `open-model`)
2. Enable [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com) and [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
3. **OAuth consent screen** → External → add scopes `spreadsheets` and `drive` → add yourself as a test user
4. **Credentials** → Create OAuth client ID → Desktop app → download JSON
5. Save the download as `config/credentials.json`

Your spreadsheet ID is configured in `config/settings.json`.

### Usage

```python
from sheets import SheetsClient

client = SheetsClient()
print(client.list_worksheets())
data = client.read_range("Weekly Financials", "A1:D20")
client.write_range("Weekly Financials", "A1", [["Hello", "World"]])
client.write_range("Weekly Financials", "D1", [["=SUM(A1:C1)"]], as_formulas=True)
```
