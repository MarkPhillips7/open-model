# Open Model

Personal research workbook and Python tooling for modeling **Opendoor (OPEN)** financial results and projections—volume funnel, inventory, revenue, contribution margin, and cost structure—to better understand present results, forward estimates, and an investment thesis.

The live model is the Google Sheet **[Opendoor Model](https://docs.google.com/spreadsheets/d/1BhauTzGc9Nyt1J9gQl3NdCnpSSKCpSLbY9H7p5Obvc4)**. This repo connects to that sheet via OAuth and documents the approach.

Sources and citations: **[RESOURCES.md](RESOURCES.md)**.

> Not investment advice. The model mixes company-reported Non-GAAP metrics, management guidance, and explicit guesses where Opendoor does not disclose detail.

---

## Goals

- Reconstruct a **weekly operating model** of Opendoor’s home funnel: acquisition contracts → purchases → listings → sales → revenue.
- Separate **reported / stubbed actuals** from **forward model** rows so gaps and surprises are visible.
- Encode **timing and attrition** (cancel rates, private closings, days on market, financed vs cash close) as adjustable assumptions.
- Project **contribution margin**, fixed costs, and inventory path under seasonal and growth scenarios.
- Use charts to compare actual vs modeled homes and money over time.

---

## Workbook map

| Tab | Role |
| --- | --- |
| **Weekly Home Activity** | Main time series (week-ending columns). Actuals + model rows for contracts, purchases, listings, sales, ASP, revenue, CM stack, opex, SBC, EPS placeholders, inventory. |
| **Transitions** | Lag / probability tables that turn contracts into purchases, purchases into listings, and listings into sales (plus cancel %, private %, cash %, price retention, close timing). |
| **Seasonality** | Monthly home-sales seasonality weights; drives weekly seasonality multipliers. |
| **Homes Chart** | Line chart of weekly home metrics (actual vs model for listings, acquisitions, sales). |
| **Money Chart** | Line chart of weekly **Revenue** vs **Revenue - Model**. |

---

## Modeling approach

### Weekly spine

- Columns are **week ending** dates (`Week Ending`, then `+7` across the horizon).
- Many “actual” cells are **quarterly totals ÷ 13** (weekly stub) until finer weekly data is filled in—e.g. homes purchased `1169/13`, home sales `2568/13`, revenue `$915M/13`, fixed costs `$37M/13`, adjusted opex `$53M/13`.
- **Model** rows prefer formulas; when an actual is blank, formulas fall back to the model row (and vice versa for some lag lookups).

### Funnel (actuals vs model)

1. **Acquisition contracts** — Observed weekly contracts where available; model = deseasonalized base × seasonality × weekly operational growth.
2. **Homes purchased** — Model = lagged contracts × **Transitions** “percent translated into purchase” over ~9 weeks (`SUMPRODUCT` / `MAP` lag).
3. **New listings** — After early hardcoded weeks, model = lagged acquisitions × listing translation weights, scaled by `(1 − cancel% − private%)`.
4. **Home sales** — Model = lagged listings × **Percent Sold by Listing Week** (up to ~21 weeks).
5. **Revenue** — Model = sales × ASP, split by cash vs financed close lags from **Transitions**, with **price retention** by listing age.
6. **Inventory** — Model rolls forward: prior inventory + acquisitions − sales (preferring actuals when present).

### Profitability stack

- **Contribution Margin - Model** = Core + Mortgage + Title/Escrow + Adjustments (mortgage / title rows are stubs for attach-rate economics).
- Core CM starts near low single digits and can step up via **Contribution Margin Improvement - Core**.
- Near-term negative adjustments reflect older-cohort / inventory-clearing pressure called out in earnings commentary.
- **Fixed Costs - Model** uses a steady quarterly run-rate (management accountability theme).
- EPS / ANI rows are placeholders for later P&L completion.

### Charts

- **Homes Chart**: New Listings, New Listings - Model, Acquisition Contracts, Acquisition Contracts - Model, Home Sales, Home Sales - Model.
- **Money Chart**: Revenue vs Revenue - Model.

---

## Key assumptions (as encoded)

These are editable levers—mostly on **Transitions** and early columns of **Weekly Home Activity**. Comments in the sheet explain the rationale; see also [RESOURCES.md](RESOURCES.md).

| Assumption | Approx. value in sheet | Intent |
| --- | --- | --- |
| Contract → purchase conversion (sum of weekly %) | ~**69%** (target commentary ~80% if ~20% cancel) | Closing attrition; early weeks intentionally low (title / seller cancel / date push-outs). |
| Purchase → public listing translation | ~**75%** | ~**25%** assumed private / never publicly listed. |
| Acquisition cancel rate | ~**18%** | Aligns with independent tracker range ~10–20%. |
| Private / non-listed completions | ~**25%** | Complements listing translation. |
| Listing → sale curve | ~21 weeks; ~**91%** by ~120 days | Calibrated to Q2 2026 DOM commentary + cohort sell-through charts. |
| Price retention by week on market | 100% → ~**93.5%** by week 21 | Longer DOM → lower effective price. |
| Offer → close (financed / cash) | **6** / **3** weeks | From Opendoor help docs. |
| Cash purchase share | ~**31.5%** | National U.S. mix; OPEN does not disclose. |
| ASP | **$377,500** | Q2 2026. |
| Seasonality | Monthly weights summing via helper **73%** | Mimics national monthly sales seasonality. |
| Acquisition growth (ops) | Weekly % ramp then fade | Growth / accountability scenarios. |
| CM path | Core improving; temporary negative adjustments; guided mid-single digits | Matches earnings CM narrative (bottom Sept 2025, Q3 guide 4–4.5%, longer-term ~5–7%). |
| Fixed opex | ~**$35M**/quarter-ish weeklyized | “Hold steady” accountability. |

Where disclosure is missing, the sheet comments say so explicitly (cancel rate, cash mix, some conversion totals).

---

## Investment-thesis framing (how to use the model)

Use the workbook to stress-test questions such as:

- Does **volume recovery** (contracts → inventory → sales) support the revenue guide (e.g. ≥20% YoY)?
- Is **CM** improving for the right reasons (new cohorts vs one-off), and does it reach the **5–7%** band management ties to adjusted profitability?
- Do **fixed costs** stay flat while volume scales (operating leverage)?
- How sensitive are revenue and inventory to **DOM / sell-through** and **cancel / private** rates?

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
```

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
data = client.read_range("Weekly Home Activity", "A1:D20")
client.write_range("Weekly Home Activity", "A1", [["Hello", "World"]])
client.write_range("Weekly Home Activity", "D1", [["=SUM(A1:C1)"]], as_formulas=True)
```
