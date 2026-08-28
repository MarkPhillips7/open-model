"""Shares tab layout and weekly share-adjustment formulas.

Aug 2026 structure (Form 8-K filed Aug 19, 2026; press release Aug 13, 2026):
  - $158M repurchase of ~45.3M shares at $3.49 (~5% reduction)
  - $650M 0% converts due 2030; initial conversion ~$4.71 (~138M shares if fully converted)
  - Capped calls cap at $6.98 offset convert dilution up to that price
  - Repurchased shares offset remaining convert dilution until stock exceeds **$10.38**
    (net share change from the combined deal ≈ 0 below that price)
"""

from __future__ import annotations

from sheets.formulas import WEEK_DATE_ROW

SHARES_SHEET = "Shares"
SHARES_SBC_PRICE_CELL = f"{SHARES_SHEET}!$B$2"
# Event table: Mode | Start | End | Max share Δ (signed) | Fraction | Window weeks
SHARES_EVENT_TABLE = f"{SHARES_SHEET}!$B$5:$G$20"

SHARES_ADJUSTMENT_LABEL = "Share Count Adjustment - Model"

# Column A labels + table rows written by setup script (B:G used in formulas).
SHARES_SHEET_GRID: list[list] = [
    ["Share count — assumptions & events"],
    ["SBC assumed $/share (weekly SBC ÷ this)", 8],
    [
        "Net-zero price ($): stock price where convert dilution restores repurchased shares "
        "(Aug 2026 deal ≈ $10.38; capped calls offset through $6.98 per 8-K)"
    ],
    [
        "Event",
        "Mode",
        "Start",
        "End",
        "Max share Δ",
        "Fraction",
        "Window wks",
        "Net-zero $",
        "Notes",
    ],
    [
        "Aug 2026 share repurchase",
        "instant",
        "8/19/2026",
        "8/19/2026",
        -45_300_000,
        1,
        1,
        10.38,
        "~45.3M shares @ $3.49; settlement Aug 19 2026 (8-K)",
    ],
    [
        "Nov 2025 warrant distribution",
        "spread_end",
        "",
        "11/20/2026",
        99_295_146,
        0.25,
        4,
        "",
        "Exercise assumed in last N weeks before expiration",
    ],
    [
        "2030 convertible notes (above net-zero)",
        "instant",
        "8/15/2030",
        "8/15/2030",
        137_960_290,
        0,
        1,
        10.38,
        "Base case 0% — no net dilution below $10.38; raise Fraction to model conversion",
    ],
]

SHARES_MODE_LEGEND = [
    ["Mode key"],
    ["instant", "Full Δ×Fraction on first week ending on/after Start"],
    ["spread_end", "Spread Δ×Fraction evenly over Window wks ending on/before End"],
]


def weekly_share_adjustment_formula(
    col: str,
    prev_col: str,
    *,
    weekly_sbc_row: int,
    week_date_row: int = WEEK_DATE_ROW,
) -> str:
    """Weekly share-count delta from Shares event table + SBC."""
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f"prevWk,{prev_col}${week_date_row},"
        f"sbc,IF(N({col}{weekly_sbc_row})>0,{col}{weekly_sbc_row}/{SHARES_SBC_PRICE_CELL},0),"
        f"tbl,{SHARES_EVENT_TABLE},"
        f"ev,BYROW(FILTER(tbl,INDEX(tbl,,1)<>\"\"),LAMBDA(r,"
        f'LET(mode,INDEX(r,1,1),start,INDEX(r,1,2),endDt,INDEX(r,1,3),'
        f"maxSh,INDEX(r,1,4),frac,INDEX(r,1,5),win,INDEX(r,1,6),"
        f"total,maxSh*frac,"
        f'IF(mode="instant",IF(AND(wk>=start,prevWk<start),total,0),'
        f'IF(AND(mode="spread_end",endDt<>"",win>0,wk<=endDt,wk>=endDt-win*7),total/win,0))'
        f"))),"
        f'IF(wk="","",sbc+SUM(ev))'
        f")"
    )


def weekly_shares_model_formula(
    col: str,
    prev_col: str,
    *,
    weekly_actual_shares_row: int,
    weekly_model_shares_row: int,
    weekly_adjustment_row: int,
    week_date_row: int = WEEK_DATE_ROW,
    q2_eop_anchor: int = 733_592_980,
) -> str:
    """Actual passthrough, else prior week model + this week's adjustment helper."""
    if col == "B":
        return (
            f"=IF(N(B{weekly_actual_shares_row})>0,B{weekly_actual_shares_row},"
            f"{q2_eop_anchor})"
        )
    return (
        f"=IF(N({col}{weekly_actual_shares_row})>0,{col}{weekly_actual_shares_row},"
        f"LET("
        f"prev,N({prev_col}{weekly_model_shares_row}),"
        f"adj,N({col}{weekly_adjustment_row}),"
        f'IF(OR({col}${week_date_row}="",prev=0),"",prev+adj)'
        f"))"
    )
