#!/usr/bin/env python3
"""Rename Weekly Home Activity → Weekly Financials and add Quarterly Financials."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402

OLD_WEEKLY = "Weekly Home Activity"
WEEKLY = "Weekly Financials"
QUARTERLY = "Quarterly Financials"

QUARTER_ENDINGS = {
    "2025 Q3": "9/30/2025",
    "2025 Q4": "12/31/2025",
    "2026 Q1": "3/31/2026",
    "2026 Q2": "6/30/2026",
    "2026 Q3": "9/30/2026",
    "2026 Q4": "12/31/2026",
    "2027 Q1": "3/31/2027",
    "2027 Q2": "6/30/2027",
    "2027 Q3": "9/30/2027",
    "2027 Q4": "12/31/2027",
    "2028 Q1": "3/31/2028",
}

# Hardcoded quarterly inputs extracted from existing /13 stubs.
QUARTERLY_INPUTS: dict[int, dict[str, str | int | float]] = {
    9: {"2025 Q3": 1169, "2025 Q4": 1706, "2026 Q1": 2474, "2026 Q2": 4378},
    15: {"2025 Q3": 2568, "2025 Q4": 1978},
    18: {
        "2025 Q3": 915_000_000,
        "2025 Q4": 736_000_000,
        "2026 Q1": 720_000_000,
        "2026 Q2": 883_000_000,
    },
    21: {"2026 Q2": 51_000_000},
    30: {
        "2025 Q3": 37_000_000,
        "2025 Q4": 35_000_000,
        "2026 Q1": 33_000_000,
        "2026 Q2": 35_000_000,
    },
    32: {
        "2025 Q3": 53_000_000,
        "2025 Q4": 50_000_000,
        "2026 Q1": 63_000_000,
        "2026 Q2": 55_000_000,
    },
    34: {"2025 Q4": 105_000_000, "2026 Q3": 110_000_000, "2026 Q4": 110_000_000},
    38: {
        "2025 Q3": 3139,
        "2025 Q4": 2867,
        "2026 Q1": 3420,
        "2026 Q2": 5459,
    },
}

# Actual rows that aggregate from weekly when no quarterly report exists.
WEEKLY_SUM_ROWS = {3, 12}

# Actual rows spread from quarterly when quarterly cell is a hardcoded value.
QUARTERLY_SPREAD_ROWS = {9, 15, 18, 21, 30, 32, 34}


def col_letter(n: int) -> str:
    """1-indexed column number → A1 letter(s)."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def parse_date(value: str) -> datetime | None:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def quarter_key(value: str) -> str | None:
    dt = parse_date(value)
    if not dt:
        return None
    return f"{dt.year} Q{(dt.month - 1) // 3 + 1}"


def weekly_from_quarterly_formula(row: int, col: str) -> str:
    return (
        f'=LET('
        f"wk,{col}$2,"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"qCol,IFERROR(MATCH(qKey,'Quarterly Financials'!$B$1:$1,0),0),"
        f"qCell,IF(qCol=0,\"\",OFFSET('Quarterly Financials'!$B${row},0,qCol-1)),"
        f'IF(qCol=0,"",IF(ISFORMULA(qCell),"",IF(qCell="","",qCell/13)))'
        f")"
    )


def weekly_inventory_formula(col: str, prev_col: str) -> str:
    if col == "B":
        return "3139"
    return (
        f'=LET('
        f"wk,{col}$2,"
        f'qKey,YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0),'
        f"qCol,MATCH(qKey,'Quarterly Financials'!$B$1:$1,0),"
        f"qEnd,INDEX('Quarterly Financials'!$B$38:$M$38,1,qCol),"
        f"qStart,IF(qCol=1,qEnd,INDEX('Quarterly Financials'!$B$38:$M$38,1,qCol-1)),"
        f"{prev_col}38+(qEnd-qStart)/13"
        f")"
    )


def quarterly_sum_formula(row: int, q_col: str) -> str:
    return (
        f"=SUM(FILTER('Weekly Financials'!$B${row}:$DY${row},"
        f"MAP('Weekly Financials'!$B$2:$DY$2,"
        f'LAMBDA(d,IF(d="","",YEAR(d)&" Q"&ROUNDUP(MONTH(d)/3,0))))={q_col}$1))'
    )


