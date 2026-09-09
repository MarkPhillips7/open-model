"""Reported quarterly actuals for EOSE (10-Q / earnings releases).

Values are native to the Quarterly Financials row units ($M unless noted).
Blank keys are omitted — the sheet leaves those Actual cells empty.
"""

from __future__ import annotations

# (year, quarter) → {label: value}
ACTUALS: dict[tuple[int, int], dict[str, float]] = {
    (2025, 1): {
        "Revenue": 10.457,
        "COGS": 34.996,
        "Gross profit": -24.539,
        "SG&A": 20.995,
        "R&D": 6.837,
        "OpEx": 28.393,
        "Adjusted EBITDA": -43.3,  # residual from 9M'25 − Q2 − Q3; see RESOURCES
        "Cash": 111.694,
    },
    (2025, 2): {
        "Revenue": 15.236,
        "COGS": 46.189,
        "Gross profit": -30.953,
        "SG&A": 25.488,
        "R&D": 7.201,
        "OpEx": 32.894,
        "Adjusted EBITDA": -51.6,
        "GAAP net income": -222.937,
    },
    (2025, 3): {
        "Revenue": 30.512,
        "COGS": 64.437,
        "Gross profit": -33.925,
        "SG&A": 20.375,  # Q3 opex $27.3M − R&D $6.925M
        "R&D": 6.925,
        "OpEx": 27.3,
        "Adjusted EBITDA": -52.690,
        "GAAP net income": -641.4,
        "Cash": 126.8,
        "Pipeline": 22.6,
        "Pipeline (GWh)": 91,
        "Backlog": 644.4,
        "Backlog (GWh)": 2.5,
        "Fully diluted shares": 271.618,
        "Long term debt": 330.407,
    },
    (2025, 4): {
        "Revenue": 57.998,
        "COGS": 112.418,
        "Gross profit": -54.420,
        "Adjusted EBITDA": -71.536,
        "GAAP net income": -120.5,
        "Cash": 624.566,
        "Pipeline": 23.6,
        "Pipeline (GWh)": 99,
        "Booked orders": 240,  # disclosed Q4 bookings, not the implied identity
        "Backlog": 701.5,
        "Backlog (GWh)": 2.8,
    },
    (2026, 1): {
        "Revenue": 56.963,
        "COGS": 101.390,
        "Gross profit": -44.427,
        "SG&A": 24.095,
        "R&D": 10.719,
        "OpEx": 34.885,
        "Adjusted EBITDA": -68.0,
        "GAAP net income": 508.883,  # FV marks; not operating earnings
        "Cash": 472.368,
        "Pipeline": 24.3,
        "Booked orders": 0.1,  # implied: Δbacklog + revenue ≈ 0
        "Backlog": 644.6,
        "Backlog (GWh)": 2.6,
        "Basic shares": 339.514,
        "Fully diluted shares": 544.829,
        "Z3 manufacturing lines": 1,
    },
    (2026, 2): {
        "Revenue": 68.775,
        "COGS": 117.576,
        "Gross profit": -48.801,
        "SG&A": 24.500,
        "R&D": 10.505,
        "OpEx": 35.010,
        "Adjusted EBITDA": -71.4,
        "GAAP net income": -275.710,
        "Cash": 364.1,
        "Pipeline": 24.6,
        "Pipeline (GWh)": 112,
        "Booked orders": 231.2,  # implied: 807 − 644.6 + 68.8
        "Backlog": 807,
        "Backlog (GWh)": 3.4,
        "Z3 manufacturing lines": 2,  # Line 2 commercial production mid-June 2026
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
}
