# Open Model

Public investment models — one Google Sheet per ticker — with Python tooling anyone can review and collaborate on.

Each vehicle (stock, ETF, or other `GOOGLEFINANCE` symbol) is a **model pack** under [`models/`](models/) keyed by ticker. Packs do **not** share a universal P&L schema: Opendoor’s iBuying funnel is specific to OPEN; a battery or solar model should use its own tabs and formulas.

> Not investment advice. Models mix company-reported figures, management guidance, and explicit guesses where issuers do not disclose detail.

## Models

| Ticker | Name | Pack | Spreadsheet |
| --- | --- | --- | --- |
| **OPEN** | Opendoor Technologies | [models/OPEN](models/OPEN/README.md) | [Opendoor Model](https://docs.google.com/spreadsheets/d/1BhauTzGc9Nyt1J9gQl3NdCnpSSKCpSLbY9H7p5Obvc4) |
| **EOSE** | Eos Energy Enterprises | [models/EOSE](models/EOSE/README.md) | [EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing) (view or comment) |

## Layout

```
models/{TICKER}/     issuer pack (README, RESOURCES, CHANGELOG, snapshot, formulas, scripts)
sheets/              shared Google Sheets kernel (OAuth, client, ticker registry, labels)
scripts/             shared CLIs (--ticker); issuer one-shots live in models/{TICKER}/scripts/
config/              OAuth credentials and settings.json (gitignored IDs)
```

**One Google Sheet per ticker.** Configure IDs in `config/settings.json` (copy from [`config/settings.example.json`](config/settings.example.json)):

```json
{
  "default_ticker": "OPEN",
  "tickers": {
    "OPEN": {
      "name": "Opendoor Technologies",
      "spreadsheet_id": "paste-or-url",
      "price_symbol": "OPEN"
    },
    "EOSE": {
      "name": "Eos Energy Enterprises",
      "spreadsheet_id": "paste-or-url",
      "price_symbol": "EOSE"
    }
  }
}
```

`price_symbol` is what `GOOGLEFINANCE` queries (e.g. `OPEN`, `SPY`, `BTCUSD`). Override the ticker with `--ticker OPEN` or `OPEN_MODEL_TICKER=OPEN`.

Repo-level changes go in [CHANGELOG.md](CHANGELOG.md). Sheet writes go in `models/{TICKER}/CHANGELOG.md`.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then complete [Google Cloud setup](#one-time-google-cloud-setup), save credentials, and run:

```bash
python scripts/auth_setup.py
python scripts/test_connection.py --ticker OPEN
python scripts/validate_workbook_snapshot.py --ticker OPEN
python scripts/validate_model_formulas.py --ticker OPEN --offline
python scripts/restore_weekly_model_formulas.py --ticker OPEN
python scripts/sync_repo_from_live_sheet.py --ticker OPEN
```

Default ticker is `OPEN` when `--ticker` is omitted.

### Add another ticker

```bash
python scripts/new_ticker.py CSIQ --name "Canadian Solar"
```

That stubs `models/CSIQ/` and prints the `settings.json` fragment. Create (or link) a Google Sheet yourself, paste the ID, and build that pack’s tabs independently — do not copy OPEN’s funnel formulas. EOSE is an example of linking a pre-existing workbook ([models/EOSE](models/EOSE/README.md)).

## One-time Google Cloud setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project (e.g. `open-model`)
2. Enable [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com) and [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
3. **OAuth consent screen** → External → add scopes `spreadsheets` and `drive` → add yourself as a test user
4. **Credentials** → Create OAuth client ID → Desktop app → download JSON
5. Save the download as `config/credentials.json`

## Usage

```python
from sheets import SheetsClient

client = SheetsClient(ticker="OPEN")
print(client.list_worksheets())
data = client.read_range("Weekly Financials", "A1:D20")
```

Shared helpers: label→row lookups in `sheets/labels.py`, weekly/quarterly spread formulas in `sheets/formulas.py`, `GOOGLEFINANCE` spill in `sheets/price_history.py` (pass `price_symbol`).

**Charts are manual-only.** Do not edit chart objects via the Sheets API; after row inserts, fix series ranges in the Google Sheets UI if lines look wrong. See `.cursor/rules/charts-manual-only.mdc`.
