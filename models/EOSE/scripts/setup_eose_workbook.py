#!/usr/bin/env python3
"""Rebuild the EOSE workbook: Quarterly Financials + Welcome, Definitions, Shares, Price History.

Keeps Feltonomics, COGS, and Reference. Does not create or edit charts.
"""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from models.EOSE.actuals import ACTUALS, SCALARS  # noqa: E402
from models.EOSE.financials_definitions import (  # noqa: E402
    FIELD_NOTES,
    FINANCIALS_DEFINITIONS_SHEET,
)
from models.EOSE.layout import (  # noqa: E402
    AS_OF_LABEL,
    FIRST_VALUE_COL_INDEX,
    LINE_RAMP,
    N_QUARTERS,
    OLD_QUARTERLY,
    QUARTERLY,
    ROWS,
    asp_model_values,
    quarters,
)
from models.EOSE.quarterly_model_formulas import (  # noqa: E402
    COLUMN_C_DEFAULTS,
    MODEL_FORMULA_LABELS,
    row_cells_for_label,
)
from models.EOSE.shares_events import SHARES_SHEET, SHARES_SHEET_GRID  # noqa: E402
from models.EOSE.welcome import (  # noqa: E402
    CLOSING,
    DISCLAIMER,
    FEEDBACK_X,
    GOALS,
    IR_URL,
    REPO_URL,
    RESOURCES,
    TAB_DESCRIPTIONS,
    TAB_GUIDE_INTRO,
    THANKS,
    TITLE,
    WELCOME_SHEET,
    X_PROFILE_URL,
)
from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.labels import sheet_id  # noqa: E402
from sheets.price_history import (  # noqa: E402
    PRICE_HISTORY_SHEET,
    price_history_spill_formula,
)
from sheets.registry import price_symbol_for  # noqa: E402

END_COL = col_letter(FIRST_VALUE_COL_INDEX + N_QUARTERS - 1)
MISSING_NOTE = "(Definition not yet written — add to models/EOSE/financials_definitions.py)"


def _hyperlink(url: str, label: str, *, standalone: bool = True) -> str:
    expr = f'HYPERLINK("{url}", "{label}")'
    return f"={expr}" if standalone else expr


def _tab_link(gid: int, title: str) -> str:
    return f'=HYPERLINK("#gid={gid}", "{title}")'


def _ensure_sheet(
    client: SheetsClient,
    title: str,
    *,
    index: int,
    rows: int,
    cols: int,
) -> None:
    existing = client.list_worksheets()
    if title in existing:
        sid = sheet_id(client, title)
        client.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": sid,
                                "index": index,
                                "gridProperties": {"rowCount": rows, "columnCount": cols},
                            },
                            "fields": "index,gridProperties.rowCount,gridProperties.columnCount",
                        }
                    }
                ]
            }
        )
        return
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                            "index": index,
                            "gridProperties": {"rowCount": rows, "columnCount": cols},
                        }
                    }
                }
            ]
        }
    )
    print(f"Added sheet {title!r}")


def rename_quarterly_tab(client: SheetsClient) -> None:
    titles = client.list_worksheets()
    if QUARTERLY in titles:
        print(f"{QUARTERLY!r} already exists")
        return
    if OLD_QUARTERLY not in titles:
        raise KeyError(f"Neither {QUARTERLY!r} nor {OLD_QUARTERLY!r} found")
    sid = sheet_id(client, OLD_QUARTERLY)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": sid, "title": QUARTERLY},
                        "fields": "title",
                    }
                }
            ]
        }
    )
    print(f"Renamed {OLD_QUARTERLY!r} → {QUARTERLY!r}")


def _empty_row() -> list:
    return [""] * (2 + N_QUARTERS)


