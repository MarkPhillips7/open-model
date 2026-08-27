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
