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

## 2026-09-01 — Price (at Close): blank future weeks

- **Tab / range:** **Weekly Financials** `B80:DY80` (Price at Close)
- **Insert/delete:** none
- **Formulas:** `=IF(OR(col$1="",col$1>TODAY()),"",IFERROR(XLOOKUP(...),""))` — no price when week-ending date is after today
- **Data:** none
- **Side effects:** `sheets/price_history.py`; **Financials Definitions** note updated

## 2026-09-01 — Price History tab (fix blank Price cells)

Replaced per-column `GOOGLEFINANCE` on **Price (at Close)** with one daily-price spill and weekly `XLOOKUP` (avoids Google rate-limit blanks).

- **Tab / range:** new **Price History** `A1` spill + `G1` note; **Weekly Financials** `B80:DY80` (Price at Close)
- **Insert/delete:** new worksheet **Price History** (500×8 grid at index 8)
- **Formulas:**
  - **Price History** `A1`: `=GOOGLEFINANCE("OPEN","all",MIN(FILTER(weeks))-30,MIN(MAX(weeks),TODAY()),"DAILY")` — one spill (Date…Close in cols A–F)
  - **Price (at Close)** `B80`: `=IF(B$1="","",IFERROR(XLOOKUP(B$1,'Price History'!$A$2:$A,'Price History'!$E$2:$E,"",-1),""))` (copied across)
- **Data:** none
- **Side effects:** `sheets/price_history.py`, `scripts/setup_price_history.py`; `add_valuation_rows.py` ensures Price History; **Financials Definitions** note updated; `config/workbook_snapshot.json` updated

## 2026-09-01 — Sync repo from live spreadsheet (manual edits)

Ran `sync_repo_from_live_sheet.py --update-snapshot` after user manual workbook edits.

- **Tab / range:** read-only pull (no sheet writes)
- **Insert/delete:** none
- **Formulas:** none — model formula validation passed (live `* - Model` rows match repo templates)
- **Data:** verified in sync — CM seasonality (`sheets/cm_seasonality.py`), CM stack anchors (`sheets/weekly_model_formulas.py`), **Financials Definitions** notes (`sheets/financials_definitions.py`), and `config/workbook_snapshot.json` already matched live. Added `scripts/pull_financials_definitions_from_sheet.py` and wired it into sync for future note edits in the UI.
- **Side effects:** `README.md` workbook map documents **Financials Definitions**

## 2026-09-01 — Financials Definitions tab

New reference tab documenting every Weekly Financials row label with Opendoor-specific notes on sourcing and formulas.

- **Tab / range:** **Financials Definitions** `A1:B83` (new sheet at index 2)
- **Insert/delete:** new worksheet **Financials Definitions** (120×4 grid)
- **Formulas:** none
- **Data:** column A mirrors **Weekly Financials** labels (rows 1–83); column B holds field definitions (manual text). Definitions maintained in `sheets/financials_definitions.py`; re-run `scripts/setup_financials_definitions.py` after row-label changes.
- **Side effects:** `config/workbook_snapshot.json` updated with new tab name

## 2026-09-01 — Sync repo from live spreadsheet (manual chart edits)

User repointed **Money Charts** on the live workbook; pulled into git.

- **Tab / range:** read-only chart metadata pull (no sheet writes)
- **Insert/delete:** none
- **Formulas:** none
- **Data:** `config/workbook_snapshot.json` — **Profit and Price** added 5 series on **Weekly Financials**:
  - **Adjusted EBITDA** actual **52** / model **53** (left axis)
  - **Price (at Close)** **80**, **Price @ P/S = 2** **82**, **Price @ P/S = 3** **83** (right axis; P/S lines medium-dashed)
- **Side effects:** **Homes Chart** unchanged; CM stack unchanged

## 2026-09-01 — TTM revenue: day-weighted quarterly proration before full year

Replaced the partial rolling 52-week sum (which read ~$1B in early 2026) with day-weighted quarterly revenue for columns with fewer than 52 weeks of history.

- **Tab / range:** **Weekly Financials** `B81:DY81` (TTM), `B82:DY83` (P/S)
- **Insert/delete:** none
- **Formulas:** TTM when `weeksAvail < 52` — sum over 6 quarters of `(overlap days ÷ quarter days) × quarter revenue`, where overlap is `[wk−365, wk]` ∩ quarter; quarter revenue = **Quarterly Financials** **Revenue** if populated → historical GAAP constants (**2024 Q4** $1.084B through **2025 Q4** $736M) → sum of weekly **Revenue** / **Revenue - Model** for that quarter. When `weeksAvail ≥ 52`, rolling 52-week sum. Week-ending quarters **2024 Q4–2025 Q4** still use flat reported TTM from earnings.
- **Data:** none
- **Side effects:** `sheets/valuation.py`; sample Jan 2026 TTM ≈ **$4.30B** (was ~$1.1B)

## 2026-08-31 — Fix TTM revenue errors; use reported TTM for Q4 2024–Q4 2025

Fixed `#NUM!` / `#VALUE!` on **Trailing Twelve Months Revenue** and dependent P/S rows; early weeks now use quarterly-reported TTM.

- **Tab / range:** **Weekly Financials** `B81:DY81` (TTM), `B82:DY83` (P/S); **Quarterly Financials** `B82`, `C82` (TTM actuals for 2025 Q3–Q4)
- **Insert/delete:** none
- **Formulas:** TTM `B81` — `IFS` on week-ending quarter for reported TTM (**2024 Q4** $5.15B, **2025 Q1** $5.13B, **2025 Q2** $5.18B, **2025 Q3** $4.72B, **2025 Q4** $4.37B from earnings supplements); else rolling 52-week sum with `INDEX` column offset `ci=c-COLUMN($B$1)+1` and `SEQUENCE(1,n-s+1,s,1)` (was wrongly `SEQUENCE(s,n)` and absolute column index)
- **Data:** **Quarterly Financials** `B82`=4,720,000,000 (2025 Q3), `C82`=4,370,000,000 (2025 Q4)
- **Side effects:** `sheets/valuation.py` updated; re-run `scripts/add_valuation_rows.py` to refresh

