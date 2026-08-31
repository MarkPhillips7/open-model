"""Label → row lookups for Weekly / Quarterly Financials."""

from __future__ import annotations

from sheets import SheetsClient

WEEKLY = "Weekly Financials"
QUARTERLY = "Quarterly Financials"


def sheet_id(client: SheetsClient, title: str) -> int:
    for sheet in client.spreadsheet.fetch_sheet_metadata()["sheets"]:
        if sheet["properties"]["title"] == title:
            return sheet["properties"]["sheetId"]
    raise KeyError(f"Sheet {title!r} not found")


def label_rows(client: SheetsClient, sheet: str, *, max_row: int = 80) -> dict[str, int]:
    rows = client.worksheet(sheet).get(f"A1:A{max_row}")
    found: dict[str, int] = {}
    for idx, row in enumerate(rows, start=1):
        if row and row[0]:
            found[row[0]] = idx
    return found


def row_by_label(label_map: dict[str, int], label: str, sheet: str) -> int:
    try:
        return label_map[label]
    except KeyError as exc:
        raise KeyError(f"Label {label!r} not found on {sheet!r}") from exc


def insert_rows_before_label(
    client: SheetsClient,
    *,
    tab: str,
    before_label: str,
    labels: list[str],
) -> int:
    """Insert blank rows before *before_label* and write *labels* in column A. Returns insert row."""
    ws = client.worksheet(tab)
    label_map = label_rows(client, tab)
    try:
        insert_at = label_map[before_label]
    except KeyError as exc:
        raise KeyError(f"{before_label!r} not found on {tab!r}") from exc

    sid = sheet_id(client, tab)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sid,
                            "dimension": "ROWS",
                            "startIndex": insert_at - 1,
                            "endIndex": insert_at - 1 + len(labels),
                        },
                        "inheritFromBefore": True,
                    }
                }
            ]
        }
    )

    ws = client.worksheet(tab)
    for offset, label in enumerate(labels):
        ws.update(
            [[label]],
            range_name=f"A{insert_at + offset}",
            value_input_option="RAW",
        )
    print(f"{tab}: inserted {len(labels)} row(s) before {before_label!r} at row {insert_at}")
    return insert_at


def write_quarterly_by_label(
    client: SheetsClient,
    col: str,
    values_by_label: dict[str, int | float | str],
) -> None:
    """Write hardcoded quarterly actuals using row labels (survives row inserts)."""
    labels = label_rows(client, QUARTERLY)
    ws = client.worksheet(QUARTERLY)
    for label, value in values_by_label.items():
        ws.update(
            [[value]],
            range_name=f"{col}{row_by_label(labels, label, QUARTERLY)}",
            value_input_option="RAW",
        )


def write_quarterly_cells(
    client: SheetsClient,
    *,
    label: str,
    values_by_col: dict[str, int | float | str],
) -> None:
    """Write one quarterly row (by label) across multiple columns."""
    labels = label_rows(client, QUARTERLY)
    row = row_by_label(labels, label, QUARTERLY)
    ws = client.worksheet(QUARTERLY)
    for col, value in values_by_col.items():
        ws.update([[value]], range_name=f"{col}{row}", value_input_option="RAW")
