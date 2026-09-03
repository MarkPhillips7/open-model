#!/usr/bin/env python3
"""Insert inventory ceiling / utilization rows (facility vs committed)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from scripts.setup_financials_definitions import ensure_definitions_sheet, build_rows  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.financials_definitions import FINANCIALS_DEFINITIONS_SHEET  # noqa: E402
from sheets.inventory_ceiling import (  # noqa: E402
    CAPACITY_LABELS,
    HOMES_CEILING_LABELS,
    INSERT_BEFORE_LABEL,
    INVENTORY_CEILING_LABELS,
    UTILIZATION_LABEL,
    UTILIZATION_LABELS,
)
from sheets.labels import (  # noqa: E402
    QUARTERLY,
    WEEKLY,
    insert_rows_before_label,
    label_rows,
    sheet_id,
)

_FORMAT_START_COL = 1
_FORMAT_END_COL = 129


def ensure_inventory_ceiling_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY, max_row=120)
    if UTILIZATION_LABEL in weekly_labels:
        print("Inventory ceiling / utilization rows already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=INSERT_BEFORE_LABEL,
        labels=list(INVENTORY_CEILING_LABELS),
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=INSERT_BEFORE_LABEL,
        labels=list(INVENTORY_CEILING_LABELS),
    )


def _number_format_requests(
    sid: int,
    labels: dict[str, int],
    row_labels: tuple[str, ...],
    pattern: str,
) -> list[dict]:
    requests = []
    for label in row_labels:
        row = labels[label]
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": _FORMAT_START_COL,
                        "endColumnIndex": _FORMAT_END_COL,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {"type": "NUMBER", "pattern": pattern}
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )
    return requests


def apply_number_formats(client: SheetsClient) -> None:
    for tab in (WEEKLY, QUARTERLY):
        sid = sheet_id(client, tab)
        labels = label_rows(client, tab, max_row=120)
        requests = _number_format_requests(sid, labels, CAPACITY_LABELS, "$#,##0")
        requests += _number_format_requests(sid, labels, HOMES_CEILING_LABELS, "#,##0")
        requests += _number_format_requests(sid, labels, UTILIZATION_LABELS, "0.0%")
        client.spreadsheet.batch_update({"requests": requests})
        print(f"{tab}: applied $ / homes / % formats on ceiling rows")


def refresh_definitions(client: SheetsClient) -> None:
    ensure_definitions_sheet(client)
    rows, missing = build_rows(client)
    end_row = len(rows)
    client.write_range(FINANCIALS_DEFINITIONS_SHEET, f"A1:B{end_row}", rows)
    print(f"Wrote {end_row} rows to {FINANCIALS_DEFINITIONS_SHEET!r}")
    if missing:
        print(f"Warning: {len(missing)} labels missing definitions:")
        for label in missing:
            print(f"  - {label}")


def main() -> None:
    client = SheetsClient()
    ensure_inventory_ceiling_rows(client)
    restore_model_formulas(client)
    apply_number_formats(client)
    refresh_definitions(client)
    print("Done.")


if __name__ == "__main__":
    main()