## 2026-08-31 — Valuation rows (price, TTM revenue, implied P/S)

Added four valuation metrics after **Earnings per Share - Model** on both financials tabs; weekly formulas populated.

- **Tab / range:** **Weekly Financials** and **Quarterly Financials** — inserted 4 rows after **Earnings per Share - Model** (weekly R80–R83, quarterly R81–R84); **Shares Outstanding (Quarter End)** on quarterly shifted to R85
- **Insert/delete:** ROWS after weekly R79 / quarterly R80, count 4
- **Formulas (weekly):**
  - **Price (at Close)** `B80`: `=LET(wk,B$1,px,GOOGLEFINANCE("OPEN","price",wk-6,wk),IF(wk="","",IFERROR(INDEX(px,ROWS(px),2),"")))` — last trading-day close in the 7-day window ending on the week date (Saturdays)
  - **Trailing Twelve Months Revenue** `B81`: rolling 52-week sum of **Revenue** with **Revenue - Model** fallback
  - **Price @ P/S = 2** `B82`: `=IF(OR(N(B81)=0,N(shares)=0),"",2*B81/shares)` where shares = **Basic Shares Outstanding** if present else **Basic Shares Outstanding - Model**
  - **Price @ P/S = 3** `B83`: same as P/S=2 with multiplier 3
- **Data:** none (formula-driven)
- **Side effects:** `scripts/add_valuation_rows.py`, `sheets/valuation.py`, `insert_rows_after_label` in `sheets/labels.py`; `validate_model_formulas.py` passes. **Homes Chart** / **Money Charts** unchanged — repoint manually if you add these series.

## 2026-08-31 — Stale sheet comments + quarterly Doma label

Corrected notes that no longer matched formulas after private-sales and Doma row changes.

- **Tab / range:** **Transitions** `A5`, `B6`, `A23`, `B23`; **Weekly Financials** `A18`; **Quarterly Financials** `A30`
- **Insert/delete:** none
- **Formulas:** none
- **Data:** **Quarterly Financials** `A30` label **Doma Refi Contribution - Model** → **Doma Refi Profit - Model** (matches weekly)
- **Notes:**
  - **Transitions A5:** replaced stale “no longer used / acquisitions canceled” text → documents **OPEN 1.0** listing timing for **New Listings - 1.0 Model** (not private sales)
  - **Transitions B6:** cleared — model uses weekly `(1 − Likelihood to List)`, not `B6`
  - **Transitions A23 / B23:** removed `B6` private-share references; timing-only curve for **Private Home Sales - Model**
  - **Weekly A18:** `B6 × purchases × row 5` → `(1 − Likelihood to List) × purchases × **row 23**`
- **Side effects:** none

### Repo

- **`README.md`** — assumptions table: row 5 scope, private share via L2L not `B6`

---

## 2026-08-31 — Private Home Sales: purchase→close curve row 23 (not row 5)

**Private Home Sales - Model** was lagging never-listed purchases on **OPEN 1.0 listing timing** (`Transitions!B5:J5`). It now uses the dedicated **purchase→private-close** curve on row 23 (`Percent of Private Completions Sold by Week`).

- **Tab / range:** **Weekly Financials** `B18:DY18` (**Private Home Sales - Model**)
- **Insert/delete:** none
- **Formulas:** lag weights `Transitions!$B$5:$J$5` → `Transitions!$B$23:$J$23` (purchases × `(1 − Likelihood to List)` unchanged)
- **Data:** none
- **Side effects:** none (charts unchanged)

### Repo

- **`sheets/open_transition.py`** — `PRIVATE_CLOSE_ROW = 23`, `PRIVATE_CLOSE_BY_WEEK`; `private_home_sales_model_formula()` default lag row **23**
- **`README.md`**, **`RESOURCES.md`** — private-sale timing docs

---

## 2026-08-31 — Doma Refi Profit row: compound formulas AT:DY

Manual fix on live sheet: **AT29:DY29** were hardcoded dollar values from the revision-2866 recovery; replaced with week-over-week compound formulas (`=prev29*col28`).

- **Tab / range:** **Weekly Financials** `AT29:DY29`
- **Insert/delete:** none
- **Formulas:** hardcoded $ (e.g. AT **14884**) → `=AS29*AT28` (template copied through **DY** as `=prev29*col28`)
- **Data:** **AR29** remains **$10,000** seed; **AS29** unchanged (`=AR29*AS28`)
- **Side effects:** repo-only sync (`sheets/doma_manual_cells.py`); live sheet already correct

### Repo

- **`sheets/doma_manual_cells.py`** — **DOMA_REFI_PROFIT_CELLS** AT:DY now formulas

---

## 2026-08-31 — Restore manual Doma Growth Multiplier and Refi Profit rows

Recovered **Doma Growth Multiplier** and **Doma Refi Profit - Model** from Google Sheets revision **2866** (~12:53 PM EDT) after `restore_weekly_model_formulas.py` had overwritten manual cells with the generic Transitions-ramp template (all zeros once Transitions B32/B33 were deleted).

- **Tab / range:** **Weekly Financials** `B28:DY29`
- **Insert/delete:** none
- **Formulas / data restored:**
  - **Doma Growth Multiplier:** zeros B–AQ; stepwise multipliers from **AR** (1.22 → 1.1 → 1.07 → 1.05 → 1.03 → 1.015 → 1.02 → 1.0 through **DY**); occasional carry-forward formulas (e.g. `=AR28`, `=BF28`)
  - **Doma Refi Profit - Model:** **$10,000** seed at **AR29**; `=AR29*AS28` at **AS**; hardcoded compounded $ through **DD**; plateau **~$1.337M/wk** **DE:DY**; early columns retain legacy Transitions ramp formula at **B** (evaluates to 0 without Transitions inputs)
- **Side effects:** repo now stores cells in `sheets/doma_manual_cells.py` so future restores preserve this layout

### Repo

- **`sheets/doma_manual_cells.py`** — canonical B:DY cell list (recovered snapshot)
- **`sheets/weekly_model_formulas.py`** — Doma rows use manual cells, not generic template
- **`sheets/ancillary_products.py`** — removed unused Transitions-ramp Doma helpers

