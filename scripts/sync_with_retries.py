#!/usr/bin/env python3
"""Run sync_repo_from_live_sheet steps with retries for flaky Sheets API responses."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_step(script: str, *args: str, attempts: int = 8) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / script), *args]
    for attempt in range(1, attempts + 1):
        print(f"\n>> {' '.join(cmd)} (attempt {attempt}/{attempts})", flush=True)
        result = subprocess.run(cmd)
        if result.returncode == 0:
            return
        wait = min(15 * attempt, 90)
        print(f"Step failed (exit {result.returncode}); retrying in {wait}s...", flush=True)
        time.sleep(wait)
    raise SystemExit(f"Step failed after {attempts} attempts: {script}")


def main() -> None:
    update_snapshot = "--update-snapshot" in sys.argv
    run_step("pull_cm_stack_from_sheet.py")
    run_step("pull_financials_definitions_from_sheet.py")
    run_step("pull_welcome_from_sheet.py")
    if update_snapshot:
        run_step("validate_workbook_snapshot.py", "--update")
    else:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_workbook_snapshot.py")],
        )
        if result.returncode != 0:
            print(
                "\nWorkbook snapshot differs from live (chart series rows). "
                "Re-run with --update-snapshot if intentional."
            )

    validate_cmd = [sys.executable, str(ROOT / "scripts" / "validate_model_formulas.py")]
    for attempt in range(1, 9):
        print(f"\n>> {' '.join(validate_cmd)} (attempt {attempt}/8)", flush=True)
        result = subprocess.run(validate_cmd)
        if result.returncode == 0:
            print("\nSync complete — review git diff.", flush=True)
            return
        wait = min(15 * attempt, 90)
        print(f"Validation failed; retrying in {wait}s...", flush=True)
        time.sleep(wait)
    raise SystemExit("Model formula validation failed after retries")


if __name__ == "__main__":
    main()
