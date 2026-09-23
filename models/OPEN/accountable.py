"""Accountable (accountable.opendoor.com) weekly actuals for the OPEN model.

Resale COEs on Accountable are cumulative quarter-to-date closings. Weekly
**Home Sales** is the week-over-week change in that series, starting the first
Q3 2026 week-ending date (2026-07-04).

**Acquisition Contracts** are the weekly `actual` series on the same page
(Saturday week-ending dates, matching Weekly Financials).
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from typing import Any
from urllib.request import Request, urlopen

ACCOUNTABLE_URL = "https://accountable.opendoor.com/"
RESALE_COES_TITLE = "Resale COEs"
HOME_SALES_LABEL = "Home Sales"
ACQUISITION_CONTRACTS_LABEL = "Acquisition Contracts"
# First Saturday week-ending in Q3 2026 — Accountable Q3 COE chart starts here.
HOME_SALES_ACCOUNTABLE_START = date(2026, 7, 4)

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
_NEXT_F_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:\\.|[^"\\])*)"\]\)')
_AS_OF_RE = re.compile(r"Data as of ([A-Za-z]{3} \d{1,2}, \d{4})")
# Acquisition chart rows look like {"date":"2026-09-19","actual":444,"proposedLow":...}
_ACQUISITION_ROW_RE = re.compile(
    r'\{"date":"(\d{4}-\d{2}-\d{2})","actual":(null|\d+),'
)


def sheet_date(value: Any) -> date | None:
    """Parse a Weekly Financials header cell (Sheets serial, datetime, or ISO)."""
    if value in ("", None):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return date(1899, 12, 30) + timedelta(days=int(value))
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def is_quarterly_spread_formula(cell: Any) -> bool:
    text = str(cell) if cell is not None else ""
    return text.startswith("=") and "Quarterly Financials" in text


def weekly_from_cumulative(
    points: list[tuple[date, int | float | None]],
) -> dict[date, int]:
    """Turn QTD cumulative COEs into weekly home-sale counts."""
    weekly: dict[date, int] = {}
    prev = 0
    for week_ending, value in points:
        if value is None:
            continue
        count = int(round(float(value) - prev))
        weekly[week_ending] = count
        prev = float(value)
    return weekly


def _unescape_next_f(payload: str) -> str:
    return payload.encode("utf-8").decode("unicode_escape")


def parse_rsc_text(html: str) -> str:
    parts = [_unescape_next_f(m.group(1)) for m in _NEXT_F_RE.finditer(html)]
    if not parts:
        raise ValueError("No Next.js RSC payload found on Accountable page")
    return "\n".join(parts)


def extract_resale_coe_points(rsc_text: str) -> list[tuple[date, int | float | None]]:
    marker = f'"title":"{RESALE_COES_TITLE}"'
    title_at = rsc_text.find(marker)
    if title_at < 0:
        raise ValueError(f"{RESALE_COES_TITLE!r} chart not found in Accountable RSC payload")
    points_at = rsc_text.find('"points":', title_at)
    if points_at < 0 or points_at - title_at > 5000:
        raise ValueError(f"{RESALE_COES_TITLE} chart has no points array")
    decoder = json.JSONDecoder()
    raw, _ = decoder.raw_decode(rsc_text, points_at + len('"points":'))
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{RESALE_COES_TITLE} points array is empty")
    out: list[tuple[date, int | float | None]] = []
    for row in raw:
        if not isinstance(row, dict) or "date" not in row:
            continue
        week = sheet_date(row["date"])
        if week is None:
            continue
        value = row.get("value")
        out.append((week, None if value is None else value))
    if not out:
        raise ValueError(f"{RESALE_COES_TITLE} points had no dated rows")
    return out


def parse_as_of(html: str) -> str | None:
    match = _AS_OF_RE.search(html)
    return match.group(1) if match else None


def fetch_accountable_html(url: str = ACCOUNTABLE_URL) -> str:
    request = Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def fetch_weekly_home_sales(
    *,
    html: str | None = None,
) -> tuple[dict[date, int], list[tuple[date, int | float | None]], str | None]:
    """Return (weekly counts, cumulative points, as-of label)."""
    page = html if html is not None else fetch_accountable_html()
    points = extract_resale_coe_points(parse_rsc_text(page))
    return weekly_from_cumulative(points), points, parse_as_of(page)


def extract_acquisition_contracts(rsc_text: str) -> dict[date, int]:
    """Parse weekly Acquisition Contracts `actual` values (skip null future weeks)."""
    # Prefer the longest contiguous run of {"date","actual",...} objects — that is
    # the contracts chart (Resale COEs use "value", not "actual").
    best: list[tuple[date, int]] = []
    for match in re.finditer(r'\[\{"date":"\d{4}-\d{2}-\d{2}","actual":', rsc_text):
        try:
            raw, _ = json.JSONDecoder().raw_decode(rsc_text, match.start())
        except json.JSONDecodeError:
            continue
        if not isinstance(raw, list) or not raw:
            continue
        if not isinstance(raw[0], dict) or "actual" not in raw[0]:
            continue
        rows: list[tuple[date, int]] = []
        for row in raw:
            if not isinstance(row, dict):
                continue
            week = sheet_date(row.get("date"))
            actual = row.get("actual")
            if week is None or actual is None:
                continue
            rows.append((week, int(actual)))
        if len(rows) > len(best):
            best = rows
    if not best:
        # Fallback: regex scan if JSON array boundaries shift.
        rows = []
        for m in _ACQUISITION_ROW_RE.finditer(rsc_text):
            if m.group(2) == "null":
                continue
            week = sheet_date(m.group(1))
            if week is not None:
                rows.append((week, int(m.group(2))))
        best = rows
    if not best:
        raise ValueError("Acquisition Contracts actual series not found in Accountable RSC")
    return dict(best)


def fetch_acquisition_contracts(
    *,
    html: str | None = None,
) -> tuple[dict[date, int], str | None]:
    """Return (week_ending → contract count, as-of label)."""
    page = html if html is not None else fetch_accountable_html()
    return extract_acquisition_contracts(parse_rsc_text(page)), parse_as_of(page)


def snapshot_payload(
    weekly: dict[date, int],
    cumulative: list[tuple[date, int | float | None]],
    *,
    as_of: str | None,
) -> dict[str, Any]:
    return {
        "source": ACCOUNTABLE_URL,
        "metric": "Resale COEs (cumulative QTD) → weekly Home Sales",
        "as_of": as_of,
        "weekly_start": HOME_SALES_ACCOUNTABLE_START.isoformat(),
        "cumulative": [
            {"date": week.isoformat(), "value": value} for week, value in cumulative
        ],
        "weekly": {week.isoformat(): count for week, count in weekly.items()},
    }


def acquisition_snapshot_payload(
    weekly: dict[date, int],
    *,
    as_of: str | None,
) -> dict[str, Any]:
    return {
        "source": ACCOUNTABLE_URL,
        "metric": "Acquisition Contracts (weekly actual)",
        "as_of": as_of,
        "weekly": {week.isoformat(): count for week, count in sorted(weekly.items())},
    }