---

## 2026-08-31 — Sync repo from live spreadsheet (manual edits, pass 3)

Compared live workbook to git and refreshed tracked artifacts so the spreadsheet remains source of truth.

- **Tab / range:** read-only pull from live sheet (no sheet writes)
- **Insert/delete:** none
- **Formulas:**
  - **Private Home Sales - Model** (`B18:DY18`): lag weights `Transitions!$B$4:$J$4` → `Transitions!$B$5:$J$5` (1.0 purchase→listing timing; purchases × `(1 − Likelihood to List)` unchanged)
- **Data synced into git:**
  - **Contribution Margin - Core:** horizon start **3.4%** (was **3.6%**); **AA** anchor **3.6%**
  - **Contribution Margin - Adjustments:** early weeks less negative (**B −1.5%**, **C/D −1.4%**; was **−2.0% / −1.9% / −1.6%**)
- **Side effects:** **Money Charts** — **Profit and Price** series repointed to post-reconciliation rows (GAAP NI **76/77**, Adj NI **58/65**); `config/workbook_snapshot.json` updated; `validate_model_formulas.py` passes

### Repo

- **`sheets/open_transition.py`** — `private_home_sales_model_formula()` default lag row **5**
- **`sheets/weekly_model_formulas.py`** — `CM_CORE_VALUES`, `CM_ADJUSTMENTS_VALUES`
- **`README.md`**, **`RESOURCES.md`** — private-sale timing docs

---

## 2026-08-31 — Revenue cash/financed close lag pairing + formula drift checks

**Revenue - 2.0 Model** and **Revenue - 1.0 Model** paired financed close lag (`Transitions!$B$18`) with cash purchase % (`$B$20`) and cash lag (`$B$19`) with financed share — reversed. Cash lag now pairs with `$B$20`; financed lag with `(1-$B$20)`.

- **Tab / range:** **Weekly Financials** `B24:DY24`, `B25:DY25` (**Revenue - 2.0 Model**, **Revenue - 1.0 Model**)
- **Insert/delete:** none
- **Formulas:** first SUMPRODUCT lag `Transitions!$B$18` → `Transitions!$B$19` (× `$B$20`); second lag `$B$19` → `$B$18` (× `(1-$B$20)`)
- **Data:** none
- **Side effects:** **Revenue - Model** (blend row) unchanged structurally; repo now validates live `* - Model` formulas match templates so manual fixes are not lost on restore

### Repo

- **`sheets/open_transition.py`** — `revenue_model_formula()` lag pairing
- **`scripts/validate_model_formulas.py`** — `collect_live_formula_drift()`; restore skips drift check
- **`scripts/sync_repo_from_live_sheet.py`** — pull CM stack + snapshot validate + drift check after manual edits
- **`README.md`** — document sync workflow

---

## 2026-08-31 — Adj→GAAP reconciliation rows (inventory, restructuring, CEO, other)

Closed remaining **GAAP NI - Model** gaps by adding earnings-supplement reconciliation lines between Adjusted Net Income and GAAP net loss: inventory valuation timing (current + prior periods), restructuring, CEO make-whole, and other GAAP adjustments.

- **Tab / range:** **Weekly Financials** and **Quarterly Financials** — inserted 10 rows before **Net Income (Loss) Attributable to Common Shareholders** (5 actual + 5 `- Model`); spread actuals; restored **GAAP NI - Model**
- **Insert/delete:** 10 rows on each tab before **Net Income (Loss) Attributable to Common Shareholders**
- **Formulas:**
  - **GAAP NI - Model:** `={adj_ni}+{debt}-{sbc}-{inv_curr}-{inv_prior}-{restruct}-{ceo}-{other}` (label-resolved; was `={adj_ni}+{debt}-{sbc}`)
  - **`* - Model` passthrough rows:** actual if spread else forward run-rate (**~$12M/qtr** current-period inventory, **~−$15M/qtr** prior-period release; restructuring / CEO / other default **0**)
- **Data (Quarterly Financials, reconciliation add-back signs from supplements, $):**

| Quarter | Inv val current | Inv val prior | Restructuring | CEO make-whole | Other |
| --- | --- | --- | --- | --- | --- |
| 2025 Q3 | 15M | −17M | 1M | 0 | −2M |
| 2025 Q4 | 9M | −21M | 0 | 5M | 0 |
| 2026 Q1 | 9M | −14M | 0 | 5M | 0 |
| 2026 Q2 | 14M | −9M | 3M | 4M | −2M |

- **Side effects:** GAAP NI - Model, EPS - Model shift +10 rows; **Money Charts** may need manual repoint. Debt / reconciliation actual rows use **week-ending-quarter ÷13** spread (no cross-quarter day blend) so Q4 debt does not leak into Q1 boundary weeks.

**Post-fix GAAP NI - Model vs quarterly reported ($M):** 2025 Q4 **−1.7** (was ~+29); 2026 Q1 **+6.6** (was ~−34); 2026 Q2 **+14.1** (unchanged). Remaining Q2 gap ≈ operating **Adjusted Net Income - Model** vs reported (−18 vs −30).

### Repo

- **`sheets/gaap_below_the_line.py`** — labels, quarterly actuals, forward run-rates
- **`sheets/formulas.py`** — `weekly_from_quarterly_end_quarter_formula` for one-time GAAP items
- **`sheets/weekly_model_formulas.py`** — GAAP NI formula + five model rows
- **`scripts/add_gaap_adj_to_gaap_rows.py`** — live migration
- **`scripts/update_weekly_quarterly_spread.py`** — end-quarter spread for debt + reconciliation rows; `max_row` / range fixes

---

## 2026-08-31 — Fix GAAP NI - Model: Adj + debt − SBC (drop interest double-count)

**Net Income (Loss) Attributable to Common Shareholders - Model** added GAAP interest expense, other income, and net interest on top of **Adjusted Net Income - Model**, but Adj NI already embeds EBITDA-bridge net interest. It also omitted **SBC**, which must be subtracted on the Adj → GAAP path (mirror of the Adj NI fix). Rewired to Opendoor’s reconciliation: **Adj NI + debt extinguishment − SBC**.

