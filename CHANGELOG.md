# Spreadsheet changelog

The live model is the Google Sheet **[Opendoor Model](https://docs.google.com/spreadsheets/d/1BhauTzGc9Nyt1J9gQl3NdCnpSSKCpSLbY9H7p5Obvc4)**. Git does not see those edits unless they are recorded here.

**After every agent write to the sheet, append an entry below before finishing.** One dated heading per change-set. Include formula edits, row/column insert/delete, and data changes — not only “big” features.

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

## 2026-08-28 — Label-based model formula restore (anti-regression)

Re-applied all `* - Model` formulas from `sheets/weekly_model_formulas.py` using `{Label}` placeholders (no hardcoded weekly row numbers). Validation passed before restore.

- **Tab / range:** **Weekly Financials** model rows `B3:DY51` (rows 3, 9, 12, 15, 16, 18, 21, 23, 24, 27, 28, 30, 32, 34, 36, 37, 41, 44, 49, 51)
- **Insert/delete:** none
- **Formulas:** GAAP NI - Model = `{cp}-{opex}-{sbc_model}-{interest_model}-{da}-{tax}` (label-resolved); EPS - Model = GAAP NI ÷ Basic Shares Outstanding - Model; funnel + shares stack refreshed
- **Data:** none
- **Side effects:** none

### Repo

- **`sheets/labels.py`** — shared `insert_rows_before_label`, `write_quarterly_cells`
- **`scripts/validate_model_formulas.py`** — template + live label checks; `--offline` for CI
- **`scripts/restore_weekly_model_formulas.py`** — blocks restore if validation fails
- All row-insert scripts now use `sheets.labels` (no duplicate row lookups)

---

## 2026-08-28 — Fix SBC - Model: flat weekly run-rate (not cumulative)

**Stock Based Compensation - Model** was rolling forward as `prior week + $110M/13`, which is correct for stock levels but wrong for a weekly flow. That inflated **Share Count Adjustment - Model** (~$8.46M/13 → shares/week compounding each column).

- **Tab / range:** **Weekly Financials** `B34:DY34` (**Stock Based Compensation - Model**); **Share Count Adjustment - Model** refreshed via restore
- **Insert/delete:** none
- **Formulas:** `IF(N(actual)>0, actual, IF(wk="", "", 110000000/13))` — was `LET(prev, prior model, prev+110000000/13)`
- **Data:** none
- **Side effects:** GAAP NI - Model SBC term also fixed (uses model row)

### Repo

- **`sheets/formulas.py`** — `weekly_sbc_model_formula` uses flat run-rate

---

## 2026-08-28 — Stock Based Compensation - Model row

Separated reported SBC from forward modeling. Removed **$110M** guidance placeholders from **Quarterly Financials** 2026 Q3–Q4 (not reported actuals). New model row uses the spread actual when present; otherwise rolls forward at **$110M ÷ 13** per week (~**$8.46M**).

- **Tab / range:** **Weekly Financials** — inserted R34 **Stock Based Compensation - Model** `B34:DY34`; **Quarterly Financials** — label row inserted before Basic Shares; cleared **F34**, **G34** (2026 Q3–Q4 SBC)
- **Insert/delete:** 1 row on Weekly + Quarterly before **Basic Shares Outstanding** (rows below shift +1)
- **Formulas:**
  - **Stock Based Compensation - Model:** `=IF(N(actual)>0, actual, IF(wk="", "", 110000000/13))` (flat weekly run-rate when no quarterly actual)
  - **Net Income (Loss) Attributable to Common Shareholders - Model:** SBC term `{col}33` → `{col}{sbc_model}`
  - **Share Count Adjustment - Model:** SBC dilution from model row (was actual row)
- **Data:** Quarterly **F34**, **G34** cleared (were $110M guidance guesses)
- **Side effects:** Basic Shares, share adjustment, GAAP NI - Model, EPS - Model row indices +1

### Repo

- **`sheets/formulas.py`** — `weekly_sbc_model_formula`, `SBC_MODEL_LABEL`
- **`sheets/weekly_model_formulas.py`** — SBC model restore + GAAP/share wiring
- **`scripts/add_sbc_model_row.py`** — live migration
- **`scripts/migrate_quarterly_financials.py`** — removed 2026 Q3–Q4 SBC from seed data

---

## 2026-08-28 — Fix GAAP NI - Model row refs after layout shifts

**Net Income (Loss) Attributable to Common Shareholders - Model** still subtracted hardcoded rows **41–43** (now Homes in Inventory - Model, Adjusted EBITDA, Net Interest actual) instead of **Net Interest Expense - Model**, **Depreciation and Amortization**, and **Taxes** (currently rows **44–46**).

- **Tab / range:** **Weekly Financials** `B49:DY49`
- **Insert/delete:** none
- **Formulas:** `={col}21-{col}32-{col}34-{col}41-{col}42-{col}43` → label-resolved `{cp}-{opex}-{sbc_model}-{interest_model}-{da}-{tax}` (no hardcoded row numbers)
- **Data:** none
- **Side effects:** `scripts/restore_weekly_model_formulas.py` re-applied

---

## 2026-08-28 — Shares tab + simplified share model (helper row)

Moved share assumptions off **Transitions** into a new **Shares** tab with a reusable event table. Simplified **Basic Shares Outstanding - Model** to actual passthrough or `prior week + adjustment`; weekly deltas live on **Share Count Adjustment - Model** (BYROW + SUM over `Shares!B5:G20` + SBC).

**Aug 2026 deal** (Form [8-K Aug 19, 2026](https://www.sec.gov/Archives/edgar/data/1801169/000114036126033739/ef20080596_8k.htm), [press release](https://investor.opendoor.com/news-releases/news-release-details/opendoor-reduces-shares-outstanding-5-first-ever-share-buyback)):
- **−45.3M** share repurchase @ **$3.49** (settlement Aug 19)
- **$650M** 0% converts, initial conversion **~$4.71** (~138M shares)
- Capped calls offset dilution through **$6.98**
- **$10.38 net-zero price**: convert dilution restores repurchased shares → **net Δ shares ≈ 0** below that level (convert row at **0% Fraction** in base case)

| Event | Mode | Max Δ | Fraction |
| --- | --- | --- | --- |
| Aug 2026 repurchase | instant | −45,300,000 | 100% |
| Nov 2025 warrants | spread_end (4 wks) | +99,295,146 | 25% |
| 2030 converts | instant @ maturity | +137,960,290 | 0% (base) |

- **Tab / range:** new **Shares** `A1:I8`, `A22:B24`; **Weekly Financials** row inserted → R35 **Share Count Adjustment - Model**, R36 **Basic Shares Outstanding - Model**, R50 **EPS - Model**; cleared **Transitions** `A25:B34`
- **Insert/delete:** 1 row on Weekly + Quarterly before Basic Shares - Model; 1 new sheet
- **Formulas:**
  - **Share Count Adjustment - Model:** `=LET(..., sbc + SUM(BYROW(FILTER(Shares!B5:G20, …))))`
  - **Basic Shares Outstanding - Model:** `=IF(N(actual)>0, actual, prev_model + adj)`
- **Data:** Shares event table as above; SBC price **$8** on `Shares!B2`
- **Side effects:** Add future buybacks/dilution by appending rows to **Shares** table (modes: `instant`, `spread_end`)

### Repo

- **`sheets/shares_events.py`** — table layout + formula builders
- **`scripts/setup_shares_sheet.py`** — live migration

---

## 2026-08-28 — Shares model: actual passthrough, roll-forward, buyback, warrant window

Reworked **Basic Shares Outstanding - Model** per user feedback:

1. **Actual passthrough** — if **Basic Shares Outstanding** is populated, model = actual (no overlay).
2. **Roll-forward** — else `prior week model + weekly deltas` (not base + cumulative overlay).
3. **Warrants** — assumed exercise spread over the last **4 weeks** before **11/20/2026** expiration (not linear from distribution).
4. **[Aug 2026 buyback](https://x.com/nejatian/status/2087844080579653833)** — **−5%** once on first week ending on/after **8/13/2026**; convert/capped-call **$10.38** floor documented on **Transitions!B34** (no incremental convert shares in base case).

- **Tab / range:** **Weekly Financials** `B35:DY35`; **Transitions** `A25:B34`; **Earnings per Share - Model** unchanged denominator row (label-resolved)
- **Insert/delete:** none
- **Formulas:** `IF(N(actual)>0, actual, LET(prev, prior model, prev + sbc + wDelta + bbAdj, …))`; `wDelta` only in `[exp−4wks, exp]`; `bbAdj = IF(wk>=bbDate AND prev_wk<bbDate, −prev×5%, 0)`
- **Data:** B29=4 (warrant window weeks); B32=8/13/2026; B33=0.05; B34=10.38 (reference)
- **Side effects:** Forward weeks with blank actuals now chain from prior model instead of going blank

### Repo

- **`sheets/formulas.py`** — `weekly_shares_model_formula` roll-forward logic
- **`scripts/update_shares_model_assumptions.py`** — refresh Transitions + restore

---

## 2026-08-28 — Basic Shares Outstanding - Model (warrants + SBC dilution)

Added **Basic Shares Outstanding - Model** below the actual shares row. **EPS - Model** now divides GAAP NI - Model by this row instead of the actual EOP-interpolation row.

Management has **not** published a forward basic share-count guide. The Nov 2025 **warrant distribution** (99.3M warrants, $9/$13/$17, expire Nov 20 2026) is the main disclosed dilution lever (~10.4% if all exercised). Model overlays (editable on **Transitions**):

| Cell | Default | Meaning |
| --- | --- | --- |
| B25 | 99,295,146 | Warrant shares if exercised |
| B26 | 25% | Assumed exercise fraction (not company guidance) |
| B27 / B28 | 11/21/2025 / 11/20/2026 | Warrant ramp window |
| B31 | $8 | $/share to convert weekly SBC into incremental shares |

- **Tab / range:** **Weekly Financials** + **Quarterly Financials** — 1 row inserted before **Open Mortgage Percent**; **Basic Shares Outstanding - Model** `B35:DY35`; **Earnings per Share - Model** `B49:DY49`; **Transitions** `A25:B31`
- **Insert/delete:** 1 row on Weekly + Quarterly tabs
- **Formulas:**
  - **Basic Shares Outstanding - Model:** `base` = **Basic Shares Outstanding** (EOP Δ/13 when reported) + linear warrant ramp (`B25×B26` over B27→B28) + weekly `SBC/B31` after distribution date
  - **Earnings per Share - Model:** `=IF(N({col}35)=0,"",{col}47/{col}35)` → `=IF(N({col}{shares_model})=0,"",{col}{gaap_ni}/{col}{shares_model})`
- **Data:** Transitions dilution defaults as above
- **Side effects:** Rows below shares shift +1 (GAAP NI - Model, EPS - Model, etc.)

### Repo

- **`sheets/formulas.py`** — `weekly_shares_model_formula`, `SHARES_MODEL_LABEL`
- **`sheets/weekly_model_formulas.py`** — shares model + EPS denominator by label
- **`scripts/add_basic_shares_model_row.py`** — migration
- **`RESOURCES.md`** — warrant / share-count notes

---

## 2026-08-28 — EPS - Model: guard blank Basic Shares

**Earnings per Share - Model** could `#DIV/0!` when **Basic Shares Outstanding** was blank (pre-report / boundary weeks) because the guard only tested `=0`.

- **Tab / range:** **Weekly Financials** `B48:DY48` (**Earnings per Share - Model**)
- **Insert/delete:** none
- **Formulas:** `=IF({col}34=0,"",{col}46/{col}34)` → `=IF(N({col}34)=0,"",{col}46/{col}34)` (`N()` treats blank as 0 before dividing)
- **Data:** none
- **Side effects:** `scripts/restore_weekly_model_formulas.py` re-applied to live sheet

---

## 2026-08-28 — GAAP net income rows; EPS - Model = GAAP NI ÷ basic shares

**Earnings per Share - Model** was `(Contribution Profit − Adj OpEx − Net Interest) ÷ shares`, which approximated adjusted net income, not GAAP EPS. Added GAAP net income rows and rewired the model to match the company definition: **Net Income (Loss) Attributable to Common Shareholders ÷ Basic Shares Outstanding** (basic weighted-average).

- **Tab / range:** **Weekly Financials** and **Quarterly Financials** — inserted 2 rows before **Earnings per Share** (now R45–R48 weekly, R46–R49 quarterly); **Basic Shares Outstanding** `B34:DY34` formulas refreshed to reference quarterly EOP shares on **R50** (was hardcoded R48)
- **Insert/delete:** 2 rows on each tab before **Earnings per Share**
- **Formulas:**
  - **Net Income (Loss) Attributable to Common Shareholders** (actual): day-weighted quarterly spread ÷13 (same pattern as other dollar rows)
  - **Net Income (Loss) Attributable to Common Shareholders - Model:** `={col}21-{col}32-{col}33-{col}41-{col}42-{col}43` (Contribution Profit − Adj OpEx − SBC − Net Interest − D&A − Taxes)
  - **Earnings per Share - Model:** `=IF({col}34=0,"",{col}{gaap_ni_model}/{col}34)` — was `=IF({col}34=0,"",({col}21-{col}32-{col}41-{col}42-{col}43)/{col}34)`
- **Data (Quarterly Financials, GAAP net loss = basic EPS × basic weighted-average shares):**

| Quarter | GAAP net income |
| --- | --- |
| 2025 Q3 | −$89,032,680 |
| 2025 Q4 | −$1,095,975,720 |
| 2026 Q1 | −$172,679,760 |
| 2026 Q2 | −$164,182,600 |

- **Side effects:** **Shares Outstanding (Quarter End)** moved to quarterly **R50**. Load scripts and `update_weekly_quarterly_spread.py` resolve EOP row by label.

### Repo

- **`sheets/weekly_model_formulas.py`** — GAAP NI - Model + EPS - Model formulas (label-based row refs)
- **`scripts/update_weekly_quarterly_spread.py`** — spread GAAP NI actual row; pass dynamic EOP row to shares interpolation
- **`scripts/add_gaap_net_income_rows.py`** — one-time migration (row insert + data + formula refresh)
- **`scripts/load_quarter_2025_q3.py`**, **`scripts/load_quarters_2025_q4_2026_h1.py`** — GAAP NI values; EPS on R48; EOP by label

---

## 2026-08-28 — Inventory & shares blank until both quarters reported

Applied the same **bothQ** guard used on day-weighted spread rows to the linear `Δ/13` interpolation rows for **Homes in Inventory** and **Basic Shares Outstanding**. Values stay blank when the current quarter’s quarterly cell (or the prior quarter’s, when `qCol>1`) is missing, a formula, or empty.

- **Tab / range:** **Weekly Financials** `C37:DY37` (Homes in Inventory), `C34:DY34` (Basic Shares Outstanding); `B37` / `B34` anchors unchanged
- **Insert/delete:** none
- **Formulas:** added `qEndHas`, `qStartHas`, `bothQ`, and `IF(OR(wk="",NOT(bothQ)),"", prev+delta)` wrapper; `delta` remains `(qEnd-qStart)/13`
- **Data:** none
- **Side effects:** Q-boundary and pre-report weeks (e.g. column **AR** onward before Q3 load) now blank on these rows instead of partial ramps

### Repo

- **`sheets/formulas.py`** — `weekly_inventory_formula`, `weekly_shares_formula`, shared `_quarterly_index_has_data`
- **`scripts/update_weekly_quarterly_spread.py`** — re-applied to live sheet

---

## 2026-08-27 — Boundary weeks blank until both quarters reported

Quarter-spanning weeks (e.g. week ending **7/4/2026**, 2 days in Q2 + 5 in Q3) previously showed a **partial** spread from the prior quarter alone when the new quarter had no hardcoded actuals yet — causing sudden dips on **Homes Chart** and **Money Chart**.

- **Tab / range:** **Weekly Financials** day-weighted spread rows — `B8:DY8`, `B14:DY14`, `B17:DY17`, `B19:DY19`, `B20:DY20`, `B22:DY22`, `B29:DY29`, `B31:DY31`, `B33:DY33`, `B39:DY45`
- **Insert/delete:** none
- **Formulas:** added `qEndHas`, `qStartHas`, `bothQ` to the LET; final guard is now `IF(OR(NOT(bothQ), blend=0), "", blend)` where `bothQ = IF(qStartKey=qEndKey, TRUE, AND(qEndHas, qStartHas))` and each `*Has` requires a non-formula, non-empty quarterly cell. Single-quarter weeks unchanged; boundary weeks stay blank until **both** adjacent quarters have reported actuals.
- **Data:** none
- **Side effects:** column **AR** (week ending 7/4/2026) and similar boundary columns should now be blank instead of ~2/7 of the prior quarter; charts lose the artificial Q-boundary drops.

### Repo

- **`sheets/formulas.py`** — `weekly_day_weighted_quarterly_formula`
- **`scripts/update_weekly_quarterly_spread.py`** — re-applied to live sheet

---

## 2026-08-27 — Weekly ASP pulls from Quarterly Financials with carry-forward

Replaced hardcoded **377,500** on **Weekly Financials** row 13 with formulas that use the matching quarter’s ASP from **Quarterly Financials** when populated, otherwise the prior week’s value.

- **Tab / range:** **Weekly Financials** `B13:DY13`
- **Insert/delete:** none
- **Formulas:** hardcoded `377500` →

```
=LET(
  wk, B$1,
  qKey, IF(wk="", "", YEAR(wk)&" Q"& ROUNDUP(MONTH(wk)/3, 0)),
  qCol, IFERROR(MATCH(qKey, 'Quarterly Financials'!$B$1:$1, 0), 0),
  qAsp, IF(qCol=0, "", INDEX('Quarterly Financials'!$B$14:$M$14, 1, qCol)),
  IF(wk="", "", IF(qAsp="", 377500, qAsp))
)
```

Column **C** onward uses `{prev_col}13` instead of `377500` when `qAsp` is blank (carry forward last ASP). Quarter keyed off week-ending date (not day-weighted).

- **Data:** Q3 2025 weeks now show ≈ **$356K** ASP (from quarterly revenue ÷ home sales); Q4 ≈ **$372K**; forward quarters follow quarterly row 14 when loaded.
- **Side effects:** `sheets/formulas.py` — `weekly_asp_formula()`; `scripts/update_weekly_quarterly_spread.py` applies ASP row on refresh.

---

Compared live **Weekly Financials** `* - Model` rows to `scripts/restore_weekly_model_formulas.py` and found several formulas out of date after the earlier restore used older CHANGELOG templates. Added canonical source `sheets/weekly_model_formulas.py` (label-based row lookup; column-relative generation for P&L rows). **No live sheet writes** — repo-only update.

- **Tab / range:** n/a (git only)
- **Insert/delete:** none
- **Formulas captured (current live sheet):**
  - **R3 Acquisition Contracts - Model:** `={col}6*{col}4` (was missing from restore script)
  - **R12 New Listings - Model:** purchase lag on `$9×$10` + unlisted backlog (`Transitions!B21` / `B23:I23`); was missing
  - **R15 Private Home Sales - Model:** purchases × `(1 − Likelihood to List)` × private close curve — **not** `Transitions!B6 × …`; seed **15** not 90
  - **R16 Home Sales - Model:** listed lag × `$10` + `$15` private sales — was missing
  - **R9, R18:** unchanged (match prior restore)
  - **R21, R23, R32, R46:** column-relative P&L stack (already fixed)
  - **R30, R41:** `35000000/13`, `20000000/13`
  - **R38 Homes in Inventory - Model:** anchor **3275** in B; `={prev}+if({col}8<>"",…,{col}9)−if({col}14<>"",…,{col}16)` from C
  - **R24–28 CM stack:** core values B–E; ramp `={prev}24+{col}28` from F; adjustments −3% (B–G) / −2% (H+); improvement **0.05%** from F
- **Data:** inventory anchor 3275; CM adjustment/improvement hardcoded values as above
- **Side effects:** `scripts/restore_weekly_model_formulas.py` now imports from `sheets/weekly_model_formulas.py`. README notes restore command and private-sales encoding.

---

Batch API writes duplicated column **B** refs across every column on P&L model rows (Sheets does not auto-adjust refs like fill-down). Regenerated per-column formulas on **Weekly Financials** `B21:DY21`, `B23:DY23`, `B32:DY32`, `B46:DY46`.

- **Tab / range:** **Weekly Financials** rows 21, 23, 32, 46 (`B:DY`)
- **Insert/delete:** none
- **Formulas:** e.g. `B21` `=B18*B23` → `C21` `=C18*C23`, `D21` `=D18*D23`, …; same pattern for R23 (CM stack sum), R32 (`={col}30+(15000000/13)`), R46 (`=IF({col}34=0,"",({col}21-{col}32-{col}41)/{col}34)`)
- **Data:** none
- **Side effects:** `scripts/restore_weekly_model_formulas.py` now emits column-specific formulas for these rows.

---

## 2026-08-27 — Restore Weekly Financials model row formulas

Reconstructed `* - Model` row formulas cleared when spread cleanup removed mistaken quarterly spread patterns from model rows. Funnel/revenue rows restored from prior CHANGELOG and agent transcript templates (row refs updated for deleted row 1). P&L model rows reconstructed from README stack logic where originals were not recoverable.

- **Tab / range:** **Weekly Financials** `B9:DY9`, `B15:DY15`, `B18:DY18`, `B21:DY21`, `B23:DY23`, `B30:DY30`, `B32:DY32`, `B41:DY41`, `B46:DY46`; **Contribution Margin - Core** ramp `F24:DY24` (`=E24+F28`, `=F24+G28`, …)
- **Insert/delete:** none
- **Formulas:**
  - **R9 Homes Purchased - Model:** SUMPRODUCT over 9-week purchase lag using contracts `$2/$3`, L2C `$7`, `Transitions!$B$2:$J$2`
  - **R15 Private Home Sales - Model:** `Transitions!$B$6` × SUMPRODUCT over purchases `$8/$9`, `Transitions!$B$19:$J$19`
  - **R18 Revenue - Model:** financed + cash listing revenue lags (`Transitions!$B$14`/`$B$15`/`$B$16`) plus private sales tail `$15×$13`
  - **R23 Contribution Margin - Model:** `=B24+B25+B26+B27`
  - **R21 Contribution Profit - Model:** `=B18*B23`
  - **R30 Fixed Costs - Model:** `=35000000/13` (~$35M/qtr accountability run-rate)
  - **R32 Adjusted Operating Expenses - Model:** `=B30+(15000000/13)` (fixed + ~$15M/qtr variable ops/marketing)
  - **R41 Net Interest Expense - Model:** `=20000000/13` (placeholder ~$20M/qtr)
  - **R46 Earnings per Share - Model:** `=IF(B34=0,"",(B21-B32-B41)/B34)` (placeholder ANI build from model rows)
- **Data:** none (formula-only restore)
- **Side effects:** Repeatable script `scripts/restore_weekly_model_formulas.py`. Col F spot-check (full Q3 2025 week): Homes Purchased - Model ≈ 101, Private Home Sales - Model ≈ 22.5, Revenue - Model ≈ $88.7M, Contribution Profit - Model ≈ −$358K, EPS - Model ≈ −$0.0078.

---

## 2026-08-27 — Fix weekly spread formulas after row 1 delete

Deleting unused **Weekly Financials** row 1 moved **Week Ending** from row 2 → row 1 and shifted all metric labels up one row, but spread formulas still referenced `B$2` (now acquisition contracts, not dates) and used **weekly row numbers** for `OFFSET('Quarterly Financials'!$B$n…)` instead of the **quarterly** row (which stayed aligned to the old numbering).

### Root cause

| Issue | Symptom |
| --- | --- |
| `wk,B$2` | Week key derived from contract counts → blank/error |
| `OFFSET(…$B$20…)` on weekly R20 Contribution Profit | Pulled **Gross Profit** (quarterly R20), not Contribution Profit (R21) |
| Spread formula on **Basic Shares Outstanding** | Wrong pattern entirely (should interpolate from row 48 EOP shares, not ÷13 spread) |

### Code / sheet fixes

- **`sheets/formulas.py`:** `WEEK_DATE_ROW = 1`; spread helpers take `quarterly_row`; inventory/shares interpolation uses dynamic weekly row refs (`{prev_col}{weekly_row}`).
- **`scripts/update_weekly_quarterly_spread.py`:** resolves rows by **label** on Weekly vs Quarterly tabs (survives future row insert/delete); clears spread formulas that landed on `* - Model` rows; refreshes inventory interpolation.
- Re-ran script — restored spread rows: Contribution Profit (R20), Basic Shares (R34), Homes in Inventory (R37), Net Interest (R40), Taxes (R43), Adjusted Net Income (R44), Earnings per Share (R45).

### Weekly Financials — spot-check (col F, full Q3 2025 week)

| Row | Value |
| --- | --- |
| Contribution Profit | ≈ $1.54M / week ($20M ÷ 13) |
| Earnings per Share | ≈ −$0.0092 / week (−$0.12 ÷ 13) |
| Basic Shares Outstanding | ramping toward Q3 EOP |

### Side effects

- **Model rows** that had mistaken quarterly spread formulas (`* - Model` on rows 9, 15, 18, 21, 23, 30, 32, 41, 46) were cleared; restored in a follow-up change-set (see **Restore Weekly Financials model row formulas** above).

---

## 2026-08-27 — 2025 Q4, 2026 Q1, 2026 Q2 earnings actuals load

Loaded and verified **2025 Q4** (`Quarterly Financials!C`), **2026 Q1** (`!D`), and **2026 Q2** (`!E`) from Open House supplements and 10-Q / 8-K filings. Filled P&L stack rows that were blank after the Q3 load; added missing **Home Sales** for 2026 Q1–Q2. Repeatable script: `scripts/load_quarters_2025_q4_2026_h1.py`.

### Reviewed rows (already populated — confirmed)

| Row | Label | 2025 Q4 | 2026 Q1 | 2026 Q2 | Source |
| --- | --- | --- | --- | --- | --- |
| 3 | Acquisition Contracts | 2,557 (formula) | 4,924 | 7,014 | Sum of weekly actuals on **Weekly Financials** |
| 9 | Homes Purchased | 1,706 | 2,474 | 4,378 | Earnings supplement — *Non-GAAP Measures & Key Metrics* |
| 12 | New Listings | 0 | 726 | 2,867 | Weekly sum (Open Tracker starts Feb 2026; Q4 2025 has no weekly new-list counts) |
| 18 | Revenue | $736M | $720M | $883M | GAAP revenue, 10-Q / 8-K |
| 30 | Fixed Costs | $35M | $33M | $35M | Segment table — *Fixed operating expense* |
| 32 | Adjusted Operating Expenses | $50M | $63M | $55M | Non-GAAP opex reconciliation |
| 38 | Homes in Inventory | 2,867 | 3,420 | 5,459 | Quarter-end inventory, earnings supplement |
| 21 | Contribution Profit | — | — | $51M | Already loaded for Q2 only; Q4/Q1 added below |

### New / updated quarterly data

| Row | Label | 2025 Q4 | 2026 Q1 | 2026 Q2 | Notes |
| --- | --- | --- | --- | --- | --- |
| 15 | Home Sales | 1,978 | 1,921 | 2,339 | Earnings supplement |
| 20 | Gross Profit | $57M | $72M | $86M | GAAP gross profit |
| 21 | Contribution Profit | $7M | $32M | (unch.) | Non-GAAP |
| 23 | Contribution Margin | 1.0% | 4.4% | 5.8% | Stored as 0.01 / 0.044 / 0.058 |
| 34 | Stock Based Compensation | $108M | $123M | $122M | SBC + market RSUs + IDSW amort (Q4 was $105M → $108M to match Q3 convention) |
| 35 | Basic Shares Outstanding | 869,822,000 | 959,332,000 | 965,780,000 | Basic weighted-average (thousands × 1,000) |
| 40 | Adjusted EBITDA | $(43)M | $(31)M | $(4)M | Non-GAAP highlights |
| 41 | Net Interest Expense | $15M | $13M | $21M | EBITDA bridge: property financing + other − interest income |
| 43 | Depreciation and Amortization | $5M | $5M | $5M | D&A excl. intangibles |
| 44 | Taxes | $1M | $0 | $0 | GAAP / bridge income tax expense |
| 45 | Adjusted Net Income | $(62)M | $(49)M | $(30)M | Adjusted net **loss** |
| 46 | Earnings per Share | $(1.26) | $(0.18) | $(0.17) | GAAP basic net loss per share |
| 48 | Shares Outstanding (Quarter End) | 957,245,487 | 963,283,777 | 968,626,958 | Balance sheet common shares at quarter end |

### Weekly Financials

- **Tab / range:** refreshed day-weighted spread formulas on rows 9, 15, 18, 20, 21, 23, 30, 32, 34, 35, 40, 41, 43, 44, 45, 46 via `update_weekly_quarterly_spread.py`
- **Insert/delete:** none
- **Side effects:** Q4 2025 EPS now spreads ÷13 day-weighted like other dollar rows (was quarterly copy only before Q3 load extended EPS spread)

---

## 2026-08-27 — Day-weighted quarterly spread (+ EPS ÷ 13)

Calendar quarters in the weekly grid are not always exactly 13 columns — boundary weeks straddle two quarters (e.g. week ending 10/4/2025 has 3 days in 2025 Q3 and 4 in 2025 Q4). Replaced the single-quarter `÷13` lookup with a **day-weighted blend** so one formula works everywhere.

### Weekly Financials — spread formulas (`B9:DY9`, `B15:DY15`, `B18:DY18`, `B21:DY21`, `B30:DY30`, `B32:DY32`, `B34:DY34`, `B20:DY20`, `B40:DY45`, **`B46:DY46`**)

**Before:** use week-ending date’s quarter only → `quarterly / 13`.

**After:** for the 7-day window ending on row 2, count days in each calendar quarter; blend each quarter’s `÷13` rate by `days / 7`:

```
=LET(
  wk, B$2,
  ws, wk-6,
  qEndKey, IF(wk="", "", YEAR(wk)&" Q"& ROUNDUP(MONTH(wk)/3, 0)),
  qStartKey, IF(wk="", "", YEAR(ws)&" Q"& ROUNDUP(MONTH(ws)/3, 0)),
  qEndCol, IFERROR(MATCH(qEndKey, 'Quarterly Financials'!$B$1:$1, 0), 0),
  qStartCol, IFERROR(MATCH(qStartKey, 'Quarterly Financials'!$B$1:$1, 0), 0),
  daysEnd, SUM(MAP(SEQUENCE(7), LAMBDA(i, --(YEAR(wk-7+i)&" Q"& ROUNDUP(MONTH(wk-7+i)/3, 0)=qEndKey)))),
  daysStart, 7-daysEnd,
  blend, (daysEnd/7)*(qEndAmt) + (daysStart/7)*(qStartAmt),
  ...
)
```

Where `qEndAmt` / `qStartAmt` = `OFFSET(...)/13` when the quarterly cell is a hardcoded value (blank if formula or empty). Example week ending **10/4/2025** revenue ≈ **$62.5M** = `3/7×($915M/13) + 4/7×($736M/13)`.

**Earnings per Share (row 46):** moved from “copy quarterly EPS to each week” into the same **÷13 day-weighted spread** as other dollar rows (`-0.12` → ≈ **-$0.0092**/week in full Q3 weeks).

**Contribution Margin (row 23):** day-weighted **blend without ÷13** (rates, not dollars). Boundary weeks with only one quarter populated show that quarter’s rate × its day fraction (e.g. ≈1% when 3/7 × 2.2% and Q4 still blank).

### Repo

- **`sheets/formulas.py`** — shared formula builders
- **`scripts/update_weekly_quarterly_spread.py`** — apply / refresh spread rows on **Weekly Financials**
- **`scripts/migrate_quarterly_financials.py`**, **`scripts/load_quarter_2025_q3.py`** — import shared formulas

### Notes

- Divisor stays **13** per quarter (nominal weekly rate). Calendar quarters sum to ~**12.86–13.14** day-weighted “week equivalents,” so totals reconcile within ~±2% once both adjacent quarters are populated; boundary weeks before the next quarter is loaded only allocate the populated quarter’s day share.
- **Homes in Inventory** (row 38) and **Basic Shares Outstanding** (row 35) still use the prior linear `Δ/13` interpolation — unchanged.

---

## 2026-08-27 — 2025 Q3 earnings actuals load

Loaded and verified **2025 Q3** (`Quarterly Financials!B`, quarter ending 9/30/2025) from the Q3 2025 Open House (Ex. 99.1, filed Nov 2025) and Form 10-Q. Added weekly spread / interpolation formulas for rows that were previously blank. Repeatable script: `scripts/load_quarter_2025_q3.py`.

### Reviewed rows (already populated — confirmed)

| Row | Label | Value | Source |
| --- | --- | --- | --- |
| 3 | Acquisition Contracts | 390 (formula) | Sum of weekly actuals on **Weekly Financials** (`131+132+127`). Horizon starts 2025-09-13, so this is **not** a full-quarter contract count — no Jul/Aug weeks in the model and Open Tracker starts Feb 2026. |
| 9 | Homes Purchased | 1,169 | Earnings supplement — *Non-GAAP Measures & Key Metrics* |
| 15 | Home Sales | 2,568 | Same |
| 18 | Revenue | $915,000,000 | GAAP revenue, 10-Q |
| 30 | Fixed Costs | $37,000,000 | 10-Q Note 14 segment table — *Fixed operating expense* |
| 32 | Adjusted Operating Expenses | $53,000,000 | Q3 2025 earnings call / 10-Q non-GAAP opex metric (marketing + operations + fixed, ex direct selling/holding in CM bridge) |
| 38 | Homes in Inventory | 3,139 | Quarter-end inventory, earnings supplement |

### New quarterly data (`Quarterly Financials!B`)

| Row | Label | Value | Source / method |
| --- | --- | --- | --- |
| 20 | Gross Profit | $66,000,000 | GAAP gross profit, 10-Q |
| 21 | Contribution Profit | $20,000,000 | Non-GAAP contribution profit reconciliation |
| 23 | Contribution Margin | 2.2% (`0.022`) | Contribution profit ÷ revenue |
| 34 | Stock Based Compensation | $31,000,000 | ANL reconciliation add-backs: SBC $13M + market-condition RSUs $14M + IDSW amort $4M (matches model convention; Q4 uses same sum-of-lines approach) |
| 35 | Basic Shares Outstanding | 741,939,000 | Basic **weighted-average** shares (741,939 reported in thousands), 10-Q |
| 40 | Adjusted EBITDA | $(33,000,000) | Non-GAAP highlights |
| 41 | Net Interest Expense | $22,000,000 | EBITDA bridge: property financing $23M + other interest $11M − interest income $12M |
| 43 | Depreciation and Amortization | $5,000,000 | EBITDA bridge — D&A excluding intangibles |
| 44 | Taxes | $1,000,000 | GAAP / bridge income tax expense |
| 45 | Adjusted Net Income | $(61,000,000) | Adjusted net **loss**, Non-GAAP |
| 46 | Earnings per Share | $(0.12) | GAAP basic net loss per share, 10-Q |
| 48 | Shares Outstanding (Quarter End) | 771,534,057 | Balance sheet common shares outstanding at 9/30/2025 (for weekly interpolation only) |

### Quarterly Financials — row 48 (new helper row)

- **Tab / range:** `A48`, `B48` (2025 Q3 EOP shares)
- **Insert/delete:** none (used empty row 48 on **Quarterly Financials** only; **Weekly Financials** row indices unchanged)
- **Data:** label `Shares Outstanding (Quarter End)`; Q3 value 771,534,057 from 9/30/2025 balance sheet. Prior-quarter anchor for interpolation when `qCol=1`: 733,592,980 (6/30/2025 10-Q).

### Weekly Financials — new / extended formulas

**Dollar rows (quarterly hard value ÷ 13)** — same LET template as existing spread rows, applied across `B20:DY20`, `B40:DY40`, `B41:DY41`, `B43:DY43`, `B44:DY44`, `B45:DY45` (and refreshed `B9:DY9`, `B15:DY15`, `B18:DY18`, `B21:DY21`, `B30:DY30`, `B32:DY32`, `B34:DY34`):

```
=LET(
  wk, B$2,
  qKey, IF(wk="", "", YEAR(wk)&" Q"& ROUNDUP(MONTH(wk)/3, 0)),
  qCol, IFERROR(MATCH(qKey, 'Quarterly Financials'!$B$1:$1, 0), 0),
  qCell, IF(qCol=0, "", OFFSET('Quarterly Financials'!$B$20, 0, qCol-1)),
  IF(qCol=0, "", IF(ISFORMULA(qCell), "", IF(qCell="", "", qCell/13)))
)
```

**Rate / per-share rows (quarterly value copied, no ÷13)** — `B23:DY23`, `B46:DY46`:

```
=LET(..., IF(qCol=0, "", IF(ISFORMULA(qCell), "", qCell)))
```

**Basic Shares Outstanding (`B35:DY35`)** — linear ramp from prior quarter-end shares to current quarter-end (`Quarterly Financials` row 48), +Δ/13 per week (same pattern as inventory row 38):

- `B35` = 733,592,980 (Q2 2025 EOP anchor; hardcoded)
- `C35` onward: `=LET(..., prevCol35 + (qEnd - qStart) / 13)`

### Q3 2025 weekly spot-check (cols B–D, weeks ending 9/13–9/27)

| Row | Weekly value |
| --- | --- |
| Gross Profit | ≈ $5.08M / week ($66M ÷ 13) |
| Contribution Profit | ≈ $1.54M / week |
| Contribution Margin | 2.2% |
| SBC | ≈ $2.38M / week |
| Shares | 733.6M → 739.4M (3-week ramp toward 771.5M EOP) |

### Future quarter checklist

1. Pull GAAP + Non-GAAP tables from the earnings supplement and 10-Q (links in `RESOURCES.md`).
2. Enter / verify volume + revenue rows (9, 15, 18, 38) and opex rows (30, 32).
3. Fill P&L stack rows 20–21, 23, 34–35, 40–41, 43–46; add **row 48** quarter-end shares from the balance sheet.
4. Acquisition contracts: enter weekly on **Weekly Financials** if available; else leave quarterly formula blank or hardcode if an external source exists.
5. Run or adapt `scripts/load_quarter_2025_q3.py` for formula rows; append this changelog.

---

## 2026-08-27 — Weekly / Quarterly Financials split

Separate quarterly inputs from the weekly time series. **Weekly Home Activity** renamed to **Weekly Financials**. New **Quarterly Financials** tab holds quarter-level actuals and aggregates weekly data where appropriate.

### Weekly Financials (renamed from Weekly Home Activity)

- **Tab / range:** sheet rename only; row layout unchanged (rows 2–47)
- **Formulas — quarterly-spread actuals** (`B9:DY9`, `B15:DY15`, `B18:DY18`, `B21:DY21`, `B30:DY30`, `B32:DY32`, `B34:DY34`): `=1169/13` (etc.) →

```
=LET(
  wk, B$2,
  qKey, IF(wk="", "", YEAR(wk)&" Q"& ROUNDUP(MONTH(wk)/3, 0)),
  qCol, IFERROR(MATCH(qKey, 'Quarterly Financials'!$B$1:$1, 0), 0),
  qCell, IF(qCol=0, "", OFFSET('Quarterly Financials'!$B$9, 0, qCol-1)),
  IF(qCol=0, "", IF(ISFORMULA(qCell), "", IF(qCell="", "", qCell/13)))
)
```

Template copied across each row’s former `/13` cells. When the matching **Quarterly Financials** cell is a **formula** (aggregated from weekly), the weekly cell stays blank for manual weekly entry. When it is a **hardcoded** quarterly report, weekly spreads `÷13`.

- **Formulas — Homes in Inventory** (`C38:DY38`; `B38` stays **3139**):

```
=LET(
  wk, E$2,
  qKey, YEAR(wk)&" Q"& ROUNDUP(MONTH(wk)/3, 0),
  qCol, MATCH(qKey, 'Quarterly Financials'!$B$1:$1, 0),
  qEnd, INDEX('Quarterly Financials'!$B$38:$M$38, 1, qCol),
  qStart, IF(qCol=1, qEnd, INDEX('Quarterly Financials'!$B$38:$M$38, 1, qCol-1)),
  D38+(qEnd-qStart)/13
)
```

Quarter-end inventory levels now live on **Quarterly Financials** row 38.

### Quarterly Financials (new sheet)

- **Tab / range:** `A1:L47`
- **Insert/delete:** new worksheet at index 1
- **Data — row 1:** quarter keys `2025 Q3` … `2028 Q1`
- **Data — row 2:** quarter-ending dates (e.g. `9/30/2025`, `12/31/2025`, …)
- **Data — rows 3–47:** same labels as **Weekly Financials** (row numbers aligned)
- **Data — hardcoded quarterly actuals migrated from old `/13` numerators:**

| Row | Label | Quarters populated |
| --- | --- | --- |
| 9 | Homes Purchased | 2025 Q3–2026 Q2 |
| 15 | Home Sales | 2025 Q3–Q4 |
| 18 | Revenue | 2025 Q3–2026 Q2 |
| 21 | Contribution Profit | 2026 Q2 |
| 30 | Fixed Costs | 2025 Q3–2026 Q2 |
| 32 | Adjusted Operating Expenses | 2025 Q3–2026 Q2 |
| 34 | Stock Based Compensation | 2025 Q4, 2026 Q3–Q4 |
| 38 | Homes in Inventory | quarter-end levels 2025 Q3–2026 Q2 |

- **Formulas — weekly-aggregated rows** (e.g. `B3` Acquisition Contracts):

```
=SUM(FILTER('Weekly Financials'!$B$3:$DY$3,
  MAP('Weekly Financials'!$B$2:$DY$2,
    LAMBDA(d, IF(d="", "", YEAR(d)&" Q"& ROUNDUP(MONTH(d)/3, 0)))) = B$1))
```

Same pattern on row 12 (New Listings). Other rows left blank.

### Side effects

- Charts on **Homes Chart** / **Money Chart** still reference sheet id 0 (now **Weekly Financials**); row indices unchanged.
- Repo docs updated (`README.md`, `RESOURCES.md`). Migration script: `scripts/migrate_quarterly_financials.py`.

---

## 2026-08-27 — Unlisted 1.0 backlog flush into listings

Finite pool of homes already owned at the horizon start (week ending 2025-09-13) that were not yet publicly listed under the old ~45-day reno wait. 2.0 lists them over the first 8 weeks. Already in inventory — not added to purchases. Not a standing add-on through March.

### Transitions

- **Tab / range:** `A21:J23` (below the private-sale curve)
- **Insert/delete:** none
- **Data:**
  - `A21` / `B21` = `Unlisted 1.0 Backlog at Horizon Start (homes)` / **450** (~5 extra weeks × Q3 2025 ~90 purchases/week)
  - `A22` / `B22:I22` = week indices 1…8
  - `A23` = `Percent of Unlisted Backlog Listed by Week`
  - `B23:I23` = `16% / 15% / 14% / 13% / 12% / 11% / 10% / 9%`
  - `J23` = `=SUM(B23:I23)` → **100%**
- **Side effects:** number format `B23:J23` = `0.00%`. Notes on `B21`, `A23`.

### Weekly Home Activity

- **Tab / range:** `B13:DY13` (New Listings - Model)
- **Insert/delete:** none
- **Formulas:** `B13:I13` hardcoded `80` replaced by the same purchase-lag SUMPRODUCT as `J13` (row 10 × Likelihood to List × Transitions row 4), plus backlog in weeks 1–8:

```
= SUMPRODUCT( … existing MAP / Transitions!$B$4:$J$4 … )
  + IF(COLUMN()-1<=8, Transitions!$B$21*INDEX(Transitions!$B$23:$I$23, 1, COLUMN()-1), 0)
```

Copied across `B13:DY13`. After week 8 (from `J13` / 2025-11-08) the IF is 0. Note on `A13`.

- **Data:** first 8 weeks listing model ≈ **162 → 117** (was 80); week 9 drops to organic **~76**. March 2026 listing model unchanged.

---

## 2026-08-27 — Private sales purchase-to-close curve

Never-listed homes (~25% of purchases) already reduced listings but never flowed into **Home Sales - Model**. They now have their own 9-week purchase → close curve and are added into modeled sales and revenue.

### Transitions

- **Tab / range:** `A18:K19` (new block below cash-mix rows; listing-to-sold refs `$B$10` / `$B$12` / `$B$14`–`$B$16` unchanged)
- **Insert/delete:** none
- **Data:**
  - `A18` = `Weeks from Purchase to Private Sale Close`; `B18:J18` = 1…9
  - `A19` = `Percent of Private Completions Sold by Week`
  - `B19:J19` = `0% / 2% / 6% / 12% / 18% / 20% / 18% / 14% / 10%` (mean lag ≈ 6.1 weeks)
  - `K19` = `=SUM(B19:J19)` → **100%**
  - `B6` left at **25%** (now used). Complements listing translation row 4 (75%).
- **Formulas:** none on existing rows
- **Side effects:** number format `B19:K19` = `0.00%`. Notes on `A19`, `B19`, `B6`.

### Weekly Home Activity

- **Insert/delete:** 1 row at row 16 (`sheetId` 0, `startIndex` 15, `endIndex` 16). Rows 16+ shifted +1. Format inherited from Home Sales - Model, then overwritten.

| Row after insert | Label |
| --- | --- |
| 15 | Home Sales |
| 16 | **Private Home Sales - Model** (new) |
| 17 | Home Sales - Model |
| 18 / 19 | Revenue / Revenue - Model |
| 38 / 39 | Homes in Inventory / Homes in Inventory - Model |

#### Private Home Sales - Model (`B16:DY16`)

```
=(Transitions!$B$6*SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 90,
        IF(INDEX($9:$9, 1, col) = "",
          INDEX($10:$10, 1, col),
          INDEX($9:$9, 1, col)
        )
      )
    )
  )),
  Transitions!$B$19:$J$19
))
```

Purchases: actual else model. Pre-horizon stub `90` (same as listings). Copied across `B16:DY16`. Note on `A16`.

#### Home Sales - Model (`B17:DY17`)

**Before** (old row 16; listings only):

```
=(SUMPRODUCT( … 21-week listing lag … , Transitions!$B$10:$V$10))
```

**After:** same listed SUMPRODUCT **+** `INDEX($16:$16, 1, COLUMN())`. Listing stub still `200`.

#### Revenue - Model (`B19:DY19`)

**Before** (old row 18): listed revenue × cash/financed close lags × price retention.

**After:** same listing revenue **+** `INDEX($16:$16, 1, COLUMN())*INDEX($14:$14, 1, COLUMN())` (private sales × ASP; no extra close lag, no DOM decay).

#### Inventory - Model

Auto-shifted with the insert. `C39` (and copies) is `=B39+if(C9<>"",C9,C10)-if(C15<>"",C15,C17)`. `B39` start inventory still `3275`.

### Charts

Homes Chart sales series now rows 15 and 17 (Home Sales / Home Sales - Model). Money Chart revenue series now rows 18 and 19. No manual chart edit.

### Calibration (left as levers)

Not refit. Spot-check: Q1 2026 modeled sales ≈ actual (−16). Q2 2026 model is higher (buy ramp + faster private path); edit `B6` / `B19:J19` to restress.

---

## 2026-08-26 — Likelihood to Close (cohort conversion)

Split contract **timing** from **attrition**. Each week-ending column is a contract cohort with its own close probability (seller cancel + Opendoor walking the deal). Purchase lag weights no longer embed a 31% residual.

### Weekly Home Activity

**Inserted 1 row at row 8** (`sheetId` 0, `startIndex` 7, `endIndex` 8). Rows 8+ shifted +1. Copied number/text format from the operational-growth row, then overwrote.

| Row after insert | Label |
| --- | --- |
| 8 | **Likelihood to Close** (new) |
| 9 | Homes Purchased |
| 10 | Homes Purchased - Model |
| 11 | New Listings |
| 12 | New Listings - Model |
| 14 / 15 | Home Sales / Home Sales - Model |
| 16 / 17 | Revenue / Revenue - Model |
| 36 / 37 | Homes in Inventory / Homes in Inventory - Model |

Homes Chart and Money Chart series ranges shifted with the insert (listings → rows 10–12, sales → 13–15, revenue → 15–17). Acquisition contract series unchanged (rows 2–4).

#### Likelihood to Close (row 8) — data

Cohort P(this contract week becomes a purchase). Percent format `0.0%`.

| Range | Value | Role |
| --- | --- | --- |
| `A8` | `Likelihood to Close` | Label |
| `B8` | `78%` | 2025 anchor (22% cancel/walk) |
| `C8:Q8` | `=$B$8` | Rest of 2025 (through week ending 2025-12-27) |
| `R8:AD8` | `=$Q8+($AE8-$Q8)*k/14` for k = 1…13 | Q1 2026 linear ramp |
| `AE8` | `67%` | Q2 2026+ anchor (~33% cancel/walk); week ending 2026-04-04 |
| `AF8:DY8` | `=$AE$8` | Hold 67% through 2028-02-19 |

Pre-horizon lags in the purchase formula (`col < 2`) use `$B$8`.

Notes added on `A8`, `B8`, `AE8`.

#### Homes Purchased - Model (`B10:DY10`) — formulas

**Before** (old row 9; attrition inside Transitions row 2, which summed to 69%):

```
=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 130,
        IF(INDEX($3:$3, 1, col) = "",
          INDEX($4:$4, 1, col),
          INDEX($3:$3, 1, col)
        )
      )
    )
  )),
  Transitions!$B$2:$J$2
))
```

**After** (same lag structure; multiply each cohort by that week’s Likelihood to Close):

```
=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      contracts, IF(col < 2, 130,
        IF(INDEX($3:$3, 1, col) = "",
          INDEX($4:$4, 1, col),
          INDEX($3:$3, 1, col)
        )
      ),
      l2c, IF(col < 2, $B$8, INDEX($8:$8, 1, col)),
      contracts * l2c
    )
  )),
  Transitions!$B$2:$J$2
))
```

Copied across `B10:DY10`. Pre-horizon contract stub still `130`.

#### New Listings - Model (`J12:DY12`) — formulas

`B12:I12` left as hardcoded `80`.

**Before** (old `J11`; static cancel + private on contracts):

```
=(1-(Transitions!$B$5+Transitions!$B$6))*(
  IF(F3<>"", F3, F4)*Transitions!$C$4+
  IF(E3<>"", E3,E4)*Transitions!$D$4+
  IF(D3<>"",D3,D4)*Transitions!$E$4+
  IF(C3<>"", C3,D3)*Transitions!$F$4+
  IF(B3<>"", B3,B4)*Transitions!$G$4
)
```

**After** (private only in the outer factor; each lag × that cohort’s L2C). Same five-lag structure, including the existing `IF(C3<>"", C3, D3)` false-branch pattern:

```
=(1-Transitions!$B$6)*(
  IF(F3<>"", F3, F4)*F8*Transitions!$C$4+
  IF(E3<>"", E3, E4)*E8*Transitions!$D$4+
  IF(D3<>"", D3, D4)*D8*Transitions!$E$4+
  IF(C3<>"", C3, D3)*C8*Transitions!$F$4+
  IF(B3<>"", B3, B4)*B8*Transitions!$G$4
)
```

Relative column refs shift with the destination column (`J` uses `F`…`B`, `K` uses `G`…`C`, … `DY`). `Transitions!$B$5` is no longer referenced.

#### Inventory - Model (`C37:DY37`) — formulas

`B37` unchanged (`3275` starting inventory).

**Before** (old `C36`; inflow = contracts):

```
=B36+if(C3<>"",C3,C4)-if(C13<>"",C13,C14)
```

**After** (inflow = homes purchased, actual else model):

```
=B37+if(C9<>"",C9,C10)-if(C14<>"",C14,C15)
```

Copied across `C37:DY37` with the usual prior-column / current-column pattern.

### Transitions

#### Row 2 — rename + rescale (timing only)

- **A2** label: `Percent Translated Into Purchase` → `Percent of Closers Purchased by Week`
- **B2:J2** weights rescaled by `1/0.69` so they sum to 100% (same shape). `K2` remains `=sum(B2:J2)` and now equals `100%`.
- Number format `B2:K2` set to `0.00%`.
- Note on `A2`.

| Week from contract | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Before | 0% | 1% | 5% | 15% | 16% | 6% | 4% | 9% | 13% | **69%** |
| After | 0% | 1.45% | 7.25% | 21.74% | 23.19% | 8.70% | 5.80% | 13.04% | 18.84% | **100%** |

Exact after values: `0`, `0.01/0.69`, `0.05/0.69`, `0.15/0.69`, `0.16/0.69`, `0.06/0.69`, `0.04/0.69`, `0.09/0.69`, `0.13/0.69`.

#### Row 5 — unused, not deleted

`Percent Acquisitions Canceled` (`B5` = 18%) is no longer used by purchase or listing formulas. Value left in place as a historical 2025 tracker note. Note added on `A5`.

### Calibration (modeled vs actual homes purchased)

L2C path chosen to fit quarterly purchase actuals on the new 100% timing curve, with Q2 2026+ held at **67%** (the ~33% cancel/walk observation) rather than the slightly tighter 65% SSE minimum.

| Quarter | Actual | Model after | Delta |
| --- | --- | --- | --- |
| 2025 Q3 (3 stub weeks) | 270 | 304 | +13% |
| 2025 Q4 | 1,706 | 1,687 | −1.1% |
| 2026 Q1 | 2,474 | 2,479 | +0.2% |
| 2026 Q2 | 4,378 | 4,528 | +3.4% |

Q3 2025 is a short stub plus pre-horizon `130 × B8` lags; not fitted tightly. Edit `B8` / `AE8` to restress the path; Q1 2026 and the forward hold follow those two anchors.

### Repo docs (not the sheet)

- `README.md` — funnel, assumptions, inventory inflow
- `RESOURCES.md` — Open Tracker cancel note
- `.cursor/rules/spreadsheet-changelog.mdc` — require this changelog on future sheet writes
