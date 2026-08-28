#!/usr/bin/env python3
"""Compare live spreadsheet layout to config/workbook_snapshot.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.workbook_snapshot import (  # noqa: E402
    compare_snapshots,
    fetch_live_snapshot,
    load_snapshot,
    save_snapshot,
)


def main() -> None:
    update = "--update" in sys.argv
    offline = "--offline" in sys.argv

    if update:
        client = SheetsClient()
        snapshot = fetch_live_snapshot(client)
        save_snapshot(snapshot)
        print(f"Updated {ROOT / 'config' / 'workbook_snapshot.json'}")
        print(f"  worksheets: {len(snapshot['worksheets'])}")
        print(f"  charts: {len(snapshot['charts'])}")
        return

    expected = load_snapshot()
    if offline:
        print("Offline: loaded snapshot only (use without --offline to compare live sheet).")
        print(f"  worksheets: {expected['worksheets']}")
        print(f"  charts: {len(expected['charts'])}")
        return

    client = SheetsClient()
    actual = fetch_live_snapshot(client)
    issues = compare_snapshots(expected, actual)
    if issues:
        print("Workbook snapshot validation FAILED:")
        for item in issues:
            print(f"  - {item}")
        print("\nIf the live sheet changed intentionally, run:")
        print("  python scripts/validate_workbook_snapshot.py --update")
        sys.exit(1)

    print("Workbook snapshot validation passed.")


if __name__ == "__main__":
    main()
