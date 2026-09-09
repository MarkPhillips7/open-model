#!/usr/bin/env python3
"""Run sync_repo_from_live_sheet steps with retries for flaky Sheets API responses."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.registry import pack_script, parse_ticker_argv, resolve_ticker  # noqa: E402

PACK_PULL_SCRIPTS = (
    "pull_cm_stack_from_sheet.py",
    "pull_financials_definitions_from_sheet.py",
    "pull_welcome_from_sheet.py",
)


def run_step(path: Path, *args: str, attempts: int = 8) -> None:
    cmd = [sys.executable, str(path), *args]
    for attempt in range(1, attempts + 1):
        print(f"\n>> {' '.join(cmd)} (attempt {attempt}/{attempts})", flush=True)
        result = subprocess.run(cmd)
        if result.returncode == 0:
            return
        wait = min(15 * attempt, 90)
        print(f"Step failed (exit {result.returncode}); retrying in {wait}s...", flush=True)
        time.sleep(wait)
    raise SystemExit(f"Step failed after {attempts} attempts: {path.name}")


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
            run_step(script)
        else:
            print(f"\n>> skip {script} (not in {ticker} pack)", flush=True)

    snapshot_script = ROOT / "scripts" / "validate_workbook_snapshot.py"
    if update_snapshot:
        run_step(snapshot_script, *ticker_flag, "--update")
    else:
        result = subprocess.run(
            [sys.executable, str(snapshot_script), *ticker_flag],
        )
        if result.returncode != 0:
            print(
                "\nWorkbook snapshot differs from live (chart series rows). "
                "Re-run with --update-snapshot if intentional."
            )

    weekly_formulas = ROOT / "models" / ticker / "weekly_model_formulas.py"
    if not weekly_formulas.is_file():
        print("\nSync complete — review git diff.", flush=True)
        return

    validate_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "validate_model_formulas.py"),
        *ticker_flag,
    ]
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
