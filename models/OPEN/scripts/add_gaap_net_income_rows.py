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
from sheets.labels import insert_rows_before_label, write_quarterly_cells  # noqa: E402
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

    write_quarterly_cells(
        client,
        label=GAAP_NET_INCOME_LABEL,
        values_by_col=GAAP_NET_INCOME_BY_COL,
    )
    print(f"Wrote GAAP net income to {QUARTERLY} cols {sorted(GAAP_NET_INCOME_BY_COL)}")

    update_weekly_formulas(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
