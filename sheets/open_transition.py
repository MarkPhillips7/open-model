"""OPEN 1.0 vs 2.0 transition blending (listings, sales, revenue)."""

from __future__ import annotations

TRANSITIONS = "Transitions"

OPEN_2_0_SOLD_WEEKS = 21
OPEN_1_0_SOLD_WEEKS = 39

# Transitions row layout after setup_open_transition.py (4 rows inserted below row 12).
OPEN_2_0_LISTING_ROW = 4
OPEN_1_0_LISTING_ROW = 5
OPEN_2_0_SOLD_ROW = 10
OPEN_2_0_RETENTION_ROW = 12
OPEN_1_0_SOLD_ROW = 14
OPEN_1_0_RETENTION_ROW = 16
LISTING_TO_SOLD_WEEK_HEADER_ROW = 8
FINANCED_CLOSE_LAG_CELL = f"{TRANSITIONS}!$B$18"
CASH_CLOSE_LAG_CELL = f"{TRANSITIONS}!$B$19"
CASH_PURCHASE_PCT_CELL = f"{TRANSITIONS}!$B$20"
UNLISTED_BACKLOG_CELL = f"{TRANSITIONS}!$B$25"
UNLISTED_BACKLOG_PCT_RANGE = f"{TRANSITIONS}!$B$27:$I$27"

TRANSITION_COMPLETENESS_LABEL = "OPEN 1.0-2.0 Transition Completeness"
NEW_LISTINGS_2_0_MODEL_LABEL = "New Listings - 2.0 Model"
NEW_LISTINGS_1_0_MODEL_LABEL = "New Listings - 1.0 Model"
HOME_SALES_2_0_MODEL_LABEL = "Home Sales - 2.0 Model"
HOME_SALES_1_0_MODEL_LABEL = "Home Sales - 1.0 Model"
REVENUE_2_0_MODEL_LABEL = "Revenue - 2.0 Model"
REVENUE_1_0_MODEL_LABEL = "Revenue - 1.0 Model"

TRANSITION_COMPLETENESS_START_DATE = "DATE(2026,2,21)"
TRANSITION_COMPLETENESS_END_DATE = "DATE(2027,1,2)"

# Pre-Kaz listing timing (~45-day reno wait; peaks later than 2.0).
OPEN_1_0_LISTING_BY_WEEK: list[float] = [
    0.02,
    0.04,
    0.08,
    0.12,
    0.18,
    0.22,
    0.18,
    0.10,
    0.06,
]

# ~51% cumulative sell-through by week 17; tail extended to week 39 (sums to 100%).
OPEN_1_0_WEEKLY_SOLD: list[float] = [
    0.047414226558708146,
    0.03793138124696652,
    0.03034510504757322,
    0.03004165409709749,
    0.02974123755612651,
    0.02944382528036525,
    0.0291493875275616,
    0.028857893552486,
    0.02856931441736114,
    0.02828361847318753,
    0.02800077788850566,
    0.0277207702091176,
    0.02744357450702642,
    0.02716913456195616,
    0.0268974368165366,
    0.02662846764817123,
    0.0263621792007651,
    0.01924439231655953,
    0.01347107462159168,
    0.00942975223511417,
    0.00660082656457992,
    0.03013955611201749,
    0.029386067209217052,
    0.028651415528986625,
    0.02793513014076196,
    0.02723675188724291,
    0.026555833090061837,
    0.02589193726281029,
    0.025244638831240035,
    0.024613522860459033,
    0.023998184788947555,
    0.023398230169223867,
    0.02281327441499327,
    0.02224294255461844,
    0.021686868990752978,
    0.021144697265984152,
    0.02061607983433455,
    0.020100677838476185,
    0.01959816089251428,
]

OPEN_1_0_WEEKLY_SOLD_MULTIPLIERS: list[float | None] = [
    None,
    0.8,
    0.8,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.99,
    0.73,
    0.7,
    0.7,
    0.7,
    *([0.975] * 18),
]

OPEN_1_0_PRICE_RETENTION: list[float] = [
    round(max(0.78, 1.0 - i * 0.0057), 4) for i in range(OPEN_1_0_SOLD_WEEKS)
]

OPEN_2_0_ROWS_TO_RENAME: dict[int, str] = {
    4: "OPEN 2.0 Percent of Ultimate Listers by Week",
    9: "OPEN 2.0 Weekly Percent Sold Multiplier",
    10: "OPEN 2.0 Percent Sold by Listing Week",
    11: "OPEN 2.0 Running Total",
    12: "OPEN 2.0 Price Retention",
}

OPEN_1_0_SELL_THROUGH_LABELS: list[str] = [
    "OPEN 1.0 Weekly Percent Sold Multiplier",
    "OPEN 1.0 Percent Sold by Listing Week",
    "OPEN 1.0 Running Total",
    "OPEN 1.0 Price Retention",
]


def _col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def sold_week_end_col(weeks: int) -> str:
    """Column letter for the last listing-week column (week 1 = B)."""
    return _col_letter(weeks + 1)


