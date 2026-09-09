#!/usr/bin/env python3
"""Create Welcome tab (leftmost) and populate visitor-facing intro copy."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import sheet_id  # noqa: E402
from models.OPEN.welcome import (  # noqa: E402
    ACCOUNTABLE_URL,
    CLOSING,
    DISCLAIMER,
    FEEDBACK_X,
    GOALS,
    REPO_URL,
    RESOURCES,
    TAB_DESCRIPTIONS,
    TAB_GUIDE_INTRO,
    THANKS,
    TITLE,
    WELCOME_SHEET,
    X_PROFILE_URL,
)

WELCOME_GRID_ROWS = 60
WELCOME_GRID_COLS = 3
# First-create defaults only. Later runs must not reset widths — they are a
# UI preference (Welcome column A is currently 659px on the live sheet).
DEFAULT_COL_A_PX = 659
DEFAULT_COL_B_PX = 720


def _hyperlink(url: str, label: str, *, standalone: bool = True) -> str:
    expr = f'HYPERLINK("{url}", "{label}")'
    return f"={expr}" if standalone else expr


def _tab_link(gid: int, title: str) -> str:
    return f'=HYPERLINK("#gid={gid}", "{title}")'


def ensure_welcome_sheet(client: SheetsClient) -> tuple[int, bool]:
    worksheets = client.list_worksheets()
    created = WELCOME_SHEET not in worksheets
    if created:
        client.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": WELCOME_SHEET,
                                "index": 0,
                                "gridProperties": {
                                    "rowCount": WELCOME_GRID_ROWS,
                                    "columnCount": WELCOME_GRID_COLS,
                                },
                            }
                        }
                    }
                ]
            }
        )
        print(f"Added sheet {WELCOME_SHEET!r} at index 0")
    else:
        print(f"{WELCOME_SHEET!r} already exists")

    sid = sheet_id(client, WELCOME_SHEET)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": sid, "index": 0},
                        "fields": "index",
                    }
                }
            ]
        }
    )
    return sid, created


def build_rows(client: SheetsClient) -> tuple[list[list[str]], int]:
    resources_text = RESOURCES.format(
        repo=REPO_URL,
        accountable=ACCOUNTABLE_URL,
    )
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
    tab_header_row = len(rows)  # 1-based row index for formatting

    for tab_title, description in TAB_DESCRIPTIONS:
        gid = sheet_id(client, tab_title)
        rows.append([_tab_link(gid, tab_title), description])

    rows.extend([[], [CLOSING]])
    return rows, tab_header_row


def _column_width_requests(welcome_sid: int) -> list[dict]:
    return [
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": welcome_sid,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": DEFAULT_COL_A_PX},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": welcome_sid,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 2,
                },
                "properties": {"pixelSize": DEFAULT_COL_B_PX},
                "fields": "pixelSize",
            }
        },
    ]


def apply_formatting(
    client: SheetsClient,
    welcome_sid: int,
    row_count: int,
    tab_header_row: int,
    *,
    set_column_widths: bool = False,
) -> None:
    requests: list[dict] = []
    if set_column_widths:
        requests.extend(_column_width_requests(welcome_sid))
    requests.extend(
        [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": welcome_sid,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 2,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "fontSize": 14},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": welcome_sid,
                        "startRowIndex": 0,
                        "endRowIndex": row_count,
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
                        "sheetId": welcome_sid,
                        "startRowIndex": tab_header_row - 1,
                        "endRowIndex": tab_header_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": 2,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat",
                }
            },
        ]
    )
    client.spreadsheet.batch_update({"requests": requests})


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    welcome_sid, created = ensure_welcome_sheet(client)
    rows, tab_header_row = build_rows(client)
    end_row = len(rows)
    end_col = "B"
    client.write_range(WELCOME_SHEET, f"A1:{end_col}{end_row}", rows, as_formulas=True)
    apply_formatting(
        client,
        welcome_sid,
        end_row,
        tab_header_row,
        set_column_widths=created,
    )
    print(f"Wrote {end_row} rows to {WELCOME_SHEET!r} (leftmost tab)")
    print("Done.")


if __name__ == "__main__":
    main()
