#!/usr/bin/env python3
"""Emergency rollback: restore chart series ranges on Weekly Financials.

Do not run routinely. The Sheets API cannot restore colors, log scale, or other
UI chart settings. Charts are manual-only — see .cursor/rules/charts-manual-only.mdc.

Series layout is defined in models/{TICKER}/snapshot.json.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import sheet_id  # noqa: E402
from sheets.registry import parse_ticker_argv, resolve_ticker, snapshot_path  # noqa: E402
from sheets.workbook_snapshot import chart_series_tuples, charts_by_tab, load_snapshot  # noqa: E402

WEEKLY_SHEET_ID = 0
CHART_FEED = "Chart Feed"


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


def restore_chart(
    client: SheetsClient,
    tab: str,
    series_spec: list[tuple],
    *,
    chart_index: int = 0,
    domain_row: int = 1,
    domain_end_col: int = 121,
) -> None:
    meta = client.spreadsheet.fetch_sheet_metadata()
    chart_tab = next(s for s in meta["sheets"] if s["properties"]["title"] == tab)
    chart = chart_tab["charts"][chart_index]
    spec = copy.deepcopy(chart["spec"])
    basic = spec.setdefault("basicChart", {})

    basic["domains"] = [
        {"domain": {"sourceRange": {"sources": [grid_range(domain_row, domain_end_col)]}}}
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
    suffix = f" chart {chart_index}" if chart_index else ""
    print(f"{tab}{suffix}: restored Weekly Financials rows {rows} (domain row {domain_row})")


def delete_chart_feed(client: SheetsClient) -> None:
    if CHART_FEED not in client.list_worksheets():
        print(f"{CHART_FEED!r} not present — skip delete")
        return
    sid = sheet_id(client, CHART_FEED)
    client.spreadsheet.batch_update({"requests": [{"deleteSheet": {"sheetId": sid}}]})
    print(f"Deleted sheet {CHART_FEED!r}")


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    if rest:
        print(f"Unknown arguments: {rest}")
        sys.exit(2)
    ticker = resolve_ticker(ticker_arg)
    client = SheetsClient(ticker=ticker)
    snapshot = load_snapshot(snapshot_path(ticker))
    for tab, charts in charts_by_tab(snapshot).items():
        for chart_index, chart in enumerate(charts):
            restore_chart(
                client,
                tab,
                chart_series_tuples(chart),
                chart_index=chart_index,
                domain_row=chart["domain_row"],
                domain_end_col=chart["domain_end_col"],
            )
    delete_chart_feed(client)
    print("Charts restored to Weekly Financials series ranges.")


if __name__ == "__main__":
    main()
