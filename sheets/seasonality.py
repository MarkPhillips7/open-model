"""Acquisition seasonality — Seasonality tab row 2.

Spreadsheet is source of truth; run scripts/pull_cm_stack_from_sheet.py after UI edits.
"""

from __future__ import annotations

# Seasonality!B2:M2 (UNFORMATTED). Jan–Dec share of annual acquisitions.
# Peak Nov–Dec so listings (~2 month lag) hit spring / early summer selling;
# trough May–Aug with June the low; Sep–Oct accelerate back toward the peak.
# Hardcoded (not a formula); must sum to 1.0.
ACQUISITION_PERCENT_BY_MONTH: tuple[float, ...] = (
    0.104,
    0.088,
    0.073,
    0.063,
    0.055,
    0.053,
    0.055,
    0.063,
    0.083,
    0.106,
    0.13,
    0.127,
)

ACQUISITION_PERCENT_LABEL = "Acquisition Percent by Month"
ACQUISITION_PERCENT_RANGE = "$B$2:$M$2"
ACQUISITION_PERCENT_TOTAL_FORMULA = "=SUM(B2:M2)"
ACQUISITION_SEASONALITY_MULTIPLIER_LABEL = "Acquisition Seasonality Multiplier"
CM_SEASONAL_ADJ_TOTAL_FORMULA = "=SUM(B6:M6)"
SEASONALITY_TOTAL_HEADER = "Total"

ACQUISITION_PERCENT_RATIONALE = (
    "Share of annual acquisitions by calendar month. Peak Nov–Dec so listings "
    "(~2 month lag) hit spring/early summer selling; trough May–Aug (June low); "
    "Sep–Oct accelerate. Hardcoded weights sum to 100%."
)
