#!/usr/bin/env python3
"""Set up OPEN 1.0 vs 2.0 transition blending on Transitions and Financials tabs."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows, sheet_id  # noqa: E402
from models.OPEN.open_transition import (  # noqa: E402
    HOME_SALES_1_0_MODEL_LABEL,
    HOME_SALES_2_0_MODEL_LABEL,
    LISTING_TO_SOLD_WEEK_HEADER_ROW,
    NEW_LISTINGS_1_0_MODEL_LABEL,
    NEW_LISTINGS_2_0_MODEL_LABEL,
    OPEN_1_0_LISTING_BY_WEEK,
    OPEN_1_0_PRICE_RETENTION,
    OPEN_1_0_SELL_THROUGH_LABELS,
    OPEN_1_0_SOLD_WEEKS,
    OPEN_1_0_WEEKLY_SOLD,
    OPEN_1_0_WEEKLY_SOLD_MULTIPLIERS,
    OPEN_2_0_ROWS_TO_RENAME,
    TRANSITION_COMPLETENESS_LABEL,
    TRANSITIONS,
    open_1_0_running_totals,
    sold_week_end_col,
)




def rename_open_2_0_labels(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    for row, label in OPEN_2_0_ROWS_TO_RENAME.items():
        ws.update([[label]], range_name=f"A{row}", value_input_option="RAW")
    print(f"{TRANSITIONS}: renamed OPEN 2.0 labels on rows {sorted(OPEN_2_0_ROWS_TO_RENAME)}")


def write_open_1_0_listing_row(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    ws.update(
        [["OPEN 1.0 Percent of Ultimate Listers by Week", *OPEN_1_0_LISTING_BY_WEEK, "=SUM(B5:J5)"]],
        range_name="A5:K5",
        value_input_option="USER_ENTERED",
    )
    print(f"{TRANSITIONS}: wrote OPEN 1.0 listing timing A5:K5")


def write_open_1_0_sell_through_block(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    end = sold_week_end_col(OPEN_1_0_SOLD_WEEKS)
    total_col = sold_week_end_col(OPEN_1_0_SOLD_WEEKS + 1)
    mult_row = ["" if m is None else m for m in OPEN_1_0_WEEKLY_SOLD_MULTIPLIERS]
    running = open_1_0_running_totals()
    rows = [
        [OPEN_1_0_SELL_THROUGH_LABELS[0], *mult_row, ""],
        [OPEN_1_0_SELL_THROUGH_LABELS[1], *OPEN_1_0_WEEKLY_SOLD, f"=SUM(B14:{end}14)"],
        [OPEN_1_0_SELL_THROUGH_LABELS[2], *running, f"={end}15"],
        [OPEN_1_0_SELL_THROUGH_LABELS[3], *OPEN_1_0_PRICE_RETENTION, ""],
    ]
    ws.update(
        rows,
        range_name=f"A13:{total_col}16",
        value_input_option="USER_ENTERED",
    )
    print(f"{TRANSITIONS}: wrote OPEN 1.0 sell-through A13:{total_col}16")


def ensure_open_1_0_sell_through_rows(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    labels = label_rows(client, TRANSITIONS, max_row=30)
    if OPEN_1_0_SELL_THROUGH_LABELS[0] in labels:
        print(f"{TRANSITIONS}: OPEN 1.0 sell-through block already present")
        write_open_1_0_sell_through_block(client)
        return

    sid = sheet_id(client, TRANSITIONS)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sid,
                            "dimension": "ROWS",
                            "startIndex": 12,
                            "endIndex": 16,
                        },
                        "inheritFromBefore": True,
                    }
                }
            ]
        }
    )
    print(f"{TRANSITIONS}: inserted 4 rows after row 12 for OPEN 1.0 sell-through")
    write_open_1_0_sell_through_block(client)


def ensure_financials_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if TRANSITION_COMPLETENESS_LABEL not in weekly_labels:
        insert_rows_before_label(
            client,
            tab=WEEKLY,
            before_label="New Listings - Model",
            labels=[TRANSITION_COMPLETENESS_LABEL],
        )
        weekly_labels = label_rows(client, WEEKLY)

    if NEW_LISTINGS_2_0_MODEL_LABEL not in weekly_labels:
        insert_rows_before_label(
            client,
            tab=WEEKLY,
            before_label="Average Sale Price (homes sold by OPEN)",
            labels=[NEW_LISTINGS_2_0_MODEL_LABEL, NEW_LISTINGS_1_0_MODEL_LABEL],
        )
        weekly_labels = label_rows(client, WEEKLY)

    if HOME_SALES_2_0_MODEL_LABEL not in weekly_labels:
        insert_rows_before_label(
            client,
            tab=WEEKLY,
            before_label="Revenue",
            labels=[HOME_SALES_2_0_MODEL_LABEL, HOME_SALES_1_0_MODEL_LABEL],
        )
        weekly_labels = label_rows(client, WEEKLY)

    quarterly_labels = label_rows(client, QUARTERLY)
    if TRANSITION_COMPLETENESS_LABEL not in quarterly_labels:
        insert_rows_before_label(
            client,
            tab=QUARTERLY,
            before_label="New Listings - Model",
            labels=[TRANSITION_COMPLETENESS_LABEL],
        )
        quarterly_labels = label_rows(client, QUARTERLY)

    if NEW_LISTINGS_2_0_MODEL_LABEL not in quarterly_labels:
        insert_rows_before_label(
            client,
            tab=QUARTERLY,
            before_label="Average Sale Price (homes sold by OPEN)",
            labels=[NEW_LISTINGS_2_0_MODEL_LABEL, NEW_LISTINGS_1_0_MODEL_LABEL],
        )
        quarterly_labels = label_rows(client, QUARTERLY)

    if HOME_SALES_2_0_MODEL_LABEL not in quarterly_labels:
        insert_rows_before_label(
            client,
            tab=QUARTERLY,
            before_label="Revenue",
            labels=[HOME_SALES_2_0_MODEL_LABEL, HOME_SALES_1_0_MODEL_LABEL],
        )
        quarterly_labels = label_rows(client, QUARTERLY)


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    rename_open_2_0_labels(client)
    write_open_1_0_listing_row(client)
    ensure_open_1_0_sell_through_rows(client)
    ensure_financials_rows(client)
    ws = client.worksheet(TRANSITIONS)
    end = sold_week_end_col(OPEN_1_0_SOLD_WEEKS)
    total_col = sold_week_end_col(OPEN_1_0_SOLD_WEEKS + 1)
    weeks = list(range(1, OPEN_1_0_SOLD_WEEKS + 1))
    ws.update(
        [["Weeks from Listing to Sold", *weeks, "Total"]],
        range_name=f"A{LISTING_TO_SOLD_WEEK_HEADER_ROW}:{total_col}{LISTING_TO_SOLD_WEEK_HEADER_ROW}",
        value_input_option="RAW",
    )
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
