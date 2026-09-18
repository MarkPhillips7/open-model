# Spreadsheet changelog

The live model is the Google Sheet **[EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)** (ticker **EOSE**). Git does not see those edits unless they are recorded here. Repo/platform changes go in the [root CHANGELOG](../../CHANGELOG.md).

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

## 2026-09-17 — Rename MWh shipped - PTC

- **Tab / range:** **Quarterly Financials** `A62`; **Financials Definitions** matching label
- **Insert/delete:** none
- **Formulas:** unchanged (row numbers). Label **MWh shipped - PTC** → **MWh shipped - Derived from PTC**
- **Data:** none
- **Side effects:** none on charts (series still point at the same row)

### Repo

- `layout.py`, `financials_definitions.py`, `README.md`, `RESOURCES.md`, `scripts/setup_cogs.py`

---

## 2026-09-17 — Remove MWh shipped - Derived

Deleted the revenue/ASP energy row. It was circular with **Revenue - Model** and not a shipment actual. Energy for unit COGS, Revenue - Model, and COGS - Model is **MWh shipped - PTC** only.

- **Tab / range:** **Quarterly Financials** deleted **MWh shipped - Derived**. **Financials Definitions** rewritten.
- **Insert/delete:** ROWS, **1 deleted** at **MWh shipped - Derived** (was row 62, between Revenue and MWh shipped - PTC). Rows below shift **−1**. Grid is 111 rows (was 112).
- **Formulas:**
  - **Unit COGS - Derived:** dropped the ASP-MWh fallback → `COGS × 1000 / MWh shipped - PTC`
  - **Revenue - Model:** `MWh shipped - PTC / 1000 × Z3 ASP - Model` (blank if no PTC energy)
  - **COGS - Model:** `Unit COGS × MWh shipped - PTC / 1000 − government credits + non-cash COGS`
  - **Government credits - Model:** still copies PTC actual; else effective 45X × **MWh shipped - PTC** / 1000
- **Data:** none (deleted formula row only)
- **Side effects:** If you added Operations/Money charts, check series in the UI after the row delete. No chart API.

### Repo

- `layout.py`, `quarterly_model_formulas.py`, `financials_definitions.py`, `README.md`, `RESOURCES.md`
- `scripts/setup_cogs.py`

---

## 2026-09-17 — Production Tax Credits → MWh → Unit COGS

Added 45X PTC actuals so historical **Unit COGS - Derived** follows the bert_gilfoyle identity (GAAP PTC ÷ 90% transfer ÷ $45/kWh = MWh; GAAP COGS / that MWh). Q2 2025 prints **$5.069M** statutory / **112.6 MWh** / **$410/kWh**.

- **Tab / range:** **Quarterly Financials** four new rows in the 45X / revenue block. **Financials Definitions** rewritten. **Welcome** goals line.
- **Insert/delete:** ROWS, **4 inserted**:
  - 1 before **45x & active electrode credits** (now row 50): **45X cell & module credit**
  - 2 before **Government credits - Model** (now rows 54–55): **Production Tax Credits**, **Production Tax Credits (statutory) - Derived**
  - 1 before **Revenue - Model** (now row 63): **MWh shipped - PTC**
  - Grid is 112 rows (was 108). Rows below each insert shift down.
- **Formulas:**
  - **Production Tax Credits (statutory) - Derived:** `PTC / (45x transfer rate / 100)` (Q2 2025: 4.562 / 0.90 = 5.069)
  - **MWh shipped - PTC:** `statutory × 1000 / 45X cell & module credit` (Q2 2025: 112.6 MWh; Q2 2026: 307.6)
  - **Unit COGS - Derived:** `COGS × 1000 / MWh shipped - PTC` when PTC energy is present, else the old `COGS × 1000 / MWh shipped - Derived`
  - **Government credits - Model:** copy **Production Tax Credits** actual when present; else effective 45X × MWh shipped - Derived / 1000
  - **45X cell & module credit:** C = 45; D:Z `=$C$row`
