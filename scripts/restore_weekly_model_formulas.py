#!/usr/bin/env python3
"""Restore Weekly Financials * - Model row formulas from the ticker pack."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sheets.registry import load_formula_module, parse_ticker_argv, resolve_ticker  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from validate_model_formulas import validate  # noqa: E402


def restore_model_formulas(client: SheetsClient, *, ticker: str | None = None) -> None:
    resolved = resolve_ticker(ticker or client.ticker)
    wfm = load_formula_module(resolved)
    tab = getattr(wfm, "FINANCIALS_TAB", WEEKLY)
    first_col = getattr(wfm, "FIRST_VALUE_COL", "B")
    first_idx = getattr(wfm, "FIRST_VALUE_COL_INDEX", 2)
    ws = client.worksheet(tab)
    labels = label_rows(client, tab, max_row=150)

    issues = validate(client, ticker=resolved, check_live_drift=False)
    if issues:
        raise RuntimeError(
            "Model formula validation failed before restore:\n"
            + "\n".join(f"  - {i}" for i in issues)
        )

    missing = [lbl for lbl in wfm.MODEL_FORMULA_LABELS if lbl not in labels]
    if missing:
        raise KeyError(f"Labels not found on {tab}: {missing}")

    data = ws.get("A1:DY150", value_render_option="FORMULA")
    last_idx = max(len(row) for row in data) if data else first_idx
    n_cols = max(1, last_idx - first_idx + 1)

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

    batch = []
    for row_num in sorted(updates):
        cells = updates[row_num]
        start_offset = 0
        while start_offset < len(cells) and cells[start_offset] is None:
            start_offset += 1
        end_offset = len(cells)
        while end_offset > start_offset and cells[end_offset - 1] is None:
            end_offset -= 1
        if start_offset >= end_offset:
            continue
        write_cells = cells[start_offset:end_offset]
        start_col = wfm.col_letter(first_idx + start_offset)
        write_end = wfm.col_letter(first_idx + end_offset - 1)
        batch.append(
            {
                "range": f"{start_col}{row_num}:{write_end}{row_num}",
                "values": [write_cells],
            }
        )
    if batch:
        ws.batch_update(batch, value_input_option="USER_ENTERED")

    print(f"Restored model formulas on {tab} rows: {sorted(updates)}")


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    if rest:
        print(f"Unknown arguments: {rest}")
        sys.exit(2)
    ticker = resolve_ticker(ticker_arg)
    try:
        load_formula_module(ticker)
    except FileNotFoundError:
        print(f"No weekly_model_formulas.py or quarterly_model_formulas.py in {ticker} pack — skip.")
        return
    client = SheetsClient(ticker=ticker)
    restore_model_formulas(client, ticker=ticker)
    print("Done.")


if __name__ == "__main__":
    main()
