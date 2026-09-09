#!/usr/bin/env python3
"""Extend OPEN 1.0 sell-through curves to 39 weeks on Transitions and restore formulas."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.open_transition import (  # noqa: E402
    LISTING_TO_SOLD_WEEK_HEADER_ROW,
    OPEN_1_0_PRICE_RETENTION,
    OPEN_1_0_SELL_THROUGH_LABELS,
    OPEN_1_0_SOLD_WEEKS,
    OPEN_1_0_WEEKLY_SOLD,
    OPEN_1_0_WEEKLY_SOLD_MULTIPLIERS,
    OPEN_2_0_SOLD_WEEKS,
    TRANSITIONS,
    open_1_0_running_totals,
    sold_week_end_col,
)


def write_listing_week_headers(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    end = sold_week_end_col(OPEN_1_0_SOLD_WEEKS)
    total_col = sold_week_end_col(OPEN_1_0_SOLD_WEEKS + 1)
    weeks = list(range(1, OPEN_1_0_SOLD_WEEKS + 1))
    ws.update(
        [["Weeks from Listing to Sold", *weeks, "Total"]],
        range_name=f"A{LISTING_TO_SOLD_WEEK_HEADER_ROW}:{total_col}{LISTING_TO_SOLD_WEEK_HEADER_ROW}",
        value_input_option="RAW",
    )
    print(
        f"{TRANSITIONS}: week headers A{LISTING_TO_SOLD_WEEK_HEADER_ROW}:{total_col}"
        f"{LISTING_TO_SOLD_WEEK_HEADER_ROW}"
    )


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
    print(f"{TRANSITIONS}: OPEN 1.0 sell-through A13:{total_col}16 (sum={sum(OPEN_1_0_WEEKLY_SOLD):.4f})")


def main() -> None:
    client = SheetsClient()
    write_listing_week_headers(client)
    write_open_1_0_sell_through_block(client)
    restore_model_formulas(client)
    print(
        f"Done. 2.0 lag={OPEN_2_0_SOLD_WEEKS} weeks; "
        f"1.0 lag={OPEN_1_0_SOLD_WEEKS} weeks."
    )


if __name__ == "__main__":
    main()
