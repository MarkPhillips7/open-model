"""Weekly valuation rows: stock price, TTM revenue, implied P/S prices."""

from __future__ import annotations

from sheets.formulas import QUARTERLY, WEEK_DATE_ROW
from sheets.price_history import weekly_price_at_close_formula

PRICE_AT_CLOSE_LABEL = "Price (at Close)"
TTM_REVENUE_LABEL = "Trailing Twelve Months Revenue"
PRICE_AT_PS_2_LABEL = "Price @ P/S = 2"
PRICE_AT_PS_3_LABEL = "Price @ P/S = 3"

VALUATION_LABELS = (
    PRICE_AT_CLOSE_LABEL,
    TTM_REVENUE_LABEL,
    PRICE_AT_PS_2_LABEL,
    PRICE_AT_PS_3_LABEL,
)

REVENUE_LABEL = "Revenue"
REVENUE_MODEL_LABEL = "Revenue - Model"
SHARES_LABEL = "Basic Shares Outstanding"
SHARES_MODEL_LABEL = "Basic Shares Outstanding - Model"

# Reported TTM revenue ($) from quarterly earnings supplements (GAAP).
REPORTED_TTM_BY_QUARTER: dict[str, int] = {
    "2024 Q4": 5_150_000_000,
    "2025 Q1": 5_130_000_000,
    "2025 Q2": 5_180_000_000,
    "2025 Q3": 4_720_000_000,
    "2025 Q4": 4_370_000_000,
}

# Quarterly GAAP revenue ($) for quarters not on the Quarterly Financials tab.
REPORTED_QUARTERLY_REVENUE: dict[str, int] = {
    "2024 Q4": 1_084_000_000,
    "2025 Q1": 1_153_000_000,
    "2025 Q2": 1_567_000_000,
    "2025 Q3": 915_000_000,
    "2025 Q4": 736_000_000,
}

# Weeks of columns before a rolling sum spans a full year (B = week 1).
FULL_YEAR_WEEKS = 52


def _historical_quarterly_revenue_ifs() -> str:
    return ",".join(f'qKey="{q}",{v}' for q, v in REPORTED_QUARTERLY_REVENUE.items())


def _quarter_revenue_expr(
    *,
    quarterly_revenue_row: int,
    revenue_row: int,
    revenue_model_row: int,
) -> str:
    """Resolve one quarter's revenue: quarterly tab → historical → weekly model sum."""
    q_sheet = (
        f"IF(qCol=0,\"\","
        f"INDEX('{QUARTERLY}'!$B${quarterly_revenue_row}:$M${quarterly_revenue_row},1,qCol))"
    )
    weekly_sum = (
        f"SUM(MAP(FILTER($B$1:$DY$1,$B$1:$DY$1<>\"\"),LAMBDA(d,"
        f'IF(YEAR(d)&" Q"&ROUNDUP(MONTH(d)/3,0)=qKey,'
        f"LET(ci,MATCH(d,$B$1:$DY$1,0),"
        f"v,INDEX($B:$DY,{revenue_row},ci),"
        f"IF(ISNUMBER(v),v,INDEX($B:$DY,{revenue_model_row},ci))),0)"
        f")))"
    )
    return (
        f"IF(AND(qCol>0,ISNUMBER({q_sheet})),{q_sheet},"
        f"IFNA(IFS({_historical_quarterly_revenue_ifs()}),{weekly_sum}))"
    )


def _proration_lambda(
    *,
    quarterly_revenue_row: int,
    revenue_row: int,
    revenue_model_row: int,
) -> str:
    q_rev = _quarter_revenue_expr(
        quarterly_revenue_row=quarterly_revenue_row,
        revenue_row=revenue_row,
        revenue_model_row=revenue_model_row,
    )
    return (
        f"LAMBDA(i,LET("
        f"qAnchor,EDATE(DATE(YEAR(wk),ROUNDUP(MONTH(wk)/3,0)*3,1),-3*(i-1)),"
        f'qKey,YEAR(qAnchor)&" Q"&ROUNDUP(MONTH(qAnchor)/3,0),'
        f"qYear,VALUE(LEFT(qKey,4)),"
        f"qNum,VALUE(MID(qKey,7,1)),"
        f"qStart,DATE(qYear,(qNum-1)*3+1,1),"
        f"qEnd,EOMONTH(DATE(qYear,qNum*3,1),0),"
        f"oStart,MAX(ttmStart,qStart),"
        f"oEnd,MIN(ttmEnd,qEnd),"
        f"oDays,IF(oStart>oEnd,0,oEnd-oStart+1),"
        f"qDays,qEnd-qStart+1,"
        f"qCol,IFERROR(MATCH(qKey,'{QUARTERLY}'!$B$1:$1,0),0),"
        f"qRev,{q_rev},"
        f"IF(OR(oDays=0,NOT(ISNUMBER(qRev))),0,qRev*oDays/qDays)"
        f"))"
    )


def weekly_ttm_revenue_formula(
    col: str,
    *,
    revenue_row: int,
    revenue_model_row: int,
    quarterly_revenue_row: int,
) -> str:
    """TTM from reported quarter-end values, else day-weighted quarterly revenue."""
    wk = f"{col}${WEEK_DATE_ROW}"
    historical_ttm_ifs = ",".join(
        f'qKey="{q}",{v}' for q, v in REPORTED_TTM_BY_QUARTER.items()
    )
    proration = (
        f"SUM(MAP(SEQUENCE(6),"
        f"{_proration_lambda(quarterly_revenue_row=quarterly_revenue_row, revenue_row=revenue_row, revenue_model_row=revenue_model_row)}"
        f"))"
    )
    rolling = (
        f"IF(weeksAvail=0,\"\",SUM(MAP(SEQUENCE(1,n-s+1,s,1),LAMBDA(c,"
        f"LET(ci,c-COLUMN($B$1)+1,v,INDEX($B:$DY,{revenue_row},ci),"
        f"IF(ISNUMBER(v),v,INDEX($B:$DY,{revenue_model_row},ci))"
        f")))))"
    )
    return (
        f"=LET("
        f"wk,{wk},"
        f'qKey,IF(wk="","",YEAR(wk)&" Q"&ROUNDUP(MONTH(wk)/3,0)),'
        f"ttmStart,wk-365,"
        f"ttmEnd,wk,"
        f"n,COLUMN(),"
        f"weeksAvail,n-1,"
        f"s,MAX(2,n-MIN({FULL_YEAR_WEEKS},n-1)),"
        f"prorated,{proration},"
        f"rolling,{rolling},"
        f'IF(wk="","",'
        f"IFS({historical_ttm_ifs},weeksAvail<{FULL_YEAR_WEEKS},prorated,TRUE,rolling)"
        f"))"
    )


def weekly_price_at_ps_formula(
    col: str,
    *,
    ps_multiple: float,
    ttm_row: int,
    shares_row: int,
    shares_model_row: int,
) -> str:
    shares = (
        f"IF(ISNUMBER({col}{shares_row}),{col}{shares_row},"
        f"IF(ISNUMBER({col}{shares_model_row}),{col}{shares_model_row},0))"
    )
    return (
        f"=IF(OR(N({col}{ttm_row})=0,N({shares})=0),\"\","
        f"{ps_multiple}*{col}{ttm_row}/{shares})"
    )
