#!/usr/bin/env python3
"""Compare live spreadsheet layout to models/{TICKER}/snapshot.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.registry import parse_ticker_argv, resolve_ticker, snapshot_path  # noqa: E402
from sheets.workbook_snapshot import (  # noqa: E402
    compare_snapshots,
    fetch_live_snapshot,
    load_snapshot,
    save_snapshot,
)


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    ticker = resolve_ticker(ticker_arg)
    update = "--update" in rest
    offline = "--offline" in rest
    unknown = [a for a in rest if a not in {"--update", "--offline"}]
    if unknown:
        print(f"Unknown arguments: {unknown}")
        sys.exit(2)

    path = snapshot_path(ticker)

    if update:
        client = SheetsClient(ticker=ticker)
        snapshot = fetch_live_snapshot(client)
        save_snapshot(snapshot, path)
        print(f"Updated {path}")
        print(f"  worksheets: {len(snapshot['worksheets'])}")
        print(f"  charts: {len(snapshot['charts'])}")
        return

    expected = load_snapshot(path)
    if offline:
        print(f"Offline: loaded {path} (use without --offline to compare live sheet).")
        print(f"  worksheets: {expected['worksheets']}")
        print(f"  charts: {len(expected['charts'])}")
        return

    client = SheetsClient(ticker=ticker)
    actual = fetch_live_snapshot(client)
    issues = compare_snapshots(expected, actual)
    if issues:
        print("Workbook snapshot validation FAILED:")
        for item in issues:
            print(f"  - {item}")
        print("\nIf the live sheet changed intentionally, run:")
        print(f"  python scripts/validate_workbook_snapshot.py --ticker {ticker} --update")
        sys.exit(1)

    print(f"Workbook snapshot validation passed for {ticker}.")


if __name__ == "__main__":
    main()
