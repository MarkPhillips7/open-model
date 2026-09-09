# Changelog (repository)

Platform and shared-tooling changes. **Sheet writes** belong in `models/{TICKER}/CHANGELOG.md` (see [models/OPEN/CHANGELOG.md](models/OPEN/CHANGELOG.md)).

Entry template:

```markdown
## YYYY-MM-DD — short title

- **What:** what changed in the repo
- **Why:** motivation
```

---

## 2026-09-08 — Multi-ticker layout

Reposition the repo as a ticker-keyed platform. One Google Sheet per ticker; Opendoor lives in `models/OPEN/`.

- **What:** `config/settings.json` is a ticker registry (`default_ticker` + `tickers.{KEY}.{spreadsheet_id,price_symbol,name}`). `SheetsClient(ticker=...)` and shared CLIs take `--ticker` (or `OPEN_MODEL_TICKER`). OPEN domain modules, snapshot, RESOURCES, and sheet CHANGELOG moved to `models/OPEN/`. Shared kernel stays in `sheets/` (registry, client, labels, formulas, parameterized `GOOGLEFINANCE`). OPEN-only scripts moved to `models/OPEN/scripts/`. Added `scripts/new_ticker.py`.
- **Why:** Keep this repository (the name already fits) so other issuers can be added without sharing Opendoor’s iBuying schema. No live sheet writes.
