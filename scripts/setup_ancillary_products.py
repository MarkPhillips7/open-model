#!/usr/bin/env python3
"""Set up mortgage and title ancillary modeling on the live sheet."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.ancillary_products import (  # noqa: E402
    DOMA_GROWTH_MULTIPLIER_LABEL,
    DOMA_REFI_PROFIT_LABEL,
    OLD_OPEN_TITLE_LABEL,
    OPEN_TITLE_PURCHASE_PERCENT_LABEL,
    TRANSITIONS,
    TRANSITIONS_ANCILLARY_ROWS,
)
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows  # noqa: E402


def write_transitions_assumptions(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    start_row = 29
    values = [[label, value] for label, value in TRANSITIONS_ANCILLARY_ROWS]
    end_row = start_row + len(values) - 1
    ws.update(values, range_name=f"A{start_row}:B{end_row}", value_input_option="RAW")
    # Clear removed Doma inputs (legacy layout had blank + B32:B33 through row 33).
    ws.batch_clear([f"A{end_row + 1}:B33"])
    print(f"{TRANSITIONS}: wrote ancillary assumptions A{start_row}:B{end_row}")


def rename_title_attach_label(client: SheetsClient) -> None:
    for tab in (WEEKLY, QUARTERLY):
        labels = label_rows(client, tab, max_row=50)
        if OLD_OPEN_TITLE_LABEL in labels:
            row = labels[OLD_OPEN_TITLE_LABEL]
            client.worksheet(tab).update(
                [[OPEN_TITLE_PURCHASE_PERCENT_LABEL]],
                range_name=f"A{row}",
                value_input_option="RAW",
            )
            print(f"{tab}: renamed row {row} to {OPEN_TITLE_PURCHASE_PERCENT_LABEL!r}")
        elif OPEN_TITLE_PURCHASE_PERCENT_LABEL in labels:
            print(f"{tab}: {OPEN_TITLE_PURCHASE_PERCENT_LABEL!r} already present")


def ensure_doma_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if DOMA_GROWTH_MULTIPLIER_LABEL in weekly_labels and DOMA_REFI_PROFIT_LABEL in weekly_labels:
        print(f"{WEEKLY}: Doma rows already present")
        return

    labels_to_insert = []
    if DOMA_GROWTH_MULTIPLIER_LABEL not in weekly_labels:
        labels_to_insert.append(DOMA_GROWTH_MULTIPLIER_LABEL)
    if DOMA_REFI_PROFIT_LABEL not in weekly_labels:
        labels_to_insert.append(DOMA_REFI_PROFIT_LABEL)
    if not labels_to_insert:
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label="Contribution Profit - Model",
        labels=labels_to_insert,
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label="Contribution Profit - Model",
        labels=labels_to_insert,
    )


def main() -> None:
    client = SheetsClient()
    write_transitions_assumptions(client)
    rename_title_attach_label(client)
    ensure_doma_rows(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