- **Data:** 10-Q/10-K 45X COGS-reduction actuals ($M) C–H (2025 Q1 – 2026 Q2): **1.799, 4.562, 5.660, 9.239, 10.341, 12.457**. Q4 2025 is FY $21.259M − 9M $12.020M.
- **Side effects:** Financials Definitions + Welcome rewritten from git. No chart API. If you added Operations/Money charts, check series in the UI after the four-row insert.

### Repo

- `layout.py`, `quarterly_model_formulas.py`, `actuals.py`, `financials_definitions.py`, `sources.py`
- `welcome.py`, `README.md`, `RESOURCES.md`
- `scripts/setup_cogs.py`, `scripts/fetch_sec_gaap.py`

---

## 2026-09-17 — Pull live Quarterly Financials into git (no sheet writes)

Captured the user's manual Quarterly Financials edits into the repo. The live sheet is still the WIP / known-wrong model; git now matches it so restore/setup cannot roll the tab back to the old GWh-shipped identity.

- **Tab / range:** repo only. Live **Quarterly Financials** `A1:Z108` was read, not written.
- **Insert/delete:** none on the sheet. Repo `layout.py` now has 108 rows: added **Booked orders** (GWh) after **Booked orders - Model**; removed **GWh shipped** / **GWh shipped - Model**; renamed **MWh shipped** → **MWh shipped - Derived**; **Z3 ASP - Model** units `$ / kWh`.
- **Formulas:** captured as typed — Booked orders - Model last-actual-or-×1.2; Backlog - Model Q1 actual then ×1.03; ASP - Model $260 then ×0.97; MWh shipped - Derived = Revenue×1000/ASP Model; Revenue - Model from derived MWh; Government credits from derived MWh/1000. Duplicate **Booked orders** labels are keyed as `Booked orders [$M]` / `Booked orders [GWh]` so MATCH/load cannot write dollar actuals onto the GWh row.
- **Data:** dropped typed MWh 265 / 307.6; Q4 2025 Booked orders GWh **1.1**. Line ramp unchanged.
- **Side effects:** `setup_eose_workbook.py` and `setup_cogs.py` now refuse unless `--force-rebuild`. `load_quarterly_actuals.py` skips formula cells and requires a layout match. Restore uses the units-aware label map and aborts if live A:B drifted from `layout.py`. No chart API.

### Repo

- `layout.py`, `quarterly_model_formulas.py`, `actuals.py`, `financials_definitions.py`, `README.md`
- `scripts/setup_eose_workbook.py`, `scripts/setup_cogs.py`, `scripts/load_quarterly_actuals.py`
- `scripts/restore_weekly_model_formulas.py`, `scripts/validate_model_formulas.py`

---

## 2026-09-17 — COGS Units / Value / Notes; quarterly path on Financials

Reorganized the **COGS** tab so column C is a narrow value column and notes live in D. Moved the quarterly engine onto **Quarterly Financials**.

- **Tab / range:** **COGS** rewritten `A1:D40` (was `A1:Z51`). **Quarterly Financials** five new rows before **Unit COGS - Derived**. Financials Definitions + Welcome.
- **Insert/delete:**
  - COGS: no row insert; grid shrunk to 6 columns (dropped the C–Z quarterly block). `frozenRowCount` **1**.
  - Quarterly Financials: ROWS, **5 inserted** before **Unit COGS - Derived** (now rows 44–48): Cost-out plan progress - Model, Guided adjusted gross margin - Model, Scale absorption blend - Model, Adj. EBITDA at $200M revenue - Guided, Adj. EBITDA at $200M revenue - Model. Rows below shift **+5**.
- **Formulas:**
  - **COGS** no longer has Year / Quarter / progress / adj. GM / unit COGS / $200M path in C–Z.
  - **Unit COGS - Model** and **Adjusted gross margin - Model**: `INDEX/MATCH` into COGS C:Z → computed on Quarterly Financials, `INDEX/MATCH`ing COGS column-C levers (start GM, guided pts, terminal $/kWh, dates, line counts, $200M illustration revenue).
- **Data:** Narrative/hyperlinks moved **C→D** at `D3:D7`, `D20`, `D30`, `D39:D40`. Row 1 header: B **Units**, C **Value**, D **Notes**. Yellow levers stay in C.
- **Side effects:** COGS column widths C **484→100**, D **493→720**; row 1 frozen + gray header fill. No chart API. If you added Operations/Money charts, check series in the UI after the five-row insert.

