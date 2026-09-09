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
