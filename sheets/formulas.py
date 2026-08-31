"""Google Sheets formula builders for the Opendoor model."""

from __future__ import annotations

QUARTERLY = "Quarterly Financials"

# Row on Weekly Financials that holds week-ending dates (column headers).
WEEK_DATE_ROW = 1


def _quarterly_index_cell(quarterly_row: int, qcol_expr: str) -> str:
    return f"INDEX('{QUARTERLY}'!$B${quarterly_row}:$M${quarterly_row},1,{qcol_expr})"


def _quarterly_index_has_data(qcol_expr: str, quarterly_row: int) -> str:
    ref = _quarterly_index_cell(quarterly_row, qcol_expr)
    return f'AND({qcol_expr}>0,NOT(ISFORMULA({ref})),{ref}<>"")'


def weekly_day_weighted_quarterly_formula(
    quarterly_row: int,
    col: str,
    *,
    per_week_divisor: int | None = 13,
    week_date_row: int = WEEK_DATE_ROW,
) -> str:
    """Spread a quarterly hardcoded value across weeks using day-weighted quarter overlap.

    Each day of the 7-day window ending on ``col``$week_date_row belongs to exactly one
    calendar quarter. The weekly amount is::

        sum over quarters q of (days_in_q / 7) * (quarterly_value_q / per_week_divisor)

    When the week falls entirely inside one quarter, this reduces to quarterly / 13.
    Boundary weeks blend adjacent quarters (e.g. 2 days in Q1 and 5 in Q2 → 2/7 and 5/7).
    """

    def quarter_cell(qcol: str) -> str:
        return f"OFFSET('{QUARTERLY}'!$B${quarterly_row},0,{qcol}-1)"

    def quarter_has_data(qcol: str) -> str:
        ref = quarter_cell(qcol)
        return f"AND({qcol}>0,NOT(ISFORMULA({ref})),{ref}<>\"\")"

    def quarter_amount(qcol: str) -> str:
        ref = quarter_cell(qcol)
        inner = f"IF(OR({qcol}=0,ISFORMULA({ref}),{ref}=\"\"),0,{ref})"
        if per_week_divisor is not None:
            return f"({inner}/{per_week_divisor})"
        return inner

    q_end = quarter_amount("qEndCol")
    q_start = quarter_amount("qStartCol")

    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f"ws,wk-6,"
        f'qEndKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f'qStartKey,IF(wk="","",YEAR(ws)&" Q"&ROUNDUP(MONTH(ws)/3,0)),'
        f"qEndCol,IFERROR(MATCH(qEndKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qStartCol,IFERROR(MATCH(qStartKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qEndHas,{quarter_has_data('qEndCol')},"
        f"qStartHas,{quarter_has_data('qStartCol')},"
        f"bothQ,IF(qStartKey=qEndKey,TRUE,AND(qEndHas,qStartHas)),"
        f"daysEnd,SUM(MAP(SEQUENCE(7),LAMBDA(i,--(YEAR(wk-7+i)&\" Q\"&ROUNDUP(MONTH(wk-7+i)/3,0)=qEndKey)))),"
        f"daysStart,7-daysEnd,"
        f"blend,(daysEnd/7)*({q_end})+(daysStart/7)*({q_start}),"
        f'IF(wk="","",IF(OR(NOT(bothQ),blend=0),"",blend))'
        f")"
    )


def weekly_from_quarterly_formula(
    quarterly_row: int,
    col: str,
    *,
    week_date_row: int = WEEK_DATE_ROW,
) -> str:
    """Alias for the standard dollar spread (÷13, day-weighted at boundaries)."""
    return weekly_day_weighted_quarterly_formula(
        quarterly_row,
        col,
        per_week_divisor=13,
        week_date_row=week_date_row,
    )


def weekly_from_quarterly_end_quarter_formula(
    quarterly_row: int,
    col: str,
    *,
    week_date_row: int = WEEK_DATE_ROW,
) -> str:
    """Spread using the week-ending quarter only (÷13, no cross-quarter day blend).

    One-time quarterly reconciliation items (debt extinguishment, restructuring,
    inventory valuation timing) should not pull the prior quarter's spike into
    boundary weeks of the next quarter.
    """
    quarter_cell = f"OFFSET('{QUARTERLY}'!$B${quarterly_row},0,qCol-1)"
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"qCol,IFERROR(MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qHas,AND(qCol>0,NOT(ISFORMULA({quarter_cell})),{quarter_cell}<>\"\"),"
        f'IF(wk="","",IF(NOT(qHas),"",{quarter_cell}/13))'
        f")"
    )


def weekly_quarterly_rate_formula(
    quarterly_row: int,
    col: str,
    *,
    week_date_row: int = WEEK_DATE_ROW,
) -> str:
    """Day-weighted blend of quarterly rates (no ÷13), e.g. contribution margin %."""
    return weekly_day_weighted_quarterly_formula(
        quarterly_row,
        col,
        per_week_divisor=None,
        week_date_row=week_date_row,
    )


