#!/usr/bin/env python3
"""Verify OAuth credentials and spreadsheet access."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.client import SheetsClient


def main() -> None:
    try:
        client = SheetsClient()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Setup incomplete: {exc}")
        sys.exit(1)

    summary = client.summary()
    print("Connection successful!\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
