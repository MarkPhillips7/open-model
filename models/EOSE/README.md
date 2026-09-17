# Eos Energy Enterprises (EOSE)

Personal research workbook and Python tooling for modeling **Eos Energy Enterprises (EOSE)** — quarterly commercial funnel (pipeline → orders → backlog → shipments), Z3 factory capacity, unit economics, cash, and a gated EV/EBITDA valuation.

This is the **EOSE** model pack in [open-model](../../README.md). The live model is the Google Sheet **[EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)** (view or comment). Shared OAuth and CLI tooling live at the repo root. This pack does **not** use OPEN’s weekly iBuying formulas; it does copy OPEN’s Actual vs Model discipline.

Sources and citations: **[RESOURCES.md](RESOURCES.md)**. Spreadsheet edits made by agents are logged in **[CHANGELOG.md](CHANGELOG.md)**.

> Not investment advice. The model mixes company-reported figures, management guidance, and explicit guesses (line ramp, cycle-time learning, cost-out haircut, $160/kWh terminal COGS, conversion lag).

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
| **COGS** | Cost-out levers and notes. Frozen header: **Units / Value / Notes**. Q2 2026 Slide 11 waterfall (25/20/20/8 pts of adj. GM) × **Percent of Guided Cost Cutting Achieved** (default 70% on Quarterly Financials); **Terminal unit COGS** (default $160/kWh) is edited here. Quarterly path (progress, adj. GM, unit COGS, $200M illustration) lives on **Quarterly Financials**. |

**Charts are manual-only.** Add Operations / Money charts in the Google Sheets UI if you want Actual (solid) vs Model (dotted). Agents must not create or edit chart objects via the API.

---

## Modeling approach

### Actual vs Model

OPEN pattern: bare label = hardcoded print (or derived from prints); `Label - Model` is always a formula. Downstream Model rows prefer an actual when the cell is non-blank (`IF(actual<>"", actual, model)`), including the backlog identity.

### Demand (quarterly)

Eos defines backlog as prior + booked orders − shipments. Pipeline is proposals + LOI. Booked orders require a PO or MSA.

The live Quarterly Financials tab currently uses a **different** (WIP) path than the old capacity/backlog identity. Repo templates match the sheet as typed, including known-wrong formulas:

1. **Pipeline / Backlog ($ and GWh)** — Actuals from earnings through **Q2 2026**. Pipeline - Model compounds at the column's growth rate. Backlog - Model copies Q1 actual then × **1.03** per quarter. Backlog (GWh) - Model = dollar model / Z3 ASP - Model.
2. **Booked orders - Model** — copy $M actual if present, else prior Model × **1.2**. A second **Booked orders** row (units GWh) holds Q4 2025 **1.1**.
3. **Z3 ASP - Model** — **$260** in 2025 Q1, then prior × **0.97**.
4. **MWh shipped - Derived** — Revenue × 1000 / Z3 ASP - Model when Z3 ASP - Derived is non-blank. **Revenue - Model** = that MWh / 1000 × ASP. There is no GWh shipped row.

### Factory (supply ceiling)

Same physics as the old sheet: cycle time, lines, utilization, kWh/module. Cycle time - Model starts at 18s, compounds at 2.9%/quarter, floored at 10s. Line ramp is an editable Model series (1 → 12). Actual lines: 1 through Q1 2026, 2 in Q2 2026 (Line 2 launch), working **1.5** in Q3 2026 (in-quarter, not a print). **Z3 modules per cube (672)** is the original **Cube** packing only — do not use it for Indensity.

### What “unit” means

Eos sells energy, but talks about three different physical packages:

| Thing | What it is |
| --- | --- |
| **Z3 module** | The battery (~1.2 kWh). Factory cycle time is per module. |
| **Cube** | Original containerized BESS. This workbook’s **672 modules/cube** is Cube-only. Ops KPIs on the call (labor/cube, material/cube, cube deliveries) are this language. |
| **Indensity** | Denser architecture using the same Z3 modules (stackable Core units). Not a separate chemistry. |

**Unit COGS / ASP in this model are $/kWh of energy**, not $/Cube or $/Indensity SKU. Bert’s [cost-out thread](https://x.com/bert_gilfoyle/status/2096422051376742414) follows Slide 11: **percentage points of adjusted gross margin** (of revenue) and Adj. EBITDA in **$M**. Older factory notes mix that with implied **$/kWh** and management’s **per-cube** cost KPIs. Eos has **not disclosed** a Cube vs Indensity sales split. Q2 2026 still reported cube deliveries (+207% YoY, +20% QoQ); Line 2 was ~1% of Q2 production. Q1 2026 commentary was that the *pipeline* has a higher mix of large-scale / Indensity quotes — that is not current-period shipments.

**MWh shipped - Derived** is a formula (revenue / Model ASP), not the old Q1/Q2 2026 typed MWh prints. Treat factory defaults (18s cycle, 672/cube) as guesses until replaced.

### Profitability

- **Unit COGS - Model** is computed on **Quarterly Financials** from COGS-tab levers, not a flat $160. Starting point is Q2 2026 adj. GM (−62.3%). Management's 12-month waterfall is **73 pts** (materials 25 / conversion 20 / projects 20 / scrap 8). **Percent of Guided Cost Cutting Achieved** (default **70%**) lives on Quarterly Financials and scales those points because Eos has repeatedly missed cost-out timelines. After Q2 2027 the remaining gap to **Terminal unit COGS** ($160, edited on the COGS tab) is blended in as manufacturing lines go from 2 → 4.
- **45X** = credit × transfer rate, applied **only** as a COGS offset (`COGS - Model` = unit COGS × GWh − credits + non-cash COGS D&A/SBC).
- **SG&A / R&D - Model** carry last actual (opex hold). **Cash OpEx run-rate** is Q2 implied adj. GP − adj. EBITDA ($28.5M), held flat.
- **Adjusted EBITDA - Model** = adj. GP − cash OpEx (company definition). **Operating cash flow - Model** equals that — the CFO said Q2 ops cash use tracked adj. EBITDA.
- **GAAP net income - Model** = adj. EBITDA − interest run-rate. It **ignores** warrant/derivative fair-value marks that dominate reported NI.

### Cash, shares, valuation

- **Cash - Model** = prior cash + operating cash flow (adj. EBITDA proxy) − capex − interest. Capex = $40M × max(0, Δ lines) — a guess.
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
python models/EOSE/scripts/setup_eose_workbook.py --force-rebuild
python models/EOSE/scripts/setup_cogs.py --force-rebuild
```

Canonical Model formulas live in `quarterly_model_formulas.py` (label placeholders, restored onto **Quarterly Financials**). Reported prints live in `actuals.py`. After each earnings release, pull GAAP from SEC companyfacts (`fetch_sec_gaap.py`), copy adj. EBITDA / pipeline / backlog from the 8-K Ex. 99.1 (links in `sources.py`), patch `actuals.py`, then `load_quarterly_actuals.py`. See [RESOURCES.md](RESOURCES.md).

Do **not** run `setup_eose_workbook.py`, `setup_cogs.py`, or `restore_weekly_model_formulas.py --ticker EOSE` unless you intend to replace the live sheet from git. The setup scripts require `--force-rebuild`. Restore aborts if Quarterly Financials labels drifted from `layout.py`.

```python
from sheets import SheetsClient

client = SheetsClient(ticker="EOSE")
print(client.list_worksheets())
```
