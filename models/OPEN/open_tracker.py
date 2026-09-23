"""Open Tracker (aubermark.github.io/open-tracker) weekly New Listings.

The Cohort Sell-Through table uses Sunday week-ending dates. Weekly Financials
uses Saturday week-ending dates, so each tracker Sunday maps to Saturday − 1 day.
PARTIAL (in-progress) weeks are skipped; CATCH-UP and complete weeks are kept.
"""

from __future__ import annotations

import re
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
