#!/usr/bin/env python3
"""Insert GAAP net income rows and refresh EPS - Model to GAAP NI ÷ basic shares."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from scripts.update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.weekly_model_formulas import GAAP_NET_INCOME_MODEL_LABEL  # noqa: E402

WEEKLY = "Weekly Financials"
QUARTERLY = "Quarterly Financials"

GAAP_NET_INCOME_LABEL = "Net Income (Loss) Attributable to Common Shareholders"

# Quarterly GAAP net loss = basic EPS × basic weighted-average shares (10-Q).
GAAP_NET_INCOME_BY_COL: dict[str, int] = {
    "B": -89_032_680,  # 2025 Q3: -0.12 × 741,939,000
    "C": -1_095_975_720,  # 2025 Q4: -1.26 × 869,822,000
    "D": -172_679_760,  # 2026 Q1: -0.18 × 959,332,000
    "E": -164_182_600,  # 2026 Q2: -0.17 × 965,780,000
}


def sheet_id(client: SheetsClient, title: str) -> int:
    for sheet in client.spreadsheet.fetch_sheet_metadata()["sheets"]:
        if sheet["properties"]["title"] == title:
            return sheet["properties"]["sheetId"]
    raise KeyError(f"Sheet {title!r} not found")


def insert_rows_before_label(
    client: SheetsClient,
    *,
    tab: str,
    before_label: str,
    labels: list[str],
) -> None:
    ws = client.worksheet(tab)
    col_a = ws.get("A1:A60")
    row_by_label = {
        idx: (row[0] if row else "")
        for idx, row in enumerate(col_a, start=1)
    }
    try:
        insert_at = next(r for r, lbl in row_by_label.items() if lbl == before_label)
    except StopIteration as exc:
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


def write_quarterly_gaap_net_income(client: SheetsClient) -> None:
    ws = client.worksheet(QUARTERLY)
    labels = {
        (row[0] if row else ""): idx
        for idx, row in enumerate(ws.get("A1:A60"), start=1)
    }
    if GAAP_NET_INCOME_LABEL not in labels:
        raise KeyError(f"{GAAP_NET_INCOME_LABEL!r} missing on {QUARTERLY!r}")

    for col, value in GAAP_NET_INCOME_BY_COL.items():
        ws.update([[value]], range_name=f"{col}{labels[GAAP_NET_INCOME_LABEL]}", value_input_option="RAW")
    print(f"Wrote GAAP net income to {QUARTERLY} cols {sorted(GAAP_NET_INCOME_BY_COL)}")


def main() -> None:
    client = SheetsClient()

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label="Earnings per Share",
        labels=[GAAP_NET_INCOME_LABEL, GAAP_NET_INCOME_MODEL_LABEL],
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label="Earnings per Share",
        labels=[GAAP_NET_INCOME_LABEL, GAAP_NET_INCOME_MODEL_LABEL],
    )

    write_quarterly_gaap_net_income(client)
    update_weekly_formulas(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