- **Tab / range:** **Weekly Financials** **Net Income (Loss) Attributable to Common Shareholders - Model** (`B67:DY67` after restore)
- **Insert/delete:** none
- **Formulas:** `={adj_ni}+{debt}+{interest_gaap}+{other}-{net_interest}` → `={adj_ni}+{debt}-{sbc_model}` (label-resolved)
- **Data:** none
- **Side effects:** **Interest Expense - Model** / **Other Income - Net - Model** rows unchanged (still passthrough/guidance for reference); **Earnings per Share - Model** picks up corrected GAAP NI denominator stack

### Repo

- **`sheets/weekly_model_formulas.py`** — GAAP NI formula + dependencies
- **`README.md`** — GAAP NI - Model definition

---

## 2026-08-31 — Private Home Sales - Model: listing lag row 4 (not row 19)

Repo template still pointed **Private Home Sales - Model** at `Transitions!$B$19:$J$19` (private close curve). Live sheet was manually corrected to **`Transitions!$B$4:$J$4`** (2.0 purchase→listing timing). Restored from canonical template.

- **Tab / range:** **Weekly Financials** `B18:DY18` (**Private Home Sales - Model**)
- **Insert/delete:** none
- **Formulas:** lag weights `Transitions!$B$19:$J$19` → `Transitions!$B$4:$J$4` (purchases × `(1 − Likelihood to List)` unchanged)
- **Data:** none
- **Side effects:** downstream **Home Sales - Model** / **Revenue - Model** pick up corrected private path on restore

### Repo

- **`sheets/open_transition.py`** — `private_home_sales_model_formula()`
- **`sheets/weekly_model_formulas.py`** — uses row **4** via helper
- **`README.md`**, **`RESOURCES.md`** — private timing docs

---

## 2026-08-31 — Adjusted EBITDA - Model; fix Adj NI - Model (drop SBC)

**Adjusted Net Income - Model** subtracted **Stock Based Compensation - Model** (~$108–123M/qtr), but Opendoor’s reported Adjusted Net Income does not — SBC is above EBITDA in the Non-GAAP bridge. That drove ~**$110M**/qtr model error vs reported. Added **Adjusted EBITDA - Model** and rewired Adj NI to match the company definition.

- **Tab / range:** **Weekly Financials** and **Quarterly Financials** — inserted 1 row before **Net Interest Expense** (weekly R53, quarterly R54); restored **Adjusted EBITDA - Model** and **Adjusted Net Income - Model** on weekly model rows
- **Insert/delete:** 1 row on each tab before **Net Interest Expense**
- **Formulas:**
  - **Adjusted EBITDA - Model:** `={cp_model}-{adj_opex_model}` (Contribution Profit − Adjusted Operating Expenses)
  - **Adjusted Net Income - Model:** `={adj_ebitda_model}-{net_interest_model}-{da}-{tax}` (was `={cp}-{opex}-{sbc}-{interest}-{da}-{tax}`)
- **Data:** none
- **Side effects:** rows below **Net Interest Expense** shift +1 on both tabs (Adj NI - Model, GAAP NI - Model, EPS - Model, etc.). **Money Charts** / **Homes Chart** series may need manual repoint if lines look wrong.

### Repo

- **`sheets/gaap_below_the_line.py`** — `ADJ_EBITDA_MODEL_LABEL`
- **`sheets/weekly_model_formulas.py`** — Adj EBITDA + Adj NI formulas and dependencies
- **`scripts/add_adj_ebitda_model_row.py`** — live migration

---

## 2026-08-31 — Remove Doma Transitions inputs; sync mortgage attach ramp

Manual cleanup on live workbook; repo updated to match.

- **Tab / range:** **Transitions `A31:B33`** (deleted); **Open Mortgage Percent** (Weekly Financials)
- **Insert/delete:** deleted Doma refi assumption rows (blank separator + **B32** net $/close + **B33** closings ramp)
- **Formulas:** **Open Mortgage Percent** smoothstep phase targets **10%→40%→80%** (was **10%→30%→75%**); terminal **80%** (was **75%**)
- **Data:** **Transitions** ancillary block now **B29:B30** only (mortgage **$4,000**, title **$2,400**). **Doma Growth Multiplier** / **Doma Refi Profit - Model** weekly rows remain but evaluate to **0**
- **Side effects:** `sheets/ancillary_products.py`, `scripts/setup_ancillary_products.py`, **README.md**, **RESOURCES.md**

---

## 2026-08-31 — Sync repo from live spreadsheet (manual edits, pass 2)

Compared live workbook to git and refreshed tracked artifacts so the spreadsheet remains source of truth.

- **Tab / range:** read-only pull from live sheet (no sheet writes)
- **Insert/delete:** none
- **Formulas:** none (templates still align; `validate_model_formulas.py` passed)
- **Data synced into git:**
  - **Seasonality B6:M6:** CM seasonal adj monthly weights updated (Feb +0.003, Mar +0.013, etc.)
  - **Weekly Financials CM stack:** `pull_cm_stack_from_sheet.py` — adjustments **AU:AZ** extended at **-0.7%**; improvement anchors **BC**/**BE**/**BS** updated
  - **Transitions row 5:** OPEN 1.0 listing curve — week 1 **0%**, revised weeks 2–9 (peak **22%** wk 6; **20%** wk 7)
  - **Transitions rows 13–14:** OPEN 1.0 sell-through multipliers (wk 4 **94%**; wks 18–38 **99.5%**; wk 39 **92%**) and recalculated weekly sold rates
- **Side effects:** `config/workbook_snapshot.json` unchanged; ancillary **B29:B33** unchanged

---

## 2026-08-31 — Sync repo from live spreadsheet (manual edits)

Compared live workbook to git and refreshed tracked artifacts so the spreadsheet remains source of truth.

