#!/usr/bin/env python3
"""Insert Cash Now More Later mix rows and Transitions capital-intensity levers."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from setup_financials_definitions import build_rows, ensure_definitions_sheet  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from models.OPEN.cnml import (  # noqa: E402
    CNML_CASH_VS_1P_ROW,
    CNML_MIX_TERMINAL_ROW,
    CNML_PERCENT_LABEL,
    CNML_PURCHASES_MODEL_LABEL,
    CNML_ROW_LABELS,
    INSERT_BEFORE_LABEL,
    TRANSITIONS,
    TRANSITIONS_CNML_ROWS,
    cnml_percent_formula,
)
from models.OPEN.financials_definitions import FINANCIALS_DEFINITIONS_SHEET  # noqa: E402
from models.OPEN.weekly_model_formulas import column_relative_formula  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.labels import (  # noqa: E402
    QUARTERLY,
    WEEKLY,
    insert_rows_before_label,
    label_rows,
    sheet_id,
)

_FORMAT_START_COL = 1
_FORMAT_END_COL = 129

CNML_PERCENT_NOTE = (
    "Share of acquisition contracts / purchases that are Cash Now, More Later (2P), "
    "formerly Cash Plus. Opendoor still buys, holds, and resells the home — this is "
    "capital-light iBuying, not a marketplace (3P). Accountable contract counts already "
    "include CNML. Disclosed waypoints: 0% ~Q1 2025; 19% last week of Q3 2025; 35% last "
    "week of Q4 2025; >1/3 of contracts in Q1 2026. Q2 2026 mix not disclosed. Default "
    "path holds ~40% from Sep 2026 (Kaz 10 Sep 2026: “More Cash Now More Later”) then "
    "smoothsteps to Transitions B36 terminal (default 50% by end-2027). Not a company "
    "target — overwrite any week to restress. Does not divert units off inventory; "
    "feeds warehouse capital intensity via Transitions B35."
)

CNML_PURCHASES_NOTE = (
    "Informational: Homes Purchased - Model × Cash Now More Later %. Still inventory "
    "adds — do not subtract from Homes in Inventory. Diagnostic only."
)

TRANSITIONS_NOTES: dict[str, str] = {
    f"B{CNML_CASH_VS_1P_ROW}": (
        "CNML cash paid at close as a fraction of a 1P (core cash offer) purchase. "
        "Default 80% — not company-disclosed. Help-doc example is ~$270k upfront vs a "
        "$350k resale. Blended intensity = (1 − CNML%) × 1 + CNML% × this. Rising mix "
        "grows warehouse debt slower than home count. Overwrite to stress capital-light "
        "scaling."
    ),
    f"B{CNML_MIX_TERMINAL_ROW}": (
        "Terminal Cash Now More Later mix after DATE(2027,12,25). Default 50%. Not "
        "company-disclosed; Kaz is still on step 2 (1P+2P) and will not move to 3P "
        "(true off-balance-sheet marketplace) until 2P is working. Weekly Cash Now "
        "More Later % smoothsteps from 40% (Sep 2026) to this value."
    ),
}


def write_transitions_cnml(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    start_row = CNML_CASH_VS_1P_ROW
    values = [[label, value] for label, value in TRANSITIONS_CNML_ROWS]
    end_row = start_row + len(values) - 1
    ws.update(values, range_name=f"A{start_row}:B{end_row}", value_input_option="RAW")
    print(f"{TRANSITIONS}: wrote CNML levers A{start_row}:B{end_row}")


def format_transitions_cnml(client: SheetsClient) -> None:
    sid = sheet_id(client, TRANSITIONS)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": CNML_CASH_VS_1P_ROW - 1,
                            "endRowIndex": CNML_MIX_TERMINAL_ROW,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {
                                    "type": "PERCENT",
                                    "pattern": "0%",
                                }
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat",
                    }
                }
            ]
        }
    )
    ws = client.worksheet(TRANSITIONS)
    for cell, note in TRANSITIONS_NOTES.items():
        ws.update_note(cell, note)
    print(f"{TRANSITIONS}: formatted B{CNML_CASH_VS_1P_ROW}:B{CNML_MIX_TERMINAL_ROW} as % and wrote notes")


def ensure_cnml_rows(client: SheetsClient) -> None:
    for tab in (WEEKLY, QUARTERLY):
        labels = label_rows(client, tab, max_row=150)
        missing = [lbl for lbl in CNML_ROW_LABELS if lbl not in labels]
        if not missing:
            print(f"{tab}: CNML rows already present")
            continue
        insert_rows_before_label(
            client,
            tab=tab,
            before_label=INSERT_BEFORE_LABEL,
            labels=missing,
        )


def apply_number_formats(client: SheetsClient) -> None:
    formats = (
        (CNML_PERCENT_LABEL, "0.0%"),
        (CNML_PURCHASES_MODEL_LABEL, "#,##0.0"),
    )
    for tab in (WEEKLY, QUARTERLY):
        sid = sheet_id(client, tab)
        labels = label_rows(client, tab, max_row=150)
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
        print(f"{tab}: applied % / homes formats on CNML rows")


def write_weekly_notes(client: SheetsClient) -> None:
    labels = label_rows(client, WEEKLY, max_row=150)
    ws = client.worksheet(WEEKLY)
    ws.update_note(f"B{labels[CNML_PERCENT_LABEL]}", CNML_PERCENT_NOTE)
    ws.update_note(f"B{labels[CNML_PURCHASES_MODEL_LABEL]}", CNML_PURCHASES_NOTE)
    print(f"{WEEKLY}: wrote CNML cell notes")


def write_quarterly_cnml_formulas(client: SheetsClient) -> None:
    """Quarterly is not restored by weekly restore; mirror mix + diagnostic formulas."""
    ws = client.worksheet(QUARTERLY)
    labels = label_rows(client, QUARTERLY, max_row=150)
    data = ws.get("A1:Z1", value_render_option="FORMULA")
    n_cols = max(1, len(data[0]) - 1) if data and data[0] else 1
    mix_row = labels[CNML_PERCENT_LABEL]
    purch_row = labels[CNML_PURCHASES_MODEL_LABEL]
    mix_cells = [cnml_percent_formula(col_letter(i + 2)) for i in range(n_cols)]
    purch_cells = [
        column_relative_formula(
            CNML_PURCHASES_MODEL_LABEL,
            col_letter(i + 2),
            label_to_row=labels,
        )
        for i in range(n_cols)
    ]
    end_col = col_letter(n_cols + 1)
    ws.update([mix_cells], range_name=f"B{mix_row}:{end_col}{mix_row}", value_input_option="USER_ENTERED")
    ws.update(
        [purch_cells],
        range_name=f"B{purch_row}:{end_col}{purch_row}",
        value_input_option="USER_ENTERED",
    )
    print(f"{QUARTERLY}: wrote CNML formulas B:{end_col} on mix and purchases")


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
    write_transitions_cnml(client)
    format_transitions_cnml(client)
    ensure_cnml_rows(client)
    restore_model_formulas(client)
    write_quarterly_cnml_formulas(client)
    apply_number_formats(client)
    write_weekly_notes(client)
    refresh_definitions(client)
    print("Done.")


if __name__ == "__main__":
    main()
