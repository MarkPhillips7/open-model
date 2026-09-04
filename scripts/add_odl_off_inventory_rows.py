#!/usr/bin/env python3
"""Insert off-inventory ODL rows and refresh Transitions ancillary levers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from scripts.setup_financials_definitions import build_rows, ensure_definitions_sheet  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.ancillary_products import (  # noqa: E402
    ODL_OFF_INVENTORY_LABELS,
    ODL_OFF_INVENTORY_LOANS_LABEL,
    ODL_OFF_INVENTORY_PROFIT_LABEL,
    TRANSITIONS,
    TRANSITIONS_ANCILLARY_ROWS,
)
from sheets.financials_definitions import FINANCIALS_DEFINITIONS_SHEET  # noqa: E402
from sheets.labels import (  # noqa: E402
    QUARTERLY,
    WEEKLY,
    insert_rows_before_label,
    label_rows,
    sheet_id,
)

_FORMAT_START_COL = 1
_FORMAT_END_COL = 129

INSERT_BEFORE_LABEL = "Contribution Profit - Model"

TRANSITIONS_NOTES: dict[str, str] = {
    "B31": (
        "Net $ per Opendoor Home Loans origination on a home Opendoor does not hold. "
        "Haircut vs B29 ($4,000 on-inventory) because Opendoor-owned homes get best pricing. "
        "Kaz confirmed off-inventory lending Sep 4 2026 (product out of beta)."
    ),
    "B32": (
        "Terminal ratio of off-inventory ODL loans to on-inventory ODL loans. "
        "Weekly formula smoothsteps 0% at Sep 6 2026 (GA) to this value by Jan 2 2028. "
        "Conservative vs national purchase-mortgage TAM until originations are disclosed."
    ),
}


def write_transitions_assumptions(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    start_row = 29
    values = [[label, value] for label, value in TRANSITIONS_ANCILLARY_ROWS]
    end_row = start_row + len(values) - 1
    ws.update(values, range_name=f"A{start_row}:B{end_row}", value_input_option="RAW")
    ws.batch_clear([f"A{end_row + 1}:B35"])
    print(f"{TRANSITIONS}: wrote ancillary assumptions A{start_row}:B{end_row}")


def ensure_odl_off_inventory_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY, max_row=120)
    if all(lbl in weekly_labels for lbl in ODL_OFF_INVENTORY_LABELS):
        print("Off-inventory ODL rows already present")
        return

    missing = [lbl for lbl in ODL_OFF_INVENTORY_LABELS if lbl not in weekly_labels]
    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=INSERT_BEFORE_LABEL,
        labels=missing,
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=INSERT_BEFORE_LABEL,
        labels=missing,
    )


def apply_number_formats(client: SheetsClient) -> None:
    formats = (
        (ODL_OFF_INVENTORY_LOANS_LABEL, "#,##0.0"),
        (ODL_OFF_INVENTORY_PROFIT_LABEL, "$#,##0"),
    )
    for tab in (WEEKLY, QUARTERLY):
        sid = sheet_id(client, tab)
        labels = label_rows(client, tab, max_row=120)
        requests = []
        for label, pattern in formats:
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
        client.spreadsheet.batch_update({"requests": requests})
        print(f"{tab}: applied loan / $ formats on off-inventory ODL rows")


def format_transitions_levers(client: SheetsClient) -> None:
    sid = sheet_id(client, TRANSITIONS)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 30,
                            "endRowIndex": 31,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {"type": "NUMBER", "pattern": "$#,##0"}
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 31,
                            "endRowIndex": 32,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {"type": "PERCENT", "pattern": "0%"}
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
            ]
        }
    )
    ws = client.worksheet(TRANSITIONS)
    for cell, note in TRANSITIONS_NOTES.items():
        ws.update_note(cell, note)
    print(f"{TRANSITIONS}: formatted B31 ($) / B32 (%) and wrote cell notes")


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
    write_transitions_assumptions(client)
    format_transitions_levers(client)
    ensure_odl_off_inventory_rows(client)
    restore_model_formulas(client)
    apply_number_formats(client)
    refresh_definitions(client)
    print("Done.")


if __name__ == "__main__":
    main()
