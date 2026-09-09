"""GOOGLEFINANCE daily price spill; weekly rows XLOOKUP this table."""

from __future__ import annotations

from sheets.formulas import WEEK_DATE_ROW
from sheets.labels import WEEKLY

PRICE_HISTORY_SHEET = "Price History"

# GOOGLEFINANCE("all", "DAILY") spill at A1: row 1 = headers, row 2+ = data.
PRICE_HISTORY_DATE_COL = "A"
PRICE_HISTORY_CLOSE_COL = "E"
PRICE_HISTORY_DATA_START_ROW = 2


def price_history_spill_formula(
    *,
    price_symbol: str,
    weekly_tab: str = WEEKLY,
) -> str:
    """One spill query for daily prices covering the Weekly Financials horizon."""
    weeks = f"FILTER('{weekly_tab}'!$B$1:$DY$1,'{weekly_tab}'!$B$1:$DY$1<>\"\")"
    return (
        f'=GOOGLEFINANCE("{price_symbol}","all",'
        f"MIN({weeks})-30,"
        f"MIN(MAX({weeks}),TODAY()),"
        f'"DAILY")'
    )


def weekly_price_at_close_formula(col: str, *, week_date_row: int = WEEK_DATE_ROW) -> str:
    """Last daily close on or before the week-ending date; blank if the week is still in the future."""
    wk = f"{col}${week_date_row}"
    dates = (
        f"'{PRICE_HISTORY_SHEET}'!${PRICE_HISTORY_DATE_COL}"
        f"${PRICE_HISTORY_DATA_START_ROW}:${PRICE_HISTORY_DATE_COL}"
    )
    closes = (
        f"'{PRICE_HISTORY_SHEET}'!${PRICE_HISTORY_CLOSE_COL}"
        f"${PRICE_HISTORY_DATA_START_ROW}:${PRICE_HISTORY_CLOSE_COL}"
    )
    return (
        f'=IF(OR({wk}="",{wk}>TODAY()),"",'
        f"IFERROR(XLOOKUP({wk},{dates},{closes},\"\",-1),\"\"))"
    )
