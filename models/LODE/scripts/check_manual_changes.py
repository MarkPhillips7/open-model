#!/usr/bin/env python3
"""Report — and optionally adopt — manual edits made to the live LODE workbook.

Run this before doing anything else with the sheet, and any time a writer script
stops and tells you the sheet has moved.

    python models/LODE/scripts/check_manual_changes.py                # report only
    python models/LODE/scripts/check_manual_changes.py --json         # machine readable
    python models/LODE/scripts/check_manual_changes.py --adopt        # sheet wins
    python models/LODE/scripts/check_manual_changes.py --accept-sheet # re-baseline only

``--adopt`` writes lever values the human changed back into ``levers.py`` defaults
and ``- Plan`` trajectories back into ``layout.py``, so git ends up agreeing with
the sheet, then re-baselines. Reported actuals are not rewritten by hand — re-run
``load_quarterly_actuals.py`` for those, since they should come from a filing.

``--accept-sheet`` re-baselines without changing any Python. Use it when the sheet
is right and you have already updated the repo yourself, or when the differences do
not belong in git.

Exit code is 1 when unadopted changes exist, so this composes in a shell chain.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402

from models.LODE import layout as L  # noqa: E402
from models.LODE import levers as LV  # noqa: E402
from models.LODE import manual_guard as guard  # noqa: E402

TICKER = "LODE"
LEVERS_PY = Path(LV.__file__)
LAYOUT_PY = Path(L.__file__)


def _as_number(text: str) -> float | int | str:
    try:
        value = float(text)
    except ValueError:
        return text
    return int(value) if value.is_integer() else value


def _adopt_lever(label: str, new_value: str) -> bool:
    """Rewrite one lever's default in levers.py. Returns True if the file changed."""
    source = LEVERS_PY.read_text()
    # Match the Lever(...) call for this label and replace only its third argument,
    # which is the default. Labels are unique, so the anchor is safe.
    pattern = re.compile(
        r"(Lever\(\s*\n\s*[A-Z_]+,\s*\n\s*[^\n]*?,\s*\n\s*)([^\n]*?)(,\s*\n)",
        re.MULTILINE,
    )
    rows = LV.lever_rows()
    if label not in rows:
        return False

    lever = LV.lever(label)
    old_literal = repr(lever.default) if isinstance(lever.default, str) else str(lever.default)
    new_literal = (
        repr(new_value)
        if isinstance(_as_number(new_value), str)
        else str(_as_number(new_value))
    )
    if old_literal == new_literal:
        return False

    # Find the constant name bound to this label so the edit is anchored precisely.
    const_match = re.search(
        rf'^([A-Z_0-9]+) = "{re.escape(label)}"$', source, re.MULTILINE
    )
    if not const_match:
        return False
    const = const_match.group(1)

    call = re.search(
        rf"(Lever\(\s*\n\s*{const},\s*\n\s*[^\n]*,\s*\n\s*)([^\n]*?)(,\s*\n)",
        source,
    )
    if not call:
        return False
    updated = source[: call.start(2)] + new_literal + source[call.end(2) :]
    if updated == source:
        return False
    LEVERS_PY.write_text(updated)
    del pattern  # kept above only to document the shape being matched
    return True


def _adopt_plan_row(label: str, values: list[str]) -> bool:
    """Rewrite one ``- Plan`` trajectory list in layout.py."""
    name = {
        L.LINES_PLAN: "LINE_PATH",
        L.UTILIZATION_PLAN: "UTILIZATION_PATH",
        L.UPLIFT_PHASE_IN: "UPLIFT_PHASE_IN_PATH",
    }.get(label)
    if name is None:
        return False

    numbers = [_as_number(v) if v else 0 for v in values]
    numbers = [n if isinstance(n, (int, float)) else 0 for n in numbers]
    if len(numbers) != L.N_QUARTERS:
        numbers = (numbers + [0] * L.N_QUARTERS)[: L.N_QUARTERS]

    lines = []
    for year_idx, year in enumerate(L.YEARS):
        chunk = numbers[year_idx * 4 : year_idx * 4 + 4]
        lines.append("    " + ", ".join(str(v) for v in chunk) + f",  # {year}")
    replacement = f"{name}: list[float] = [\n" + "\n".join(lines) + "\n]"

    source = LAYOUT_PY.read_text()
    pattern = re.compile(rf"{name}: list\[float\] = \[.*?\n\]", re.DOTALL)
    if not pattern.search(source):
        return False
    updated = pattern.sub(replacement, source, count=1)
    if updated == source:
        return False
    LAYOUT_PY.write_text(updated)
    return True


