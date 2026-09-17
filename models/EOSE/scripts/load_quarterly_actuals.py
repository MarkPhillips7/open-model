#!/usr/bin/env python3
"""Write models/EOSE/actuals.py onto Quarterly Financials (Actual rows only).

Does not touch Model formula rows. Repeat after each earnings print once
actuals.py is updated (see fetch_sec_gaap.py + RESOURCES.md).

Refuses to run if live labels drifted from layout.ROWS, and skips any target
cell that currently holds a formula (so a load cannot wipe model edits).

    python models/EOSE/scripts/load_quarterly_actuals.py
    python models/EOSE/scripts/load_quarterly_actuals.py --dry-run
    python models/EOSE/scripts/load_quarterly_actuals.py --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from models.EOSE.actuals import ACTUALS, ACTUALS_BY_UNITS  # noqa: E402
from models.EOSE.layout import (  # noqa: E402
    FIRST_VALUE_COL_INDEX,
    QUARTERLY,
    quarters,
    require_live_layout_match,
    row_number_for,
)
from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402


def column_for(year: int, quarter: int) -> str:
    idx = quarters().index((year, quarter))
    return col_letter(FIRST_VALUE_COL_INDEX + idx)


def build_updates() -> list[dict]:
    updates: list[dict] = []
    for (year, q), fields in sorted(ACTUALS.items()):
        col = column_for(year, q)
        for label, value in fields.items():
            row = row_number_for(label)
            updates.append({"range": f"{col}{row}", "values": [[value]]})
    for (year, q), fields in sorted(ACTUALS_BY_UNITS.items()):
        col = column_for(year, q)
        for (label, units), value in fields.items():
            row = row_number_for(label, units)
            updates.append({"range": f"{col}{row}", "values": [[value]]})
    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Write even if live Quarterly Financials labels differ from layout.ROWS",
    )
    args = parser.parse_args()

    client = SheetsClient(ticker="EOSE")
    if not args.force:
        require_live_layout_match(client, action="load quarterly actuals")
    updates = build_updates()
    for (year, q), fields in ACTUALS.items():
        print(f"{year} Q{q} {column_for(year, q)}: {len(fields)} actuals")
    extra = sum(len(v) for v in ACTUALS_BY_UNITS.values())
    if extra:
        print(f"Plus {extra} unit-disambiguated actuals")
    print(f"Total cells: {len(updates)}")
    if args.dry_run:
        print("Dry run — no sheet writes.")
        return

    ws = client.worksheet(QUARTERLY)
    live = client.batch_get(
        [f"{QUARTERLY}!{u['range']}" for u in updates], as_formulas=True
    )
    filtered: list[dict] = []
    skipped = 0
    for update, grid in zip(updates, live, strict=True):
        cell = ""
        if grid and grid[0]:
            cell = grid[0][0]
        if isinstance(cell, str) and cell.startswith("="):
            print(f"Skip {update['range']}: live cell is a formula")
            skipped += 1
            continue
        filtered.append(update)
    if skipped:
        print(f"Skipped {skipped} formula cell(s)")
    if not filtered:
        print("Nothing to write.")
        return
    ws.batch_update(filtered, value_input_option="RAW")
    print(f"Wrote {len(filtered)} cells on {QUARTERLY!r}")


if __name__ == "__main__":
    main()
