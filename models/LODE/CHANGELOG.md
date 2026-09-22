# Spreadsheet changelog

The live model is the Google Sheet **[LODE Model](https://docs.google.com/spreadsheets/d/1_2X0QzVWN5XiH4WX2V_outtKgQQYti81T28H22g9xDM/edit?usp=sharing)** (ticker **LODE**). Git does not see those edits unless they are recorded here. Repo/platform changes go in the [root CHANGELOG](../../CHANGELOG.md).

**After every agent write to the sheet, append an entry below before finishing.** One dated heading per change-set.

Entry template:

```markdown
## YYYY-MM-DD — short title

- **Tab / range:** what changed
- **Insert/delete:** dimension, start index, count
- **Formulas:** before → after (a template is enough if copied across columns)
- **Data:** cells and values, plus why
- **Side effects:** charts, notes, number formats
```

---

## 2026-09-22 — Adopt lever + Valuation inputs; freeze Year/Quarter

User edited yellow inputs on the live sheet; fold into the repo. Also freeze Year and Quarter with the Units header on Quarterly Financials.

- **Tab / range:** Levers `C29` (SSOF value achieved); Valuation `C3` (Reference quarter); Quarterly Financials grid freeze
- **Insert/delete:** none
- **Formulas:** none
- **Data:**
  - `SSOF value achieved` **55 → 80** (Levers value; repo default matched)
  - `Reference quarter` **2029 Q4 → 2028 Q4** (Valuation input; `DEFAULT_REFERENCE_QUARTER` matched)
- **Side effects:** Quarterly Financials `frozenRowCount` **1 → 3** (Units + Year + Quarter). No charts.

### Repo

- `levers.py`, `valuation.py`, `scripts/setup_lode_workbook.py`, `live_fingerprint.json`

## 2026-09-22 — Fix Valuation (+ Asset Monetization) after Levers rebuild

Levers row numbers shifted when the tab was rebuilt (tailings / silver levers). Valuation and Asset Monetization still pointed at the old `Levers!$C$…` cells. On Valuation, Metals business value multiplied by **Mining sale second tranche quarter** (`2027 Q4`) and produced `#VALUE!` down through equity value / per-share / upside; SSOF, fuels, multiple, and net-cash-credited were also reading the wrong levers. Asset Monetization had the same stale refs (wrong numbers, no `#VALUE!`).

- **Tab / range:** Valuation `A1:D33`; Asset Monetization `A1:D34` (full rewrites from repo)
- **Insert/delete:** none (Valuation gained one data row vs prior live layout: `SSOF stake sold for cash`)
- **Formulas:** stale absolute Levers refs → current `lever_ref()` targets, e.g. Valuation
  - Metals multiple: `Levers!$C$40` → `Levers!$C$45`
  - Metals achieved: `Levers!$C$41` → `Levers!$C$46`
  - Net cash credit: `Levers!$C$42` → `Levers!$C$47`
  - SSOF / Fuels blocks similarly retargeted; SSOF stake value now nets `SSOF stake sold for cash` when monetization ≤ reference quarter
- **Data:** Reference quarter left at `2029 Q4` (default input)
- **Side effects:** `#VALUE!` cleared on Valuation result lines; fingerprint refreshed. No chart tabs.

### Repo

- `live_fingerprint.json` only (no Python changes; sheet caught up to existing `valuation.py` / `asset_monetization.py`)

## 2026-09-21 — Tailings stockpile + strong-2030 silver underwrite

Model the CEO's "prefer not to sell tailings once extraction is in sight" path, and raise the metal underwrite toward most-of-the-silver / higher-purity product by 2030.

- **Tab / range:** Levers (full rebuild A:G); Quarterly Financials — **inserted 4 rows** before `COMSTOCK METALS — UNIT ECONOMICS`; A:B labels; all `* - Model` formulas C:Z; uplift plan path; Financials Definitions; Welcome B6
- **Insert/delete:** rows, start at former `COMSTOCK METALS — UNIT ECONOMICS` index, count **4** (`Tailings stockpile add/inventory/draw`, `Stockpile metal revenue`)
- **Formulas:**
  - **Recovered material per ton - Model:** base − offtake×stockpile_frac×(1 − phase×metal_ach) + (glass+metal uplifts)×phase
  - **Metals revenue - Model:** tons×$/t ÷ 1e6 **+ Stockpile metal revenue**
  - New inventory roll-forward and backlog draw (`Tailings backlog draw rate` lever, default 1.0×)
- **Data (Levers defaults):**
  - Metal extraction uplift **350**; Metal extraction achieved **85**
  - New: Tailings offtake in base **100**; Tailings stockpiled **100%**; start **2027 Q1**; backlog draw **1.0**
- **Side effects:** Chart series on any Metals chart tabs may have shifted with the row insert — **verify/adjust series manually in the Sheets UI**. Fingerprint refreshed.

### Repo

- `levers.py`, `layout.py`, `quarterly_model_formulas.py`, `financials_definitions.py`, `welcome.py`
- `scripts/sync_tailings_stockpile.py`