def adopt(changes: list[guard.Change]) -> tuple[list[str], list[str]]:
    """Fold user-owned sheet edits into the repo. Returns (adopted, skipped)."""
    adopted: list[str] = []
    skipped: list[str] = []

    lever_rows = {row: label for label, row in LV.lever_rows().items()}

    for change in changes:
        if change.owner != "user":
            skipped.append(f"{change.describe()} (this repo generates this cell)")
            continue

        if change.tab == LV.LEVERS_SHEET and change.col == 3:
            label = lever_rows.get(change.row)
            if label and _adopt_lever(label, change.after):
                adopted.append(f"levers.py: {label} default → {change.after}")
            else:
                skipped.append(f"{change.describe()} (could not locate lever default)")
            continue

        if change.tab == L.QUARTERLY and change.label in L.EDITABLE_PATH_LABELS:
            # Plan rows are adopted whole, not cell by cell.
            if any(a.startswith(f"layout.py: {change.label}") for a in adopted):
                continue
            row_values = _live_row(change.tab, change.row)
            if _adopt_plan_row(change.label, row_values):
                adopted.append(f"layout.py: {change.label} trajectory updated")
            else:
                skipped.append(f"{change.describe()} (could not locate trajectory list)")
            continue

        skipped.append(
            f"{change.describe()} (reported actual or prose — re-run "
            "load_quarterly_actuals.py, or edit the pack module directly)"
        )

    return adopted, skipped


_LIVE_CACHE: dict[str, list[list[str]]] = {}


def _live_row(tab: str, row: int) -> list[str]:
    grid = _LIVE_CACHE.get(tab, [])
    if row - 1 < len(grid):
        values = grid[row - 1]
        return [v for v in values[L.FIRST_VALUE_COL_INDEX - 1 :]]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit changes as JSON.")
    parser.add_argument(
        "--adopt",
        action="store_true",
        help="Write user-owned sheet edits into the repo, then re-baseline.",
    )
    parser.add_argument(
        "--accept-sheet",
        action="store_true",
        help="Re-baseline to the live sheet without editing any Python.",
    )
    args = parser.parse_args()

    client = SheetsClient(ticker=TICKER)
    live = guard.fingerprint(client)
    for tab, payload in live.get("tabs", {}).items():
        _LIVE_CACHE[tab] = payload.get("rows", [])

    baseline = guard.load()
    if baseline is None:
        print(
            f"No baseline recorded yet ({guard.FINGERPRINT_PATH.name} is missing).\n"
            "Recording the current live sheet as the baseline."
        )
        guard.save(live)
        return

    changes = guard.diff(baseline, live)

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "tab": c.tab,
                        "cell": c.a1,
                        "label": c.label,
                        "owner": c.owner,
                        "before": c.before,
                        "after": c.after,
                    }
                    for c in changes
                ],
                indent=2,
            )
        )
        sys.exit(1 if changes else 0)

    print(guard.summarize(changes))

    if not changes:
        return

    if args.accept_sheet:
        guard.save(live)
        print(
            f"\nRe-baselined {guard.FINGERPRINT_PATH.name} to the live sheet. "
            "No Python was changed — make sure the repo already reflects these edits."
        )
        return

    if args.adopt:
        adopted, skipped = adopt(changes)
        print()
        if adopted:
            print("Adopted into the repo:")
            for item in adopted:
                print(f"  {item}")
        if skipped:
            print("Not adopted automatically:")
            for item in skipped:
                print(f"  {item}")
        guard.save(live)
        print(
            f"\nRe-baselined {guard.FINGERPRINT_PATH.name}. Review `git diff` before "
            "committing, and log the sheet edits in models/LODE/CHANGELOG.md."
        )
        if skipped:
            sys.exit(1)
        return

    print(
        "\nNothing was changed. Re-run with --adopt to fold these into git, "
        "or --accept-sheet to only re-baseline."
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
