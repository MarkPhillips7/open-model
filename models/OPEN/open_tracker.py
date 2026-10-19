"""Open Tracker (aubermark.github.io/open-tracker) weekly New Listings.

The Cohort Sell-Through table uses Sunday week-ending dates. Weekly Financials
uses Saturday week-ending dates, so each tracker Sunday maps to Saturday − 1 day.
PARTIAL (in-progress) weeks are skipped; CATCH-UP and complete weeks are kept.

Daily delistings (P. Sold) are a provisional stand-in for Home Sales on
new-quarter days before Accountable posts its next-quarter chart. Recent days
run high until relists are netted out, so each day keeps only the share its
week is still expected to lose before settling.
"""

from __future__ import annotations

import json
import re
import statistics
from datetime import date, datetime, timedelta
from typing import Any
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

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


_WEEKLY_SOLD_MARKER = "const weeklySoldData = "
_NEW_VS_REMOVED_MARKER = "const newVsRemovedData = "
# The tracker's business dates are midnight in its own timezone, sent as UTC.
_TRACKER_TZ = ZoneInfo("Europe/Madrid")
# Weeks this recent have not had time for relists to be netted out.
SETTLE_WEEKS = 4
RELIST_SAMPLE_WEEKS = 12


def _js_array(html: str, marker: str) -> list[dict[str, Any]]:
    at = html.find(marker)
    if at < 0:
        raise ValueError(f"Open Tracker {marker.split()[1]} not found")
    rows, _ = json.JSONDecoder().raw_decode(html, at + len(marker))
    return rows


def extract_daily_removed(html: str) -> dict[date, int]:
    """Daily P. Sold net of relists so far, from cumulative permanent delistings.

    Recent days equal the Daily Summary's Houses P. Sold; older days shrink as
    relisted homes are taken back out.
    """
    daily: dict[date, int] = {}
    prev: int | None = None
    for row in _js_array(html, _NEW_VS_REMOVED_MARKER):
        stamp = datetime.fromisoformat(row["business_date"].replace("Z", "+00:00"))
        day = stamp.astimezone(_TRACKER_TZ).date()
        cumulative = int(row["cumulative_removed"])
        if prev is not None:
            daily[day] = cumulative - prev
        prev = cumulative
    if not daily:
        raise ValueError("Open Tracker newVsRemovedData had no daily rows")
    return daily


def relist_factors(html: str) -> tuple[float, dict[date, float]]:
    """(settled relist rate, Mon–Sun week-end Sunday → remaining multiplier).

    Settled rate is the median `noise_pct` over recent settled weeks. A newer
    week that has already netted out `n` keeps (1 − settled) / (1 − n) of its
    current count, so partly corrected days are not discounted twice.
    """
    rows = sorted(_js_array(html, _WEEKLY_SOLD_MARKER), key=lambda r: r["week_end"])
    settled_rows = rows[:-SETTLE_WEEKS][-RELIST_SAMPLE_WEEKS:]
    rates = [float(r["noise_pct"]) / 100 for r in settled_rows if r.get("noise_pct") is not None]
    if not rates:
        raise ValueError("Open Tracker weeklySoldData has no settled weeks")
    settled = statistics.median(rates)
    factors: dict[date, float] = {}
    for row in rows[-SETTLE_WEEKS:]:
        netted = float(row.get("noise_pct") or 0) / 100
        factors[date.fromisoformat(row["week_end"])] = min(
            1.0, (1 - settled) / (1 - netted)
        )
    return settled, factors


def remaining_factor(day: date, settled: float, factors: dict[date, float]) -> float:
    """Multiplier for a day's net count; weeks not in `factors` get the full discount."""
    sunday = day + timedelta(days=(6 - day.weekday()) % 7)
    if sunday in factors:
        return factors[sunday]
    if factors and sunday < min(factors):
        return 1.0
    return 1 - settled


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
