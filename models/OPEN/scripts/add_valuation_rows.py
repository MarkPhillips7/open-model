#!/usr/bin/env python3
"""Insert valuation rows (price, TTM revenue, implied P/S) and populate weekly formulas."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import (  # noqa: E402
    QUARTERLY,
    WEEKLY,
    insert_rows_after_label,
    label_rows,
    row_by_label,
)
from models.OPEN.valuation import (  # noqa: E402
    PRICE_AT_CLOSE_LABEL,
    PRICE_AT_PS_2_LABEL,
    PRICE_AT_PS_3_LABEL,
    REPORTED_TTM_BY_QUARTER,
    REVENUE_LABEL,
    REVENUE_MODEL_LABEL,
    SHARES_LABEL,
    SHARES_MODEL_LABEL,
    TTM_REVENUE_LABEL,
    VALUATION_LABELS,
    weekly_price_at_close_formula,
    weekly_price_at_ps_formula,
    weekly_ttm_revenue_formula,
)
from models.OPEN.weekly_model_formulas import col_letter  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from setup_price_history import (  # noqa: E402
    ensure_price_history_sheet,
    write_price_history_query,
)

EPS_MODEL_LABEL = "Earnings per Share - Model"


def ensure_valuation_rows(client: SheetsClient) -> None:
    weekly_labels = label_rows(client, WEEKLY, max_row=100)
    if PRICE_AT_CLOSE_LABEL in weekly_labels:
        print(f"Valuation rows already on {WEEKLY}")
        return

    insert_rows_after_label(
        client,
        tab=WEEKLY,
        after_label=EPS_MODEL_LABEL,
        labels=list(VALUATION_LABELS),
    )
    insert_rows_after_label(
        client,
        tab=QUARTERLY,
        after_label=EPS_MODEL_LABEL,
        labels=list(VALUATION_LABELS),
    )


def write_quarterly_ttm_actuals(client: SheetsClient) -> None:
    """Write reported TTM revenue on Quarterly Financials for quarters on the sheet."""
    labels = label_rows(client, QUARTERLY, max_row=100)
    ws = client.worksheet(QUARTERLY)
    ttm_row = row_by_label(labels, TTM_REVENUE_LABEL, QUARTERLY)
    headers = ws.get("B1:M1")[0]
    for col_idx, header in enumerate(headers, start=2):
        if header in REPORTED_TTM_BY_QUARTER:
            col = col_letter(col_idx)
            ws.update(
                [[REPORTED_TTM_BY_QUARTER[header]]],
                range_name=f"{col}{ttm_row}",
                value_input_option="RAW",
            )
            print(f"Wrote {QUARTERLY} {col}{ttm_row} TTM ({header})")


def write_weekly_valuation_formulas(client: SheetsClient) -> None:
    labels = label_rows(client, WEEKLY, max_row=100)
    quarterly_labels = label_rows(client, QUARTERLY, max_row=100)
    ws = client.worksheet(WEEKLY)

    price_row = row_by_label(labels, PRICE_AT_CLOSE_LABEL, WEEKLY)
    ttm_row = row_by_label(labels, TTM_REVENUE_LABEL, WEEKLY)
    ps2_row = row_by_label(labels, PRICE_AT_PS_2_LABEL, WEEKLY)
    ps3_row = row_by_label(labels, PRICE_AT_PS_3_LABEL, WEEKLY)
    revenue_row = row_by_label(labels, REVENUE_LABEL, WEEKLY)
    revenue_model_row = row_by_label(labels, REVENUE_MODEL_LABEL, WEEKLY)
    shares_row = row_by_label(labels, SHARES_LABEL, WEEKLY)
    shares_model_row = row_by_label(labels, SHARES_MODEL_LABEL, WEEKLY)
    quarterly_revenue_row = row_by_label(quarterly_labels, REVENUE_LABEL, QUARTERLY)

    data = ws.get("A1:DY90", value_render_option="FORMULA")
    n_cols = max(len(row) for row in data) - 1
    end_col = col_letter(n_cols + 1)

    rows_to_update: dict[int, list[str]] = {}
    for col_idx in range(n_cols):
        col = col_letter(col_idx + 2)
        rows_to_update.setdefault(price_row, []).append(weekly_price_at_close_formula(col))
        rows_to_update.setdefault(ttm_row, []).append(
            weekly_ttm_revenue_formula(
                col,
                revenue_row=revenue_row,
                revenue_model_row=revenue_model_row,
                quarterly_revenue_row=quarterly_revenue_row,
            )
        )
        rows_to_update.setdefault(ps2_row, []).append(
            weekly_price_at_ps_formula(
                col,
                ps_multiple=2,
                ttm_row=ttm_row,
                shares_row=shares_row,
                shares_model_row=shares_model_row,
            )
        )
        rows_to_update.setdefault(ps3_row, []).append(
            weekly_price_at_ps_formula(
                col,
                ps_multiple=3,
                ttm_row=ttm_row,
                shares_row=shares_row,
                shares_model_row=shares_model_row,
            )
        )

    for row_num in sorted(rows_to_update):
        ws.update(
            [rows_to_update[row_num]],
            range_name=f"B{row_num}:{end_col}{row_num}",
            value_input_option="USER_ENTERED",
        )
        print(f"Wrote {WEEKLY} B{row_num}:{end_col}{row_num}")


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    ensure_valuation_rows(client)
    ensure_price_history_sheet(client)
    write_price_history_query(client)
    write_quarterly_ttm_actuals(client)
    write_weekly_valuation_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