def build_quarterly_grid(label_to_row: dict[str, int]) -> list[list]:
    qs = quarters()
    asp_model = asp_model_values()
    grid = [_empty_row() for _ in ROWS]

    for r, (label, units) in enumerate(ROWS):
        grid[r][0] = label
        grid[r][1] = units

    year_i = label_to_row["Year"] - 1
    q_i = label_to_row["Quarter"] - 1
    asof_i = label_to_row[AS_OF_LABEL] - 1
    grid[asof_i][2] = "=DATE(2026,9,9)"

    for i, (year, q) in enumerate(qs):
        c = 2 + i
        grid[year_i][c] = year
        grid[q_i][c] = q

    for label, value in {
        **COLUMN_C_DEFAULTS,
        **{k: v for k, v in SCALARS.items() if k != AS_OF_LABEL},
    }.items():
        if label not in label_to_row:
            continue
        grid[label_to_row[label] - 1][2] = value

    lines_i = label_to_row["Z3 manufacturing lines - Model"] - 1
    asp_i = label_to_row["Z3 ASP - Model"] - 1
    for i, (lines, asp) in enumerate(zip(LINE_RAMP, asp_model, strict=True)):
        grid[lines_i][2 + i] = lines
        grid[asp_i][2 + i] = asp

    for (year, q), fields in ACTUALS.items():
        idx = qs.index((year, q))
        c = 2 + idx
        for label, value in fields.items():
            grid[label_to_row[label] - 1][c] = value

    for label in MODEL_FORMULA_LABELS:
        cells = row_cells_for_label(label, N_QUARTERS, label_to_row=label_to_row)
        if cells is None:
            continue
        r = label_to_row[label] - 1
        for i, cell in enumerate(cells):
            if cell is None:
                continue
            grid[r][2 + i] = cell

    return grid


def write_quarterly(client: SheetsClient) -> dict[str, int]:
    from models.EOSE.layout import label_row_numbers

    label_to_row = label_row_numbers()
    grid = build_quarterly_grid(label_to_row)
    sid = sheet_id(client, QUARTERLY)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "unmergeCells": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": 120,
                            "startColumnIndex": 0,
                            "endColumnIndex": 28,
                        }
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sid,
                            "gridProperties": {
                                "rowCount": max(120, len(grid) + 10),
                                "columnCount": 28,
                            },
                        },
                        "fields": "gridProperties.rowCount,gridProperties.columnCount",
                    }
                },
            ]
        }
    )
    ws = client.worksheet(QUARTERLY)
    ws.clear()
    ws.update(grid, range_name=f"A1:{END_COL}{len(grid)}", value_input_option="USER_ENTERED")
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sid,
                            "gridProperties": {"frozenRowCount": 3, "frozenColumnCount": 2},
                        },
                        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": len(grid),
                            "startColumnIndex": 0,
                            "endColumnIndex": 1,
                        },
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        },
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sid,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1,
                        },
                        "properties": {"pixelSize": 280},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sid,
                            "dimension": "COLUMNS",
                            "startIndex": 1,
                            "endIndex": 2,
                        },
                        "properties": {"pixelSize": 90},
                        "fields": "pixelSize",
                    }
                },
            ]
        }
    )
    print(f"Wrote {len(grid)} rows × {2 + N_QUARTERS} cols to {QUARTERLY!r}")
    return label_to_row


def write_price_history(client: SheetsClient) -> None:
    _ensure_sheet(client, PRICE_HISTORY_SHEET, index=4, rows=500, cols=8)
    symbol = price_symbol_for("EOSE")
    note = (
        f"Single GOOGLEFINANCE spill for {symbol} daily prices. "
        "Quarterly Financials → Stock price XLOOKUPs close (E) by quarter-ending date."
    )
    ws = client.worksheet(PRICE_HISTORY_SHEET)
    ws.update([[note]], range_name="G1", value_input_option="RAW")
    ws.update(
        [[price_history_spill_formula(price_symbol=symbol, start_expr="DATE(2024,1,1)", end_expr="TODAY()")]],
        range_name="A1",
        value_input_option="USER_ENTERED",
    )
    print(f"Wrote {PRICE_HISTORY_SHEET} spill for {symbol}")


def write_shares(client: SheetsClient) -> None:
    _ensure_sheet(client, SHARES_SHEET, index=3, rows=40, cols=10)
    ws = client.worksheet(SHARES_SHEET)
    ws.clear()
    ws.update(SHARES_SHEET_GRID, range_name="A1:E8", value_input_option="USER_ENTERED")
    print(f"Wrote {SHARES_SHEET} event table")


