#!/usr/bin/env python3
"""Create Financials Definitions tab mirroring Weekly Financials labels with field notes."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from sheets import SheetsClient  # noqa: E402
from models.OPEN.financials_definitions import (  # noqa: E402
    FIELD_NOTES,
    FINANCIALS_DEFINITIONS_SHEET,
)
from sheets.labels import WEEKLY, label_rows  # noqa: E402

MISSING_NOTE = "(Definition not yet written — add to models/OPEN/financials_definitions.py)"


def ensure_definitions_sheet(client: SheetsClient) -> None:
    if FINANCIALS_DEFINITIONS_SHEET not in client.list_worksheets():
        client.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": FINANCIALS_DEFINITIONS_SHEET,
                                "index": 2,
                                "gridProperties": {"rowCount": 120, "columnCount": 4},
                            }
                        }
                    }
                ]
            }
        )
        print(f"Added sheet {FINANCIALS_DEFINITIONS_SHEET!r}")
    else:
        print(f"{FINANCIALS_DEFINITIONS_SHEET!r} already exists")


def build_rows(client: SheetsClient) -> tuple[list[list[str]], list[str]]:
    weekly_labels = label_rows(client, WEEKLY, max_row=120)
    ordered = sorted(weekly_labels.items(), key=lambda kv: kv[1])
    labels = [label for label, _ in ordered]

    missing: list[str] = []
    notes: list[str] = []
    for label in labels:
        if label in FIELD_NOTES:
            notes.append(FIELD_NOTES[label])
        else:
            missing.append(label)
            notes.append(MISSING_NOTE)

    rows = [[label, note] for label, note in zip(labels, notes, strict=True)]
    return rows, missing


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    ensure_definitions_sheet(client)

    rows, missing = build_rows(client)
    end_row = len(rows)
    client.write_range(FINANCIALS_DEFINITIONS_SHEET, f"A1:B{end_row}", rows)

    print(f"Wrote {end_row} rows to {FINANCIALS_DEFINITIONS_SHEET!r} (A=labels, B=notes)")
    if missing:
        print(f"Warning: {len(missing)} labels missing definitions:")
        for label in missing:
            print(f"  - {label}")
    else:
        print("All Weekly Financials labels have definitions.")


if __name__ == "__main__":
    main()
