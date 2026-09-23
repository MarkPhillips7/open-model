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

## 2026-09-23 — Projected stock price + Present defaults to Implied

- **Tab / range:** Quarterly Financials `A88:Z88` (new), `C87:Z87` (Present formula);
  Financials Definitions (Present / Projected notes)
- **Insert/delete:** ROWS, start index 87 (0-based after Present), count 1
- **Formulas:**
  - **Present stock price discounted - Model:** when years from present ≤ 0, was `""`
    → now equals **Implied stock price - Model** (still discounts when years > 0)
  - **Projected stock price - Model** (new): `0.44×Present(t) + 0.33×Present(t+4) + 0.23×Present(t+8)`;
    blank near spine end when t+8 missing
- **Data:** none
- **Side effects:** Number format `#,##0.00` on Projected. Chart objects untouched —
  add Projected to Money Charts manually if desired. Fingerprint refreshed.

### Repo

- `layout.py`, `quarterly_model_formulas.py`, `financials_definitions.py`,
  `scripts/sync_quarterly_valuation.py`, `live_fingerprint.json`

## 2026-09-23 — Lever tweaks + Money Charts tab

User raised three achieved levers on the live sheet and added a **Money Charts**
tab with **LODE Profit and Price**. Folded into the repo; Welcome tab guide
updated to describe the new chart.

- **Tab / range:** Levers `C8`/`D8`, `C16`/`D16`, `C30`/`D30` (+ rationale `G`);
  new worksheet **Money Charts**; Welcome tab-guide rows; `snapshot.json`
- **Insert/delete:** new worksheet **Money Charts** (user-created in UI; between
  Financials Definitions and Asset Monetization)
- **Formulas:** none
- **Data:**
  - `Line expansion achieved` **70 → 75**
  - `Glass upgrade achieved` **65 → 70**
  - `SSOF value achieved` **80 → 85**
  - Defaults + glass/line-expansion rationale text matched to the new values;
    also synced stale `Metals core business value` Default **25 → 50** (Value
    already 50 from earlier adopt)
  - Welcome: new **Money Charts** blurb (Profit and Price: stock / implied /
    present on left; metals cash contribution on right)
- **Side effects:** Chart objects untouched by agents (manual UI only).
  `snapshot.json` created from live (1 chart). `setup_lode_workbook.py`
  TAB_ORDER now preserves **Money Charts** on rebuild without auto-creating it.
  Fingerprint re-baselined (`--adopt` + Welcome/Default push).

### Repo

- `levers.py`, `welcome.py`, `scripts/setup_lode_workbook.py`,
  `live_fingerprint.json`, `snapshot.json` (new)

## 2026-09-22 — Lines / util plan aligned to guidance

User edited yellow `- Plan` trajectories on Quarterly Financials to better match
management's end-2027 "full" + facility-2 soft guide and five facilities by 2030.

- **Tab / range:** Quarterly Financials `Operating production lines - Plan` O:Z;
  `Capacity utilization - Plan` K:Q (other quarters unchanged)
- **Insert/delete:** none
- **Formulas:** none (plan rows are data; `- Model` still applies achieved levers)
- **Data:**
  - Lines: 2028 **1,2,2,2 → 1.5,1.5,2,2**; 2029 **2,3,3,3 → 2.5,3,3,3.5**;
    2030 **3,4,4,4 → 4,4,4.5,5** (five lines by 2030 Q4)
  - Util: 2027 **35,45,55,65 → 45,60,70,78**; 2028 Q1–Q3 **70,75,80 → 85,85,85**
    (terminal "full" ~85% from early 2028; end-2027 ~78%)
- **Side effects:** none on chart objects; implied/present price paths will move
  with higher mid-ramp throughput. Fingerprint re-baselined (`--adopt`).

### Repo

- `layout.py` (`LINE_PATH`, `UTILIZATION_PATH` + comments), `financials_definitions.py`,
  `live_fingerprint.json`

## 2026-09-22 — Adopt Metals core business value $50M

User raised the yellow lever on the live sheet; fold into the repo default.

