#!/usr/bin/env python3
"""Stub a models/{TICKER}/ pack. Does not create or clone a Google Sheet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.registry import MODELS_DIR, validate_ticker_key  # noqa: E402

README_STUB = """# {name} ({ticker})

Investment model pack for **{name}** (`{ticker}`).

This pack is independent of other tickers — do not copy another issuer's operating-model formulas. Shared tooling (OAuth, `--ticker`, Price History) is documented in the [repo README](../../README.md).

The live workbook is a Google Sheet. Paste its ID into `config/settings.json` under `tickers.{ticker}.spreadsheet_id`.

Sources: [RESOURCES.md](RESOURCES.md). Sheet edits: [CHANGELOG.md](CHANGELOG.md).
"""

RESOURCES_STUB = """# Resources

Sources and references for the **{name}** (`{ticker}`) model. Not investment advice.

Spreadsheet: add the Google Sheet URL here after you create or link it.
"""

CHANGELOG_STUB = """# Spreadsheet changelog

The live model is the Google Sheet for **{name}** (`{ticker}`). Git does not see those edits unless they are recorded here. Repo/platform changes go in the [root CHANGELOG](../../CHANGELOG.md).

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
"""

SNAPSHOT_STUB = {
    "worksheets": [],
    "charts": [],
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create models/{TICKER}/ stubs. Does not create a Google Sheet."
    )
    parser.add_argument(
        "ticker",
        help="Filesystem-safe ticker key (OPEN, EOSE, CSIQ, BTCUSD)",
    )
    parser.add_argument("--name", default="", help="Display name (default: ticker)")
    parser.add_argument(
        "--price-symbol",
        default="",
        help="GOOGLEFINANCE symbol (default: ticker)",
    )
    args = parser.parse_args()

    try:
        ticker = validate_ticker_key(args.ticker)
    except ValueError as exc:
        print(exc)
        sys.exit(2)

    name = args.name.strip() or ticker
    price_symbol = args.price_symbol.strip() or ticker
    pack = MODELS_DIR / ticker
    if pack.exists():
        print(f"Already exists: {pack}")
        sys.exit(1)

    pack.mkdir(parents=True)
    (pack / "scripts").mkdir()
    (pack / "__init__.py").write_text(f'"""Model pack for {name} ({ticker})."""\n')
    (pack / "README.md").write_text(README_STUB.format(name=name, ticker=ticker))
    (pack / "RESOURCES.md").write_text(RESOURCES_STUB.format(name=name, ticker=ticker))
    (pack / "CHANGELOG.md").write_text(CHANGELOG_STUB.format(name=name, ticker=ticker))
    (pack / "snapshot.json").write_text(json.dumps(SNAPSHOT_STUB, indent=2) + "\n")

    fragment = {
        ticker: {
            "name": name,
            "spreadsheet_id": "paste-or-url",
            "price_symbol": price_symbol,
        }
    }
    print(f"Created {pack}")
    print()
    print("Add this to config/settings.json under \"tickers\":")
    print(json.dumps(fragment, indent=2))
    print()
    print("Then create or link a Google Sheet and paste its ID. Do not copy another")
    print("ticker's operating-model formulas — only the shared kernel is reusable.")


if __name__ == "__main__":
    main()
