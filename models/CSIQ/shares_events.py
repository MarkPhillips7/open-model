"""Share-count events worth having on one page. The quarterly share row does not read this tab."""

from __future__ import annotations

SHARES_SHEET = "Shares"

HEADER = ["Date", "Event", "Shares or dollars", "Notes"]
COL_WIDTHS_PX: dict[int, int] = {0: 140, 1: 280, 2: 220, 3: 780}

EVENTS: list[tuple[str, str, str, str]] = [
    (
        "2025-06-30",
        "Basic weighted-average shares",
        "67.167M",
        "Q2 2025 earnings release, as reprinted in the Q2 2026 comparative.",
    ),
    (
        "2025-12-31",
        "Convertible notes",
        "$195M carrying value",
        "Balance sheet in the Q2 2026 release. Common share count barely moved through this period.",
    ),
    (
        "2025-12-01",
        "CS PowerTech formed",
        "CSIQ holds 75.1%",
        "Not a CSIQ share issuance. It changes who owns the US factories. CSI Solar holds the other 24.9%.",
    ),
    (
        "2026-03-31",
        "Convertible notes issued",
        "$223M net proceeds",
        "Q1 2026 cash flow. Quarter-end carrying value was described as about $0.4B, not typed as an exact actual.",
    ),
    (
        "2026-03-31",
        "Basic weighted-average shares",
        "67.818M",
        "Q1 2026. Dilution of the common is small next to the convert.",
    ),
    (
        "2026-06-30",
        "Basic weighted-average shares",
        "67.908M",
        "Q2 2026. This is the share count the primary price uses.",
    ),
    (
        "2026-06-30",
        "Convertible notes",
        "$420M carrying value",
        "Subtracted in the basic-share equity value. Added back on the diluted-price row.",
    ),
    (
        "2026-04-28",
        "Thesis diluted count",
        "about 90M",
        "Lucas Sacerdote's fully diluted shares, the denominator of his $100. A lever, not a filing.",
    ),
]


def grid() -> list[list[str]]:
    return [list(HEADER), *([list(row) for row in EVENTS])]
