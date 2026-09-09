#!/usr/bin/env python3
"""Insert senior/mezzanine warehouse financing rows and seed 10-Q actuals."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from setup_financials_definitions import ensure_definitions_sheet, build_rows  # noqa: E402
from update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from models.OPEN.financials_definitions import FINANCIALS_DEFINITIONS_SHEET  # noqa: E402
from sheets.labels import (  # noqa: E402
    QUARTERLY,
    WEEKLY,
    insert_rows_before_label,
    label_rows,
    sheet_id,
    write_quarterly_by_label,
)
from models.OPEN.warehouse_financing import (  # noqa: E402
    ADJ_EBITDA_LABEL,
    MEZZ_DEBT_BY_QUARTER,
    MEZZ_DEBT_LABEL,
    MEZZ_INTEREST_RATE_LABEL,
    MEZZ_SHARE_LABEL,
    SENIOR_DEBT_BY_QUARTER,
    SENIOR_DEBT_LABEL,
    SENIOR_INTEREST_RATE_LABEL,
    WAREHOUSE_FINANCING_LABELS,
    WAREHOUSE_INTEREST_MODEL_LABEL,
)

# B=1, DY=128 (0-based); exclusive end is 129.
_FORMAT_START_COL = 1
_FORMAT_END_COL = 129

PERCENT_LABELS = (
    SENIOR_INTEREST_RATE_LABEL,
    MEZZ_INTEREST_RATE_LABEL,
    MEZZ_SHARE_LABEL,
)
DOLLAR_LABELS = (
    SENIOR_DEBT_LABEL,
    MEZZ_DEBT_LABEL,
    WAREHOUSE_INTEREST_MODEL_LABEL,
    "Senior Warehouse Debt - Model",
    "Mezzanine Warehouse Debt - Model",
)


def ensure_warehouse_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY, max_row=120)
    if SENIOR_INTEREST_RATE_LABEL in weekly_labels:
        print("Warehouse financing rows already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=ADJ_EBITDA_LABEL,
        labels=list(WAREHOUSE_FINANCING_LABELS),
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=ADJ_EBITDA_LABEL,
        labels=list(WAREHOUSE_FINANCING_LABELS),
    )


def write_quarterly_debt_actuals(client: SheetsClient) -> None:
    for col, value in SENIOR_DEBT_BY_QUARTER.items():
        write_quarterly_by_label(client, col, {SENIOR_DEBT_LABEL: value})
        print(f"{QUARTERLY} {col} {SENIOR_DEBT_LABEL} = {value:,}")
    for col, value in MEZZ_DEBT_BY_QUARTER.items():
        write_quarterly_by_label(client, col, {MEZZ_DEBT_LABEL: value})
        print(f"{QUARTERLY} {col} {MEZZ_DEBT_LABEL} = {value:,}")


def _number_format_requests(
    sid: int,
    labels: dict[str, int],
    row_labels: tuple[str, ...] | list[str],
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
        requests = _number_format_requests(sid, labels, PERCENT_LABELS, "0.00%")
        requests += _number_format_requests(sid, labels, DOLLAR_LABELS, "$#,##0")
        client.spreadsheet.batch_update({"requests": requests})
        print(f"{tab}: applied % / $ formats on warehouse rows")


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
    client = SheetsClient(ticker="OPEN")
    ensure_warehouse_rows(client)
    write_quarterly_debt_actuals(client)
    restore_model_formulas(client)
    update_weekly_formulas(client)
    apply_number_formats(client)
    refresh_definitions(client)
    print("Done.")


if __name__ == "__main__":
    main()
