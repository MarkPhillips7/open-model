"""Shares tab: dated dilution events for EOSE fully-diluted share path."""

from __future__ import annotations

SHARES_SHEET = "Shares"

SHARES_SHEET_GRID: list[list] = [
    ["Share count — events"],
    [
        "Fully diluted shares - Model on Quarterly Financials = last reported actual "
        "plus the sum of Share Δ (million) for events whose Date falls in that quarter. "
        "Leave Fraction at 0 to park a known convert/warrant without assuming conversion."
    ],
    [],
    [
        "Event",
        "Date",
        "Share Δ (million)",
        "Fraction",
        "Notes",
    ],
    [
        "Nov 2025 convert + registered direct offering",
        "11/15/2025",
        0,
        0,
        "$600M convert + equity (YE 2025 cash $625M). Set Δ when the 10-K share count is split out.",
    ],
    [
        "2026 Q1 diluted (warrants / converts in-the-money)",
        "3/31/2026",
        0,
        0,
        "Q1 2026 10-Q: ~339.5M basic, ~544.8M diluted. Actuals row already has the print; "
        "do not double-count here unless you clear the Actual cell.",
    ],
    [
        "Future convert / warrant exercise (placeholder)",
        "12/31/2030",
        0,
        0,
        "Raise Fraction / Δ to model incremental dilution after the last actual.",
    ],
]

SHARES_EVENT_TABLE = f"{SHARES_SHEET}!$B$5:$C$20"
