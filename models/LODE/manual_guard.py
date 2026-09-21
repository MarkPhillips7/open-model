"""Detect manual spreadsheet edits before any agent writes to the LODE workbook.

The live Google Sheet and this repository are two copies of the same model, and
either one can move first. A human may retype a lever, extend a ramp, or paste a
fresh quarter's actuals straight into the sheet; a script may then come along and
overwrite it. This module exists so that never happens silently.

How it works
------------
After every successful agent write, the full live grid of each tracked tab is
recorded to ``live_fingerprint.json`` (checked into git). Before the next write,
the live sheet is read again and diffed against that baseline. Anything that
differs was changed by hand in the interim.

Each differing cell is classified by **ownership**:

``agent``
    Cells this repo generates: row labels, units, the quarterly spine, and every
    ``- Model`` formula. A manual change here is a genuine conflict — either the
    edit was intentional and the repo should be updated to match, or the sheet
    drifted and should be restored. Either way a human decides, not a script.

``user``
    Cells a human is *supposed* to own: lever values, the ``- Plan`` trajectory
    rows, reported actuals, and prose. Changes here are adopted back into the
    repo by ``check_manual_changes.py --adopt`` so git reflects the sheet.

Writer scripts call :func:`require_reconciled` first. It raises unless the sheet
matches the baseline, and the message tells you exactly which cells moved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

from models.LODE import layout as L
from models.LODE import levers as lv

PACK_DIR = Path(__file__).resolve().parent
FINGERPRINT_PATH = PACK_DIR / "live_fingerprint.json"

Owner = Literal["agent", "user"]

# Tabs whose contents are tracked cell-for-cell, with the range to snapshot.
# Anything outside these ranges is not compared, so adding scratch columns far to
# the right will not trip the guard.
TRACKED_RANGES: dict[str, str] = {
    L.QUARTERLY: f"A1:{L.LAST_VALUE_COL}{len(L.ROWS)}",
    lv.LEVERS_SHEET: f"A1:G{len(lv.grid())}",
    "Asset Monetization": "A1:E80",
    "Valuation": "A1:E60",
    "Financials Definitions": "A1:B200",
    "Welcome": "A1:B80",
    "Reference": "A1:C60",
    "Shares": "A1:E40",
}

# Prose tabs: a human rewriting the wording is expected and always adoptable.
PROSE_TABS: frozenset[str] = frozenset(
    {"Welcome", "Financials Definitions", "Reference"}
)

# Price History holds one volatile GOOGLEFINANCE spill, so its values change on
# their own every day. Tracking it would produce nothing but noise.
UNTRACKED_TABS: frozenset[str] = frozenset({"Price History"})


@dataclass(frozen=True)
class Change:
    tab: str
    a1: str
    row: int
    col: int
    before: str
    after: str
    owner: Owner
    label: str

    def describe(self) -> str:
        where = f"{self.tab}!{self.a1}"
        what = f"{self.label} — " if self.label else ""
        return f"[{self.owner}] {where}: {what}{self.before!r} → {self.after!r}"


def _col_letter(n: int) -> str:
    out = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def _norm(value: Any) -> str:
    """Compare as trimmed strings. Sheets round-trips 1 as '1' or 1 depending on path."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _model_labels() -> frozenset[str]:
    from models.LODE import quarterly_model_formulas as qmf

    return frozenset(qmf.MODEL_FORMULA_LABELS)


def _quarterly_owner(row_label: str, col: int) -> Owner:
    """Ownership of one Quarterly Financials cell. ``col`` is 1-based."""
    if col <= 2:
        return "agent"  # column A labels and column B units come from layout.ROWS
    if row_label in {L.YEAR, L.QUARTER, L.QUARTER_ENDING}:
        return "agent"  # the time spine is generated
    if row_label in L.EDITABLE_PATH_LABELS:
        return "user"  # "- Plan" trajectories are meant to be edited by hand
    if row_label in _model_labels():
        return "agent"  # canonical formulas live in quarterly_model_formulas.py
    if row_label in L.SECTION_LABELS or not row_label:
        return "agent"
    return "user"  # everything else on this tab is a reported print


def _levers_owner(col: int) -> Owner:
    # Only column C (the live value) is the human's to set; the rest documents it.
    return "user" if col == 3 else "agent"


def cell_owner(tab: str, row_label: str, col: int) -> Owner:
    if tab in PROSE_TABS:
        return "user"
    if tab == L.QUARTERLY:
        return _quarterly_owner(row_label, col)
    if tab == lv.LEVERS_SHEET:
        return _levers_owner(col)
    # Asset Monetization / Valuation / Shares: column A labels and B units are
    # generated; assumption and note columns are the human's.
    return "agent" if col <= 2 else "user"


