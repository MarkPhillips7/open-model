#!/usr/bin/env python3
"""Create Shares tab, move events from Transitions, add adjustment helper row."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.formulas import SHARES_MODEL_LABEL  # noqa: E402
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows  # noqa: E402
from sheets.shares_events import (  # noqa: E402
    SHARES_ADJUSTMENT_LABEL,
    SHARES_MODE_LEGEND,
    SHARES_SHEET,
    SHARES_SHEET_GRID,
)

TRANSITIONS = "Transitions"


def ensure_shares_sheet(client: SheetsClient) -> None:
    if SHARES_SHEET in client.list_worksheets():
        print(f"{SHARES_SHEET!r} already exists")
    else:
        client.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": SHARES_SHEET,
                                "index": 3,
                                "gridProperties": {"rowCount": 40, "columnCount": 12},
                            }
                        }
                    }
                ]
            }
        )
        print(f"Added sheet {SHARES_SHEET!r}")

    ws = client.worksheet(SHARES_SHEET)
    ws.update(SHARES_SHEET_GRID, range_name="A1:I8", value_input_option="USER_ENTERED")
    ws.update(SHARES_MODE_LEGEND, range_name="A22:B24", value_input_option="USER_ENTERED")
    print(f"Wrote {SHARES_SHEET} event table and legend")


def clear_transitions_share_block(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    ws.batch_clear(["A25:B34"])
    print(f"Cleared {TRANSITIONS}!A25:B34")


def ensure_adjustment_row(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if SHARES_ADJUSTMENT_LABEL in weekly_labels:
        print(f"{SHARES_ADJUSTMENT_LABEL!r} already on {WEEKLY}")
        return
    if SHARES_MODEL_LABEL not in weekly_labels:
        raise KeyError(f"{SHARES_MODEL_LABEL!r} missing on {WEEKLY}")
    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=SHARES_MODEL_LABEL,
        labels=[SHARES_ADJUSTMENT_LABEL],
    )
    quarterly_labels = label_rows(client, QUARTERLY)
    if SHARES_ADJUSTMENT_LABEL not in quarterly_labels and SHARES_MODEL_LABEL in quarterly_labels:
        insert_rows_before_label(
            client,
            tab=QUARTERLY,
            before_label=SHARES_MODEL_LABEL,
            labels=[SHARES_ADJUSTMENT_LABEL],
        )


def main() -> None:
    client = SheetsClient()
    ensure_shares_sheet(client)
    clear_transitions_share_block(client)
    ensure_adjustment_row(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
