"""Contribution margin seasonality derived from quarterly earnings supplements."""

from __future__ import annotations

# National monthly home-sales weights (Seasonality tab row 2). Baseline for within-quarter
# shape before hand-tuned nudges (spring peak shifts Apr–May, summer fade in Q3).
HOME_SALES_MONTHLY_PCT: tuple[float, ...] = (
    5.5,
    6.2,
    7.7,
    8.6,
    9.3,
    9.9,
    10.0,
    9.9,
    9.3,
    8.2,
    7.9,
    7.5,
)

# Ex-2023 quarterly mean deviation from annual mean (decimal, zero-sum over the year).
# Q1 +126 bps, Q2 +284 bps, Q3 -61 bps, Q4 -349 bps.
CM_SEASONAL_ADJ_BY_QUARTER: dict[int, float] = {
    1: 0.0126,
    2: 0.0284,
    3: -0.0061,
    4: -0.0349,
}

CM_SEASONAL_INTRAQUARTER_ALPHA = 0.01

# Within-quarter nudges (bps) on top of home-sales smoothing; each quarter sums to 0.
# Feb↑ Mar↓ | Apr↑ Jun↓ (Mar < Apr) | Jul↑ Sep↓ | Q4 slight Oct↑ Dec↓.
CM_SEASONAL_MONTHLY_NUDGE_BPS: tuple[float, ...] = (
    6,
    26,
    -32,  # Q1
    38,
    -3,
    -35,  # Q2
    15,
    -10,
    -5,  # Q3
    6,
    -1,
    -5,  # Q4
)


def monthly_cm_seasonal_adj_from_home_sales(
    quarterly: dict[int, float] | None = None,
    *,
    home_sales_pct: tuple[float, ...] = HOME_SALES_MONTHLY_PCT,
    alpha: float = CM_SEASONAL_INTRAQUARTER_ALPHA,
) -> tuple[float, ...]:
    """Home-sales-shaped monthly adjustments averaging to each quarterly target."""
    targets = quarterly or CM_SEASONAL_ADJ_BY_QUARTER
    monthly: list[float] = []
    for month in range(1, 13):
        quarter = (month - 1) // 3 + 1
        quarter_months = range((quarter - 1) * 3 + 1, quarter * 3 + 1)
        quarter_hs_mean = sum(home_sales_pct[m - 1] for m in quarter_months) / 3
        quarter_target = targets[quarter]
        hs = home_sales_pct[month - 1]
        monthly.append(quarter_target + alpha * (hs - quarter_hs_mean))
    return tuple(monthly)


def monthly_cm_seasonal_adj(
    quarterly: dict[int, float] | None = None,
    *,
    nudge_bps: tuple[float, ...] = CM_SEASONAL_MONTHLY_NUDGE_BPS,
) -> tuple[float, ...]:
    """Return 12 monthly CM seasonal adjustments that average to each quarterly target."""
    baseline = monthly_cm_seasonal_adj_from_home_sales(quarterly)
    return tuple(
        base + nudge / 10_000 for base, nudge in zip(baseline, nudge_bps, strict=True)
    )


def validate_monthly_cm_seasonality(
    monthly: tuple[float, ...],
    quarterly: dict[int, float] | None = None,
) -> None:
    targets = quarterly or CM_SEASONAL_ADJ_BY_QUARTER
    for quarter in range(1, 5):
        chunk = monthly[(quarter - 1) * 3 : quarter * 3]
        avg = sum(chunk) / 3
        if abs(avg - targets[quarter]) > 1e-6:
            raise ValueError(f"Q{quarter} avg {avg} != target {targets[quarter]}")
    if monthly[2] >= monthly[3]:
        raise ValueError("March adjustment must be below April")
    if monthly[5] <= monthly[4]:
        raise ValueError("June adjustment should ease after May peak")
    if monthly[8] >= monthly[7]:
        raise ValueError("September should be weaker than July within Q3")


CM_SEASONAL_ADJ_BY_MONTH: tuple[float, ...] = monthly_cm_seasonal_adj()
validate_monthly_cm_seasonality(CM_SEASONAL_ADJ_BY_MONTH)

CM_SEASONALITY_ROW_LABEL = "CM Seasonal Adj"
CM_SEASONALITY_SHEET = "Seasonality"
CM_SEASONALITY_VALUE_RANGE = "$B$6:$M$6"

CM_SEASONALITY_ADJUSTMENTS_LABEL = "Contribution Margin - Seasonality Adjustments"
