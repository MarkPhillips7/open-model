#!/usr/bin/env python3
"""Restore Weekly Financials * - Model row formulas from the ticker pack."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sheets.registry import load_pack_module, parse_ticker_argv, pack_dir, resolve_ticker  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from validate_model_formulas import validate  # noqa: E402


def restore_model_formulas(client: SheetsClient, *, ticker: str | None = None) -> None:
    resolved = resolve_ticker(ticker or client.ticker)
    wfm = load_pack_module(resolved, "weekly_model_formulas")
    ws = client.worksheet(WEEKLY)
    labels = label_rows(client, WEEKLY, max_row=120)

    issues = validate(client, ticker=resolved, check_live_drift=False)
    if issues:
        raise RuntimeError(
            "Model formula validation failed before restore:\n"
            + "\n".join(f"  - {i}" for i in issues)
        )

    missing = [lbl for lbl in wfm.MODEL_FORMULA_LABELS if lbl not in labels]
    if missing:
        raise KeyError(f"Labels not found on {WEEKLY}: {missing}")

    data = ws.get("A1:DY120", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = wfm.col_letter(n_cols + 1)

    existing_by_row: dict[int, list] = {
        idx: (list(row[1:]) if len(row) > 1 else [])
        for idx, row in enumerate(data, start=1)
    }

    updates: dict[int, list] = {}

    for label in wfm.MODEL_FORMULA_LABELS:
        cells = wfm.row_cells_for_label(label, n_cols, label_to_row=labels)
        if cells is not None:
            updates[labels[label]] = cells

    if hasattr(wfm, "cm_stack_updates"):
        updates.update(
            wfm.cm_stack_updates(n_cols, label_to_row=labels, existing=existing_by_row)
        )

    batch = [
        {
            "range": f"B{row_num}:{end_col}{row_num}",
            "values": [updates[row_num]],
        }
        for row_num in sorted(updates)
    ]
    if batch:
        ws.batch_update(batch, value_input_option="USER_ENTERED")

    print(f"Restored model formulas on rows: {sorted(updates)}")


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    if rest:
        print(f"Unknown arguments: {rest}")
        sys.exit(2)
    ticker = resolve_ticker(ticker_arg)
    if not (pack_dir(ticker) / "weekly_model_formulas.py").is_file():
        print(f"No weekly_model_formulas.py in {ticker} pack — skip.")
        return
    client = SheetsClient(ticker=ticker)
    restore_model_formulas(client, ticker=ticker)
    print("Done.")


if __name__ == "__main__":
    main()
