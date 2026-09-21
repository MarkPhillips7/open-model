#!/usr/bin/env python3
"""Write reported actuals onto Quarterly Financials from models/LODE/actuals.py.

Run this after each earnings release, once ``fetch_sec_actuals.py`` has refreshed
``data/sec_quarterly_actuals.json``:

    python models/LODE/scripts/fetch_sec_actuals.py
    python models/LODE/scripts/load_quarterly_actuals.py

Only actual (bare-label) rows are touched. ``- Model`` formulas and ``- Plan``
trajectories are left exactly as they are, and cells for quarters that have not been
reported are left blank rather than zeroed — a blank means "not reported", and zero
would be a claim.

The manual-change guard runs first, so a hand edit is never silently overwritten.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402

from models.LODE import actuals as ACT  # noqa: E402
from models.LODE import layout as L  # noqa: E402
from models.LODE import manual_guard as guard  # noqa: E402

TICKER = "LODE"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="Skip the manual-change check."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without touching the sheet.",
    )
    args = parser.parse_args()

    client = SheetsClient(ticker=TICKER)
    if not args.dry_run:
        guard.require_reconciled(
            client, action="load quarterly actuals", force=args.force
        )

    # Abort if the label stack drifted — writing by row number into a shifted
    # layout is how models quietly become wrong.
    L.require_live_layout_match(client, action="load quarterly actuals")

    rows = L.label_map_from_ab(L.live_quarterly_ab(client))
    keys = L.quarter_keys()
    end_col = col_letter(L.FIRST_VALUE_COL_INDEX + L.N_QUARTERS - 1)

    data = ACT.quarterly_actuals()
    batch: list[dict] = []
    for label, series in data.items():
        if label not in rows:
            print(f"  skip {label!r} — not on the live sheet")
            continue
        values = [series.get(key, "") for key in keys]
        batch.append(
            {
                "range": f"{L.FIRST_VALUE_COL}{rows[label]}:{end_col}{rows[label]}",
                "values": [values],
            }
        )
        reported = sum(1 for v in values if v != "")
        print(f"  {label}: {reported} reported quarter(s)")

    if args.dry_run:
        print(f"\nDry run — {len(batch)} row(s) would be written. Nothing changed.")
        return

    client.worksheet(L.QUARTERLY).batch_update(batch, value_input_option="USER_ENTERED")
    guard.record(client)
    print(
        f"\nWrote {len(batch)} actual row(s) through {ACT.latest_reported_quarter()}.\n"
        f"Re-baselined {guard.FINGERPRINT_PATH.name}. "
        "Log this in models/LODE/CHANGELOG.md."
    )


if __name__ == "__main__":
    main()