### Repo

- `cogs.py`, `layout.py`, `quarterly_model_formulas.py`, `scripts/setup_cogs.py`, `scripts/setup_eose_workbook.py`, `financials_definitions.py`, `welcome.py`, `README.md`

---

## 2026-09-17 — Q3 2026 manufacturing lines Actual = 1.5

User replaced the I31 text `="2 to 1"` with **1.5**.

- **Tab / range:** **Quarterly Financials** `I31` (**Z3 manufacturing lines**, 2026 Q3)
- **Insert/delete:** none
- **Formulas:** none (hardcoded actual)
- **Data:** `I31` **1.5**. Working in-quarter figure — Q3 2026 has not printed. Does not change **Z3 manufacturing lines - Model** (I32 still **1.75** on the line ramp).
- **Side effects:** none on charts

### Repo

- `actuals.py`, `financials_definitions.py`, `README.md`, `RESOURCES.md`

---

## 2026-09-17 — Sync repo from live spreadsheet (manual edits)

Pulled after user edits on **Quarterly Financials** and **Financials Definitions**. **Terminal unit COGS** is no longer a Quarterly Financials row — it lives only on the **COGS** tab.

- **Tab / range:** **Quarterly Financials** row 44 (was **Terminal unit COGS**); **Financials Definitions** matching label; **COGS** `C9` (unbroke the MATCH after the QF delete)
- **Insert/delete:** ROWS, 1 deleted on Quarterly Financials at **Terminal unit COGS** (was row 44; Haircut stays row 43). Rows below shift **−1**. Definitions dropped **Units** (header-only) and **Terminal unit COGS**.
- **Formulas:**
  - **Unit COGS - Model** still `INDEX/MATCH`s the COGS engine (unchanged).
  - **Unit COGS w/ 45x - Model** live `=C45-C48` (auto-shifted) captured as `{Unit COGS - Model}-{Effective 45x credit - Model}` so restore keeps it.
  - **COGS C9 Terminal unit COGS:** `INDEX/MATCH` into Quarterly Financials (now `#N/A`) → hardcoded **160** (yellow editable lever). Haircut still pulls from QF `C43`.
- **Data:** Column-C scalars, line ramp, ASP, and reported actuals otherwise match the repo. **Z3 manufacturing lines** `I31` (2026 Q3) is the text `="2 to 1"` on the live sheet — not a numeric actual, left as typed.
- **Side effects:** No chart API. No chart objects in this workbook. Welcome tab copy unchanged.

### Repo

- `layout.py`, `quarterly_model_formulas.py`, `cogs.py`, `scripts/setup_cogs.py`, `financials_definitions.py`, `README.md`

---

## 2026-09-09 — Manual Quarterly Financials rows into repo + Definitions

Synced live-sheet edits (new rows, derived $/kWh, column widths) into `layout.py` / formulas / Definitions. Duplicate **Revenue** label with units MWh was renamed **MWh shipped** so MATCH keys stay unique.

- **Tab / range:** **Quarterly Financials** row 10 insert + Model restore `C:Z` on pipeline / derived ASP/COGS / GWh shipped. **Financials Definitions** `A1:B98`. Welcome rewrite. Column widths on QF / Welcome / Definitions / COGS.
- **Insert/delete:** ROWS, 1 inserted before **Pipeline (GWh)** (now row 10): **Pipeline quarterly growth rate**.
- **Formulas:**
  - Duplicate A-label `Revenue` (B=`MWh`) → **MWh shipped**; leftover `Z3 ASP` → **Z3 ASP - Derived**
  - **Pipeline - Model:** Q1 2025 = Pipeline actual, then `prior × (1+$C$growth/100)` (default 10% QoQ). Does **not** pick up later pipeline actuals.
  - **Pipeline (GWh) - Model:** live C was `1000×Pipeline-Model/C50` (Unit COGS w/ 45x after a row shift) → `1000 × Pipeline - Model / Z3 ASP - Model` on C:Z
  - **Z3 ASP - Derived** = Revenue×1000/MWh; **Unit COGS - Derived** = COGS×1000/MWh (blank if no MWh)
  - **GWh shipped** = MWh/1000 when MWh present
