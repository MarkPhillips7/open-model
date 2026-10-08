# Changelog (repository)

Platform and shared-tooling changes. **Sheet writes** belong in `models/{TICKER}/CHANGELOG.md` (see [OPEN](models/OPEN/CHANGELOG.md), [EOSE](models/EOSE/CHANGELOG.md)).

Entry template:

```markdown
## YYYY-MM-DD — short title

- **What:** what changed in the repo
- **Why:** motivation
```

## 2026-09-25 — CSIQ model pack

- **What:** Added `models/CSIQ/` for Canadian Solar, on the Comstock workbook pattern (levers, actuals vs model rows, yellow plans, sum of parts). Settings example and the models table include CSIQ.
- **Why:** The live CSIQ sheet needed a pack of its own. Operating formulas are Canadian Solar's, not a copy of Comstock's recycling math.

## 2026-10-07 — OPEN Home Sales: provisional new-quarter days from Open Tracker

- **What:** `open_tracker.py` parses Daily Summary **Houses P. Sold** (column found by header) and a settled relist rate from `weeklySoldData` (median `noise_pct`, last 12 weeks excluding the newest 4). `accountable.py` adds `uncovered_new_quarter_days()`. `load_home_sales()` fills those days with P. Sold × (1 − relist rate) and stores them under `provisional` in the snapshot, outside quarter history. `sync_weekly_actuals.py` fetches the tracker page once for both listings and Home Sales.
- **Why:** After a quarter ends, Accountable's as-of date moves into the new quarter before it posts a new chart, which left the first days of the quarter blank.

## 2026-10-06 — OPEN weekly sync: new weeks, quarter-end stubs, quarter history

- **What:** `sync_weekly_actuals.py` pads row reads to the full week spine, so blank future weeks can be filled. Before this fix, the Sheets API dropped trailing blanks and the sync could only revise existing weeks. `accountable.py` maps non-Saturday COE points (quarter-end stubs like 9/30) to the next Saturday week. It also keeps each quarter's cumulative series in `accountable_resale_coes.json` (`quarters`) and merges them, via the shared `load_home_sales()` used by both sync scripts.
- **Why:** The 10/3 week wouldn't write, the 9/30 stub was silently dropped, and when Accountable switches to its Q4 chart the old code would have blanked every Q3 Home Sales week on the sheet.

## 2026-10-06 — Google OAuth re-prompt actually fires on a revoked token

- **What:** `sheets.auth.get_client()` now refreshes the saved credentials immediately, inside the `RefreshError` handler, instead of leaving gspread to refresh lazily on the first spreadsheet call.
- **Why:** The 2026-09-10 re-prompt never ran: the expired token only failed later in `open_by_key`, outside the `try`, so scripts crashed with `invalid_grant` instead of opening a sign-in window.

## 2026-10-06 — `sync_weekly_actuals.py` can add new weeks

- **What:** `read_weekly_row()` pads the row read out to every week column.
- **Why:** The Sheets API drops trailing blank cells, so blank future weeks were missing from the existing-values map and got skipped. The script could revise weeks already on the sheet but never fill in a new one.

## 2026-10-06 — `sync_weekly_actuals.py` can add new weeks

- **What:** `read_weekly_row()` pads the row read out to every week column.
- **Why:** The Sheets API drops trailing blank cells, so blank future weeks were missing from the existing-values map and got skipped. The script could revise weeks already on the sheet but never fill in a new one.

## 2026-10-06 — `sync_weekly_actuals.py` can add new weeks

- **What:** `read_weekly_row()` pads the row read out to every week column.
- **Why:** The Sheets API drops trailing blank cells, so blank future weeks were missing from the existing-values map and got skipped. The script could revise weeks already on the sheet but never fill in a new one.

---

## 2026-09-23 — OPEN weekly actuals sync (Accountable + Open Tracker)

- **What:** Added `models/OPEN/scripts/sync_weekly_actuals.py` plus Accountable acquisition-contract parsing and Open Tracker New Listings parsing (`open_tracker.py`). Snapshots for contracts/listings under `models/OPEN/data/`.
- **Why:** Weekly funnel refreshes were mostly manual (only Home Sales was scripted); one CLI now covers contracts, listings, and Home Sales.

---

## 2026-09-22 — ASP formulas treat missing revenue / zero as blank

