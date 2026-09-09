#!/usr/bin/env python3
"""Push acquisition monthly weights from models/OPEN/seasonality.py to the sheet.

Prefer pull_cm_stack_from_sheet.py when the live workbook was edited manually.
"""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from sheets import SheetsClient  # noqa: E402
from models.OPEN.cm_seasonality import CM_SEASONALITY_SHEET  # noqa: E402
from models.OPEN.seasonality import (  # noqa: E402
    ACQUISITION_PERCENT_BY_MONTH,
    ACQUISITION_PERCENT_LABEL,
    ACQUISITION_PERCENT_RATIONALE,
    ACQUISITION_PERCENT_TOTAL_FORMULA,
    CM_SEASONAL_ADJ_TOTAL_FORMULA,
    SEASONALITY_TOTAL_HEADER,
)


def push_acquisition_seasonality(client: SheetsClient) -> None:
    ws = client.worksheet(CM_SEASONALITY_SHEET)
    total = sum(ACQUISITION_PERCENT_BY_MONTH)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Acquisition monthly percents must sum to 1.0, got {total:.6f}")

    ws.update(
        [[ACQUISITION_PERCENT_LABEL, *ACQUISITION_PERCENT_BY_MONTH]],
        range_name="A2:M2",
        value_input_option="RAW",
    )
    ws.update(
        [[SEASONALITY_TOTAL_HEADER], [ACQUISITION_PERCENT_TOTAL_FORMULA]],
        range_name="N1:N2",
        value_input_option="USER_ENTERED",
    )
    ws.update(
        [[CM_SEASONAL_ADJ_TOTAL_FORMULA]],
        range_name="N6",
        value_input_option="USER_ENTERED",
    )
    ws.update(
        [[ACQUISITION_PERCENT_RATIONALE]],
        range_name="A3",
        value_input_option="RAW",
    )
    ws.update(
        [[
            "Ex-2023 quarterly CM mean deviation (bps): Q1 +126, Q2 +284, Q3 -61, Q4 -349. "
            "Monthly values are hardcoded on B6:M6 (spreadsheet is source of truth). "
            "See models/OPEN/cm_seasonality.py."
        ]],
        range_name="A7",
        value_input_option="RAW",
    )
    ws.format(
        "B2:N2",
        {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}},
    )
    print(
        f"{CM_SEASONALITY_SHEET}: wrote {ACQUISITION_PERCENT_LABEL!r} "
        f"B2:M2 ({len(ACQUISITION_PERCENT_BY_MONTH)} months, sum={total:.1%})"
    )


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    push_acquisition_seasonality(client)
    print("Done.")


if __name__ == "__main__":
    main()