def weekly_inventory_formula(
    col: str,
    prev_col: str,
    *,
    weekly_row: int,
    quarterly_row: int = 38,
    week_date_row: int = WEEK_DATE_ROW,
    first_col_anchor: int = 3139,
) -> str:
    if col == "B":
        return str(first_col_anchor)
    q_end = _quarterly_index_cell(quarterly_row, "qCol")
    q_start = (
        f"IF(qCol<=1,{q_end},IF(qCol=0,\"\","
        f"{_quarterly_index_cell(quarterly_row, 'qCol-1')}))"
    )
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"qCol,IFERROR(MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qEnd,IF(qCol=0,\"\",{q_end}),"
        f"qStart,{q_start},"
        f"qEndHas,{_quarterly_index_has_data('qCol', quarterly_row)},"
        f"qStartHas,IF(qCol<=1,qEndHas,{_quarterly_index_has_data('qCol-1', quarterly_row)}),"
        f"bothQ,AND(qEndHas,qStartHas),"
        f"delta,(qEnd-qStart)/13,"
        f'IF(OR(wk="",NOT(bothQ)),"",{prev_col}{weekly_row}+delta)'
        f")"
    )


def weekly_asp_formula(
    col: str,
    prev_col: str,
    *,
    weekly_row: int,
    quarterly_row: int,
    week_date_row: int = WEEK_DATE_ROW,
    first_col_fallback: int | float = 377_500,
) -> str:
    """Use quarterly ASP when populated; otherwise carry forward the prior week."""
    q_asp = f"INDEX('{QUARTERLY}'!$B${quarterly_row}:$M${quarterly_row},1,qCol)"
    fallback = str(first_col_fallback) if col == "B" else f"{prev_col}{weekly_row}"
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"qCol,IFERROR(MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qAsp,IF(qCol=0,\"\",{q_asp}),"
        f'IF(wk="","",IF(qAsp="",{fallback},qAsp))'
        f")"
    )


SHARES_MODEL_LABEL = "Basic Shares Outstanding - Model"

SBC_MODEL_LABEL = "Stock Based Compensation - Model"
# Q3 2026 management guide (~$110M/quarter); flat weekly run-rate when no quarterly actual.
SBC_GUIDANCE_QUARTERLY = 110_000_000
# Matches live sheet literal (110M ÷ 13 rounded in Sheets).
SBC_WEEKLY_RUN_RATE = 8_461_538.46153846


def weekly_sbc_model_formula(
    col: str,
    *,
    weekly_actual_sbc_row: int,
    week_date_row: int = WEEK_DATE_ROW,
    weekly_run_rate: float = SBC_WEEKLY_RUN_RATE,
) -> str:
    """Actual SBC passthrough; else flat $110M/quarter weekly amount (not cumulative)."""
    return (
        f"=IF(N({col}{weekly_actual_sbc_row})>0,{col}{weekly_actual_sbc_row},"
        f'IF({col}${week_date_row}="","",{weekly_run_rate}))'
    )


def weekly_gaap_below_line_model_formula(
    col: str,
    *,
    weekly_actual_row: int,
    weekly_run_rate: float,
    week_date_row: int = WEEK_DATE_ROW,
) -> str:
    """Passthrough spread actual (including negatives/zero); else flat weekly run-rate."""
    return (
        f"=IF(ISNUMBER({col}{weekly_actual_row}),{col}{weekly_actual_row},"
        f'IF({col}${week_date_row}="","",{weekly_run_rate}))'
    )


def weekly_shares_formula(
    col: str,
    prev_col: str,
    *,
    weekly_row: int,
    quarterly_eop_row: int = 50,
    week_date_row: int = WEEK_DATE_ROW,
    q2_eop_anchor: int = 733_592_980,
) -> str:
    if col == "B":
        return str(q2_eop_anchor)
    q_end = _quarterly_index_cell(quarterly_eop_row, "qCol")
    q_start = (
        f"IF(qCol=1,{q2_eop_anchor},IF(qCol=0,\"\","
        f"{_quarterly_index_cell(quarterly_eop_row, 'qCol-1')}))"
    )
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"qCol,IFERROR(MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qEnd,IF(qCol=0,\"\",{q_end}),"
        f"qStart,{q_start},"
        f"qEndHas,{_quarterly_index_has_data('qCol', quarterly_eop_row)},"
        f"qStartHas,IF(qCol<=1,TRUE,{_quarterly_index_has_data('qCol-1', quarterly_eop_row)}),"
        f"bothQ,AND(qEndHas,qStartHas),"
        f"delta,(qEnd-qStart)/13,"
        f'IF(OR(wk="",NOT(bothQ)),"",{prev_col}{weekly_row}+delta)'
        f")"
    )