- **Tab / range:** read-only pull from live sheet (no sheet writes)
- **Insert/delete:** 1 row before **Contribution Profit - Model** — **Doma Growth Multiplier** (Weekly + Quarterly)
- **Formulas:**
  - **Doma Refi Contribution - Model** renamed → **Doma Refi Profit - Model**; column B = refi ramp; column C+ = prior profit × current **Doma Growth Multiplier**
  - **Doma Growth Multiplier:** B = **0** seed; C+ carries forward prior column
  - **Contribution Profit - Model:** `Revenue × CM` only (Doma refi no longer added)
  - **Open Mortgage Percent:** four-phase smoothstep ramp **0% → 10% → 30% → 75%** (Jan 2026 – Jan 2029)
  - **Open Title Purchase Percent:** linear **0% → 100%** (Jan 2025 – Jun 2027)
  - **OPEN 1.0-2.0 Transition Completeness:** ramp **Feb 2026 → Jan 2027** (was Sep 2025 → Jul 2026)
- **Data synced into git:**
  - **Transitions B29/B30:** max mortgage **$4,000** / max title **$2,400** per close
  - **CM stack:** `pull_cm_stack_from_sheet.py` refreshed `CM_*` constants
  - **Workbook snapshot:** chart series rows — Homes Chart NL dotted **13**, inventory **50/51**; Money Charts shares **45/47**, Contribution Profit model **30**, GAAP NI **65/66**, adj NI **57/64**
- **Side effects:** `validate_workbook_snapshot.py` and `validate_model_formulas.py` pass against live sheet

---

Split listing, sales, and revenue models into OPEN 1.0 and OPEN 2.0 cohort paths with a linear transition-completeness ramp (0% at horizon start → 100% by week ending **2026-07-04**).

### Transitions

- **Tab / range:** `A4:K5`, `A9:V16`; downstream rows **+4** from insert after row 12 (cash-mix **B18:B20**, unlisted backlog **B25/B27**, ancillary **B29:B33**)
- **Insert/delete:** 4 rows at row 13 (`startIndex` 12, count 4)
- **Data:**
  - Renamed rows 4, 9–12 → **OPEN 2.0 …** (listing timing, sell-through multiplier, % sold, running total, price retention)
  - **Row 5** `OPEN 1.0 Percent of Ultimate Listers by Week` — slower purchase→listing curve (peak weeks 6–7; ~45-day reno prior)
  - **Rows 13–16** OPEN 1.0 sell-through block — ~**51%** cumulative sold by week 17 (~120 DOM; pre-Kaz) vs ~**92%** for 2.0; price retention **100% → 88.6%** by week 21 (vs 2.0 **93.5%**)
- **Formulas:** none changed on Transitions (values only)

### Weekly Financials

- **Insert/delete:** 7 rows total — 1 before **New Listings - Model**, 2 before **ASP**, 2 before **Revenue**, 2 before **Gross Profit**
- **New rows:** **OPEN 1.0-2.0 Transition Completeness** (R12); **New Listings - 2.0 Model** / **- 1.0 Model** (R14–15); **Home Sales - 2.0 / - 1.0 Model** (R20–21); **Revenue - 2.0 / - 1.0 Model** (R24–25)
- **Formulas:**
  - **Transition Completeness:** `MIN(1, MAX(0, (week − DATE(2025,9,13)) / (DATE(2026,7,4) − DATE(2025,9,13))))`
  - **New Listings - 2.0 Model:** prior **New Listings - Model** on `Transitions!B4` (no 1.0 backlog)
  - **New Listings - 1.0 Model:** same lag on `Transitions!B5` **+** unlisted backlog drain (`B25` × `B27:I27`, weeks 1–8)
  - **New Listings - Model:** `completeness × 2.0 + (1 − completeness) × 1.0` (same pattern for **Home Sales - Model** and **Revenue - Model**)
  - **Home Sales / Revenue 2.0** use `Transitions` rows **10/12**; **1.0** use rows **14/16**; cash lags now **B18–B20**

### Quarterly Financials

- **Insert/delete:** same 7-row pattern (labels only; model cells left blank)

### Side effects

- **Homes Chart** / **Money Charts** series repointed after row inserts (user-verified):
  - **Homes Chart:** NL actual **11** / dotted **12** (**OPEN 1.0-2.0 Transition Completeness**), HS **17** / model **19**, inventory **49/50**
  - **Money Charts — Revenue and Shares:** revenue **22/23**, shares **44/46**
  - **Money Charts — Profit and Price:** gross profit **27**, contribution profit model **29**, adj NI **56/63**, GAAP NI **64/65**
- Repo: `sheets/open_transition.py`, `scripts/setup_open_transition.py`, `weekly_model_formulas.py`; ancillary Transitions refs **B29:B33**; `label_rows` default `max_row` **80**; `config/workbook_snapshot.json` synced to live chart series

---

## 2026-08-30 — OPEN 1.0 sell-through extended to 39 weeks

1.0 cohort curves now sum to **100%**; **Home Sales - 1.0 Model** and **Revenue - 1.0 Model** use a **39-week** listing lag (2.0 unchanged at 21).

- **Tab / range:** **Transitions** `A8:AO16` (week headers + OPEN 1.0 rows 13–16); **Weekly Financials** **Home Sales - 1.0 Model** and **Revenue - 1.0 Model** formulas
- **Insert/delete:** none
- **Formulas:** 1.0 home-sales/revenue `MAP(SEQUENCE(1,39), …)` over `Transitions!B14:AN14` / `B16:AN16` (was 21 weeks / `B:V`)
- **Data:**
  - Weeks **1–21** unchanged (~**51%** cumulative @ week 17)
  - Weeks **22–39** decaying tail (weekly multiplier **97.5%** on prior week’s rate) so row 14 sums to **100%**
  - Price retention extended through week **39** (continues **−0.57%/wk**, floor **78%**)
  - Row 8 week index extended **1…39** (+ Total in **AO**)
- **Side effects:** none on charts. Repo: `scripts/extend_open_1_0_sell_through.py`, `sheets/open_transition.py`

---

User repointed chart series on the live workbook after the OPEN 1.0/2.0 row inserts; pulled into git.

- **Tab / range:** read-only chart metadata pull (no sheet writes)
- **Insert/delete:** none
- **Formulas:** none
- **Data:** `config/workbook_snapshot.json` updated to match live **Homes Chart** / **Money Charts** series rows (notably Homes Chart dotted series remains **row 12** = transition completeness, not **New Listings - Model** on row 13)
- **Side effects:** `validate_workbook_snapshot.py` passes against live sheet

