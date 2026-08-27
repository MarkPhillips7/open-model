"""Google Sheets formula builders for the Opendoor model."""

from __future__ import annotations

QUARTERLY = "Quarterly Financials"

# Row on Weekly Financials that holds week-ending dates (column headers).
WEEK_DATE_ROW = 1


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

    def quarter_amount(qcol: str) -> str:
        ref = f"OFFSET('{QUARTERLY}'!$B${quarterly_row},0,{qcol}-1)"
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
        f"daysEnd,SUM(MAP(SEQUENCE(7),LAMBDA(i,--(YEAR(wk-7+i)&\" Q\"&ROUNDUP(MONTH(wk-7+i)/3,0)=qEndKey)))),"
        f"daysStart,7-daysEnd,"
        f"blend,(daysEnd/7)*({q_end})+(daysStart/7)*({q_start}),"
        f'IF(wk="","",IF(AND(qEndCol=0,qStartCol=0),"",IF(blend=0,"",blend)))'
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
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f'qKey,YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0),'
        f"qCol,MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),"
        f"qEnd,INDEX('{QUARTERLY}'!$B${quarterly_row}:$M${quarterly_row},1,qCol),"
        f"qStart,IF(qCol=1,qEnd,INDEX('{QUARTERLY}'!$B${quarterly_row}:$M${quarterly_row},1,qCol-1)),"
        f"{prev_col}{weekly_row}+(qEnd-qStart)/13"
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


def weekly_shares_formula(
    col: str,
    prev_col: str,
    *,
    weekly_row: int,
    quarterly_eop_row: int = 48,
    week_date_row: int = WEEK_DATE_ROW,
    q2_eop_anchor: int = 733_592_980,
) -> str:
    if col == "B":
        return str(q2_eop_anchor)
    return (
        f'=LET('
        f"wk,{col}${week_date_row},"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"qCol,IFERROR(MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qEnd,IF(qCol=0,\"\",INDEX('{QUARTERLY}'!$B${quarterly_eop_row}:$M${quarterly_eop_row},1,qCol)),"
        f"qStart,IF(qCol=1,{q2_eop_anchor},IF(qCol=0,\"\",INDEX('{QUARTERLY}'!$B${quarterly_eop_row}:$M${quarterly_eop_row},1,qCol-1))),"
        f"{prev_col}{weekly_row}+(qEnd-qStart)/13"
        f")"
    )