- **Tab / range:** Levers `Metals core business value` (Value + Default)
- **Insert/delete:** none
- **Formulas:** none
- **Data:** `Metals core business value` **25 → 50** (live Value; repo default matched)
- **Side effects:** none (QF already reads the lever). Fingerprint not required for Value-only adopt if unchanged elsewhere — refresh if recording.

### Repo

- `levers.py`

## 2026-09-22 — Metals core business value (assets / IP / R&D)

Add a fixed platform credit as of 2025 Q1 so metals SoP is not just the cash-contribution multiple while the ramp is loss-making.

- **Tab / range:** Levers (full rebuild A:G); Quarterly Financials — **inserted 1 row** before `Metals business value - Model`; A:B; valuation formulas; Valuation A:D; Financials Definitions
- **Insert/delete:** rows, before `Metals business value - Model`, count **1** (`Metals core business value - Model`)
- **Formulas:** `Metals business value - Model` = `(EBITDA proxy × multiple × achieved/100) + Metals core business value - Model`; core row = Levers scalar (flat)
- **Data (Levers defaults):** new `Metals core business value` **25** $M (0…60) — ASSUMPTION for demo plant + process IP + R&D as of 2025 Q1; prior Values preserved
- **Side effects:** Chart series may need a one-row nudge if any chart pointed below this insert — verify manually. Fingerprint refreshed.

### Repo

- `levers.py`, `layout.py`, `quarterly_model_formulas.py`, `valuation.py`, `financials_definitions.py`, `live_fingerprint.json`

## 2026-09-22 — Allow negative Metals business value

Drop the zero floor so early-ramp losses flow through the SoP instead of blanking the metals pillar.

- **Tab / range:** Quarterly Financials `Metals business value - Model` C:Z; Financials Definitions; Valuation notes
- **Insert/delete:** none
- **Formulas:** `MAX(0, EBITDA proxy × multiple × achieved/100)` → `EBITDA proxy × multiple × achieved/100`
- **Data:** none
- **Side effects:** Implied / Present stock price can go negative (or more negative) in loss-making quarters. Fingerprint refreshed.

### Repo

- `quarterly_model_formulas.py`, `financials_definitions.py`, `valuation.py`, `live_fingerprint.json`

## 2026-09-22 — Quarterly SoP valuation + SSOF/Fuels growth levers

Add a full sum-of-parts series on Quarterly Financials (chartable implied / present prices) and let SSOF and Bioleum values compound from the As of date instead of sitting flat through 2030.

- **Tab / range:** Levers (full rebuild A:G); Quarterly Financials — **inserted 14 rows** after `Market cap`; A:B labels; all `* - Model` formulas C:Z; Valuation A:D; Financials Definitions; Welcome
- **Insert/delete:** rows, start after `Market cap`, count **14** (spacer + `VALUATION` + 12 SoP metrics)
- **Formulas:**
  - New QF block: annualized metals contribution / corp G&A → Metals EBITDA proxy → Metals business value (× Metals EV / annualized cash contribution × achieved); SSOF gross grown from As of date; SSOF / Fuels stake values; net cash credited; equity; **Implied stock price - Model**; **Present stock price discounted - Model**
  - `SSOF monetization proceeds - Model` now uses grown `SSOF gross asset value - Model` at the monetization quarter (was flat Levers gross)
  - Valuation tab reads metals / SSOF / Fuels / equity / implied / present from QF at the reference quarter (single source of truth)
- **Data (Levers defaults):**
  - New: `SSOF value quarterly growth rate` **2** %/q (−5…5)
  - New: `Comstock Fuels value quarterly growth rate` **0** %/q (−5…5) — flat liquidation floor by default
  - Prior lever Values preserved (including SSOF value achieved 80)
- **Side effects:** No chart objects touched — **chart `Implied stock price - Model` (and optionally Present) manually in the Sheets UI**. Fingerprint refreshed.

### Repo

- `levers.py`, `layout.py`, `quarterly_model_formulas.py`, `valuation.py`, `financials_definitions.py`, `welcome.py`
- `scripts/sync_quarterly_valuation.py`, `live_fingerprint.json`

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