---

## 2026-08-30 — Sync repo from live spreadsheet (manual edits)

Compared live workbook to git and refreshed tracked artifacts so the spreadsheet remains source of truth.

- **Tab / range:** read-only pull from live sheet (no sheet writes)
- **Insert/delete:** none detected beyond prior ancillary-product row shifts already on the sheet
- **Formulas:** model-row templates still align (`validate_model_formulas.py` passed)
- **Data synced into git:**
  - **Workbook snapshot:** chart series rows updated for row shifts — Homes Chart inventory **42/43** (was 40/41); Money Charts shares **37/39** (was 35/37), Contribution Profit - Model **22** (was 21), Adjusted/GAAP net income **49/56–58** (was 47/54–56)
  - **CM stack:** explicit **AR:DY** adjustment zeros on live sheet pulled into `CM_ADJUSTMENTS_VALUES`; seasonality monthly values unchanged
- **Side effects:** `scripts/pull_cm_stack_from_sheet.py` now reads Seasonality with `UNFORMATTED_VALUE` (percent-formatted display no longer breaks pull)

---

## 2026-08-30 — Fix Doma refi Transitions row alignment

Removed section-header row that left **B28** blank; Doma inputs now match formula cell refs. Ramp reads **B29** instead of a hardcoded constant.

- **Tab / range:** **Transitions `A25:B29`**; **Doma Refi Contribution - Model** (weekly + quarterly)
- **Insert/delete:** none
- **Formulas:** `… × Transitions!$B$29` (was hardcoded `1.5`) for weekly closings ramp
- **Data:** B28 **$350** net/close; B29 **1.5** closings/wk ramp; cleared stale **A30:B30**
- **Side effects:** none on charts

---

## 2026-08-29 — Ancillary products: mortgage, title, Doma refi

Implemented ODL mortgage attach, purchase title/escrow CM, and separate Doma refi contribution per modeling recommendations.

- **Tab / range:**
  - **Transitions `A25:B30`** — ancillary unit-economics assumptions
  - **Weekly Financials** — renamed **Open Title and Escrow (Doma) Percent** → **Open Title Purchase Percent** (row 40); inserted **Doma Refi Contribution - Model** before **Contribution Profit - Model** (row 21); restored formulas on CM stack, attach %, and profit rows
  - **Quarterly Financials** — same rename (row 41); inserted **Doma Refi Contribution - Model** (row 22)
- **Insert/delete:** 1 row before **Contribution Profit - Model** on Weekly + Quarterly
- **Formulas:**
  - **Open Mortgage Percent:** 0% before Jul 2026 → linear ramp 15%→45% by Jan 2028 (cap 50%)
  - **Open Title Purchase Percent:** 0% before Jul 2026 → 95% forward
  - **Contribution Margin - Mortgage:** `Open Mortgage Percent × Transitions!$B$25 ÷ ASP`
  - **Contribution Margin - Title and Escrow:** `Open Title Purchase Percent × Transitions!$B$26 ÷ ASP`
  - **Doma Refi Contribution - Model:** `Transitions!$B$28 × MIN(100, MAX(0, weeks since Apr 2026 × 1.5/wk))`
  - **Contribution Profit - Model:** `Revenue × CM + Doma Refi Contribution`
- **Data (`Transitions`):**
  - B25 mortgage net $/loan **$2,000**
  - B26 title net $/purchase close **$1,800**
  - B28 Doma refi net $/close **$350**
  - B29 Doma refi closings ramp **1.5/wk** (cap 100/wk in formula)
- **Side effects:** Row insert may shift **Homes Chart** / **Money Charts** series — verify manually. Code: `sheets/ancillary_products.py`, `scripts/setup_ancillary_products.py`, `weekly_model_formulas.py`.

---

## 2026-08-29 — Sync CM stack from live spreadsheet

Pulled manual spreadsheet edits into git so the workbook is source of truth for CM seasonality and stack constants.

- **Tab / range:** none (read-only pull from live sheet)
- **Insert/delete:** none
- **Formulas:** none on sheet
- **Data synced into git:**
  - **Seasonality `B6:M6`:** Jan `-1.00%` … Dec `-2.30%` (absolute monthly CM seasonal adj)
  - **Weekly CM Core `B24`:** `3.8%` anchor (was `2.6%`)
  - **Weekly CM Adjustments `B28:AQ28`:** inventory-clearing ramp through `AQ`, `0` from `AR`
  - **Weekly CM Improvement anchors `F29`/`U29`/`AP29`:** `0.01%` / `0.02%` / `0.03%` with carry-forward
  - **Seasonality row formula:** all weeks `B` onward (not only `H+`)
- **Side effects:** `sheets/cm_seasonality.py`, `sheets/weekly_model_formulas.py`, `scripts/pull_cm_stack_from_sheet.py`; `sync_cm_seasonality_table.py` now documents push-only direction

---

## 2026-08-29 — Retune CM monthly seasonality shape

Second pass on **CM Seasonal Adj** monthly ramp: Feb↑ Mar↓, Apr↑ Jun↓ (Mar now below Apr), Jul↑ Sep↓; quarterly averages unchanged.

- **Tab / range:** **Seasonality** `B6:M6`, note `A7`
- **Insert/delete:** none
- **Formulas:** none
- **Data (`B6:M6`, decimal):** Jan `0.0035`, Feb `0.0125`, Mar `0.0217`, Apr `0.0255`, May `0.0284`, Jun `0.0312`, Jul `-0.0019`, Aug `-0.0054`, Sep `-0.0109`, Oct `-0.0310`, Nov `-0.0347`, Dec `-0.0391`
- **Side effects:** `sheets/cm_seasonality.py` — `CM_SEASONAL_MONTHLY_NUDGE_BPS` on home-sales baseline

---

## 2026-08-28 — Smooth CM seasonality within quarters

Monthly **CM Seasonal Adj** values now ramp within each quarter using U.S. home-sales seasonality (row 2) while preserving the same quarterly averages (+126 / +284 / -61 / -349 bps).

