# Eos Energy Enterprises (EOSE)

Personal research workbook and Python tooling for modeling **Eos Energy Enterprises (EOSE)** — quarterly commercial funnel (pipeline → orders → backlog → shipments), Z3 factory capacity, unit economics, cash, and a gated EV/EBITDA valuation.

This is the **EOSE** model pack in [open-model](../../README.md). The live model is the Google Sheet **[EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)** (view or comment). Shared OAuth and CLI tooling live at the repo root. This pack does **not** use OPEN’s weekly iBuying formulas; it does copy OPEN’s Actual vs Model discipline.

Sources and citations: **[RESOURCES.md](RESOURCES.md)**. Spreadsheet edits made by agents are logged in **[CHANGELOG.md](CHANGELOG.md)**.

> Not investment advice. The model mixes company-reported figures, management guidance, and explicit guesses (line ramp, cycle-time learning, $160/kWh terminal COGS, conversion lag).

---

## Goals

- Keep **reported actuals** on their own rows (blank until the 10-Q / earnings print) and a parallel **Model** path so misses are visible.
- Project **quarterly shipments** as `MIN(factory capacity, beginning backlog GWh / conversion lag)`.
- Convert shipments into **revenue, COGS (45X as a COGS offset only), gross profit, adj. EBITDA, cash, and shares**.
- Translate **positive** annualized EBITDA into an implied share price; leave EV blank while EBITDA is negative.

There is no weekly spine. Eos does not publish a high-frequency unit funnel.

---

## Workbook map

| Tab | Role |
| --- | --- |
| **Welcome** | Disclaimer, goals, tab guide with links. Canonical copy in `welcome.py`. |
| **Financials Definitions** | Column A mirrors Quarterly Financials labels; column B documents each field. Canonical text in `financials_definitions.py`. |
| **Quarterly Financials** | Main time series. Column A label, B units, **C–Z** = **2025 Q1 – 2030 Q4**. Actuals + Model rows. |
| **Shares** | Dated dilution events (offerings, converts, warrants). Model currently carries last reported diluted shares; fill Δ when you want incremental dilution. |
| **Price History** | One `GOOGLEFINANCE` spill of EOSE daily OHLCV. **Stock price** XLOOKUPs the close by quarter-ending date. |
| **Reference** | Source links (ASP, 45X treatment, Feltonomics). |
| **Feltonomics** | Placeholder (empty) — independent model cited on Reference. Kept for later. |
| **COGS** | Placeholder (empty) — unit-cost build-up to revisit. Unit COGS currently lives on Quarterly Financials. |

**Charts are manual-only.** Add Operations / Money charts in the Google Sheets UI if you want Actual (solid) vs Model (dotted). Agents must not create or edit chart objects via the API.

---

## Modeling approach

### Actual vs Model

OPEN pattern: bare label = hardcoded print (or derived from prints); `Label - Model` is always a formula. Downstream Model rows prefer an actual when the cell is non-blank (`IF(actual<>"", actual, model)`), including the backlog identity.

### Demand (quarterly)

Eos defines backlog as prior + booked orders − shipments. Pipeline is proposals + LOI. Booked orders require a PO or MSA.

1. **Pipeline / Backlog ($ and GWh)** — Actuals from earnings through **Q2 2026**. Model carries last actual pipeline; rolls backlog with preferred orders and revenue.
2. **Booked orders - Model** — last actual bookings carried forward (Q4 2025 $240M disclosed; Q2 2026 implied ~$231M).
3. **GWh shipped - Model** — `MIN(Factory capacity - Model, beginning backlog GWh / Backlog conversion lag)`. Default lag **4** quarters (column C).
4. **Revenue - Model** — GWh shipped - Model × Z3 ASP - Model. **Does not add 45X credits.**

### Factory (supply ceiling)

Same physics as the old sheet: cycle time, lines, utilization, kWh/module. Cycle time - Model starts at 18s, compounds at 2.9%/quarter, floored at 10s. Line ramp is an editable Model series (1 → 12). Actual lines: 1 through Q1 2026, 2 from Q2 2026 (Line 2 launch).

### Profitability

- **Unit COGS - Model** is an explicit thesis (**$160/kWh**), not a fit to today’s ~−71% gross margin. Actual COGS/GM show the gap.
- **45X** = credit × transfer rate, applied **only** as a COGS offset (`COGS - Model` = unit COGS × GWh − credits).
- **SG&A / R&D - Model** carry last actual (opex hold).
- **Adjusted EBITDA - Model** = gross profit - Model − opex - Model.
- **GAAP net income - Model** = adj. EBITDA − interest run-rate. It **ignores** warrant/derivative fair-value marks that dominate reported NI.

### Cash, shares, valuation

- **Cash - Model** = prior cash + adj. EBITDA − capex − interest. Capex = $40M × max(0, Δ lines) — a guess.
- **Stock price** from Price History (quarter-end close).
- **Enterprise value - Model** = annualized EBITDA × EV/EBITDA / 1000 **only if** annualized EBITDA > 0.
- **Present price** = `-PV(discount rate, years from present, 0, implied future price)`. **As of date** is `C` on that row (default 9 Sep 2026).

---

## Python tooling

```bash
python scripts/test_connection.py --ticker EOSE
python scripts/validate_workbook_snapshot.py --ticker EOSE
python scripts/validate_model_formulas.py --ticker EOSE
python scripts/restore_weekly_model_formulas.py --ticker EOSE
python models/EOSE/scripts/fetch_sec_gaap.py
python models/EOSE/scripts/load_quarterly_actuals.py
python models/EOSE/scripts/setup_eose_workbook.py
```

Canonical Model formulas live in `quarterly_model_formulas.py` (label placeholders, restored onto **Quarterly Financials**). Reported prints live in `actuals.py`. After each earnings release, pull GAAP from SEC companyfacts (`fetch_sec_gaap.py`), copy adj. EBITDA / pipeline / backlog from the 8-K Ex. 99.1 (links in `sources.py`), patch `actuals.py`, then `load_quarterly_actuals.py`. See [RESOURCES.md](RESOURCES.md).

```python
from sheets import SheetsClient

client = SheetsClient(ticker="EOSE")
print(client.list_worksheets())
```
