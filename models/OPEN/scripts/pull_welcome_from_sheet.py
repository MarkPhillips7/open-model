#!/usr/bin/env python3
"""Pull Welcome tab copy from the live sheet into models/OPEN/welcome.py."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from sheets import SheetsClient  # noqa: E402
from models.OPEN.welcome import WELCOME_SHEET  # noqa: E402

WELCOME_FILE = PACK / "welcome.py"

# Fixed row layout from scripts/setup_welcome.py (0-based indices).
ROW_DISCLAIMER = 2
ROW_THANKS = 6
ROW_GOALS = 10
ROW_TAB_GUIDE = 12
ROW_TAB_HEADER = 14
ROW_TABS_START = 15


def _cell(rows: list[list[str]], row_idx: int, col: int = 0) -> str:
    if row_idx < 0 or row_idx >= len(rows):
        return ""
    row = rows[row_idx]
    return row[col] if len(row) > col else ""


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _replace_paragraph(text: str, name: str, value: str) -> str:
    if not value:
        return text
    pattern = re.compile(rf"{name} = \(\n(?:    .*?\n)+\)", re.DOTALL)
    replacement = f'{name} = (\n    "{_escape(value)}"\n)'
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text


def _replace_tab_descriptions(text: str, tabs: list[tuple[str, str]]) -> str:
    if not tabs:
        return text
    lines = ["TAB_DESCRIPTIONS: list[tuple[str, str]] = ["]
    for title, desc in tabs:
        lines.append("    (")
        lines.append(f'        "{_escape(title)}",')
        lines.append(f'        "{_escape(desc)}",')
        lines.append("    ),")
    lines.append("]")
    block = "\n".join(lines)
    pattern = re.compile(
        r"TAB_DESCRIPTIONS: list\[tuple\[str, str\]\] = \[.*?\n\]",
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    return text


def pull_and_write(client: SheetsClient) -> bool:
    rows = client.batch_get(["Welcome!A1:B30"])[0]
    text = WELCOME_FILE.read_text()
    original = text

    text = _replace_paragraph(text, "DISCLAIMER", _cell(rows, ROW_DISCLAIMER))
    text = _replace_paragraph(text, "THANKS", _cell(rows, ROW_THANKS))
    text = _replace_paragraph(text, "GOALS", _cell(rows, ROW_GOALS))
    text = _replace_paragraph(text, "TAB_GUIDE_INTRO", _cell(rows, ROW_TAB_GUIDE))

    tabs: list[tuple[str, str]] = []
    for row in rows[ROW_TABS_START:]:
        if not row or not row[0]:
            continue
        title = row[0]
        desc = row[1] if len(row) > 1 else ""
        if title == "Tab" or not desc:
            continue
        if title.startswith("If you spot"):
            text = _replace_paragraph(text, "CLOSING", title)
            break
        tabs.append((title, desc))

    text = _replace_tab_descriptions(text, tabs)

    if text != original:
        WELCOME_FILE.write_text(text)
        return True
    return False


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    if pull_and_write(client):
        print(f"Updated {WELCOME_FILE.name} from live {WELCOME_SHEET!r} tab")
    else:
        print(f"{WELCOME_FILE.name}: already matches live Welcome tab")


if __name__ == "__main__":
    main()
