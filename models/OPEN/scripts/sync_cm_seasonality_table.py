#!/usr/bin/env python3
"""Push CM Seasonal Adj row from models/OPEN/cm_seasonality.py to the spreadsheet.

Prefer pull_cm_stack_from_sheet.py when the live workbook was edited manually.
"""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from add_cm_seasonality_row import ensure_seasonality_table  # noqa: E402
from sheets import SheetsClient  # noqa: E402


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    ensure_seasonality_table(client, force_refresh=True)
    print("Done.")


if __name__ == "__main__":
    main()
