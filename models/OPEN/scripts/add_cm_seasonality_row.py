#!/usr/bin/env python3
"""Add CM seasonality table and Contribution Margin - Seasonality Adjustments model row."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from models.OPEN.cm_seasonality import (  # noqa: E402
    CM_SEASONALITY_ADJUSTMENTS_LABEL,
    CM_SEASONALITY_ROW_LABEL,
    CM_SEASONALITY_SHEET,
    CM_SEASONALITY_VALUE_RANGE,
    CM_SEASONAL_ADJ_BY_MONTH,
)
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows  # noqa: E402


def ensure_seasonality_table(client: SheetsClient, *, force_refresh: bool = False) -> None:
    ws = client.worksheet(CM_SEASONALITY_SHEET)
    existing = ws.get("A6:M6")
    label = existing[0][0] if existing and existing[0] else ""
    if label == CM_SEASONALITY_ROW_LABEL and not force_refresh:
        print(f"{CM_SEASONALITY_SHEET}: CM seasonality row already present")
        return

    ws.update(
        [[CM_SEASONALITY_ROW_LABEL, *CM_SEASONAL_ADJ_BY_MONTH]],
        range_name="A6:M6",
        value_input_option="RAW",
    )
    ws.update(
        [[
            "Monthly CM seasonal adjustments (absolute %, not quarterly-mean deviation). "
            "Spreadsheet is source of truth — run scripts/pull_cm_stack_from_sheet.py after edits."
        ]],
        range_name="A7",
        value_input_option="RAW",
    )
    print(f"{CM_SEASONALITY_SHEET}: wrote {CM_SEASONALITY_ROW_LABEL} {CM_SEASONALITY_VALUE_RANGE}")


def ensure_seasonality_model_row(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if CM_SEASONALITY_ADJUSTMENTS_LABEL in weekly_labels:
        print(f"{WEEKLY}: {CM_SEASONALITY_ADJUSTMENTS_LABEL!r} already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label="Contribution Margin - Adjustments",
        labels=[CM_SEASONALITY_ADJUSTMENTS_LABEL],
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label="Contribution Margin - Adjustments",
        labels=[CM_SEASONALITY_ADJUSTMENTS_LABEL],
    )


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    ensure_seasonality_table(client)
    ensure_seasonality_model_row(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