def rename_weekly_sheet(client: SheetsClient) -> None:
    meta = client.spreadsheet.fetch_sheet_metadata()
    weekly_sheet_id = None
    for sheet in meta["sheets"]:
        if sheet["properties"]["title"] == OLD_WEEKLY:
            weekly_sheet_id = sheet["properties"]["sheetId"]
            break
    if weekly_sheet_id is None:
        if any(s["properties"]["title"] == WEEKLY for s in meta["sheets"]):
            print(f"Sheet already renamed to {WEEKLY!r}; skipping rename.")
            return
        raise RuntimeError(f"Could not find sheet {OLD_WEEKLY!r}")

    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": weekly_sheet_id, "title": WEEKLY},
                        "fields": "title",
                    }
                }
            ]
        }
    )
    print(f"Renamed {OLD_WEEKLY!r} → {WEEKLY!r}")


def ensure_quarterly_sheet(client: SheetsClient) -> None:
    if QUARTERLY in client.list_worksheets():
        print(f"{QUARTERLY!r} already exists; skipping add.")
        return

    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": QUARTERLY,
                            "index": 1,
                            "gridProperties": {"rowCount": 60, "columnCount": 20},
                        }
                    }
                }
            ]
        }
    )
    print(f"Added sheet {QUARTERLY!r}")


def build_quarterly_sheet(client: SheetsClient) -> None:
    weekly_ws = client.worksheet(WEEKLY)
    labels = weekly_ws.get("A2:A47")
    labels = [row[0] if row else "" for row in labels]

    quarters = list(QUARTER_ENDINGS.keys())
    n_q = len(quarters)

    # Row 1: quarter keys; row 2: quarter ending + labels from weekly row 2.
    row1 = ["Quarter", *quarters]
    row2 = ["Quarter Ending", *[QUARTER_ENDINGS[q] for q in quarters]]
    grid: list[list] = [row1, row2]

    for idx, label in enumerate(labels):
        row_num = idx + 2
        if row_num <= 2:
            continue
        row_vals: list = [label]
        for q_idx, q in enumerate(quarters):
            q_col = col_letter(q_idx + 2)
            if row_num in QUARTERLY_INPUTS and q in QUARTERLY_INPUTS[row_num]:
                row_vals.append(QUARTERLY_INPUTS[row_num][q])
            elif row_num in WEEKLY_SUM_ROWS:
                row_vals.append(quarterly_sum_formula(row_num, q_col))
            else:
                row_vals.append("")
        grid.append(row_vals)

    end_col = col_letter(n_q + 1)
    end_row = len(grid)
    client.write_range(QUARTERLY, f"A1:{end_col}{end_row}", grid, as_formulas=True)
    print(f"Wrote {QUARTERLY} structure A1:{end_col}{end_row}")


def update_weekly_formulas(client: SheetsClient) -> None:
    weekly_ws = client.worksheet(WEEKLY)
    data = weekly_ws.get("A2:DY47", value_render_option="FORMULA")

    rows_to_write: dict[int, list] = {}
    changed_cells = 0

    for row_idx, row in enumerate(data):
        row_num = row_idx + 2
        cells = list(row[1:])
        row_changed = False

        for col_idx, cell in enumerate(cells):
            col = col_letter(col_idx + 2)
            prev_col = col_letter(col_idx + 1)

            if row_num == 38:
                new_val = weekly_inventory_formula(col, prev_col)
                if str(cell) != new_val:
                    cells[col_idx] = new_val
                    row_changed = True
                    changed_cells += 1
                continue

            if row_num not in QUARTERLY_SPREAD_ROWS:
                continue

            is_div13 = isinstance(cell, str) and "/13" in cell
            if not is_div13:
                continue

            cells[col_idx] = weekly_from_quarterly_formula(row_num, col)
            row_changed = True
            changed_cells += 1

        if row_changed:
            rows_to_write[row_num] = cells

    end_col = col_letter(len(data[0]))
    for row_num in sorted(rows_to_write):
        weekly_ws.update(
            [rows_to_write[row_num]],
            range_name=f"B{row_num}:{end_col}{row_num}",
            value_input_option="USER_ENTERED",
        )

    print(f"Updated {changed_cells} weekly cells across rows {sorted(rows_to_write)}")


def main() -> None:
    client = SheetsClient()
    rename_weekly_sheet(client)
    ensure_quarterly_sheet(client)
    build_quarterly_sheet(client)
    update_weekly_formulas(client)
    print("\nDone. Worksheets:", client.list_worksheets())


if __name__ == "__main__":
    main()
