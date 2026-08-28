#!/usr/bin/env python3
"""Emergency rollback: restore chart series ranges on Weekly Financials.

Do not run routinely. The Sheets API cannot restore colors, log scale, or other
UI chart settings. Charts are manual-only — see .cursor/rules/charts-manual-only.mdc.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import sheet_id  # noqa: E402

WEEKLY_SHEET_ID = 0
HOMES_CHART = "Homes Chart"
MONEY_CHART = "Money Chart"
CHART_FEED = "Chart Feed"

# (weekly_row_1based, line_style, axis, end_column_index exclusive)
HOMES_SERIES = [
    (2, "SOLID", "LEFT_AXIS", 121),
    (3, "DOTTED", "LEFT_AXIS", 121),
    (8, "SOLID", "LEFT_AXIS", 129),
    (9, "DOTTED", "LEFT_AXIS", 129),
    (11, "SOLID", "LEFT_AXIS", 121),
    (12, "DOTTED", "LEFT_AXIS", 121),
    (14, "SOLID", "LEFT_AXIS", 121),
    (16, "DOTTED", "LEFT_AXIS", 121),
]

MONEY_SERIES = [
    (17, "SOLID", "LEFT_AXIS", 129),
    (18, "DOTTED", "LEFT_AXIS", 129),
    (35, "SOLID", "RIGHT_AXIS", 129),
    (37, "DOTTED", "RIGHT_AXIS", 129),
]

DOMAIN_ROW = 1
DOMAIN_END_COL = 121


def grid_range(row_1based: int, end_col: int) -> dict:
    return {
        "sheetId": WEEKLY_SHEET_ID,
        "startRowIndex": row_1based - 1,
        "endRowIndex": row_1based,
        "startColumnIndex": 0,
        "endColumnIndex": end_col,
    }


def build_series(row: int, line_type: str, axis: str, end_col: int) -> dict:
    entry: dict = {
        "series": {"sourceRange": {"sources": [grid_range(row, end_col)]}},
        "targetAxis": axis,
        "dataLabel": {"type": "NONE", "textFormat": {"fontFamily": "Roboto"}},
    }
    if line_type == "DOTTED":
        entry["lineStyle"] = {"type": "DOTTED"}
    return entry


def restore_chart(client: SheetsClient, tab: str, series_spec: list[tuple]) -> None:
    meta = client.spreadsheet.fetch_sheet_metadata()
    chart_tab = next(s for s in meta["sheets"] if s["properties"]["title"] == tab)
    chart = chart_tab["charts"][0]
    spec = copy.deepcopy(chart["spec"])
    basic = spec.setdefault("basicChart", {})

    basic["domains"] = [
        {"domain": {"sourceRange": {"sources": [grid_range(DOMAIN_ROW, DOMAIN_END_COL)]}}}
    ]
    basic["series"] = [
        build_series(row, line, axis, end_col) for row, line, axis, end_col in series_spec
    ]
    basic["headerCount"] = 1
    basic["legendPosition"] = "RIGHT_LEGEND"

    spec["hiddenDimensionStrategy"] = "SKIP_HIDDEN_ROWS_AND_COLUMNS"
    spec["fontName"] = "Roboto"

    client.spreadsheet.batch_update(
        {"requests": [{"updateChartSpec": {"chartId": chart["chartId"], "spec": spec}}]}
    )
    rows = [r for r, *_ in series_spec]
    print(f"{tab}: restored Weekly Financials rows {rows} (domain row {DOMAIN_ROW})")


def delete_chart_feed(client: SheetsClient) -> None:
    if CHART_FEED not in client.list_worksheets():
        print(f"{CHART_FEED!r} not present — skip delete")
        return
    sid = sheet_id(client, CHART_FEED)
    client.spreadsheet.batch_update({"requests": [{"deleteSheet": {"sheetId": sid}}]})
    print(f"Deleted sheet {CHART_FEED!r}")


def main() -> None:
    client = SheetsClient()
    restore_chart(client, HOMES_CHART, HOMES_SERIES)
    restore_chart(client, MONEY_CHART, MONEY_SERIES)
    delete_chart_feed(client)
    print("Charts restored to Weekly Financials (pre–Chart Feed).")


if __name__ == "__main__":
    main()
