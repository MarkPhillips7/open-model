from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import gspread

from .auth import get_client

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"


def _extract_spreadsheet_id(value: str) -> str:
    """Accept a raw ID or a full Google Sheets URL."""
    value = value.strip()
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", value)
    return match.group(1) if match else value


class SheetsClient:
    """Thin wrapper around gspread for common spreadsheet operations."""

    def __init__(
        self,
        spreadsheet_id: Optional[str] = None,
        client: Optional[gspread.Client] = None,
    ):
        self._client = client or get_client()
        self._spreadsheet_id = spreadsheet_id or self._load_spreadsheet_id()
        self._spreadsheet = self._client.open_by_key(self._spreadsheet_id)

    @staticmethod
    def _load_spreadsheet_id() -> str:
        if not SETTINGS_FILE.exists():
            raise FileNotFoundError(
                f"Missing {SETTINGS_FILE}.\n"
                "Copy config/settings.example.json to config/settings.json "
                "and set your spreadsheet_id."
            )

        settings = json.loads(SETTINGS_FILE.read_text())
        spreadsheet_id = settings.get("spreadsheet_id", "").strip()
        if not spreadsheet_id or spreadsheet_id == "paste-your-spreadsheet-id-here":
            raise ValueError(
                "Set spreadsheet_id in config/settings.json "
                "(paste the ID or full Google Sheets URL)."
            )

        return _extract_spreadsheet_id(spreadsheet_id)

    @property
    def spreadsheet(self) -> gspread.Spreadsheet:
        return self._spreadsheet

    @property
    def spreadsheet_id(self) -> str:
        return self._spreadsheet_id

    def list_worksheets(self) -> list[str]:
        return [ws.title for ws in self._spreadsheet.worksheets()]

    def worksheet(self, title: str) -> gspread.Worksheet:
        return self._spreadsheet.worksheet(title)

    def read_range(
        self,
        sheet_name: str,
        cell_range: str,
        *,
        as_formulas: bool = False,
    ) -> list[list]:
        option = "FORMULA" if as_formulas else "UNFORMATTED_VALUE"
        return self.worksheet(sheet_name).get(cell_range, value_render_option=option)

    def batch_get(
        self,
        ranges: list[str],
        *,
        as_formulas: bool = False,
    ) -> list[list[list]]:
        """Read multiple A1 ranges in one API call. Returns one values grid per range."""
        params = {"valueRenderOption": "FORMULA" if as_formulas else "UNFORMATTED_VALUE"}
        result = self._spreadsheet.values_batch_get(ranges, params=params)
        return [vr.get("values", []) for vr in result.get("valueRanges", [])]

    def write_range(
        self,
        sheet_name: str,
        cell_range: str,
        values: list[list],
        *,
        as_formulas: bool = False,
    ) -> None:
        """Write values. Use as_formulas=True to preserve formula syntax (=SUM(...))."""
        input_option = "USER_ENTERED" if as_formulas else "RAW"
        self.worksheet(sheet_name).update(
            values,
            range_name=cell_range,
            value_input_option=input_option,
        )

    def summary(self) -> dict:
        worksheets = self._spreadsheet.worksheets()
        return {
            "title": self._spreadsheet.title,
            "spreadsheet_id": self._spreadsheet_id,
            "url": self._spreadsheet.url,
            "worksheets": [
                {"title": ws.title, "rows": ws.row_count, "cols": ws.col_count}
                for ws in worksheets
            ],
        }
