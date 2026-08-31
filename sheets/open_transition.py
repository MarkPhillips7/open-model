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
    0,
    0.02,
    0.06,
    0.12,
    0.18,
    0.22,
    0.2,
    0.13,
    0.07,
]

# ~51% cumulative sell-through by week 17; tail extended to week 39 (sums to 100%).
OPEN_1_0_WEEKLY_SOLD: list[float] = [
    0.047,
    0.0376,
    0.030080000000000003,
    0.0282752,
    0.027992448,
    0.02771252352,
    0.0274353982848,
    0.027161044301952,
    0.02688943385893248,
    0.026620539520343156,
    0.026354334125139725,
    0.02609079078388833,
    0.025829882876049443,
    0.02557158404728895,
    0.02531586820681606,
    0.025062709524747897,
    0.024812082429500417,
    0.024688022017352915,
    0.02456458190726615,
    0.02444175899772982,
    0.02431955020274117,
    0.024197952451727463,
    0.024076962689468826,
    0.02395657787602148,
    0.023836794986641374,
    0.02371761101170817,
    0.02359902295664963,
    0.02348102784186638,
    0.023363622702657048,
    0.02324680458914376,
    0.023130570566198043,
    0.023014917713367052,
    0.02289984312480022,
    0.022785343909176217,
    0.022671417189630335,
    0.022558060103682182,
    0.022445269803163772,
    0.022333043454147952,
    0.020546399977816116,
]

OPEN_1_0_WEEKLY_SOLD_MULTIPLIERS: list[float | None] = [
    None,
    0.8,
    0.8,
    0.94,
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
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.995,
    0.92,
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


def private_home_sales_model_formula(*, lag_row: int = OPEN_1_0_LISTING_ROW) -> str:
    """Non-listed share of purchases, lagged on the 1.0 purchase→listing timing curve."""
    return f"""=(SUMPRODUCT(
  MAP(SEQUENCE(1,9), LAMBDA(lag,
    LET(
      col, COLUMN() - lag,
      IF(col < 2, 15,
        IF(INDEX(${{Homes Purchased}}:${{Homes Purchased}}, 1, col) = "",
          INDEX(${{Homes Purchased - Model}}:${{Homes Purchased - Model}}, 1, col),
          INDEX(${{Homes Purchased}}:${{Homes Purchased}}, 1, col)
        )*(1-INDEX(${{Likelihood to List}}:${{Likelihood to List}}, 1, col))
      )
    )
  )),
  {_listing_range(lag_row)}
))"""


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
)*{CASH_PURCHASE_PCT_CELL}+
 SUMPRODUCT(
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
)*(1-{CASH_PURCHASE_PCT_CELL})+INDEX(${{Private Home Sales - Model}}:${{Private Home Sales - Model}}, 1, COLUMN())*INDEX(${{Average Sale Price (homes sold by OPEN)}}:${{Average Sale Price (homes sold by OPEN)}}, 1, COLUMN()))"""
