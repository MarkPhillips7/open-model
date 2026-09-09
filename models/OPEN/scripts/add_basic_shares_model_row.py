#!/usr/bin/env python3
"""Insert Basic Shares Outstanding - Model and wire EPS - Model to it.

Superseded by setup_shares_sheet.py for share events; kept for one-time row insert history.
"""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from scripts.restore_weekly_model_formulas import restore_model_formulas  # noqa: E402
from sheets import SheetsClient  # noqa: E402
from sheets.formulas import SHARES_MODEL_LABEL  # noqa: E402
from sheets.labels import QUARTERLY, WEEKLY, insert_rows_before_label  # noqa: E402

TRANSITIONS = "Transitions"

# Nov 2025 warrant distribution (424B5 / 8-K); no management % exercise guide — 25% default.
TRANSITIONS_DILUTION_ROWS: list[list] = [
    ["Warrant shares (Nov 2025 distribution, if exercised)", 99_295_146],
    ["Assumed warrant exercise fraction", 0.25],
    ["Warrant distribution date", "11/21/2025"],
    ["Warrant expiration date", "11/20/2026"],
    ["", ""],
    ["", ""],
    ["Assumed share price for SBC dilution ($)", 8],
]


def write_transitions_dilution_assumptions(client: SheetsClient) -> None:
    ws = client.worksheet(TRANSITIONS)
    ws.update(
        TRANSITIONS_DILUTION_ROWS,
        range_name="A25:B31",
        value_input_option="USER_ENTERED",
    )
    print(f"Wrote share dilution assumptions to {TRANSITIONS}!A25:B31")


def main() -> None:
    client = SheetsClient(ticker="OPEN")

    insert_rows_before_label(
        client,
        tab=WEEKLY,
        before_label="Open Mortgage Percent",
        labels=[SHARES_MODEL_LABEL],
    )
    insert_rows_before_label(
        client,
        tab=QUARTERLY,
        before_label="Open Mortgage Percent",
        labels=[SHARES_MODEL_LABEL],
    )

    write_transitions_dilution_assumptions(client)
    restore_model_formulas(client)
    print("Done.")


if __name__ == "__main__":
    main()
