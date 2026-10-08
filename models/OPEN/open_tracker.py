"""Open Tracker (aubermark.github.io/open-tracker) weekly New Listings.

The Cohort Sell-Through table uses Sunday week-ending dates. Weekly Financials
uses Saturday week-ending dates, so each tracker Sunday maps to Saturday − 1 day.
PARTIAL (in-progress) weeks are skipped; CATCH-UP and complete weeks are kept.

Daily **Houses P. Sold** (delistings) is a provisional stand-in for Home Sales on
new-quarter days before Accountable posts its next-quarter chart. Raw daily
counts run high until relists are netted out, so they are discounted by the
typical relist rate of settled weeks.
"""

from __future__ import annotations

import json
import re
import statistics
from datetime import date, datetime, timedelta
from typing import Any
from urllib.request import Request, urlopen

OPEN_TRACKER_URL = "https://aubermark.github.io/open-tracker/"
NEW_LISTINGS_LABEL = "New Listings"

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
_LAST_UPDATE_RE = re.compile(
    r"Last update</[^>]*>\s*<[^>]+>([^<]+)",
    re.IGNORECASE,
)
# Cohort table row: Sunday week-ending date, active listings, new listed count.
_COHORT_ROW_RE = re.compile(
    r'<td class="date-cell"[^>]*>\s*'
    r"(?P<date>\d{4}-\d{2}-\d{2})"
    r"(?P<meta>.*?)</td>\s*"
    r'<td class="num-cell"[^>]*>.*?</td>\s*'
    r'<td class="num-cell"[^>]*>\s*(?:<[^>]+>)?(?P<listed>\d+)',
    re.IGNORECASE | re.DOTALL,
)


def fetch_open_tracker_html(url: str = OPEN_TRACKER_URL) -> str:
    request = Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def parse_last_update(html: str) -> str | None:
    match = _LAST_UPDATE_RE.search(html)
    return match.group(1).strip() if match else None


def _sunday_to_sheet_saturday(sunday: date) -> date:
    """Tracker cohort 'Week Ending' Sundays → Weekly Financials Saturday spine."""
    return sunday - timedelta(days=1)


def extract_weekly_new_listings(html: str) -> dict[date, int]:
    """Parse Cohort Sell-Through Listed counts → Saturday week-ending dict.

    Trailing PARTIAL (in-progress) weeks are skipped. Older PARTIAL / CATCH-UP
    weeks are kept — Open Tracker marks scraper-gap weeks as PARTIAL even after
    they close (e.g. the 5-listing week ending 2026-09-06).
    """
    start = html.find("Cohort Sell-Through")
    section = html[start:] if start >= 0 else html
    end = section.find("LISTINGS/ACQUISITIONS")
    if end > 0:
        section = section[:end]

    rows: list[tuple[date, int, bool]] = []
    for match in _COHORT_ROW_RE.finditer(section):
        meta = match.group("meta") or ""
        partial = bool(re.search(r"PARTIAL", meta, re.IGNORECASE))
        sunday = datetime.strptime(match.group("date"), "%Y-%m-%d").date()
        listed = int(match.group("listed"))
        rows.append((_sunday_to_sheet_saturday(sunday), listed, partial))
    if not rows:
        raise ValueError("Open Tracker cohort table had no Listed weeks")

    # Drop only the newest trailing PARTIAL week(s) still in progress.
    rows.sort(key=lambda r: r[0])
    while rows and rows[-1][2]:
        rows.pop()

    weekly = {week: listed for week, listed, _partial in rows}
    if not weekly:
        raise ValueError("Open Tracker cohort table had no completed Listed weeks")
    return weekly


_DAILY_ROW_RE = re.compile(
    r'<td class="date-cell"[^>]*>\s*(\d{2}/\d{2}/\d{4})\s*</td>(.*?)</tr>',
    re.DOTALL,
)
_CELL_RE = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL)
_WEEKLY_SOLD_MARKER = "const weeklySoldData = "
# Weeks this recent have not had time for relists to be netted out.
SETTLE_WEEKS = 4
RELIST_SAMPLE_WEEKS = 12


def _cell_text(raw: str) -> str:
    return re.sub(r"<[^>]+>|\s+", " ", raw).strip()


def extract_daily_p_sold(html: str) -> dict[date, int]:
    """Daily Summary 'Houses P. Sold' by calendar day (blank days skipped)."""
    first = _DAILY_ROW_RE.search(html)
    if not first:
        raise ValueError("Open Tracker Daily Summary rows not found")
    thead_at = html.rfind("<thead", 0, first.start())
    headers = [_cell_text(c) for c in _CELL_RE.findall(html[thead_at:first.start()])]
    try:
        col = headers.index("Houses P. Sold") - 1  # minus the Date column
    except ValueError as exc:
        raise ValueError(f"Daily Summary has no 'Houses P. Sold' column: {headers}") from exc

    daily: dict[date, int] = {}
    for match in _DAILY_ROW_RE.finditer(html):
        cells = [_cell_text(c) for c in _CELL_RE.findall(match.group(2))]
        if col >= len(cells) or not cells[col].replace(",", "").isdigit():
            continue
        day = datetime.strptime(match.group(1), "%d/%m/%Y").date()
        daily[day] = int(cells[col].replace(",", ""))
    return daily


def settled_relist_rate(html: str) -> float:
    """Median share of P. Sold later relisted, over recent settled weeks."""
    at = html.find(_WEEKLY_SOLD_MARKER)
    if at < 0:
        raise ValueError("Open Tracker weeklySoldData not found")
    rows, _ = json.JSONDecoder().raw_decode(html, at + len(_WEEKLY_SOLD_MARKER))
    rows = sorted(rows, key=lambda r: r["week_end"])
    settled = rows[:-SETTLE_WEEKS][-RELIST_SAMPLE_WEEKS:]
    rates = [float(r["noise_pct"]) / 100 for r in settled if r.get("noise_pct") is not None]
    if not rates:
        raise ValueError("Open Tracker weeklySoldData has no settled weeks")
    return statistics.median(rates)


def fetch_weekly_new_listings(
    *,
    html: str | None = None,
) -> tuple[dict[date, int], str | None]:
    """Return (Saturday week_ending → new listings, last-update label)."""
    page = html if html is not None else fetch_open_tracker_html()
    return extract_weekly_new_listings(page), parse_last_update(page)


def listings_snapshot_payload(
    weekly: dict[date, int],
    *,
    last_update: str | None,
) -> dict[str, Any]:
    return {
        "source": OPEN_TRACKER_URL,
        "metric": "New Listings (Cohort Sell-Through Listed → Saturday week-ending)",
        "last_update": last_update,
        "weekly": {week.isoformat(): count for week, count in sorted(weekly.items())},
    }
