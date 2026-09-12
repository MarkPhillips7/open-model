"""Cash Now More Later (2P) mix and capital-intensity helpers.

CNML is still iBuying: Opendoor buys, holds, renovates, and resells the home.
Sellers take less cash at close and a share of residual proceeds at resale
(COGS, not a volume diversion). Mix is a weekly % of purchases; capital
intensity scales warehouse debt vs 1P cash-at-close.
"""

from __future__ import annotations

TRANSITIONS = "Transitions"

CNML_PERCENT_LABEL = "Cash Now More Later %"
CNML_PURCHASES_MODEL_LABEL = "CNML Purchases - Model"
CNML_ROW_LABELS: tuple[str, ...] = (
    CNML_PERCENT_LABEL,
    CNML_PURCHASES_MODEL_LABEL,
)
INSERT_BEFORE_LABEL = "Homes Purchased"

# Transitions levers (appended after ancillary B29:B34).
CNML_CASH_VS_1P_ROW = 35
CNML_MIX_TERMINAL_ROW = 36
CNML_CASH_VS_1P_CELL = f"{TRANSITIONS}!$B${CNML_CASH_VS_1P_ROW}"
CNML_MIX_TERMINAL_CELL = f"{TRANSITIONS}!$B${CNML_MIX_TERMINAL_ROW}"

CNML_CASH_VS_1P_LABEL = "CNML cash at close vs 1P"
CNML_MIX_TERMINAL_LABEL = "CNML mix terminal %"

# Help-doc example is ~$270k upfront vs a $350k resale; 80% is a round guess.
CNML_CASH_VS_1P_DEFAULT = 0.80
# Not company-disclosed. Kaz is still on step 2 (1P+2P); 3P is later.
CNML_MIX_TERMINAL_DEFAULT = 0.50

# Mix waypoints (week-ending Saturdays that match disclosed prints).
# 0% through Q1 2025; 19% last week of Q3 2025; 35% last week of Q4 2025;
# ~40% from Sep 2026 (Kaz “More Cash Now More Later”); terminal by end-2027.
CNML_LAUNCH_END = "DATE(2025,3,29)"
CNML_Q3_2025_END = "DATE(2025,9,27)"
CNML_Q4_2025_END = "DATE(2025,12,27)"
CNML_SEP_2026 = "DATE(2026,9,12)"
CNML_END_2027 = "DATE(2027,12,25)"

CNML_MIX_Q3_2025 = 0.19
CNML_MIX_Q4_2025 = 0.35
CNML_MIX_SEP_2026 = 0.40

TRANSITIONS_CNML_ROWS: list[tuple[str, float]] = [
    (CNML_CASH_VS_1P_LABEL, CNML_CASH_VS_1P_DEFAULT),
    (CNML_MIX_TERMINAL_LABEL, CNML_MIX_TERMINAL_DEFAULT),
]


def _smoothstep(col: str, start: str, end: str) -> str:
    t = f"(({col}$1-{start})/({end}-{start}))"
    return f"(3*{t}^2-2*{t}^3)"


def cnml_percent_formula(col: str) -> str:
    """Date-driven mix: disclosed 0→19%→35%, then guessed 40% (Sep 2026) → terminal."""
    s0 = CNML_LAUNCH_END
    s1 = CNML_Q3_2025_END
    s2 = CNML_Q4_2025_END
    s3 = CNML_SEP_2026
    s4 = CNML_END_2027
    q3 = f"{CNML_MIX_Q3_2025:.0%}"
    q4 = f"{CNML_MIX_Q4_2025:.0%}"
    sep = f"{CNML_MIX_SEP_2026:.0%}"
    delta_q4 = f"{CNML_MIX_Q4_2025 - CNML_MIX_Q3_2025:.0%}"
    delta_sep = f"{CNML_MIX_SEP_2026 - CNML_MIX_Q4_2025:.0%}"
    terminal = CNML_MIX_TERMINAL_CELL
    return (
        f"=IFS({col}$1<={s0},0%,"
        f"{col}$1<={s1},{q3}*{_smoothstep(col, s0, s1)},"
        f"{col}$1<={s2},{q3}+{delta_q4}*{_smoothstep(col, s1, s2)},"
        f"{col}$1<={s3},{q4}+{delta_sep}*{_smoothstep(col, s2, s3)},"
        f"{col}$1<={s4},{sep}+({terminal}-{sep})*{_smoothstep(col, s3, s4)},"
        f"TRUE,{terminal})"
    )


def cnml_capital_intensity_expr(col: str, *, label_to_row: dict[str, int]) -> str:
    """Blended cash-at-close vs 1P: (1 − mix) × 1 + mix × CNML cash vs 1P."""
    mix_row = label_to_row[CNML_PERCENT_LABEL]
    return f"((1-{col}{mix_row})+{col}{mix_row}*{CNML_CASH_VS_1P_CELL})"


def cnml_intensity_ratio_expr(
    col: str,
    prev_col: str,
    *,
    label_to_row: dict[str, int],
) -> str:
    """this-week intensity / last-week intensity (1 when mix is stable)."""
    this = cnml_capital_intensity_expr(col, label_to_row=label_to_row)
    prev = cnml_capital_intensity_expr(prev_col, label_to_row=label_to_row)
    return f"IF({prev}=0,1,{this}/{prev})"
