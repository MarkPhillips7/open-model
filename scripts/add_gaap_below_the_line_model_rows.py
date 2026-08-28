#!/usr/bin/env python3
"""Insert GAAP below-the-line - Model rows and refresh GAAP NI - Model formula."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.gaap_below_the_line import (  # noqa: E402
    ADJ_NET_INCOME_MODEL_LABEL,
    BELOW_THE_LINE_MODEL_LABELS,
)
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows  # noqa: E402


def ensure_model_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if all(lbl in weekly_labels for lbl in BELOW_THE_LINE_MODEL_LABELS):
        print("Below-the-line - Model rows already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=ADJ_NET_INCOME_MODEL_LABEL,
        labels=list(BELOW_THE_LINE_MODEL_LABELS),
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=ADJ_NET_INCOME_MODEL_LABEL,
        labels=list(BELOW_THE_LINE_MODEL_LABELS),
    )


def main() -> None:
    client = SheetsClient()
    ensure_model_rows(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
