#!/usr/bin/env python3
"""Verify OAuth credentials and spreadsheet access."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.client import SheetsClient
from sheets.registry import parse_ticker_argv, resolve_ticker


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    if rest:
        print(f"Unknown arguments: {rest}")
        sys.exit(2)
    try:
        ticker = resolve_ticker(ticker_arg)
        client = SheetsClient(ticker=ticker)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"Setup incomplete: {exc}")
        sys.exit(1)

    summary = client.summary()
    print("Connection successful!\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
