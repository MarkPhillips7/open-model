# Eos Energy Enterprises (EOSE)

Personal research workbook and Python tooling for modeling **Eos Energy Enterprises (EOSE)** — Z3 zinc-battery manufacturing capacity, unit economics, and a simple EV/EBITDA valuation.

This is the **EOSE** model pack in [open-model](../../README.md). The live model is the Google Sheet **[EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)** (view or comment). Shared OAuth and CLI tooling live at the repo root; this pack does **not** use OPEN’s weekly iBuying formulas.

Sources and citations: **[RESOURCES.md](RESOURCES.md)**. Spreadsheet edits made by agents are logged in **[CHANGELOG.md](CHANGELOG.md)**.

> Not investment advice. The model mixes company-reported figures, management commentary, tax-credit mechanics, and explicit guesses (line count, cycle-time learning, multiples).

---

## Goals

- Project **quarterly Z3 module output** from manufacturing lines, cycle time, and utilization.
- Convert output into **revenue, COGS, IRA 45X credits, gross profit, and EBITDA**.
- Translate annualized EBITDA into an **implied share price** (EV/EBITDA, net of assumed debt) and discount it back to today.

---

## Workbook map

| Tab | Role |
| --- | --- |
| **Quarterly Results/Projections** | Entire operating model. Column A is the row label, B is units, **C–Z** are calendar quarters **2025 Q1 – 2030 Q4**. |
| **Reference** | Source links (earnings ASP, 45X / PTC treatment, Feltonomics). |
| **Feltonomics** | Placeholder (empty). Named for the independent model cited on **Reference**. |
| **COGS** | Placeholder (empty). Unit COGS currently lives on the quarterly tab. |

There is no Weekly Financials tab, no Price History spill, and no chart tabs. Do not copy OPEN funnel formulas here.

---

## Modeling approach

### Time spine

- One column per quarter. Year labels sit on the Q1 of each year (C, G, K, O, S, W).
- **Years from present** starts at **2025 Q3** (column E = −0.25) and steps `+0.25` through 2030 Q4. 2025 Q1–Q2 (C–D) hold a few reported actuals only.

### Manufacturing (Z3)

Assumptions (editable): ASP, kWh/module, cycle time, lines, utilization, 45X credit, SG&A, R&D, debt, diluted shares, EV/EBITDA, discount rate.

Derived:

1. **Lines utilized** = lines × utilization.
2. **Modules per line (annualized, millions)** = (365/7) × days/week × hours/day × 3600 / cycle time / 1e6.
3. **Capacity per line (GWh/yr)** = kWh/module × modules per line × utilization.
4. **Annualized production** = modules per line × lines utilized; **quarterly modules** = annualized / 4.
5. **Energy (GWh)** follows the same annualized → quarterly split, using **line count** (not utilized lines) on the annualized energy row.
6. **Cycle time** holds 18s for two quarters, then compounds at the **quarterly module cycle time reduction rate** (2.9%). The last quarter is hardcoded at **10s** (a floor).

### Profitability

- **Unit COGS** ($/kWh) minus **effective 45X** (credit × transfer rate) → **unit COGS w/ 45X**.
- **Government credits ($M)** = effective 45X × quarterly GWh produced.
- **COGS derived** = unit COGS × GWh − government credits (credits as a COGS offset).
- **Revenue (modeled, 2025 Q4 onward)** = quarterly modules × ASP + government credits.
- **2025 Q1–Q3 revenue** and **Q1–Q2 gross profit** are hardcoded actuals. **2025 Q3 gross profit** uses **COGS actual**; later quarters use **COGS derived**.
- **OpEx** = SG&A + R&D (2025 Q3 adds a +0.585 plug).
- **EBITDA** = gross profit − OpEx.

**Reference** notes that tax credits are recorded as negative COGS, not revenue. The current formulas both reduce derived COGS **and** add credits into modeled revenue — treat that as an explicit model choice, not GAAP.

### Valuation

- **Enterprise value ($B)** = annualized EBITDA × EV/EBITDA / 1000 (default multiple **30**).
- **Market cap derived** = EV − total debt (debt assumed **$1B** across the horizon).
- **Implied future stock price** = derived market cap / diluted shares.
- **Present price** = `-PV(discount rate, years from present, 0, implied future price)` (default **20%**).
- **Market cap actual** / **stock price actual** are filled only on 2025 Q3.

---

## Python tooling

OAuth, `--ticker`, and shared snapshot/sync CLIs are documented in the [repo README](../../README.md). EOSE-specific commands:

```bash
python scripts/test_connection.py --ticker EOSE
python scripts/validate_workbook_snapshot.py --ticker EOSE
python scripts/sync_repo_from_live_sheet.py --ticker EOSE
```

This pack has no `weekly_model_formulas.py`. `validate_model_formulas.py` / `restore_weekly_model_formulas.py` skip EOSE.

Workbook layout is snapshotted in `snapshot.json`. After intentional tab changes, refresh with `python scripts/validate_workbook_snapshot.py --ticker EOSE --update`.

```python
from sheets import SheetsClient

client = SheetsClient(ticker="EOSE")
print(client.list_worksheets())
data = client.read_range("Quarterly Results/Projections", "A1:G40")
```
