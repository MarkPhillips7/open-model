"""Contribution margin seasonality — values synced from live Seasonality tab."""

from __future__ import annotations

# Seasonality!B6:M6 (UNFORMATTED). Spreadsheet is source of truth; run
# scripts/pull_cm_stack_from_sheet.py to refresh from the live workbook.
CM_SEASONAL_ADJ_BY_MONTH: tuple[float, ...] = (
    -0.01,
    0.003,
    0.013,
    0.017,
    0.02,
    0.021,
    0.011,
    -0.003,
    -0.013,
    -0.017,
    -0.021,
    -0.021,
)

CM_SEASONALITY_ROW_LABEL = "CM Seasonal Adj"
CM_SEASONALITY_SHEET = "Seasonality"
CM_SEASONALITY_VALUE_RANGE = "$B$6:$M$6"

CM_SEASONALITY_ADJUSTMENTS_LABEL = "Contribution Margin - Seasonality Adjustments"