def fingerprint(client: Any) -> dict[str, Any]:
    """Read every tracked tab as formulas and return a comparable snapshot."""
    live_tabs = [t for t in client.list_worksheets() if t not in UNTRACKED_TABS]
    tabs = {t: r for t, r in TRACKED_RANGES.items() if t in live_tabs}
    if not tabs:
        return {"spreadsheet_id": client.spreadsheet_id, "tabs": {}}
    ranges = [f"'{tab}'!{rng}" for tab, rng in tabs.items()]
    grids = client.batch_get(ranges, as_formulas=True)
    return {
        "recorded": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "spreadsheet_id": client.spreadsheet_id,
        "tabs": {
            tab: {"range": tabs[tab], "rows": [[_norm(c) for c in row] for row in grid]}
            for tab, grid in zip(tabs, grids, strict=True)
        },
    }


def load() -> dict[str, Any] | None:
    if not FINGERPRINT_PATH.exists():
        return None
    return json.loads(FINGERPRINT_PATH.read_text())


def save(snapshot: dict[str, Any]) -> None:
    FINGERPRINT_PATH.write_text(json.dumps(snapshot, indent=2) + "\n")


def record(client: Any) -> dict[str, Any]:
    """Re-baseline: call this immediately after a successful agent write."""
    snapshot = fingerprint(client)
    save(snapshot)
    return snapshot


def _row_label(grid: list[list[str]], row_idx: int) -> str:
    if row_idx < len(grid) and grid[row_idx]:
        return grid[row_idx][0]
    return ""


def _cell(grid: list[list[str]], row_idx: int, col_idx: int) -> str:
    if row_idx >= len(grid):
        return ""
    row = grid[row_idx]
    return row[col_idx] if col_idx < len(row) else ""


def diff(baseline: dict[str, Any], live: dict[str, Any]) -> list[Change]:
    """Cells that differ between the recorded baseline and the live sheet."""
    changes: list[Change] = []
    base_tabs = baseline.get("tabs", {})
    live_tabs = live.get("tabs", {})
    for tab in sorted(set(base_tabs) | set(live_tabs)):
        base_grid = base_tabs.get(tab, {}).get("rows", [])
        live_grid = live_tabs.get(tab, {}).get("rows", [])
        n_rows = max(len(base_grid), len(live_grid))
        for r in range(n_rows):
            width = max(
                len(base_grid[r]) if r < len(base_grid) else 0,
                len(live_grid[r]) if r < len(live_grid) else 0,
            )
            # Prefer the live label so a renamed row still reports usefully.
            label = _row_label(live_grid, r) or _row_label(base_grid, r)
            for c in range(width):
                before = _cell(base_grid, r, c)
                after = _cell(live_grid, r, c)
                if before == after:
                    continue
                changes.append(
                    Change(
                        tab=tab,
                        a1=f"{_col_letter(c + 1)}{r + 1}",
                        row=r + 1,
                        col=c + 1,
                        before=before,
                        after=after,
                        owner=cell_owner(tab, label, c + 1),
                        label=label,
                    )
                )
    return changes


def detect(client: Any) -> tuple[list[Change], bool]:
    """Return (changes, had_baseline). No baseline yet means nothing to compare."""
    baseline = load()
    if baseline is None:
        return [], False
    return diff(baseline, fingerprint(client)), True


def summarize(changes: Iterable[Change]) -> str:
    items = list(changes)
    if not items:
        return "No manual changes detected — live sheet matches the recorded baseline."
    user = [c for c in items if c.owner == "user"]
    agent = [c for c in items if c.owner == "agent"]
    lines: list[str] = []
    if user:
        lines.append(f"{len(user)} change(s) in cells you own (adoptable into git):")
        lines += [f"  {c.describe()}" for c in user[:40]]
        if len(user) > 40:
            lines.append(f"  … {len(user) - 40} more")
    if agent:
        if lines:
            lines.append("")
        lines.append(
            f"{len(agent)} change(s) in cells this repo generates (needs a decision):"
        )
        lines += [f"  {c.describe()}" for c in agent[:40]]
        if len(agent) > 40:
            lines.append(f"  … {len(agent) - 40} more")
    return "\n".join(lines)


def require_reconciled(
    client: Any,
    *,
    action: str,
    force: bool = False,
) -> None:
    """Abort *action* if the sheet has manual edits that git does not know about.

    Called at the top of every script that writes to the workbook. ``force=True``
    is the deliberate override, and it says so out loud rather than staying quiet.
    """
    if force:
        print(f"--force: skipping the manual-change check before {action}.")
        return

    changes, had_baseline = detect(client)
    if not had_baseline:
        print(
            f"No {FINGERPRINT_PATH.name} yet — nothing to compare against, "
            f"proceeding with {action}. A baseline will be recorded afterwards."
        )
        return
    if not changes:
        return

    raise SystemExit(
        f"Refusing to {action}: the live sheet has changed since this repo last "
        f"wrote to it.\n\n"
        f"{summarize(changes)}\n\n"
        "Pick one:\n"
        "  1. Keep the sheet's version — adopt it into git:\n"
        "       python models/LODE/scripts/check_manual_changes.py --adopt\n"
        "  2. Keep the repo's version — overwrite the sheet:\n"
        "       python models/LODE/scripts/check_manual_changes.py --accept-sheet\n"
        "     then re-run this command\n"
        "  3. Override for this run only: pass --force\n"
    )
