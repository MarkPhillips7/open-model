#!/usr/bin/env python3
"""Build the EOSE COGS tab and wire cost-out levers onto Quarterly Financials.

Idempotent: inserts any missing Quarterly Financials rows from layout.ROWS,
rewrites COGS, restores Model formulas, refreshes Welcome / Definitions,
and fills Adjusted gross profit actuals.

    python models/EOSE/scripts/setup_cogs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(PACK / "scripts"))

from models.EOSE.cogs import (  # noqa: E402
    COGS_SHEET,
    DEFAULT_HAIRCUT_PCT,
    write_cogs_sheet,
)
from models.EOSE.financials_definitions import FIELD_NOTES  # noqa: E402
from models.EOSE.layout import (  # noqa: E402
    CASH_OPEX_RUNRATE_LABEL,
    HAIRCUT_LABEL,
    NONCASH_COGS_LABEL,
    QUARTERLY,
    ROWS,
    TERMINAL_UNIT_COGS_LABEL,
)
from models.EOSE.quarterly_model_formulas import COLUMN_C_DEFAULTS  # noqa: E402
from restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from setup_eose_workbook import write_definitions, write_welcome  # noqa: E402
from load_quarterly_actuals import build_updates  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.labels import (  # noqa: E402
    insert_rows_after_label,
    insert_rows_before_label,
    label_rows,
    sheet_id,
)

HAIRCUT_NOTE = (
    "Haircut on the Q2 2026 Slide 11 cost-out (73 pts of adj. GM over 12 months). "
    f"Default {DEFAULT_HAIRCUT_PCT:.0f}% because Eos has repeatedly missed cost-out "
    "timelines. 100% = take the CFO plan at face value. Waterfall is on the COGS tab."
)


def _desired_labels() -> list[tuple[str, str]]:
    return [(label, units) for label, units in ROWS if label]


def ensure_quarterly_rows(client: SheetsClient) -> dict[str, int]:
    """Insert any layout.ROWS labels that are missing, grouped by insert point."""
    import time

    labels = label_rows(client, QUARTERLY, max_row=160)
    desired = _desired_labels()
    groups: list[tuple[str, list[str]]] = []
    pending: list[str] = []
    for lab, _units in desired:
        if lab in labels:
            if pending:
                groups.append((lab, pending))
                pending = []
            continue
        pending.append(lab)
    if pending:
        last_on_sheet = None
        for prev, _ in reversed(desired):
            if prev in labels:
                last_on_sheet = prev
                break
        if last_on_sheet is None:
            raise KeyError("Cannot place remaining labels: no existing Quarterly Financials labels")
        insert_rows_after_label(
            client, tab=QUARTERLY, after_label=last_on_sheet, labels=pending
        )
        print(f"Inserted after {last_on_sheet!r}: {pending}")
        time.sleep(2)

    for before, labs in groups:
        insert_rows_before_label(
            client, tab=QUARTERLY, before_label=before, labels=labs
        )
        print(f"Inserted before {before!r}: {labs}")
        time.sleep(2)

    time.sleep(1)
    return label_rows(client, QUARTERLY, max_row=160)


NEW_SCALAR_LABELS = frozenset(
    {
        HAIRCUT_LABEL,
        TERMINAL_UNIT_COGS_LABEL,
        CASH_OPEX_RUNRATE_LABEL,
        NONCASH_COGS_LABEL,
    }
)


def write_units_and_defaults(client: SheetsClient, labels: dict[str, int]) -> None:
    ws = client.worksheet(QUARTERLY)
    unit_updates = [
        {"range": f"B{labels[lab]}", "values": [[units]]}
        for lab, units in _desired_labels()
    ]
    ws.batch_update(unit_updates, value_input_option="RAW")

    # New scalars always seeded (blank insert, or format inherited from the row above).
    value_updates = [
        {"range": f"C{labels[lab]}", "values": [[COLUMN_C_DEFAULTS[lab]]]}
        for lab in NEW_SCALAR_LABELS
    ]
    if value_updates:
        ws.batch_update(value_updates, value_input_option="USER_ENTERED")
        print(f"Seeded {len(value_updates)} column-C defaults: {sorted(NEW_SCALAR_LABELS)}")


def highlight_haircut(client: SheetsClient, labels: dict[str, int]) -> None:
    sid = sheet_id(client, QUARTERLY)
    yellow = {"red": 1, "green": 0.95, "blue": 0.8}
    requests = []
    for lab in (
        HAIRCUT_LABEL,
        TERMINAL_UNIT_COGS_LABEL,
        CASH_OPEX_RUNRATE_LABEL,
        NONCASH_COGS_LABEL,
    ):
        row = labels[lab]
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": yellow}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )
    client.spreadsheet.batch_update({"requests": requests})
    ws = client.worksheet(QUARTERLY)
    ws.update_note(f"C{labels[HAIRCUT_LABEL]}", HAIRCUT_NOTE)


def expand_quarterly_grid(client: SheetsClient, n_rows: int) -> None:
    sid = sheet_id(client, QUARTERLY)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sid,
                            "gridProperties": {
                                "rowCount": max(140, n_rows + 10),
                                "columnCount": 28,
                            },
                        },
                        "fields": "gridProperties.rowCount,gridProperties.columnCount",
                    }
                }
            ]
        }
    )


def load_new_actuals(client: SheetsClient, labels: dict[str, int]) -> None:
    updates = build_updates(labels)
    client.worksheet(QUARTERLY).batch_update(updates, value_input_option="RAW")
    print(f"Wrote {len(updates)} actual cells (including adj. gross profit)")


def main() -> None:
    client = SheetsClient(ticker="EOSE")
    expand_quarterly_grid(client, len(ROWS))
    labels = ensure_quarterly_rows(client)
    write_units_and_defaults(client, labels)
    highlight_haircut(client, labels)
    write_cogs_sheet(client, labels)
    restore_model_formulas(client, ticker="EOSE")
    write_definitions(client, [lab for lab, _ in ROWS])
    write_welcome(client)
    load_new_actuals(client, label_rows(client, QUARTERLY, max_row=160))
    missing = [lab for lab, _ in _desired_labels() if lab not in FIELD_NOTES]
    if missing:
        print(f"Warning: definitions still missing {missing}")
    print("Done.")
    print(f"{COGS_SHEET} engine rows: Unit COGS / Adj GM feed Quarterly Financials.")
    print(f"Haircut default {DEFAULT_HAIRCUT_PCT:.0f}% on {QUARTERLY} C{labels[HAIRCUT_LABEL]}.")


if __name__ == "__main__":
    main()
