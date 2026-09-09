#!/usr/bin/env python3
"""Insert GAAP below-the-line rows and refresh GAAP NI - Model reconciliation."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from update_weekly_quarterly_spread import update_weekly_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from models.OPEN.gaap_below_the_line import (  # noqa: E402
    BELOW_THE_LINE_BY_COL,
    BELOW_THE_LINE_LABELS,
)
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label, label_rows, write_quarterly_by_label  # noqa: E402
from models.OPEN.weekly_model_formulas import GAAP_NET_INCOME_MODEL_LABEL  # noqa: E402

GAAP_NET_INCOME_LABEL = "Net Income (Loss) Attributable to Common Shareholders"


def ensure_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY)
    if all(lbl in weekly_labels for lbl in BELOW_THE_LINE_LABELS):
        print("Below-the-line rows already present")
        return

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label=GAAP_NET_INCOME_LABEL,
        labels=list(BELOW_THE_LINE_LABELS),
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label=GAAP_NET_INCOME_LABEL,
        labels=list(BELOW_THE_LINE_LABELS),
    )


def write_quarterly_actuals(client: SheetsClient) -> None:
    for col, values in BELOW_THE_LINE_BY_COL.items():
        write_quarterly_by_label(client, col, values)
        print(f"Wrote {len(values)} below-the-line values to {col}")


def main() -> None:
    client = SheetsClient(ticker="OPEN")
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
