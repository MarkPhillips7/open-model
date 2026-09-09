#!/usr/bin/env python3
"""Insert Adjusted EBITDA - Model and refresh Adj NI - Model formula."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from models.OPEN.gaap_below_the_line import ADJ_EBITDA_MODEL_LABEL  # noqa: E402
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows  # noqa: E402

NET_INTEREST_LABEL = "Net Interest Expense"


def ensure_adj_ebitda_model_row(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if ADJ_EBITDA_MODEL_LABEL in weekly_labels:
        print(f"{ADJ_EBITDA_MODEL_LABEL!r} already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=NET_INTEREST_LABEL,
        labels=[ADJ_EBITDA_MODEL_LABEL],
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=NET_INTEREST_LABEL,
        labels=[ADJ_EBITDA_MODEL_LABEL],
    )


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    ensure_adj_ebitda_model_row(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
