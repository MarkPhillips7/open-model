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
