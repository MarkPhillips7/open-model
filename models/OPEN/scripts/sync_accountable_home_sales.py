#!/usr/bin/env python3
"""Pull Accountable Resale COEs into Weekly Financials Home Sales.

Starting week-ending 2026-07-04, Home Sales is the week-over-week change in
the cumulative Q3 (then current-quarter) Resale COEs chart on
https://accountable.opendoor.com/. Earlier weeks stay on the quarterly ÷13
spread. Re-running update_weekly_quarterly_spread.py will not overwrite these
cells.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from models.OPEN.accountable import (  # noqa: E402
    ACCOUNTABLE_URL,
    HOME_SALES_ACCOUNTABLE_START,
    HOME_SALES_LABEL,
    fetch_weekly_home_sales,
    merge_quarter_history,
    parse_as_of_date,
    sheet_date,
    snapshot_payload,
    uncovered_new_quarter_days,
    week_ending,
)
from models.OPEN.open_tracker import (  # noqa: E402
    OPEN_TRACKER_URL,
    extract_daily_p_sold,
    fetch_open_tracker_html,
    settled_relist_rate,
)
from models.OPEN.financials_definitions import FINANCIALS_DEFINITIONS_SHEET  # noqa: E402
from models.OPEN.weekly_model_formulas import col_letter  # noqa: E402
from setup_financials_definitions import build_rows, ensure_definitions_sheet  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.labels import QUARTERLY, WEEKLY, label_rows  # noqa: E402

SNAPSHOT_PATH = PACK / "data" / "accountable_resale_coes.json"

HOME_SALES_NOTE = (
    f"From week ending {HOME_SALES_ACCOUNTABLE_START.isoformat()}, weekly Home Sales "
    f"are the week-over-week change in cumulative Resale COEs on {ACCOUNTABLE_URL} "
    "(QTD closings; later recordings stay in the then-current period). "
    "Quarter-end stub days (e.g. 9/27–9/30) roll into the next Saturday week. "
    "New-quarter days Accountable has not charted yet are filled provisionally with "
    f"Open Tracker daily Houses P. Sold × (1 − settled relist rate) from {OPEN_TRACKER_URL}; "
    "the next Accountable chart replaces them. "
    "Earlier weeks remain quarterly earnings actual ÷13 (day-weighted). "
    "Refresh with models/OPEN/scripts/sync_weekly_actuals.py "
    "(or sync_accountable_home_sales.py for Home Sales only). "
    "Do not restore quarterly spread on this row from 7/4/2026 onward."
)


def provisional_tracker_sales(
    points: list,
    as_of: str | None,
    tracker_html: str | None,
) -> dict | None:
    """Open Tracker P. Sold (relist-discounted) for new-quarter days Accountable lacks."""
    days = uncovered_new_quarter_days(points, parse_as_of_date(as_of))
    if not days:
        return None
    page = tracker_html if tracker_html is not None else fetch_open_tracker_html()
    daily = extract_daily_p_sold(page)
    relist = settled_relist_rate(page)
    missing = [d for d in days if d not in daily]
    if missing:
        print(
            "Warning: Open Tracker Daily Summary lacks "
            f"{', '.join(d.isoformat() for d in missing)}; those days are not filled"
        )
    raw_by_week: dict = {}
    for day in days:
        if day in daily:
            week = week_ending(day)
            raw_by_week[week] = raw_by_week.get(week, 0) + daily[day]
    weekly = {week: int(round(raw * (1 - relist))) for week, raw in raw_by_week.items()}
    return {
        "source": OPEN_TRACKER_URL,
        "metric": "Daily Houses P. Sold × (1 − settled relist rate)",
        "relist_rate": round(relist, 4),
        "days": {d.isoformat(): daily[d] for d in days if d in daily},
        "weekly_raw": {w.isoformat(): n for w, n in sorted(raw_by_week.items())},
        "weekly": {w.isoformat(): n for w, n in sorted(weekly.items())},
    }


def load_home_sales(
    html: str | None = None,
    tracker_html: str | None = None,
) -> tuple[dict, dict, str | None]:
    """Live Accountable chart merged with prior quarters → (weekly, snapshot, as_of).

    New-quarter days that Accountable has not charted yet are filled
    provisionally from Open Tracker; the next Accountable chart replaces them.
    """
    _live_weekly, points, as_of = fetch_weekly_home_sales(html=html)
    if not any(value is not None for _day, value in points):
        raise RuntimeError("Accountable Resale COEs had no actual weekly points")
    previous = json.loads(SNAPSHOT_PATH.read_text()) if SNAPSHOT_PATH.exists() else None
    quarters, weekly = merge_quarter_history(previous, points)
    provisional = provisional_tracker_sales(points, as_of, tracker_html)
    if provisional:
        for week_iso, count in provisional["weekly"].items():
            week = sheet_date(week_iso)
            weekly[week] = weekly.get(week, 0) + count
            print(
                f"Provisional Home Sales {week_iso}: +{count} from Open Tracker "
                f"(raw {provisional['weekly_raw'][week_iso]} × "
                f"{1 - provisional['relist_rate']:.3f})"
            )
    payload = snapshot_payload(weekly, quarters, as_of=as_of)
    if provisional:
        payload["provisional"] = provisional
    return weekly, payload, as_of


def quarterly_sum_formula(weekly_row: int, q_col: str) -> str:
    return (
        f"=SUM(FILTER('Weekly Financials'!$B${weekly_row}:$DY${weekly_row},"
        f"MAP('Weekly Financials'!$B$1:$DY$1,"
        f'LAMBDA(d,IF(d="","",YEAR(d)&" Q"&ROUNDUP(MONTH(d)/3,0))))={q_col}$1))'
    )


def write_weekly_home_sales(
    client: SheetsClient,
    weekly: dict,
) -> tuple[str, str, list[tuple[str, str, int]]]:
    labels = label_rows(client, WEEKLY, max_row=150)
    row = labels[HOME_SALES_LABEL]
    header = client.read_range(WEEKLY, "B1:DY1")[0]
    cells: list = []
    written: list[tuple[str, str, int]] = []
    start_idx: int | None = None
    for i, raw in enumerate(header):
        week = sheet_date(raw)
        col_n = i + 2
        if week is None or week < HOME_SALES_ACCOUNTABLE_START:
            if start_idx is None:
                continue
            cells.append("")
            continue
        if start_idx is None:
            start_idx = col_n
        if week in weekly:
            cells.append(weekly[week])
            written.append((col_letter(col_n), week.isoformat(), weekly[week]))
        else:
            cells.append("")
    if start_idx is None or not cells:
        raise RuntimeError("No Weekly Financials columns on/after 2026-07-04")
    end_col = col_letter(start_idx + len(cells) - 1)
    start_col = col_letter(start_idx)
    client.write_range(WEEKLY, f"{start_col}{row}:{end_col}{row}", [cells])
    ws = client.worksheet(WEEKLY)
    ws.update_note(f"B{row}", HOME_SALES_NOTE)
    print(f"{WEEKLY} {HOME_SALES_LABEL} {start_col}{row}:{end_col}{row}: wrote {len(written)} weeks")
    return start_col, end_col, written


def write_quarterly_sums(client: SheetsClient) -> list[str]:
    """Q3 2026 onward aggregates weekly Accountable actuals until an earnings print."""
    q_labels = label_rows(client, QUARTERLY, max_row=150)
    w_labels = label_rows(client, WEEKLY, max_row=150)
    q_row = q_labels[HOME_SALES_LABEL]
    w_row = w_labels[HOME_SALES_LABEL]
    header = client.read_range(QUARTERLY, "A1:L1")[0]
    existing = client.read_range(QUARTERLY, f"A{q_row}:L{q_row}", as_formulas=True)[0]
    updates: list[str] = []
    for idx, key in enumerate(header[1:], start=2):
        if str(key) < "2026 Q3":
            continue
        cell = existing[idx - 1] if idx - 1 < len(existing) else ""
        if cell not in ("", None) and not str(cell).startswith("="):
            continue
        col = col_letter(idx)
        formula = quarterly_sum_formula(w_row, col)
        if str(cell) != formula:
            client.write_range(QUARTERLY, f"{col}{q_row}", [[formula]], as_formulas=True)
            updates.append(f"{col}{q_row}")
    if updates:
        print(f"{QUARTERLY} {HOME_SALES_LABEL}: weekly SUM on {', '.join(updates)}")
    return updates


def refresh_definitions(client: SheetsClient) -> None:
    ensure_definitions_sheet(client)
    rows, missing = build_rows(client)
    client.write_range(FINANCIALS_DEFINITIONS_SHEET, f"A1:B{len(rows)}", rows)
    print(f"Wrote {len(rows)} rows to {FINANCIALS_DEFINITIONS_SHEET!r}")
    if missing:
        print(f"Warning: {len(missing)} labels missing definitions")


def main() -> None:
    weekly, payload, as_of = load_home_sales()
    SNAPSHOT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {SNAPSHOT_PATH.relative_to(ROOT)} ({len(weekly)} weeks, as of {as_of})")

    client = SheetsClient(ticker="OPEN")
    start_col, end_col, written = write_weekly_home_sales(client, weekly)
    write_quarterly_sums(client)
    refresh_definitions(client)
    for col, week, count in written:
        print(f"  {col} {week}: {count}")
    print(f"Done. {WEEKLY} Home Sales {start_col}:{end_col} from Accountable.")


if __name__ == "__main__":
    main()
