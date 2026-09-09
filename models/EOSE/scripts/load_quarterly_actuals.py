#!/usr/bin/env python3
"""Write models/EOSE/actuals.py onto Quarterly Financials (Actual rows only).

Does not touch Model formula rows. Repeat after each earnings print once
actuals.py is updated (see fetch_sec_gaap.py + RESOURCES.md).

    python models/EOSE/scripts/load_quarterly_actuals.py
    python models/EOSE/scripts/load_quarterly_actuals.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from models.EOSE.actuals import ACTUALS  # noqa: E402
from models.EOSE.layout import (  # noqa: E402
    FIRST_VALUE_COL_INDEX,
    QUARTERLY,
    quarters,
)
from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.labels import label_rows, row_by_label  # noqa: E402


def column_for(year: int, quarter: int) -> str:
    idx = quarters().index((year, quarter))
    return col_letter(FIRST_VALUE_COL_INDEX + idx)


def build_updates(label_map: dict[str, int]) -> list[dict]:
    updates: list[dict] = []
    for (year, q), fields in sorted(ACTUALS.items()):
        col = column_for(year, q)
        for label, value in fields.items():
            row = row_by_label(label_map, label, QUARTERLY)
            updates.append({"range": f"{col}{row}", "values": [[value]]})
    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = SheetsClient(ticker="EOSE")
    labels = label_rows(client, QUARTERLY)
    updates = build_updates(labels)
    by_q: dict[tuple[int, int], int] = {}
    for (year, q), fields in ACTUALS.items():
        by_q[(year, q)] = len(fields)
        print(f"{year} Q{q} {column_for(year, q)}: {len(fields)} actuals")
    print(f"Total cells: {len(updates)}")
    if args.dry_run:
        print("Dry run — no sheet writes.")
        return
    client.worksheet(QUARTERLY).batch_update(updates, value_input_option="RAW")
    print(f"Wrote {len(updates)} cells on {QUARTERLY!r}")


if __name__ == "__main__":
    main()