- **What:** `sheets/formulas.py` adds `quarterly_asp_formula()` (blank when revenue or home sales is 0) and `weekly_asp_formula()` now carry-forwards on 0 / `#DIV/0!`, not only blank. OPEN spread script restores quarterly ASP.
- **Why:** Forward quarters with Accountable home sales but no revenue were printing ASP `0` / `#DIV/0!` into Weekly Financials.

## 2026-09-10 — Re-prompt Google OAuth when the saved token is revoked

- **What:** `sheets.auth.get_client()` catches `RefreshError`, deletes `config/authorized_user.json`, and retries so `auth_setup.py` opens a browser instead of dying on `invalid_grant`.
- **Why:** A revoked refresh token was reused silently; the user never got a login prompt.

## 2026-09-10 — OPEN CM-stack pull actually reads hardcoded cells

- **What:** `models/OPEN/scripts/pull_cm_stack_from_sheet.py` was passing `[grid]` into a helper that already expects a grid, so every CM Core / Adjustments / Improvement cell looked like a formula. Sync now reads `A1:A120` and unwraps one level. Captured the live late-Aug/Sep CM adjustment path (see `models/OPEN/CHANGELOG.md`).
- **Why:** Manual Kaz 9 Sep 2026 CM edits would have been overwritten on the next restore.

---

## 2026-09-09 — EOSE MWh shipped / derived $/kWh rows

- **What:** Quarterly Financials layout now has **MWh shipped**, **Z3 ASP - Derived**, **Unit COGS - Derived**, and **Pipeline quarterly growth rate**. Pipeline (GWh) - Model uses ASP not unit COGS. Column widths captured from the live sheet. `pull_financials_definitions_from_sheet.py` added for EOSE.
- **Why:** User added energy and derived-unit rows by hand; a duplicate Revenue label would have broken MATCH, and Pipeline GWh had a shifted denominator.

---

## 2026-09-09 — EOSE COGS cost-out engine

- **What:** `models/EOSE/cogs.py` plus Quarterly Financials haircut / adj. GM / adj. EBITDA-as-cash-proxy formulas. `setup_cogs.py` writes the live **COGS** tab (see `models/EOSE/CHANGELOG.md`).
- **Why:** Model the Q2 2026 73-pt cost-out with an explicit execution haircut instead of a flat $160/kWh from day one.

## 2026-09-09 — EOSE Actual vs Model pack

Wire the EOSE quarterly model to OPEN’s restore/validate loop and rebuild the live sheet.

- **What:** `models/EOSE/` quarterly formulas, actuals, Welcome, Definitions, Shares. Shared CLIs load `quarterly_model_formulas.py` when there is no weekly module. `GOOGLEFINANCE` spill can take an explicit date range. Live EOSE sheet rewritten (see `models/EOSE/CHANGELOG.md`). Feltonomics and COGS tabs kept. No chart API writes.
- **Why:** Distinguish reported prints from the factory/backlog forecast so Q2 2026 misses are visible, without copying OPEN’s weekly funnel.

## 2026-09-09 — Add EOSE model pack

Register Eos Energy as a second vehicle beside OPEN.

- **What:** `models/EOSE/` pack (README, RESOURCES, CHANGELOG, workbook snapshot). `tickers.EOSE` in `config/settings.example.json`. Shared formula restore/validate CLIs skip packs that have no `weekly_model_formulas.py`. No writes to the live EOSE sheet.
- **Why:** Link the existing [EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing) without forcing OPEN’s weekly iBuying schema onto a quarterly Z3 manufacturing model.

## 2026-09-08 — Multi-ticker layout

Reposition the repo as a ticker-keyed platform. One Google Sheet per ticker; Opendoor lives in `models/OPEN/`.

- **What:** `config/settings.json` is a ticker registry (`default_ticker` + `tickers.{KEY}.{spreadsheet_id,price_symbol,name}`). `SheetsClient(ticker=...)` and shared CLIs take `--ticker` (or `OPEN_MODEL_TICKER`). OPEN domain modules, snapshot, RESOURCES, and sheet CHANGELOG moved to `models/OPEN/`. Shared kernel stays in `sheets/` (registry, client, labels, formulas, parameterized `GOOGLEFINANCE`). OPEN-only scripts moved to `models/OPEN/scripts/`. Added `scripts/new_ticker.py`.
- **Why:** Keep this repository (the name already fits) so other issuers can be added without sharing Opendoor’s iBuying schema. No live sheet writes.
