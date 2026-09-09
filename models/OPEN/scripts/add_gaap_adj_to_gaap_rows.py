#!/usr/bin/env python3
"""Insert Adj→GAAP reconciliation rows and refresh GAAP NI - Model formula."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from scripts.update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.gaap_below_the_line import (  # noqa: E402
    ADJ_TO_GAAP_BY_COL,
    ADJ_TO_GAAP_LABELS,
    CEO_MAKE_WHOLE_LABEL,
    CEO_MAKE_WHOLE_MODEL_LABEL,
    INV_VAL_CURRENT_LABEL,
    INV_VAL_CURRENT_MODEL_LABEL,
    INV_VAL_PRIOR_LABEL,
    INV_VAL_PRIOR_MODEL_LABEL,
    OTHER_GAAP_ADJ_LABEL,
    OTHER_GAAP_ADJ_MODEL_LABEL,
    RESTRUCTURING_LABEL,
    RESTRUCTURING_MODEL_LABEL,
)
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows, write_quarterly_by_label  # noqa: E402
from sheets.weekly_model_formulas import GAAP_NET_INCOME_MODEL_LABEL  # noqa: E402

GAAP_NET_INCOME_LABEL = "Net Income (Loss) Attributable to Common Shareholders"

INSERT_LABELS: tuple[str, ...] = (
    INV_VAL_CURRENT_LABEL,
    INV_VAL_CURRENT_MODEL_LABEL,
    INV_VAL_PRIOR_LABEL,
    INV_VAL_PRIOR_MODEL_LABEL,
    RESTRUCTURING_LABEL,
    RESTRUCTURING_MODEL_LABEL,
    CEO_MAKE_WHOLE_LABEL,
    CEO_MAKE_WHOLE_MODEL_LABEL,
    OTHER_GAAP_ADJ_LABEL,
    OTHER_GAAP_ADJ_MODEL_LABEL,
)


def ensure_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if all(lbl in weekly_labels for lbl in ADJ_TO_GAAP_LABELS):
        print("Adj→GAAP reconciliation rows already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=GAAP_NET_INCOME_LABEL,
        labels=list(INSERT_LABELS),
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=GAAP_NET_INCOME_LABEL,
        labels=list(INSERT_LABELS),
    )


def write_quarterly_actuals(client: SheetsClient) -> None:
    for col, values in ADJ_TO_GAAP_BY_COL.items():
        write_quarterly_by_label(client, col, values)
        print(f"Wrote {len(values)} Adj→GAAP values to {col}")


def main() -> None:
    client = SheetsClient()
    weekly = label_rows(client, WEEKLY)
    if GAAP_NET_INCOME_MODEL_LABEL not in weekly:
        raise KeyError(f"{GAAP_NET_INCOME_MODEL_LABEL!r} missing on {WEEKLY}")

    ensure_rows(client)
    write_quarterly_actuals(client)
    update_weekly_formulas(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