def write_definitions(client: SheetsClient, labels: list[str]) -> None:
    _ensure_sheet(client, FINANCIALS_DEFINITIONS_SHEET, index=1, rows=120, cols=4)
    missing: list[str] = []
    rows: list[list[str]] = []
    for label in labels:
        if not label:
            continue
        if label in FIELD_NOTES:
            rows.append([label, FIELD_NOTES[label]])
        else:
            missing.append(label)
            rows.append([label, MISSING_NOTE])
    client.worksheet(FINANCIALS_DEFINITIONS_SHEET).clear()
    client.write_range(FINANCIALS_DEFINITIONS_SHEET, f"A1:B{len(rows)}", rows)
    print(f"Wrote {len(rows)} rows to {FINANCIALS_DEFINITIONS_SHEET!r}")
    if missing:
        print(f"Warning: {len(missing)} labels missing definitions: {missing}")


def write_welcome(client: SheetsClient) -> None:
    _ensure_sheet(client, WELCOME_SHEET, index=0, rows=60, cols=3)
    resources_text = RESOURCES.format(repo=REPO_URL, ir=IR_URL)
    feedback = f'="{FEEDBACK_X}"&{_hyperlink(X_PROFILE_URL, "@MarkPhillips7", standalone=False)}'
    rows: list[list[str]] = [
        [TITLE],
        [],
        [DISCLAIMER],
        [],
        [feedback],
        [],
        [THANKS],
        [],
        [resources_text],
        [],
        [GOALS],
        [],
        [TAB_GUIDE_INTRO],
        [],
        ["Tab", "What you'll find"],
    ]
    tab_header_row = len(rows)
    for tab_title, description in TAB_DESCRIPTIONS:
        gid = sheet_id(client, tab_title)
        rows.append([_tab_link(gid, tab_title), description])
    rows.extend([[], [CLOSING]])
    ws = client.worksheet(WELCOME_SHEET)
    ws.clear()
    ws.update(rows, range_name=f"A1:B{len(rows)}", value_input_option="USER_ENTERED")
    sid = sheet_id(client, WELCOME_SHEET)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": sid, "index": 0},
                        "fields": "index",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 2,
                        },
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 14}}},
                        "fields": "userEnteredFormat.textFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": len(rows),
                            "startColumnIndex": 0,
                            "endColumnIndex": 2,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "wrapStrategy": "WRAP",
                                "verticalAlignment": "TOP",
                            }
                        },
                        "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": tab_header_row - 1,
                            "endRowIndex": tab_header_row,
                            "startColumnIndex": 0,
                            "endColumnIndex": 2,
                        },
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sid,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1,
                        },
                        "properties": {"pixelSize": 280},
                        "fields": "pixelSize",
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sid,
                            "dimension": "COLUMNS",
                            "startIndex": 1,
                            "endIndex": 2,
                        },
                        "properties": {"pixelSize": 720},
                        "fields": "pixelSize",
                    }
                },
            ]
        }
    )
    print(f"Wrote {len(rows)} rows to {WELCOME_SHEET!r}")


def order_tabs(client: SheetsClient) -> None:
    order = [
        WELCOME_SHEET,
        FINANCIALS_DEFINITIONS_SHEET,
        QUARTERLY,
        SHARES_SHEET,
        PRICE_HISTORY_SHEET,
        "Reference",
        "Feltonomics",
        "COGS",
    ]
    requests = []
    for index, title in enumerate(order):
        if title not in client.list_worksheets():
            continue
        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {"sheetId": sheet_id(client, title), "index": index},
                    "fields": "index",
                }
            }
        )
    if requests:
        client.spreadsheet.batch_update({"requests": requests})
        print("Reordered tabs")


def main() -> None:
    client = SheetsClient(ticker="EOSE")
    rename_quarterly_tab(client)
    write_price_history(client)
    write_shares(client)
    labels = write_quarterly(client)
    write_definitions(client, [label for label, _ in ROWS])
    write_welcome(client)
    order_tabs(client)
    print("Done.")
    print(f"Labels: {len(labels)}")


if __name__ == "__main__":
    main()
