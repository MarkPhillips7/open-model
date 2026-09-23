#!/usr/bin/env python3
"""Sync OPEN weekly funnel actuals from Accountable + Open Tracker.

One command for the weekly refresh:

  python models/OPEN/scripts/sync_weekly_actuals.py
  python models/OPEN/scripts/sync_weekly_actuals.py --dry-run
  python models/OPEN/scripts/sync_weekly_actuals.py --changelog

Writes:
  - Home Sales ← Accountable Resale COEs (Δ cumulative), from 2026-07-04
  - Acquisition Contracts ← Accountable weekly actuals
  - New Listings ← Open Tracker Cohort Sell-Through Listed (Sunday→Saturday)

By default, contracts/listings only fill blank cells and revise weeks on/after
``--since`` (default: 12 weeks before the latest source actual). Pass ``--all``
to overwrite every overlapping week from the source.

`sync_accountable_home_sales.py` remains as a Home Sales-only entry point.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from models.OPEN.accountable import (  # noqa: E402
    ACQUISITION_CONTRACTS_LABEL,
    ACCOUNTABLE_URL,
    acquisition_snapshot_payload,
    fetch_accountable_html,
    fetch_acquisition_contracts,
    fetch_weekly_home_sales,
    sheet_date,
    snapshot_payload,
)
from models.OPEN.open_tracker import (  # noqa: E402
    NEW_LISTINGS_LABEL,
    OPEN_TRACKER_URL,
    fetch_weekly_new_listings,
    listings_snapshot_payload,
)
from models.OPEN.weekly_model_formulas import col_letter  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sync_accountable_home_sales import (  # noqa: E402
    SNAPSHOT_PATH as HOME_SALES_SNAPSHOT,
    refresh_definitions,
    write_quarterly_sums,
    write_weekly_home_sales,
)

CONTRACTS_SNAPSHOT = PACK / "data" / "accountable_acquisition_contracts.json"
LISTINGS_SNAPSHOT = PACK / "data" / "open_tracker_new_listings.json"
CHANGELOG_PATH = PACK / "CHANGELOG.md"
DEFAULT_REVISE_WEEKS = 12


def _cell_int(value: Any) -> int | None:
    if value in ("", None):
        return None
    try:
        return int(round(float(str(value).replace(",", ""))))
    except ValueError:
        return None


def week_columns(client: SheetsClient) -> list[tuple[date, str, int]]:
    header = client.read_range(WEEKLY, "B1:DY1")[0]
    out: list[tuple[date, str, int]] = []
    for i, raw in enumerate(header):
        week = sheet_date(raw)
        if week is None:
            continue
        col_n = i + 2
        out.append((week, col_letter(col_n), col_n))
    return out


def read_weekly_row(
    client: SheetsClient,
    label: str,
    columns: list[tuple[date, str, int]],
) -> dict[date, int | None]:
    labels = label_rows(client, WEEKLY, max_row=150)
    row = labels[label]
    if not columns:
        return {}
    start_c, end_c = columns[0][1], columns[-1][1]
    values = client.read_range(WEEKLY, f"{start_c}{row}:{end_c}{row}")[0]
    out: dict[date, int | None] = {}
    for (week, _col, _n), raw in zip(columns, values):
        out[week] = _cell_int(raw)
    return out


def select_updates(
    existing: dict[date, int | None],
    incoming: dict[date, int],
    *,
    since: date | None,
    all_weeks: bool,
) -> dict[date, int]:
    """Choose which source weeks to write onto the sheet."""
    if all_weeks:
        return {w: v for w, v in incoming.items() if w in existing}
    if since is None and incoming:
        since = max(incoming) - timedelta(weeks=DEFAULT_REVISE_WEEKS)
    selected: dict[date, int] = {}
    for week, new in incoming.items():
        if week not in existing:
            continue
        old = existing[week]
        if old is None or (since is not None and week >= since):
            selected[week] = new
    return selected


def diff_weekly(
    existing: dict[date, int | None],
    incoming: dict[date, int],
) -> list[tuple[date, int | None, int]]:
    """Return (week, old_or_None, new) for cells that would change."""
    changes: list[tuple[date, int | None, int]] = []
    for week, new in sorted(incoming.items()):
        if week not in existing:
            continue
        old = existing[week]
        if old != new:
            changes.append((week, old, new))
    return changes


def write_sparse_weekly(
    client: SheetsClient,
    label: str,
    weekly: dict[date, int],
    columns: list[tuple[date, str, int]],
    *,
    dry_run: bool,
    since: date | None,
    all_weeks: bool,
) -> list[tuple[str, str, int | None, int]]:
    """Overwrite selected week columns; leave other weeks untouched."""
    labels = label_rows(client, WEEKLY, max_row=150)
    row = labels[label]
    existing = read_weekly_row(client, label, columns)
    selected = select_updates(existing, weekly, since=since, all_weeks=all_weeks)
    changes = diff_weekly(existing, selected)
    written: list[tuple[str, str, int | None, int]] = []
    for week, old, new in changes:
        col = next(c for w, c, _ in columns if w == week)
        written.append((col, week.isoformat(), old, new))
        if not dry_run:
            client.write_range(WEEKLY, f"{col}{row}", [[new]])
    action = "Would write" if dry_run else "Wrote"
    print(f"{action} {WEEKLY} {label}: {len(written)} cell(s)")
    for col, week, old, new in written:
        old_s = "blank" if old is None else str(old)
        print(f"  {col} {week}: {old_s} → {new}")
    return written


def append_changelog(
    *,
    as_of: str | None,
    tracker_update: str | None,
    home_sales: list[tuple[str, str, int]],
    contracts: list[tuple[str, str, int | None, int]],
    listings: list[tuple[str, str, int | None, int]],
) -> None:
    today = date.today().isoformat()
    hs_last = home_sales[-1] if home_sales else None
    contract_bits = ", ".join(
        f"`{col}` **{new}**" + (f" (was {old})" if old is not None and old != new else "")
        for col, _week, old, new in contracts
    ) or "none"
    listing_bits = ", ".join(
        f"`{col}` **{new}**" + (f" (was {old})" if old is not None and old != new else "")
        for col, _week, old, new in listings
    ) or "none"
    hs_note = (
        f"**{hs_last[2]}** on `{hs_last[0]}` ({hs_last[1]})"
        if hs_last
        else "unchanged set rewritten from Accountable"
    )
    entry = f"""## {today} — Weekly actuals sync (Accountable + Open Tracker)

