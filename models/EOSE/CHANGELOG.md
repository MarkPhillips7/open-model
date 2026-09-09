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
