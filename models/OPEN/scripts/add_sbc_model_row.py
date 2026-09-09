#!/usr/bin/env python3
"""Insert Stock Based Compensation - Model and clear guidance guesses from quarterly."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.formulas import SBC_MODEL_LABEL  # noqa: E402
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows, row_by_label  # noqa: E402

# 2026 Q3/Q4 were management-guide placeholders, not reported actuals.
SBC_GUIDANCE_CLEAR = {
    "F": 110_000_000,  # 2026 Q3
    "G": 110_000_000,  # 2026 Q4
}


def clear_quarterly_sbc_guesses(client: SheetsClient) -> None:
    ws = client.worksheet(QUARTERLY)
    labels = label_rows(client, QUARTERLY)
    sbc_row = row_by_label(labels, "Stock Based Compensation", QUARTERLY)
    for col, expected in SBC_GUIDANCE_CLEAR.items():
        cell = f"{col}{sbc_row}"
        current = ws.get(cell)
        val = current[0][0] if current and current[0] else ""
        if val in ("", None):
            print(f"{cell} already blank")
            continue
        if isinstance(val, (int, float)) and abs(val - expected) > 1:
            raise ValueError(f"{cell} is {val!r}, expected {expected} before clearing")
        ws.update([[""]], range_name=cell, value_input_option="RAW")
        print(f"Cleared {cell} (was ${expected:,})")


def ensure_sbc_model_row(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if SBC_MODEL_LABEL in weekly_labels:
        print(f"{SBC_MODEL_LABEL!r} already on {WEEKLY}")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label="Basic Shares Outstanding",
        labels=[SBC_MODEL_LABEL],
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label="Basic Shares Outstanding",
        labels=[SBC_MODEL_LABEL],
    )


def main() -> None:
    client = SheetsClient()
    clear_quarterly_sbc_guesses(client)
    ensure_sbc_model_row(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