- **Data:** MWh shipped Q1 2026 **265**, Q2 2026 **307.6** (working estimates, not a 10-Q line). Pipeline growth **10**. Implied ASP ~$215 / $224 vs Model $256. Widths: QF A=280 B=90 C–Z=60; Welcome A=638 B=720; Definitions A=288 B=734; COGS A=287 B=58 C=484 D=493.
- **Side effects:** One row insert near the top of Quarterly Financials. No chart API. If you added Operations/Money charts, check series in the UI.

---

## 2026-09-09 — Cost-out plan on COGS tab (70% haircut)

Incorporated the Q2 2026 Slide 11 cost-out waterfall and [bert_gilfoyle’s thread](https://x.com/bert_gilfoyle/status/2096422051376742414): adj. GM path, adj. EBITDA as ops-cash proxy, Lines 3–4 scale absorption. Default **Percent of Guided Cost Cutting Achieved = 70%**.

- **Tab / range:** **COGS** `A1:Z51` rewritten (was empty). **Quarterly Financials** new rows + Model formula restore `C:Z`. Welcome, Financials Definitions.
- **Insert/delete:** ROWS, 9 inserted on Quarterly Financials:
  - 2 before **Unit COGS - Model** (now rows 42–43): Percent of Guided Cost Cutting Achieved, Terminal unit COGS
  - 4 before **SG&A** (now 61–64): Adjusted gross profit / - Model, Adjusted gross margin / - Model
  - 1 before **Adjusted EBITDA margin** (now 73): Operating cash flow - Model
  - 2 before **Long term debt** (now 85–86): Cash OpEx run-rate, Non-cash COGS (D&A + SBC)
- **Formulas:**
  - **Unit COGS - Model** `$160` copy-from-C → `INDEX(COGS, MATCH("Unit COGS - Model"))` (Q2 2026 −62.3% adj. GM + haircut × 73 pts over Q2’26–Q2’27, then blend to terminal $/kWh as lines 2→4)
  - **Adjusted gross margin - Model** from COGS; **Adjusted gross profit - Model** = Revenue - Model × adj. GM / 100
  - **COGS - Model** += `$C$Non-cash COGS` (Q2 SBC+D&A $5.932M)
  - **Adjusted EBITDA - Model** GP−OpEx → Adj. GP − Cash OpEx run-rate ($28.486M, Q2 implied). **Operating cash flow - Model** = Adj. EBITDA (CFO proxy)
- **Data:** Haircut **70** (C42), Terminal unit COGS **160** (C43), Cash OpEx **28.486**, Non-cash COGS **5.932**. Adj. GP actuals Q2 2025–Q2 2026 from the 8-K recon. COGS tab: guided 25/20/20/8 pts, $200M/qtr illustration, thread + Slide 11 links.
- **Side effects:** No chart API. No chart objects in this workbook today; if you add Operations/Money charts later, row inserts will have shifted series — fix in the UI.

## 2026-09-09 — Populate reported actuals Q1 2025–Q2 2026

Filled Actual rows from 10-Q/10-K XBRL and earnings 8-K Ex. 99.1 / transcripts. Repeatable via `models/EOSE/scripts/fetch_sec_gaap.py` and `load_quarterly_actuals.py`.

- **Tab / range:** `Quarterly Financials` C–H (2025 Q1 – 2026 Q2) Actual cells; `Financials Definitions` B for Long term debt / Total debt
- **Insert/delete:** none
- **Formulas:** unchanged (Model rows not rewritten)
- **Data:** 112 Actual cells. Notable fills/corrections vs prior blanks/approximations:
  - **Q1 2025:** pipeline $15.6B / 60 GWh, backlog $680.9M / 2.6 GWh, bookings $9.2M, adj. EBITDA **−$43.238M** (recon, was residual −$43.3M), GAAP NI **+$15.136M**, shares 225.5M / 436.4M diluted, LTD $66.2M, total debt $325.5M
  - **Q2 2025:** pipeline $18.8B / 77 GWh, backlog $672.5M / 2.6 GWh, bookings $6.9M, cash **$183.175M** (was blank), shares, debt
  - **Q3 2025:** SG&A **$19.786M** (was $20.375M derived as opex−R&D), opex $27.296M, total debt $448.5M, basic shares
  - **Q4 2025:** SG&A $18.841M, R&D $7.579M, opex $26.850M (were blank), shares 307.664M WAS, LTD $662.5M, total debt $813.3M
  - **Q1 2026:** pipeline GWh **107**, basic WAS 339.602M, LTD $506.4M, total debt $619.5M, adj. EBITDA −$68.019M
  - **Q2 2026:** adj. EBITDA **−$71.355M** (was −$71.4M), cash $364.070M, basic 339.799M, LTD $453.8M, total debt $617.1M. Fully diluted Actual left blank so Model keeps Q1 544.8M if-converted
- **Side effects:** none on charts (no chart API). Gross margin / adj. EBITDA margin formulas will populate where Revenue actuals already existed.

## 2026-09-09 — Units column, freeze after Quarter

Column B is units only. Numbers and formulas start at C. Freeze sits between Quarter and Quarter ending.

- **Tab / range:** `Quarterly Financials` `A1:Z` (grid rewritten). Financials Definitions notes for C-column scalars.
- **Insert/delete:** none
- **Formulas:** Scalar refs `$B$` → `$C$` (As of date, cycle-time floor, capex per line, net interest). Copy-across levers are `=$C$row` on D:Z; C keeps the seed value (no self-ref).
- **Data:** Restored unit strings in B (including B1 `Units`). Moved As of date, FY2026 guide, utilization, 45X, unit COGS, EV/EBITDA, discount, cycle floor, capex, interest, module energy, modules per cube, conversion lag into C. A1 blank.
- **Side effects:** `frozenRowCount` 6 → 3 (Year + Quarter stay frozen). B1 bold. No chart edits.

## 2026-09-09 — Actual vs Model rebuild (quarterly)

Rebuild the operating model on OPEN’s Actual / Model pattern without adding a weekly spine. Feltonomics and COGS left in place (empty). No chart objects created.

- **Tab / range:** Renamed **Quarterly Results/Projections** → **Quarterly Financials** (`A1:Z93`). Added **Welcome**, **Financials Definitions**, **Shares**, **Price History**. Reordered tabs; **Reference** / **Feltonomics** / **COGS** unchanged.
- **Insert/delete:** New sheets added (Welcome, Financials Definitions, Shares, Price History). Quarterly grid cleared and rewritten (93 rows × 26 cols). Unmerged leftover year-header merges so every quarter has Year/Quarter.
- **Formulas:** Capacity-only revenue (`modules × ASP + 45X`) replaced with paired Actual / Model rows. **Revenue - Model** = GWh shipped × ASP (no 45X). **COGS - Model** = unit COGS × GWh − 45X credits. Backlog - Model = prior + orders − revenue (prefer actual). GWh shipped - Model = `MIN(factory capacity, beginning backlog GWh / lag)`. EV blank unless annualized EBITDA > 0. **Stock price** XLOOKUPs Price History by quarter-end. Canonical templates in `quarterly_model_formulas.py`.
- **Data:** Actuals through **Q2 2026** (revenue, COGS, GM, opex, adj. EBITDA, NI, cash, pipeline, backlog, bookings where known, lines, shares). As of date **2026-09-09**. FY2026 guide **$300–350M** in column B. Line ramp and $160/kWh unit COGS kept as Model levers.
- **Side effects:** Frozen A–B and rows 1–6 on Quarterly Financials. Bold labels. Column A widened. **No charts** — add Actual vs Model series in the UI if you want them. Price History GOOGLEFINANCE spill may take a minute to fill.

## 2026-09-09 — Pack linked to existing workbook

No sheet writes. Registered this live workbook as the EOSE vehicle (`snapshot.json` tabs: Quarterly Results/Projections, Feltonomics, COGS, Reference; 0 charts).
