"""Reported quarterly actuals for EOSE (10-Q / earnings releases).

Values are native to the Quarterly Financials row units ($M unless noted).
Blank keys are omitted — the sheet leaves those Actual cells empty.

GAAP lines: SEC companyfacts / 10-Q / 10-K (see sources.py).
Adj. EBITDA, pipeline, backlog, booked orders: earnings 8-K Ex. 99.1.
Pipeline GWh: earnings slides or transcript when the release omits GWh.

Reload the live sheet with::

    python models/EOSE/scripts/load_quarterly_actuals.py
"""

from __future__ import annotations

# (year, quarter) → {label: value}
ACTUALS: dict[tuple[int, int], dict[str, float]] = {
    (2025, 1): {
        "Pipeline": 15.6,
        "Pipeline (GWh)": 60,
        "Booked orders": 9.2,  # Q1 slides
        "Backlog": 680.9,
        "Backlog (GWh)": 2.6,
        "Z3 manufacturing lines": 1,
        "Revenue": 10.457,
        "COGS": 34.996,
        "Gross profit": -24.539,
        "SG&A": 20.995,
        "R&D": 6.837,
        "OpEx": 28.393,  # incl. $0.561M PP&E write-down
        "Adjusted EBITDA": -43.238,
        "GAAP net income": 15.136,  # FV marks; not operating
        "Cash": 111.694,
        "Long term debt": 66.215,  # 10-Q "Long-term debt" line
        "Total debt": 325.514,  # all borrowings carrying value
        "Basic shares": 225.474,
        "Fully diluted shares": 436.368,  # dilutive WAS (GAAP profit quarter)
    },
    (2025, 2): {
        "Pipeline": 18.8,
        "Pipeline (GWh)": 77,
        "Booked orders": 6.9,  # Q2 slides
        "Backlog": 672.5,
        "Backlog (GWh)": 2.6,
        "Z3 manufacturing lines": 1,
        "Revenue": 15.236,
        "COGS": 46.189,
        "Gross profit": -30.953,
        "Adjusted gross profit": -27.818,
        "SG&A": 25.488,
        "R&D": 7.201,
        "OpEx": 32.894,
        "Adjusted EBITDA": -51.626,
        "GAAP net income": -222.937,
        "Cash": 183.175,
        "Long term debt": 307.274,
        "Total debt": 445.277,
        "Basic shares": 237.741,
        "Fully diluted shares": 237.741,  # loss quarter; diluted = basic
    },
    (2025, 3): {
        "Pipeline": 22.6,
        "Pipeline (GWh)": 91,
        "Backlog": 644.4,
        "Backlog (GWh)": 2.5,
        "Z3 manufacturing lines": 1,
        "Revenue": 30.512,
        "COGS": 64.437,
        "Gross profit": -33.925,
        "Adjusted gross profit": -30.408,
        "SG&A": 19.786,
        "R&D": 6.925,
        "OpEx": 27.296,
        "Adjusted EBITDA": -52.690,
        "GAAP net income": -641.393,
        "Cash": 126.799,
        "Long term debt": 330.407,
        "Total debt": 448.455,
        "Basic shares": 271.618,
        "Fully diluted shares": 271.618,
    },
    (2025, 4): {
        "Pipeline": 23.6,
        "Pipeline (GWh)": 99,  # Q4 2025 earnings call
        "Booked orders": 240,  # disclosed Q4 bookings (~1.1 GWh)
        "Backlog": 701.5,
        "Backlog (GWh)": 2.8,
        "Z3 manufacturing lines": 1,
        "Revenue": 57.998,
        "COGS": 112.418,
        "Gross profit": -54.420,
        "Adjusted gross profit": -49.132,
        "SG&A": 18.841,
        "R&D": 7.579,
        "OpEx": 26.850,
        "Adjusted EBITDA": -71.536,
        "GAAP net income": -120.453,
        "Cash": 624.566,
        "Long term debt": 662.467,
        "Total debt": 813.266,
        "Basic shares": 307.664,
        "Fully diluted shares": 307.664,
    },
    (2026, 1): {
        "Pipeline": 24.3,
        "Pipeline (GWh)": 107,  # Q1 2026 earnings call
        "Booked orders": 0.1,  # implied: Δbacklog + revenue; not disclosed
        "Backlog": 644.6,
        "Backlog (GWh)": 2.6,
        "Z3 manufacturing lines": 1,
        "Revenue": 56.963,
        "COGS": 101.390,
        "Gross profit": -44.427,
        "Adjusted gross profit": -39.040,
        "SG&A": 24.095,
        "R&D": 10.719,
        "OpEx": 34.885,
        "Adjusted EBITDA": -68.019,
        "GAAP net income": 508.883,  # FV marks; not operating earnings
        "Cash": 472.368,
        "Long term debt": 506.399,
        "Total debt": 619.519,
        "Basic shares": 339.602,
        "Fully diluted shares": 544.829,  # if-converted WAS (GAAP profit quarter)
        "MWh shipped": 265,
    },
    (2026, 2): {
        "Pipeline": 24.6,
        "Pipeline (GWh)": 112,  # Q2 2026 earnings call ("nearly 112")
        "Booked orders": 231.2,  # implied: 807 − 644.6 + 68.8; 6 customers
        "Backlog": 807,
        "Backlog (GWh)": 3.4,
        "Z3 manufacturing lines": 2,  # Line 2 commercial production mid-June 2026
        "Revenue": 68.775,
        "COGS": 117.576,
        "Gross profit": -48.801,
        "Adjusted gross profit": -42.869,
        "SG&A": 24.500,
        "R&D": 10.505,
        "OpEx": 35.010,
        "Adjusted EBITDA": -71.355,
        "GAAP net income": -275.710,
        "Cash": 364.070,
        "Long term debt": 453.835,
        "Total debt": 617.118,
        "Basic shares": 339.799,
        "MWh shipped": 307.6,
        # Fully diluted shares omitted: GAAP diluted WAS = basic in a loss quarter.
        # Leaving blank keeps Fully diluted shares - Model on Q1's 544.8 if-converted.
    },
}

# Column-C scalars (not a time series). Column B is units only.
SCALARS: dict[str, float | str] = {
    "As of date": "2026-09-09",
    "Cycle time floor": 10,
    "Capex per incremental line": 40,
    "Net interest run-rate": 12,
    "FY 2026 revenue guidance — low": 300,
    "FY 2026 revenue guidance — high": 350,
    "Z3 modules per cube": 672,
    "Z3 Module Energy Capacity": 1.19047619,
    "Backlog conversion lag": 4,
    "EV / EBITDA": 30,
    "Discount rate": 20,
    "Pipeline quarterly growth rate": 10,
}
