#!/usr/bin/env python3
"""Build the CSIQ workbook from the repo.

Refuses to run without --force-rebuild. Does not create or edit charts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.price_history import (  # noqa: E402
    PRICE_HISTORY_SHEET,
    price_history_spill_formula,
)
from sheets.registry import price_symbol_for  # noqa: E402

from models.CSIQ import actuals as ACT  # noqa: E402
from models.CSIQ import financials_definitions as DEF  # noqa: E402
from models.CSIQ import layout as L  # noqa: E402
from models.CSIQ import levers as LV  # noqa: E402
from models.CSIQ import pillars as PIL  # noqa: E402
from models.CSIQ import quarterly_model_formulas as QMF  # noqa: E402
from models.CSIQ import reference as REF  # noqa: E402
from models.CSIQ import shares_events as SH  # noqa: E402
from models.CSIQ import valuation as VAL  # noqa: E402
from models.CSIQ import welcome as WEL  # noqa: E402

TICKER = "CSIQ"

TAB_ORDER: tuple[str, ...] = (
    WEL.WELCOME_SHEET,
    LV.LEVERS_SHEET,
    L.QUARTERLY,
    DEF.DEFINITIONS_SHEET,
    PIL.PILLARS_SHEET,
    VAL.VALUATION_SHEET,
    SH.SHARES_SHEET,
    PRICE_HISTORY_SHEET,
    REF.REFERENCE_SHEET,
)

BOLD = {"textFormat": {"bold": True}}
HEADER_FMT = {
    "backgroundColor": {"red": 0.20, "green": 0.25, "blue": 0.32},
    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
}
SECTION_FMT = {
    "backgroundColor": {"red": 0.87, "green": 0.90, "blue": 0.94},
    "textFormat": {"bold": True},
}
YELLOW_FMT = {"backgroundColor": L.YELLOW}
WRAP = {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}


def _sheet_ids(client: SheetsClient) -> dict[str, int]:
    meta = client.spreadsheet.fetch_sheet_metadata()
    return {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}


def _col_width_requests(sheet_id: int, widths: dict[int, int]) -> list[dict]:
    return [
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": idx,
                    "endIndex": idx + 1,
                },
                "properties": {"pixelSize": px},
                "fields": "pixelSize",
            }
        }
        for idx, px in widths.items()
    ]


def _repeat(sheet_id: int, a1_rows: tuple[int, int], a1_cols: tuple[int, int], cell: dict, fields: str) -> dict:
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": a1_rows[0],
                "endRowIndex": a1_rows[1],
                "startColumnIndex": a1_cols[0],
                "endColumnIndex": a1_cols[1],
            },
            "cell": {"userEnteredFormat": cell},
            "fields": fields,
        }
    }


def ensure_tabs(client: SheetsClient) -> dict[str, int]:
    existing = client.list_worksheets()
    requests: list[dict] = []
    sizes = {
        L.QUARTERLY: (len(L.ROWS) + 4, 2 + L.N_QUARTERS + 2),
        LV.LEVERS_SHEET: (len(LV.grid()) + 4, 8),
        DEF.DEFINITIONS_SHEET: (len(L.ROWS) + len(DEF.INTRO) + 12, 3),
        PIL.PILLARS_SHEET: (len(PIL.ROWS) + 6, 4),
        VAL.VALUATION_SHEET: (len(VAL.grid()) + 6, 4),
        SH.SHARES_SHEET: (len(SH.EVENTS) + 8, 4),
        WEL.WELCOME_SHEET: (len(WEL.TAB_DESCRIPTIONS) + 24, 3),
        REF.REFERENCE_SHEET: (len(REF.ROWS) + 8, 4),
        PRICE_HISTORY_SHEET: (2000, 8),
    }
    for index, title in enumerate(TAB_ORDER):
        if title in existing:
            continue
        rows, cols = sizes[title]
        requests.append(
            {
                "addSheet": {
                    "properties": {
                        "title": title,
                        "index": index,
                        "gridProperties": {"rowCount": rows, "columnCount": cols},
                    }
                }
            }
        )
    if requests:
        client.spreadsheet.batch_update({"requests": requests})
        print(f"Added tabs: {[r['addSheet']['properties']['title'] for r in requests]}")

    ids = _sheet_ids(client)
    order = [
        {
            "updateSheetProperties": {
                "properties": {"sheetId": ids[title], "index": index},
                "fields": "index",
            }
        }
        for index, title in enumerate(TAB_ORDER)
        if title in ids
    ]
    if order:
        client.spreadsheet.batch_update({"requests": order})

    leftovers = [t for t in client.list_worksheets() if t not in TAB_ORDER]
    if leftovers:
        ids = _sheet_ids(client)
        client.spreadsheet.batch_update(
            {"requests": [{"deleteSheet": {"sheetId": ids[t]}} for t in leftovers]}
        )
        print(f"Removed stray tabs: {leftovers}")
    return _sheet_ids(client)


def write_quarterly(client: SheetsClient, sheet_id: int) -> None:
    ws = client.worksheet(L.QUARTERLY)
    n = L.N_QUARTERS
    end_col = col_letter(L.FIRST_VALUE_COL_INDEX + n - 1)
    ws.update(
        [[label, units] for label, units in L.ROWS],
        range_name=f"A1:B{len(L.ROWS)}",
        value_input_option="RAW",
    )
    rows = L.label_row_numbers()
    keys = L.quarter_keys()
    batch: list[dict] = []

    def put(label: str, values: list) -> None:
        batch.append(
            {
                "range": f"{L.FIRST_VALUE_COL}{rows[label]}:{end_col}{rows[label]}",
                "values": [values],
            }
        )

    put(L.YEAR, [y for y, _q in L.quarters()])
    put(L.QUARTER, [q for _y, q in L.quarters()])
    put(L.QUARTER_ENDING, L.quarter_end_dates())
    for label, path in L.EDITABLE_PATHS.items():
        put(label, list(path))
    for label, series in ACT.quarterly_actuals().items():
        put(label, [series.get(k, "") for k in keys])
    ws.batch_update(batch, value_input_option="USER_ENTERED")

    formula_batch = []
    for label in QMF.MODEL_FORMULA_LABELS:
        cells = QMF.row_cells_for_label(label, n, label_to_row=rows)
        if cells is None:
            continue
        formula_batch.append(
            {
                "range": f"{L.FIRST_VALUE_COL}{rows[label]}:{end_col}{rows[label]}",
                "values": [cells],
            }
        )
    ws.batch_update(formula_batch, value_input_option="USER_ENTERED")
    print(f"{L.QUARTERLY}: wrote {len(L.ROWS)} rows × {n} quarters")
    _format_quarterly(client, sheet_id)


def _format_quarterly(client: SheetsClient, sheet_id: int) -> None:
    rows = L.label_row_numbers()
    n = L.N_QUARTERS
    last_col = L.FIRST_VALUE_COL_INDEX + n
    requests: list[dict] = _col_width_requests(sheet_id, L.QUARTERLY_COL_WIDTHS_PX)
    requests.append(
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 3, "frozenColumnCount": 2},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        }
    )
    requests.append(_repeat(sheet_id, (0, 1), (0, last_col), HEADER_FMT, "userEnteredFormat"))
    for label in L.SECTION_LABELS:
        r = rows[label] - 1
        requests.append(_repeat(sheet_id, (r, r + 1), (0, last_col), SECTION_FMT, "userEnteredFormat"))
    for label in L.EDITABLE_PATH_LABELS:
        r = rows[label] - 1
        requests.append(
            _repeat(
                sheet_id,
                (r, r + 1),
                (L.FIRST_VALUE_COL_INDEX - 1, last_col),
                YELLOW_FMT,
                "userEnteredFormat.backgroundColor",
            )
        )
    for label, _units in L.ROWS:
        if not label or label in L.SECTION_LABELS:
            continue
        if label.endswith(" - Model") or label.endswith(" - Plan"):
            continue
        r = rows[label] - 1
        requests.append(_repeat(sheet_id, (r, r + 1), (0, 1), BOLD, "userEnteredFormat.textFormat.bold"))
    for label, fmt in L.NUMBER_FORMAT_BY_LABEL.items():
        r = rows[label] - 1
        requests.append(
            _repeat(
                sheet_id,
                (r, r + 1),
                (L.FIRST_VALUE_COL_INDEX - 1, last_col),
                {"numberFormat": {"type": "NUMBER", "pattern": fmt}},
                "userEnteredFormat.numberFormat",
            )
        )
    for label in (L.QUARTER_ENDING, L.AS_OF_DATE):
        r = rows[label] - 1
        requests.append(
            _repeat(
                sheet_id,
                (r, r + 1),
                (L.FIRST_VALUE_COL_INDEX - 1, last_col),
                {"numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}},
                "userEnteredFormat.numberFormat",
            )
        )
    client.spreadsheet.batch_update({"requests": requests})


def write_levers(client: SheetsClient, sheet_id: int) -> None:
    ws = client.worksheet(LV.LEVERS_SHEET)
    grid = LV.grid()
    ws.update(grid, range_name=f"A1:G{len(grid)}", value_input_option="USER_ENTERED")
    requests: list[dict] = _col_width_requests(sheet_id, LV.COL_WIDTHS_PX)
    requests.append(
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        }
    )
    requests.append(_repeat(sheet_id, (0, 1), (0, 7), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 7), WRAP, "userEnteredFormat"))
    for r in LV.section_rows():
        requests.append(_repeat(sheet_id, (r - 1, r), (0, 7), SECTION_FMT, "userEnteredFormat"))
    for r in LV.value_rows():
        requests.append(
            _repeat(
                sheet_id,
                (r - 1, r),
                (2, 3),
                {**YELLOW_FMT, "textFormat": {"bold": True}},
                "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold",
            )
        )
    rows = LV.lever_rows()
    for item in LV.LEVERS:
        if not isinstance(item, LV.Lever) or not item.number_format:
            continue
        r = rows[item.label] - 1
        kind = "DATE" if item.number_format.startswith("yyyy") else "NUMBER"
        requests.append(
            _repeat(
                sheet_id,
                (r, r + 1),
                (2, 6),
                {"numberFormat": {"type": kind, "pattern": item.number_format}},
                "userEnteredFormat.numberFormat",
            )
        )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{LV.LEVERS_SHEET}: wrote {len(grid)} rows")


def write_definitions(client: SheetsClient, sheet_id: int) -> None:
    grid: list[list[str]] = [list(DEF.HEADER)]
    for heading, text in DEF.INTRO:
        grid.append([heading, text])
    grid.append(["", ""])
    section_rows: list[int] = []
    for label, _units in L.ROWS:
        if not label:
            grid.append(["", ""])
            continue
        if label in L.SECTION_LABELS:
            section_rows.append(len(grid) + 1)
            grid.append([label, DEF.SECTION_NOTES.get(label, "")])
            continue
        grid.append([label, DEF.DEFINITIONS[label]])
    ws = client.worksheet(DEF.DEFINITIONS_SHEET)
    ws.update(grid, range_name=f"A1:B{len(grid)}", value_input_option="RAW")
    requests: list[dict] = _col_width_requests(sheet_id, DEF.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 2), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 2), WRAP, "userEnteredFormat"))
    for r in section_rows:
        requests.append(_repeat(sheet_id, (r - 1, r), (0, 2), SECTION_FMT, "userEnteredFormat"))
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{DEF.DEFINITIONS_SHEET}: wrote {len(grid)} rows")


def write_pillars(client: SheetsClient, sheet_id: int) -> None:
    grid = PIL.grid()
    ws = client.worksheet(PIL.PILLARS_SHEET)
    ws.update(grid, range_name=f"A1:D{len(grid)}", value_input_option="RAW")
    requests: list[dict] = _col_width_requests(sheet_id, PIL.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 4), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 4), WRAP, "userEnteredFormat"))
    for r in PIL.section_rows():
        requests.append(_repeat(sheet_id, (r - 1, r), (0, 4), SECTION_FMT, "userEnteredFormat"))
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{PIL.PILLARS_SHEET}: wrote {len(grid)} rows")


def write_valuation(client: SheetsClient, sheet_id: int) -> None:
    grid = VAL.grid()
    ws = client.worksheet(VAL.VALUATION_SHEET)
    ws.update(grid, range_name=f"A1:D{len(grid)}", value_input_option="USER_ENTERED")
    ws.update([[VAL.NOTE]], range_name=f"A{len(grid) + 2}", value_input_option="RAW")
    requests: list[dict] = _col_width_requests(sheet_id, VAL.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 4), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid) + 2), (0, 4), WRAP, "userEnteredFormat"))
    requests.append(
        _repeat(
            sheet_id,
            (1, len(grid)),
            (1, 3),
            {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}},
            "userEnteredFormat.numberFormat",
        )
    )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{VAL.VALUATION_SHEET}: wrote {len(grid)} rows")


def write_shares(client: SheetsClient, sheet_id: int) -> None:
    grid = SH.grid()
    ws = client.worksheet(SH.SHARES_SHEET)
    ws.update(grid, range_name=f"A1:D{len(grid)}", value_input_option="RAW")
    requests: list[dict] = _col_width_requests(sheet_id, SH.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 4), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 4), WRAP, "userEnteredFormat"))
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{SH.SHARES_SHEET}: wrote {len(grid)} rows")


def write_reference(client: SheetsClient, sheet_id: int) -> None:
    grid = REF.grid()
    ws = client.worksheet(REF.REFERENCE_SHEET)
    ws.update(grid, range_name=f"A1:C{len(grid)}", value_input_option="RAW")
    ws.update([[REF.NOTE]], range_name=f"A{len(grid) + 2}", value_input_option="RAW")
    requests: list[dict] = _col_width_requests(sheet_id, REF.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 3), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid) + 2), (0, 3), WRAP, "userEnteredFormat"))
    for r in REF.section_rows():
        requests.append(_repeat(sheet_id, (r - 1, r), (0, 3), SECTION_FMT, "userEnteredFormat"))
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{REF.REFERENCE_SHEET}: wrote {len(grid)} rows")


def write_welcome(client: SheetsClient, sheet_id: int) -> None:
    grid: list[list[str]] = [
        [WEL.TITLE, ""],
        ["", ""],
        ["Disclaimer", WEL.DISCLAIMER],
        ["Goal", WEL.GOALS],
        ["Approach", WEL.APPROACH],
        ["Why levers", WEL.WHY_LEVERS],
        ["Calibration", WEL.CALIBRATION],
        ["Manual edits", WEL.MANUAL_EDITS],
        ["Sources", WEL.SOURCES_NOTE],
        ["Feedback", WEL.FEEDBACK + WEL.X_PROFILE_URL],
        ["Repository", WEL.REPO_URL],
        ["Live sheet", WEL.SHEET_URL],
        ["Company IR", WEL.IR_URL],
        ["", ""],
        ["Tab guide", ""],
    ]
    for title, description in WEL.TAB_DESCRIPTIONS:
        grid.append([title, description])
    grid.append(["", ""])
    grid.append(["", WEL.CLOSING])
    ws = client.worksheet(WEL.WELCOME_SHEET)
    ws.update(grid, range_name=f"A1:B{len(grid)}", value_input_option="RAW")
    requests: list[dict] = _col_width_requests(sheet_id, WEL.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 2), WRAP, "userEnteredFormat"))
    requests.append(
        _repeat(
            sheet_id,
            (0, 1),
            (0, 2),
            {"textFormat": {"bold": True, "fontSize": 16}},
            "userEnteredFormat.textFormat",
        )
    )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{WEL.WELCOME_SHEET}: wrote {len(grid)} rows")


def write_price_history(client: SheetsClient, sheet_id: int) -> None:
    symbol = price_symbol_for(TICKER)
    formula = price_history_spill_formula(
        price_symbol=symbol,
        start_expr="DATE(2024,12,1)",
        end_expr="TODAY()",
    )
    ws = client.worksheet(PRICE_HISTORY_SHEET)
    ws.update([[formula]], range_name="A1", value_input_option="USER_ENTERED")
    client.spreadsheet.batch_update(
        {
            "requests": _col_width_requests(
                sheet_id, {0: 160, 1: 120, 2: 120, 3: 120, 4: 120}
            )
        }
    )
    print(f"{PRICE_HISTORY_SHEET}: {symbol} daily spill")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Required. Replaces tab contents from the repo.",
    )
    args = parser.parse_args()
    if not args.force_rebuild:
        print("Refusing to build without --force-rebuild.")
        sys.exit(2)
    client = SheetsClient(ticker=TICKER)
    ids = ensure_tabs(client)
    write_levers(client, ids[LV.LEVERS_SHEET])
    write_quarterly(client, ids[L.QUARTERLY])
    write_definitions(client, ids[DEF.DEFINITIONS_SHEET])
    write_pillars(client, ids[PIL.PILLARS_SHEET])
    write_valuation(client, ids[VAL.VALUATION_SHEET])
    write_shares(client, ids[SH.SHARES_SHEET])
    write_price_history(client, ids[PRICE_HISTORY_SHEET])
    write_reference(client, ids[REF.REFERENCE_SHEET])
    write_welcome(client, ids[WEL.WELCOME_SHEET])
    print("CSIQ workbook built. Charts were not touched.")


if __name__ == "__main__":
    main()
