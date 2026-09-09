#!/usr/bin/env python3
"""Pull Financials Definitions column B notes from the live EOSE sheet into git."""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from models.EOSE.financials_definitions import (  # noqa: E402
    FIELD_NOTES,
    FINANCIALS_DEFINITIONS_SHEET,
)

DEFINITIONS_FILE = PACK / "financials_definitions.py"


def pull_notes(client: SheetsClient) -> dict[str, str]:
    rows = client.batch_get([f"{FINANCIALS_DEFINITIONS_SHEET}!A1:B160"])[0]
    notes: dict[str, str] = {}
    for row in rows:
        if not row or not row[0]:
            continue
        label = row[0]
        note = row[1] if len(row) > 1 else ""
        notes[label] = note
    return notes


def _format_note_value(note: str) -> str:
    parts = textwrap.wrap(note, width=85, break_long_words=False, break_on_hyphens=False)
    if not parts:
        return '""'
    if len(parts) == 1:
        return f'"{parts[0]}"'
    lines = ["("]
    for i, part in enumerate(parts):
        suffix = " " if i < len(parts) - 1 else ""
        lines.append(f'        "{part}{suffix}"')
    lines.append("    )")
    return "\n".join(lines)


def _format_field_notes(notes: dict[str, str]) -> str:
    lines = ["FIELD_NOTES: dict[str, str] = {"]
    for label, note in notes.items():
        lines.append(f"    {label!r}: {_format_note_value(note)},")
    lines.append("}")
    return "\n".join(lines)


def write_field_notes(notes: dict[str, str]) -> None:
    text = DEFINITIONS_FILE.read_text()
    pattern = re.compile(r"FIELD_NOTES: dict\[str, str\] = \{.*?\n\}", re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"FIELD_NOTES block not found in {DEFINITIONS_FILE}")
    DEFINITIONS_FILE.write_text(pattern.sub(_format_field_notes(notes), text, count=1))


def main() -> None:
    client = SheetsClient(ticker="EOSE")
    live = pull_notes(client)
    if live == FIELD_NOTES:
        print(f"{DEFINITIONS_FILE.name}: already matches live sheet")
        return
    write_field_notes(live)
    print(f"Updated {DEFINITIONS_FILE.name} ({len(live)} field notes from live sheet)")


if __name__ == "__main__":
    main()