- **Tab / range:** **Seasonality** `B6:M6`, note `A7`
- **Insert/delete:** none
- **Formulas:** none (weekly `INDEX(Seasonality!$B$6:$M$6, MONTH(...))` unchanged)
- **Data (`B6:M6`, decimal):** Jan `0.0029`, Feb `0.0099`, Mar `0.0249`, Apr `0.0217`, May `0.0287`, Jun `0.0347`, Jul `-0.0034`, Aug `-0.0044`, Sep `-0.0104`, Oct `-0.0316`, Nov `-0.0346`, Dec `-0.0386`
- **Side effects:** `sheets/cm_seasonality.py` — `monthly_cm_seasonal_adj()`; `scripts/sync_cm_seasonality_table.py`

---

## 2026-08-28 — CM seasonality row and Seasonality tab CM table

Isolated contribution margin seasonality from other CM adjustments. Historical quarterly CM since 2021 shows a distinct pattern from home-sales seasonality (CM peaks Q2; home sales peak late summer). Replaced flat **-2%** forward **Contribution Margin - Adjustments** values with a dedicated seasonality row driven by a new **Seasonality** table.

- **Tab / range:** **Seasonality** `A6:M7`; **Weekly Financials** inserted row 27 (**Contribution Margin - Seasonality Adjustments**), `B27:DY27` (formula from H / week of 10/25/2025), `AR27:BE27` forward; **Contribution Margin - Adjustments** `H28:DY28` cleared from **-2%** → **0**; **Contribution Margin - Model** `B23:DY23` (`=core+mortgage+title+seasonality+adj`)
- **Insert/delete:** **Weekly Financials** and **Quarterly Financials** — 1 row before **Contribution Margin - Adjustments** (weekly row 27, quarterly row 28)
- **Formulas:**
  - **Contribution Margin - Seasonality Adjustments:** `=INDEX(Seasonality!$B$6:$M$6, MONTH({col}$1))` from column H forward; B–G = 0
  - **Contribution Margin - Model:** `=core+mortgage+title+adj` → `=core+mortgage+title+seasonality+adj`
- **Data (Seasonality `B6:M6`, ex-2023 quarterly mean deviation from annual CM, decimal):**
  - Jan–Mar: `0.0126` (+126 bps)
  - Apr–Jun: `0.0284` (+284 bps)
  - Jul–Sep: `-0.0061` (-61 bps)
  - Oct–Dec: `-0.0349` (-349 bps)
- **Side effects:** `data/contribution_margin_quarterly.json`, `sheets/cm_seasonality.py`, `scripts/add_cm_seasonality_row.py`; Q4 historical adj is inflated by 2022/2025 structural troughs — consider tuning `Seasonality!J6:L6` if forward Q4 should stay inside 5–7% at 6% core. Verify **Homes Chart** / **Money Charts** if CM model lines shifted.

---

## 2026-08-28 — Homes in Inventory - Model passthrough actual

**Homes in Inventory - Model** now uses the published **Homes in Inventory** weekly value when present; otherwise it rolls forward from the prior week using actual-or-model purchases minus actual-or-model sales (unchanged fallback).

- **Tab / range:** **Weekly Financials** `B41:DY41` (Homes in Inventory - Model)
- **Insert/delete:** none
- **Formulas:** `={prev}+if({col}8<>"",…,{col}9)−if({col}14<>"",…,{col}16)` → `=IF({col}40<>"",{col}40,{prev}+if({col}8<>"",…,{col}9)−if({col}14<>"",…,{col}16))`; `B41` anchor `3275` → `=IF(B40<>"",B40,3275)`
- **Data:** none
- **Side effects:** `sheets/weekly_model_formulas.py` — `inventory_model_formula()`; restored via `scripts/restore_weekly_model_formulas.py`

---

## 2026-08-28 — Chart tab rename and series updates (manual)

Renamed **Money Chart** → **Money Charts**; added a second chart and expanded **Homes Chart** series. Manual UI edits only (no agent/script chart API writes).

- **Tab / range:** **Money Charts** (renamed from **Money Chart**); **Homes Chart** + **Money Charts** chart specs
- **Insert/delete:** none
- **Formulas:** none
- **Data:** none
- **Side effects:**
  - **Homes Chart** — 10 series on Weekly Financials rows 2, 3, 8, 9, 11, 12, 14, 16, 40, 41 (domain row 1); added Homes in Inventory actual + model
  - **Money Charts** chart 0 (**Revenue and Shares**) — rows 17, 18, 35, 37 (domain row 1)
  - **Money Charts** chart 1 (**Profit and Price**) — rows 20, 21, 47, 54, 55, 56 (domain row 1)

---

## 2026-08-28 — Revert Chart Feed; restore charts to Weekly Financials

Chart Feed repoint stripped legend/labels/colors via API partial spec. Undid: deleted **Chart Feed** tab; restored **Homes Chart** / **Money Chart** series to **Weekly Financials** (sheet id 0) with pre-change row indices and `headerCount` / `legendPosition`.

- **Tab / range:** deleted **Chart Feed**; **Homes Chart** + **Money Chart** chart specs
- **Insert/delete:** deleted **Chart Feed** sheet
- **Formulas:** none
- **Data:** none
- **Side effects:**
  - **Homes Chart** series → Weekly rows 2, 3, 8, 9, 11, 12, 14, 16 (domain row 1); 8 series restored
  - **Money Chart** series → Weekly rows 17, 18, 35, 37 (domain row 1); share-count right axis restored
  - `headerCount=1`, `legendPosition=RIGHT_LEGEND` set on both charts
  - Removed `sheets/chart_feed.py`, `scripts/setup_chart_feed.py`; added `scripts/restore_charts.py`

---

## 2026-08-28 — Chart Feed tab (stable chart series) — **reverted**

Charts previously referenced fixed row numbers on **Weekly Financials**; row inserts desynced series (wrong metric or missing line). Added **Chart Feed** with label-resolved `INDEX`/`MATCH` formulas and repointed both charts to fixed feed rows.