Automated refresh via `sync_weekly_actuals.py`. Accountable as of **{as_of or "?"}**; Open Tracker last update **{tracker_update or "?"}**.

- **Tab / range:** **Weekly Financials** Home Sales / Acquisition Contracts / New Listings; definitions refresh; snapshots under `models/OPEN/data/`
- **Insert/delete:** none
- **Formulas:** none
- **Data:**
  - **Home Sales** (Accountable Resale COEs Δ): last print {hs_note}; {len(home_sales)} weeks on sheet from 2026-07-04
  - **Acquisition Contracts** ({ACCOUNTABLE_URL}): {contract_bits}
  - **New Listings** ({OPEN_TRACKER_URL}): {listing_bits}
- **Side effects:** **Homes Charts** funnel actuals may step — eyeball in the UI; agents did not edit chart objects.

"""
    text = CHANGELOG_PATH.read_text()
    match = re.search(r"\n## \d{4}-\d{2}-\d{2} —", text)
    if not match:
        CHANGELOG_PATH.write_text(text.rstrip() + "\n\n" + entry)
        return
    insert_at = match.start() + 1
    CHANGELOG_PATH.write_text(text[:insert_at] + entry + text[insert_at:])
    print(f"Appended entry to {CHANGELOG_PATH.relative_to(ROOT)}")


def run(
    *,
    dry_run: bool,
    changelog: bool,
    skip_definitions: bool,
    since: date | None,
    all_weeks: bool,
) -> None:
    accountable_html = fetch_accountable_html()
    home_sales, cumulative, as_of = fetch_weekly_home_sales(html=accountable_html)
    contracts, _ = fetch_acquisition_contracts(html=accountable_html)
    listings, tracker_update = fetch_weekly_new_listings()

    if not home_sales:
        raise RuntimeError("Accountable Resale COEs had no actual weekly points")
    if not contracts:
        raise RuntimeError("Accountable Acquisition Contracts had no actuals")
    if not listings:
        raise RuntimeError("Open Tracker had no completed New Listings weeks")

    print(
        f"Accountable as of {as_of}: {len(home_sales)} home-sales weeks, "
        f"{len(contracts)} contract weeks"
    )
    print(f"Open Tracker last update {tracker_update}: {len(listings)} listing weeks")
    if all_weeks:
        print("Contracts/listings mode: overwrite all overlapping weeks (--all)")
    else:
        effective_since = since
        if effective_since is None and contracts:
            effective_since = max(contracts) - timedelta(weeks=DEFAULT_REVISE_WEEKS)
        print(
            f"Contracts/listings mode: fill blanks + revise on/after "
            f"{effective_since.isoformat() if effective_since else '?'}"
        )

    if not dry_run:
        HOME_SALES_SNAPSHOT.write_text(
            json.dumps(snapshot_payload(home_sales, cumulative, as_of=as_of), indent=2)
            + "\n"
        )
        CONTRACTS_SNAPSHOT.write_text(
            json.dumps(acquisition_snapshot_payload(contracts, as_of=as_of), indent=2)
            + "\n"
        )
        LISTINGS_SNAPSHOT.write_text(
            json.dumps(
                listings_snapshot_payload(listings, last_update=tracker_update),
                indent=2,
            )
            + "\n"
        )
        print(f"Wrote snapshots under {PACK.relative_to(ROOT)}/data/")

    client = SheetsClient(ticker="OPEN")
    columns = week_columns(client)

    if dry_run:
        existing_hs = read_weekly_row(client, "Home Sales", columns)
        hs_changes = diff_weekly(existing_hs, home_sales)
        print(f"Would write {WEEKLY} Home Sales: {len(hs_changes)} cell(s)")
        for week, old, new in hs_changes:
            col = next(c for w, c, _ in columns if w == week)
            old_s = "blank" if old is None else str(old)
            print(f"  {col} {week.isoformat()}: {old_s} → {new}")
        hs_written = [
            (next(c for w, c, _ in columns if w == week), week.isoformat(), new)
            for week, _old, new in hs_changes
        ]
    else:
        _start, _end, hs_written = write_weekly_home_sales(client, home_sales)
        write_quarterly_sums(client)

    contract_written = write_sparse_weekly(
        client,
        ACQUISITION_CONTRACTS_LABEL,
        contracts,
        columns,
        dry_run=dry_run,
        since=since,
        all_weeks=all_weeks,
    )
    listing_written = write_sparse_weekly(
        client,
        NEW_LISTINGS_LABEL,
        listings,
        columns,
        dry_run=dry_run,
        since=since,
        all_weeks=all_weeks,
    )

    if not dry_run and not skip_definitions:
        refresh_definitions(client)

    if changelog and not dry_run:
        append_changelog(
            as_of=as_of,
            tracker_update=tracker_update,
            home_sales=hs_written,
            contracts=contract_written,
            listings=listing_written,
        )
    elif changelog and dry_run:
        print("Skipping --changelog on --dry-run")

    print("Done." + (" (dry-run)" if dry_run else ""))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch sources and show sheet diffs without writing",
    )
    parser.add_argument(
        "--changelog",
        action="store_true",
        help=f"Append a dated entry to {CHANGELOG_PATH.relative_to(ROOT)}",
    )
    parser.add_argument(
        "--skip-definitions",
        action="store_true",
        help="Do not refresh the Financials Definitions tab",
    )
    parser.add_argument(
        "--since",
        type=date.fromisoformat,
        default=None,
        help=(
            "Earliest Saturday week-ending to revise for contracts/listings "
            f"(default: {DEFAULT_REVISE_WEEKS} weeks before latest source actual). "
            "Blank cells are always filled."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Overwrite every overlapping contracts/listings week from source",
    )
    args = parser.parse_args()
    run(
        dry_run=args.dry_run,
        changelog=args.changelog,
        skip_definitions=args.skip_definitions,
        since=args.since,
        all_weeks=args.all,
    )


if __name__ == "__main__":
    main()
