#!/usr/bin/env python3
"""Pull tracked spreadsheet state into git after manual workbook edits.

The live Google Sheet is the source of truth for CM stack constants, seasonality,
Financials Definitions notes, and chart series layout. Model-row formulas are defined in sheets/*.py — if this
script reports formula drift, update those modules (or run restore after fixing
the repo) before committing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from validate_model_formulas import validate  # noqa: E402


def _run(script: str, *args: str, check: bool = True) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / script), *args]
    print(f"\n>> {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.returncode


def main() -> None:
    _run("pull_cm_stack_from_sheet.py")
    _run("pull_financials_definitions_from_sheet.py")

    if "--update-snapshot" in sys.argv:
        _run("validate_workbook_snapshot.py", "--update")
    elif _run("validate_workbook_snapshot.py", check=False) != 0:
        print(
            "\nWorkbook snapshot differs from live (chart series rows). "
            "Re-run with --update-snapshot if intentional."
        )

    client = SheetsClient()
    issues = validate(client, check_live_drift=True)
    if issues:
        print("\nModel formula drift detected (live sheet != repo templates):")
        for item in issues:
            print(f"  - {item}")
        print(
            "\nUpdate sheets/*.py to match intentional manual formula edits, then re-run. "
            "Or run restore_weekly_model_formulas.py if the sheet is wrong and repo is right."
        )
        sys.exit(1)

    print("\nSync complete — review git diff and commit.")


if __name__ == "__main__":
    main()
