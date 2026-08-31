#!/usr/bin/env python3
"""Restore Weekly Financials * - Model row formulas from sheets/weekly_model_formulas.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sheets.weekly_model_formulas import (  # noqa: E402
    MODEL_FORMULA_LABELS,
    cm_stack_updates,
    col_letter,
    row_cells_for_label,
)

sys.path.insert(0, str(ROOT / "scripts"))
from validate_model_formulas import validate  # noqa: E402


def restore_model_formulas(client: SheetsClient) -> None:
    ws = client.worksheet(WEEKLY)
    labels = label_rows(client, WEEKLY, max_row=100)

    issues = validate(client, check_live_drift=False)
    if issues:
        raise RuntimeError(
            "Model formula validation failed before restore:\n"
            + "\n".join(f"  - {i}" for i in issues)
        )

    missing = [lbl for lbl in MODEL_FORMULA_LABELS if lbl not in labels]
    if missing:
        raise KeyError(f"Labels not found on {WEEKLY}: {missing}")

    cm_labels = (
        "Contribution Margin - Core",
        "Contribution Margin - Seasonality Adjustments",
        "Contribution Margin - Adjustments",
        "Contribution Margin Improvement - Core",
    )
    for lbl in cm_labels:
        if lbl not in labels:
            raise KeyError(f"CM stack label not found on {WEEKLY}: {lbl!r}")

    data = ws.get("A1:DY90", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)

    existing_by_row: dict[int, list] = {
        idx: (list(row[1:]) if len(row) > 1 else [])
        for idx, row in enumerate(data, start=1)
    }

    updates: dict[int, list] = {}

    for label in MODEL_FORMULA_LABELS:
        cells = row_cells_for_label(label, n_cols, label_to_row=labels)
        if cells is not None:
            updates[labels[label]] = cells

    updates.update(
        cm_stack_updates(n_cols, label_to_row=labels, existing=existing_by_row)
    )

    for row_num in sorted(updates):
        ws.update(
            [updates[row_num]],
            range_name=f"B{row_num}:{end_col}{row_num}",
            value_input_option="USER_ENTERED",
        )

    print(f"Restored model formulas on rows: {sorted(updates)}")


def main() -> None:
    client = SheetsClient()
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
