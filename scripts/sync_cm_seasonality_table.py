#!/usr/bin/env python3
"""Refresh Seasonality tab CM Seasonal Adj row from sheets/cm_seasonality.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.add_cm_seasonality_row import ensure_seasonality_table  # noqa: E402
from sheets import SheetsClient  # noqa: E402


def main() -> None:
    client = SheetsClient()
    ensure_seasonality_table(client, force_refresh=True)
    print("Done.")


if __name__ == "__main__":
    main()
