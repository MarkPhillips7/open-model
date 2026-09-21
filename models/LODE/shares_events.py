"""Shares tab: dated dilution events for LODE.

Comstock has funded itself almost entirely with equity, and the share count is the
main thing that has destroyed per-share value historically. So dilution gets its own
tab rather than living inside a growth rate.

The default ``Shares outstanding - Model`` crawl on Quarterly Financials is a ~1%
per quarter drip for vesting stock compensation and routine at-the-market use. That
is the model's most optimistic assumption, given the company raised $34.5M in one
quarter and $61.0M in another. If you expect a specific offering, add a dated row
here and set the Quarterly Financials actual for that quarter, rather than editing
the formula.

History for context (all post the 1-for-10 reverse split of 2025-02-24):

    2025 Q1   26.90M shares    $0.0M raised
    2025 Q2   32.42M shares    $1.5M raised
    2025 Q3   51.26M shares   $34.5M raised
    2025 Q4   51.85M shares    $2.2M raised
    2026 Q1   74.10M shares   $61.0M raised
    2026 Q2   75.95M shares    $0.0M raised

That is 26.90M to 75.95M shares — a 2.8x increase — in five quarters.
"""

from __future__ import annotations

SHARES_SHEET = "Shares"

HEADER = ["Date", "Event", "Shares (M)", "Gross proceeds ($M)", "Notes"]
COL_WIDTHS_PX: dict[int, int] = {0: 110, 1: 300, 2: 110, 3: 150, 4: 700}

# (date, event, shares_m, gross_proceeds_m, notes)
# Historical rows are reported facts. Leave the forward section empty until an
# offering is actually announced — a placeholder raise is a forecast, not a fact.
EVENTS: list[tuple[str, str, object, object, str]] = [
    (
        "2025-02-24",
        "1-for-10 reverse stock split",
        "",
        "",
        "Every share figure in this workbook is on the post-split basis. The Quarterly Financials "
        "spine starts at 2025 Q1, after the split, so no adjustment is applied anywhere.",
    ),
    (
        "2025-03-31",
        "Shares outstanding (reported)",
        26.90,
        "",
        "Period-end shares issued and outstanding per the 10-Q. Not the weighted average.",
    ),
    (
        "2025-06-30",
        "Shares outstanding (reported)",
        32.42,
        1.50,
        "Proceeds are the quarter's reported gross issuance of common stock.",
    ),
    (
        "2025-09-30",
        "Shares outstanding (reported)",
        51.26,
        34.50,
        "Large capitalisation round. Management framed 2025 as the year it fixed being "
        "'undercapitalized' once and for all.",
    ),
    (
        "2025-12-31",
        "Shares outstanding (reported)",
        51.85,
        2.22,
        "",
    ),
    (
        "2026-03-31",
        "Shares outstanding (reported)",
        74.10,
        60.98,
        "Second large round, raised to accelerate the metals buildout and to increase the SSOF "
        "position ahead of monetisation.",
    ),
    (
        "2026-06-30",
        "Shares outstanding (reported)",
        75.95,
        0.00,
        "Latest reported count. This is the anchor the model's dilution drip starts from.",
    ),
]

NOTE = (
    "Reported period-end share counts and gross equity proceeds. To model a future offering, add a "
    "dated row below and enter the resulting share count as the 'Shares outstanding' actual for that "
    "quarter on Quarterly Financials — the Model row will pick it up automatically. The model "
    "deliberately assumes no future raise, so that a negative Cash - Model reads as the funding gap "
    "that still has to be closed."
)


def grid() -> list[list[object]]:
    return [list(HEADER)] + [list(row) for row in EVENTS]