- **Tab / range:** new **Chart Feed** `A1:DY11` (labels in A, formulas `B:DY` per row)
- **Insert/delete:** none on Weekly / Quarterly
- **Formulas:** per cell (example row 6 / Home Sales, column B):

```
=IFERROR(INDEX('Weekly Financials'!B:DY, MATCH($A6, 'Weekly Financials'!A:A, 0), 1), "")
```

  Same pattern with column index 1…128 across `B:DY`; copied for feed rows 1–11.
- **Data:** column A labels — Week Ending (1), Acquisition Contracts (2), Acquisition Contracts - Model (3), New Listings (4), New Listings - Model (5), Home Sales (6), Home Sales - Model (7), Revenue (8), Revenue - Model (9), Basic Shares Outstanding (10), Basic Shares Outstanding - Model (11)
- **Side effects:**
  - **Homes Chart** series → Chart Feed rows 2–7 (domain row 1); dropped stale Homes Purchased series that had pointed at Weekly rows 8–9
  - **Money Chart** series → Chart Feed rows 8–11 (domain row 1); share-count secondary axis preserved
  - Repo: `sheets/chart_feed.py`, `scripts/setup_chart_feed.py`; README updated

---

## 2026-08-28 — Fix New Listings - Model purchase lag input

**New Listings - Model** was lagging **Homes Purchased** (actuals) instead of **Homes Purchased - Model**. Introduced in the 2026-08-28 label-placeholder refactor: old template used `$9:$9` (model row) but was mapped to `{Homes Purchased}`.

- **Tab / range:** **Weekly Financials** `B12:DY12` (New Listings - Model)
- **Insert/delete:** none
- **Formulas:** purchase-lag term `INDEX($9:$9, …)` → `INDEX($10:$10, …)` (Homes Purchased - Model × Likelihood to List); copied across `B12:DY12`
- **Data:** none
- **Side effects:** `sheets/weekly_model_formulas.py` dependency set updated; `scripts/restore_weekly_model_formulas.py` re-applied

---

Added **- Model** rows for debt extinguishment, GAAP interest expense, and other income — same passthrough pattern as **Stock Based Compensation - Model**. **GAAP NI - Model** now reads only model rows so forward weeks work without quarterly actuals.

- **Tab / range:** **Weekly Financials** and **Quarterly Financials** — inserted 3 rows before **Adjusted Net Income - Model** (weekly R51–R53, quarterly R52–R54); restored model formulas on weekly R51–R54, R56, R58
- **Insert/delete:** 3 rows on each tab before **Adjusted Net Income - Model**
- **Formulas:**
  - **(Loss) Gain on Extinguishment of Debt - Model:** `IF(ISNUMBER(actual), actual, IF(wk="", "", 0))`
  - **Interest Expense - Model:** passthrough actual else **−$27M ÷ 13** per week
  - **Other Income - Net - Model:** passthrough actual else **$10.5M ÷ 13** per week
  - **Net Income (Loss) Attributable to Common Shareholders - Model:** `={adj_ni}+{debt_model}+{interest_model}+{other_model}-{net_interest_model}` (was actual rows + **Net Interest Expense** actual)
- **Data:** none
- **Side effects:** Adj NI - Model, GAAP NI - Model, EPS - Model shift +3 rows

### Repo

- **`sheets/gaap_below_the_line.py`** — model label constants + guidance run-rates
- **`sheets/formulas.py`** — `weekly_gaap_below_line_model_formula` (`ISNUMBER` for negative actuals)
- **`sheets/weekly_model_formulas.py`** — three model rows + GAAP NI wiring
- **`scripts/add_gaap_below_the_line_model_rows.py`** — live migration

---

Q4 2025 GAAP net loss (**−$1.096B**, **−$1.26** EPS) was dominated by a **−$933M** loss on debt extinguishment plus GAAP **interest expense** and **other income**, none of which were in the model. **Net Income (Loss) Attributable to Common Shareholders - Model** only reflected the operating stack (~**−$13M**/week), so it understated GAAP loss by ~**$71M**/week in Q4.

- **Tab / range:** **Weekly Financials** and **Quarterly Financials** — inserted 4 rows before **Net Income (Loss) Attributable to Common Shareholders** (weekly R48–R51, quarterly R49–R52); spread formulas on weekly R48–R50; model formulas restored on R51 (**Adjusted Net Income - Model**) and R53 (**GAAP NI - Model**)
- **Insert/delete:** 4 rows on each tab before **Net Income (Loss) Attributable to Common Shareholders**
- **Formulas:**
  - **Adjusted Net Income - Model:** `={cp}-{opex}-{sbc_model}-{interest_model}-{da}-{tax}` (former GAAP NI - Model operating stack)
  - **Net Income (Loss) Attributable to Common Shareholders - Model:** `={adj_ni}+{debt}+{interest_gaap}+{other_income}-{net_interest}` (label-resolved)
- **Data (Quarterly Financials, $ millions from Q4 2025 / 2026 earnings supplement & 10-Q):**

| Quarter | (Loss) Gain on Extinguishment of Debt | Interest Expense | Other Income - Net |
| --- | --- | --- | --- |
| 2025 Q3 | −$1M | −$34M | $14M |
| 2025 Q4 | **−$933M** | −$28M | $14M |
| 2026 Q1 | −$1M | −$23M | $10M |
| 2026 Q2 | $0 | −$29M | $11M |

- **Side effects:** GAAP NI - Model, EPS - Model, and rows below shift +4; Q4 weekly GAAP NI - Model now ~**−$87M**/week vs reported ~**−$84M**/week (remaining gap = operating model vs reported Adjusted NI, not missing debt line)

### Repo

- **`sheets/gaap_below_the_line.py`** — quarterly actuals + label constants
- **`sheets/weekly_model_formulas.py`** — split Adj NI - Model vs GAAP NI - Model
- **`scripts/add_gaap_below_the_line_rows.py`** — live migration
- **`scripts/update_weekly_quarterly_spread.py`**, **`scripts/load_quarter_2025_q3.py`**, **`scripts/load_quarters_2025_q4_2026_h1.py`** — spread + load below-the-line actuals

---

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