def open_1_0_running_totals() -> list[float]:
    total = 0.0
    out: list[float] = []
    for value in OPEN_1_0_WEEKLY_SOLD:
        total += value
        out.append(total)
    return out


def _listing_range(row: int) -> str:
    return f"{TRANSITIONS}!$B${row}:$J${row}"


def _sold_range(row: int, *, weeks: int) -> str:
    end = sold_week_end_col(weeks)
    return f"{TRANSITIONS}!$B${row}:${end}${row}"


def _retention_range(row: int, *, weeks: int) -> str:
    end = sold_week_end_col(weeks)
    return f"{TRANSITIONS}!$B${row}:${end}${row}"


def transition_completeness_formula(col: str) -> str:
    return (
        f'=IF({col}$1="","",MIN(1,MAX(0,'
        f"({col}$1-{TRANSITION_COMPLETENESS_START_DATE})/"
        f"({TRANSITION_COMPLETENESS_END_DATE}-{TRANSITION_COMPLETENESS_START_DATE}))))"
    )


def blend_model_formula(
    col: str,
    *,
    label_to_row: dict[str, int],
    blended_label: str,
    model_2_0_label: str,
    model_1_0_label: str,
) -> str:
    completeness = label_to_row[TRANSITION_COMPLETENESS_LABEL]
    row_2_0 = label_to_row[model_2_0_label]
    row_1_0 = label_to_row[model_1_0_label]
    return (
        f"={col}{completeness}*{col}{row_2_0}"
        f"+(1-{col}{completeness})*{col}{row_1_0}"
    )


def new_listings_model_formula(*, listing_row: int, include_backlog: bool) -> str:
    backlog = (
        f"+IF(COLUMN()-1<=8, {UNLISTED_BACKLOG_CELL}*"
        f"INDEX({UNLISTED_BACKLOG_PCT_RANGE}, 1, COLUMN()-1), 0)"
        if include_backlog
        else ""
    )
    return f"""=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      purchases, IF(col < 2, 90, INDEX(${{Homes Purchased - Model}}:${{Homes Purchased - Model}}, 1, col)*INDEX(${{Likelihood to List}}:${{Likelihood to List}}, 1, col)),
      purchases
    )
  )),
  {_listing_range(listing_row)}
){backlog})"""


def home_sales_model_formula(*, sold_row: int, sold_weeks: int) -> str:
    return f"""=(SUMPRODUCT(
  MAP(SEQUENCE(1,{sold_weeks}), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 140,
        IF(INDEX(${{New Listings}}:${{New Listings}}, 1, col) = "",
          INDEX(${{New Listings - Model}}:${{New Listings - Model}}, 1, col),
          INDEX(${{New Listings}}:${{New Listings}}, 1, col)
        )*INDEX(${{Likelihood to List}}:${{Likelihood to List}}, 1, col)
      )
    )
  )),
  {_sold_range(sold_row, weeks=sold_weeks)}
)+INDEX(${{Private Home Sales - Model}}:${{Private Home Sales - Model}}, 1, COLUMN()))"""


def revenue_model_formula(*, sold_row: int, retention_row: int, sold_weeks: int) -> str:
    sold_rng = _sold_range(sold_row, weeks=sold_weeks)
    ret_rng = _retention_range(retention_row, weeks=sold_weeks)
    return f"""=(SUMPRODUCT(
  MAP(SEQUENCE(1,{sold_weeks}), LAMBDA(lag,
    LET(
      col, COLUMN() - lag - {FINANCED_CLOSE_LAG_CELL},
      IF(col < 2, 160*356000,
        IF(INDEX(${{New Listings}}:${{New Listings}}, 1, col) = "",
          INDEX(${{New Listings - Model}}:${{New Listings - Model}}, 1, col),
          INDEX(${{New Listings}}:${{New Listings}}, 1, col)
        )*INDEX(${{Average Sale Price (homes sold by OPEN)}}:${{Average Sale Price (homes sold by OPEN)}}, 1, col)
      )
    )
  )),
  {sold_rng},
  {ret_rng}
)*{CASH_PURCHASE_PCT_CELL}+
 SUMPRODUCT(
  MAP(SEQUENCE(1,{sold_weeks}), LAMBDA(lag,
    LET(
      col, COLUMN() - lag - {CASH_CLOSE_LAG_CELL},
      IF(col < 2, 160*356000,
        IF(INDEX(${{New Listings}}:${{New Listings}}, 1, col) = "",
          INDEX(${{New Listings - Model}}:${{New Listings - Model}}, 1, col),
          INDEX(${{New Listings}}:${{New Listings}}, 1, col)
        )*INDEX(${{Average Sale Price (homes sold by OPEN)}}:${{Average Sale Price (homes sold by OPEN)}}, 1, col)
      )
    )
  )),
  {sold_rng},
  {ret_rng}
)*(1-{CASH_PURCHASE_PCT_CELL})+INDEX(${{Private Home Sales - Model}}:${{Private Home Sales - Model}}, 1, COLUMN())*INDEX(${{Average Sale Price (homes sold by OPEN)}}:${{Average Sale Price (homes sold by OPEN)}}, 1, COLUMN()))"""
