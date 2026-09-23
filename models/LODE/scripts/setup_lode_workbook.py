#!/usr/bin/env python3
"""Build the LODE workbook from the repo: tabs, layout, levers, formulas, formatting.

This is the only script that creates structure. It is destructive by design, so it
refuses to run unless you pass ``--force-rebuild``, and it always checks for manual
spreadsheet edits first (see models/LODE/manual_guard.py).

Normal maintenance does NOT need this script:

    python models/LODE/scripts/load_quarterly_actuals.py      # new quarter reported
    python scripts/restore_weekly_model_formulas.py --ticker LODE   # repair formulas
    python models/LODE/scripts/check_manual_changes.py        # see what moved

Charts are never created or touched here. Add them by hand in the Sheets UI.
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

from models.LODE import actuals as ACT  # noqa: E402
from models.LODE import asset_monetization as AM  # noqa: E402
from models.LODE import financials_definitions as DEF  # noqa: E402
from models.LODE import layout as L  # noqa: E402
from models.LODE import levers as LV  # noqa: E402
from models.LODE import manual_guard as guard  # noqa: E402
from models.LODE import quarterly_model_formulas as QMF  # noqa: E402
from models.LODE import reference as REF  # noqa: E402
from models.LODE import shares_events as SH  # noqa: E402
from models.LODE import valuation as VAL  # noqa: E402
from models.LODE import welcome as WEL  # noqa: E402

TICKER = "LODE"

# Tab order in the workbook. Levers sits second because it is where you start.
# Money Charts is created/edited only in the Sheets UI — listed here so a rebuild
# does not delete it as a stray tab (see .cursor/rules/charts-manual-only.mdc).
MONEY_CHARTS_SHEET = "Money Charts"
TAB_ORDER: tuple[str, ...] = (
    WEL.WELCOME_SHEET,
    LV.LEVERS_SHEET,
    L.QUARTERLY,
    DEF.DEFINITIONS_SHEET,
    MONEY_CHARTS_SHEET,
    AM.ASSET_SHEET,
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


def ensure_tabs(client: SheetsClient) -> dict[str, int]:
    """Create any missing tab, drop the default 'Sheet1', and order them.

    Chart tabs (Money Charts) are never created here — only preserved if already
    present so a rebuild does not wipe the user's charts.
    """
    existing = client.list_worksheets()
    requests: list[dict] = []

    sizes = {
        L.QUARTERLY: (len(L.ROWS) + 4, 2 + L.N_QUARTERS + 2),
        LV.LEVERS_SHEET: (len(LV.grid()) + 4, 8),
        DEF.DEFINITIONS_SHEET: (len(L.ROWS) + len(DEF.INTRO) + 12, 3),
        AM.ASSET_SHEET: (len(AM.ROWS) + 4, 5),
        VAL.VALUATION_SHEET: (len(VAL.ROWS) + 4, 5),
        SH.SHARES_SHEET: (len(SH.EVENTS) + 12, 6),
        WEL.WELCOME_SHEET: (len(WEL.TAB_DESCRIPTIONS) + 24, 3),
        REF.REFERENCE_SHEET: (len(REF.ROWS) + 6, 4),
        PRICE_HISTORY_SHEET: (2000, 8),
    }
    # Never auto-create chart tabs; charts are manual-only in the Sheets UI.
    do_not_create = {MONEY_CHARTS_SHEET}

    for index, title in enumerate(TAB_ORDER):
        if title in existing or title in do_not_create:
            continue
        rows, cols = sizes.get(title, (200, 26))
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

    order_requests = [
        {
            "updateSheetProperties": {
                "properties": {"sheetId": ids[title], "index": index},
                "fields": "index",
            }
        }
        for index, title in enumerate(TAB_ORDER)
        if title in ids
    ]
    if order_requests:
        client.spreadsheet.batch_update({"requests": order_requests})

    # Remove the default empty tab only once real tabs exist, so the file is never
    # left with zero sheets (the API rejects that).
    leftovers = [t for t in client.list_worksheets() if t not in TAB_ORDER]
    if leftovers:
        ids = _sheet_ids(client)
        client.spreadsheet.batch_update(
            {"requests": [{"deleteSheet": {"sheetId": ids[t]}} for t in leftovers]}
        )
        print(f"Removed stray tabs: {leftovers}")

    return _sheet_ids(client)


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


# --- Quarterly Financials --------------------------------------------------


def write_quarterly(client: SheetsClient, sheet_id: int) -> None:
    ws = client.worksheet(L.QUARTERLY)
    n = L.N_QUARTERS
    end_col = col_letter(L.FIRST_VALUE_COL_INDEX + n - 1)

    # Column A labels and column B units.
    ws.update(
        [[label, units] for label, units in L.ROWS],
        range_name=f"A1:B{len(L.ROWS)}",
        value_input_option="RAW",
    )

    rows = L.label_row_numbers()
    keys = L.quarter_keys()
    quarters = L.quarters()

    batch: list[dict] = []

    def put(label: str, values: list, *, formulas: bool = False) -> None:
        batch.append(
            {
                "range": f"{L.FIRST_VALUE_COL}{rows[label]}:{end_col}{rows[label]}",
                "values": [values],
                "_formulas": formulas,
            }
        )

    # Time spine.
    put(L.YEAR, [y for y, _q in quarters])
    put(L.QUARTER, [q for _y, q in quarters])
    put(L.QUARTER_ENDING, L.quarter_end_dates())

    # Editable "- Plan" trajectories.
    for label, path in L.EDITABLE_PATHS.items():
        put(label, list(path))

    # Reported actuals, blank where not reported.
    for label, series in ACT.quarterly_actuals().items():
        put(label, [series.get(k, "") for k in keys])

    raw = [b for b in batch if not b["_formulas"]]
    ws.batch_update(
        [{"range": b["range"], "values": b["values"]} for b in raw],
        value_input_option="USER_ENTERED",
    )

    # Model formulas, straight from the canonical templates.
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


def format_quarterly(client: SheetsClient, sheet_id: int) -> None:
    rows = L.label_row_numbers()
    n = L.N_QUARTERS
    last_col_idx = L.FIRST_VALUE_COL_INDEX + n - 1
    requests: list[dict] = _col_width_requests(sheet_id, L.QUARTERLY_COL_WIDTHS_PX)

    # Freeze Units header + Year + Quarter, and label columns.
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
    requests.append(_repeat(sheet_id, (0, 1), (0, last_col_idx), HEADER_FMT, "userEnteredFormat"))

    # Section heading bands.
    for label in L.SECTION_LABELS:
        r = rows[label] - 1
        requests.append(
            _repeat(sheet_id, (r, r + 1), (0, last_col_idx), SECTION_FMT, "userEnteredFormat")
        )

    # Yellow for the editable "- Plan" trajectories.
    for label in L.EDITABLE_PATH_LABELS:
        r = rows[label] - 1
        requests.append(
            _repeat(
                sheet_id,
                (r, r + 1),
                (L.FIRST_VALUE_COL_INDEX - 1, last_col_idx),
                YELLOW_FMT,
                "userEnteredFormat.backgroundColor",
            )
        )

    # Bold the reported-actual labels so prints stand out from projections.
    for label, _units in L.ROWS:
        if not label or label in L.SECTION_LABELS:
            continue
        if label.endswith(" - Model") or label.endswith(" - Plan"):
            continue
        r = rows[label] - 1
        requests.append(
            _repeat(sheet_id, (r, r + 1), (0, 1), BOLD, "userEnteredFormat.textFormat.bold")
        )

    # Number formats.
    for label, fmt in L.NUMBER_FORMAT_BY_LABEL.items():
        if label not in rows:
            continue
        r = rows[label] - 1
        requests.append(
            _repeat(
                sheet_id,
                (r, r + 1),
                (L.FIRST_VALUE_COL_INDEX - 1, last_col_idx),
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
                (L.FIRST_VALUE_COL_INDEX - 1, last_col_idx),
                {"numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}},
                "userEnteredFormat.numberFormat",
            )
        )

    client.spreadsheet.batch_update({"requests": requests})
    print(f"{L.QUARTERLY}: formatting applied")


# --- Levers ----------------------------------------------------------------


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
    for r in LV.section_rows():
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 7), SECTION_FMT, "userEnteredFormat")
        )
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
    for r in LV.date_rows():
        requests.append(
            _repeat(
                sheet_id,
                (r - 1, r),
                (2, 4),
                {"numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}},
                "userEnteredFormat.numberFormat",
            )
        )
    # Wrap the rationale column; it is long on purpose.
    requests.append(_repeat(sheet_id, (1, len(grid)), (6, 7), WRAP, "userEnteredFormat"))
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{LV.LEVERS_SHEET}: wrote {len(grid)} rows")


# --- Financials Definitions ------------------------------------------------


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
        grid.append([label, DEF.DEFINITIONS.get(label, "")])

    ws = client.worksheet(DEF.DEFINITIONS_SHEET)
    ws.update(grid, range_name=f"A1:B{len(grid)}", value_input_option="RAW")

    requests: list[dict] = _col_width_requests(sheet_id, DEF.COL_WIDTHS_PX)
    requests.append(
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        }
    )
    requests.append(_repeat(sheet_id, (0, 1), (0, 2), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 2), WRAP, "userEnteredFormat"))
    for r in section_rows:
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 2), SECTION_FMT, "userEnteredFormat")
        )
    for r in range(2, 2 + len(DEF.INTRO)):
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 1), BOLD, "userEnteredFormat.textFormat.bold")
        )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{DEF.DEFINITIONS_SHEET}: wrote {len(grid)} rows")


# --- Asset Monetization / Valuation / Shares / Reference / Welcome ---------


def write_asset_monetization(client: SheetsClient, sheet_id: int) -> None:
    grid = AM.grid()
    ws = client.worksheet(AM.ASSET_SHEET)
    ws.update(grid, range_name=f"A1:D{len(grid)}", value_input_option="USER_ENTERED")

    requests: list[dict] = _col_width_requests(sheet_id, AM.COL_WIDTHS_PX)
    requests.append(
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        }
    )
    requests.append(_repeat(sheet_id, (0, 1), (0, 4), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (3, 4), WRAP, "userEnteredFormat"))
    for r in AM.section_rows():
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 4), SECTION_FMT, "userEnteredFormat")
        )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{AM.ASSET_SHEET}: wrote {len(grid)} rows")


def write_valuation(client: SheetsClient, sheet_id: int) -> None:
    qf_rows = L.label_row_numbers()
    formulas = VAL.value_formulas(qf_rows)
    grid: list[list[object]] = [list(VAL.HEADER)]
    for label, units, note in VAL.ROWS:
        if label in VAL.SECTION_LABELS:
            grid.append([label, "", "", ""])
            continue
        grid.append([label, units, formulas.get(label, ""), note])

    ws = client.worksheet(VAL.VALUATION_SHEET)
    ws.update(grid, range_name=f"A1:D{len(grid)}", value_input_option="USER_ENTERED")

    rows = VAL.label_rows()
    requests: list[dict] = _col_width_requests(sheet_id, VAL.COL_WIDTHS_PX)
    requests.append(
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        }
    )
    requests.append(_repeat(sheet_id, (0, 1), (0, 4), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (3, 4), WRAP, "userEnteredFormat"))
    for label in VAL.SECTION_LABELS:
        r = rows[label]
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 4), SECTION_FMT, "userEnteredFormat")
        )
    for label in VAL.INPUT_LABELS:
        r = rows[label]
        requests.append(
            _repeat(
                sheet_id,
                (r - 1, r),
                (2, 3),
                {**YELLOW_FMT, "textFormat": {"bold": True}},
                "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold",
            )
        )
    for label, fmt in VAL.NUMBER_FORMAT_BY_LABEL.items():
        r = rows[label]
        requests.append(
            _repeat(
                sheet_id,
                (r - 1, r),
                (2, 3),
                {"numberFormat": {"type": "NUMBER", "pattern": fmt}},
                "userEnteredFormat.numberFormat",
            )
        )
    r = rows[VAL.AS_OF]
    requests.append(
        _repeat(
            sheet_id,
            (r - 1, r),
            (2, 3),
            {"numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}},
            "userEnteredFormat.numberFormat",
        )
    )
    # Emphasise the two answers people actually read.
    for label in (VAL.PRESENT_VALUE_PER_SHARE, VAL.UPSIDE_TO_PRESENT):
        r = rows[label]
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 3), BOLD, "userEnteredFormat.textFormat.bold")
        )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{VAL.VALUATION_SHEET}: wrote {len(grid)} rows")


def write_shares(client: SheetsClient, sheet_id: int) -> None:
    grid = SH.grid()
    ws = client.worksheet(SH.SHARES_SHEET)
    ws.update(grid, range_name=f"A1:E{len(grid)}", value_input_option="USER_ENTERED")
    ws.update([[SH.NOTE]], range_name=f"A{len(grid) + 2}", value_input_option="RAW")

    requests: list[dict] = _col_width_requests(sheet_id, SH.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 5), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (4, 5), WRAP, "userEnteredFormat"))
    requests.append(
        _repeat(sheet_id, (len(grid) + 1, len(grid) + 2), (0, 5), WRAP, "userEnteredFormat")
    )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{SH.SHARES_SHEET}: wrote {len(grid)} rows")


def write_reference(client: SheetsClient, sheet_id: int) -> None:
    grid = REF.grid()
    ws = client.worksheet(REF.REFERENCE_SHEET)
    ws.update(grid, range_name=f"A1:C{len(grid)}", value_input_option="USER_ENTERED")
    ws.update([[REF.NOTE]], range_name=f"A{len(grid) + 2}", value_input_option="RAW")

    requests: list[dict] = _col_width_requests(sheet_id, REF.COL_WIDTHS_PX)
    requests.append(_repeat(sheet_id, (0, 1), (0, 3), HEADER_FMT, "userEnteredFormat"))
    requests.append(_repeat(sheet_id, (1, len(grid)), (0, 3), WRAP, "userEnteredFormat"))
    for r in REF.section_rows():
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 3), SECTION_FMT, "userEnteredFormat")
        )
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
        ["", ""],
        ["Tab guide", ""],
    ]
    first_tab_row = len(grid) + 1
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
    for r in list(range(3, 12)) + [13] + list(range(first_tab_row, first_tab_row + len(WEL.TAB_DESCRIPTIONS))):
        requests.append(
            _repeat(sheet_id, (r - 1, r), (0, 1), BOLD, "userEnteredFormat.textFormat.bold")
        )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"{WEL.WELCOME_SHEET}: wrote {len(grid)} rows")


def write_price_history(client: SheetsClient, sheet_id: int) -> None:
    symbol = price_symbol_for(TICKER)
    ws = client.worksheet(PRICE_HISTORY_SHEET)
    # No weekly tab in this pack, so drive the window off the quarterly spine.
    start = f"DATE({L.YEARS[0] - 1},12,1)"
    formula = price_history_spill_formula(
        price_symbol=symbol, start_expr=start, end_expr="TODAY()"
    )
    ws.update(
        [[f"Daily {symbol} prices. Quarterly Financials 'Stock price' XLOOKUPs column E."]],
        range_name="H1",
        value_input_option="RAW",
    )
    ws.update([[formula]], range_name="A1", value_input_option="USER_ENTERED")
    print(f"{PRICE_HISTORY_SHEET}: wrote GOOGLEFINANCE spill for {symbol}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Required. Replaces the live workbook structure from git.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip the manual-change check (use only if you know the sheet is disposable).",
    )
    args = parser.parse_args()

    if not args.force_rebuild:
        print(
            "Refusing to run without --force-rebuild.\n"
            "This script replaces the live workbook structure. For routine updates use:\n"
            "  python models/LODE/scripts/load_quarterly_actuals.py\n"
            "  python scripts/restore_weekly_model_formulas.py --ticker LODE"
        )
        sys.exit(2)

    client = SheetsClient(ticker=TICKER)
    guard.require_reconciled(client, action="rebuild the LODE workbook", force=args.force)

    ids = ensure_tabs(client)

    write_welcome(client, ids[WEL.WELCOME_SHEET])
    write_levers(client, ids[LV.LEVERS_SHEET])
    write_quarterly(client, ids[L.QUARTERLY])
    format_quarterly(client, ids[L.QUARTERLY])
    write_definitions(client, ids[DEF.DEFINITIONS_SHEET])
    write_asset_monetization(client, ids[AM.ASSET_SHEET])
    write_valuation(client, ids[VAL.VALUATION_SHEET])
    write_shares(client, ids[SH.SHARES_SHEET])
    write_price_history(client, ids[PRICE_HISTORY_SHEET])
    write_reference(client, ids[REF.REFERENCE_SHEET])

    guard.record(client)
    print(
        f"\nDone. Recorded a manual-change baseline in {guard.FINGERPRINT_PATH.name}.\n"
        "Charts were not touched — add them by hand in the Sheets UI if you want them."
    )


if __name__ == "__main__":
    main()
