#!/usr/bin/env python3
"""Pull tracked spreadsheet state into git after manual workbook edits.

The live Google Sheet is the source of truth for pack-specific constants
(Welcome copy, definitions notes, seasonality) and chart series layout.
Model-row formulas are defined in models/{TICKER}/*.py — if this script reports
formula drift, update those modules (or run restore after fixing the repo)
before committing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.registry import pack_script, parse_ticker_argv, resolve_ticker  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from validate_model_formulas import validate  # noqa: E402

PACK_PULL_SCRIPTS = (
    "pull_cm_stack_from_sheet.py",
    "pull_financials_definitions_from_sheet.py",
    "pull_welcome_from_sheet.py",
)


def _run(path: Path, *args: str, check: bool = True) -> int:
    cmd = [sys.executable, str(path), *args]
    print(f"\n>> {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.returncode


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    ticker = resolve_ticker(ticker_arg)
    update_snapshot = "--update-snapshot" in rest
    unknown = [a for a in rest if a != "--update-snapshot"]
    if unknown:
        print(f"Unknown arguments: {unknown}")
        sys.exit(2)

    ticker_flag = ("--ticker", ticker)
    for name in PACK_PULL_SCRIPTS:
        script = pack_script(ticker, name)
        if script.is_file():
            _run(script, check=(name != "pull_welcome_from_sheet.py"))
        else:
            print(f"\n>> skip {script} (not in {ticker} pack)")

    snapshot_script = ROOT / "scripts" / "validate_workbook_snapshot.py"
    if update_snapshot:
        _run(snapshot_script, *ticker_flag, "--update")
    elif _run(snapshot_script, *ticker_flag, check=False) != 0:
        print(
            "\nWorkbook snapshot differs from live (chart series rows). "
            "Re-run with --update-snapshot if intentional."
        )

    weekly_formulas = ROOT / "models" / ticker / "weekly_model_formulas.py"
    quarterly_formulas = ROOT / "models" / ticker / "quarterly_model_formulas.py"
    if not weekly_formulas.is_file() and not quarterly_formulas.is_file():
        print(f"\nNo model formula module in {ticker} pack — skip formula drift check.")
        print("\nSync complete — review git diff and commit.")
        return

    client = SheetsClient(ticker=ticker)
    issues = validate(client, ticker=ticker, check_live_drift=True)
    if issues:
        print("\nModel formula drift detected (live sheet != repo templates):")
        for item in issues:
            print(f"  - {item}")
        print(
            "\nUpdate models/{TICKER}/*.py to match intentional manual formula edits, then re-run. "
            "Or run restore_weekly_model_formulas.py if the sheet is wrong and repo is right."
        )
        sys.exit(1)

    print("\nSync complete — review git diff and commit.")


if __name__ == "__main__":
    main()
