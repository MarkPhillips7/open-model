"""Checked-in workbook layout: worksheet tabs and chart series on Weekly Financials."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import SheetsClient

SNAPSHOT_FILE = Path(__file__).resolve().parent.parent / "config" / "workbook_snapshot.json"

SeriesSpec = tuple[int, str, str, int]  # weekly_row, line_style, axis, end_column


def load_snapshot(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or SNAPSHOT_FILE).read_text())


def save_snapshot(data: dict[str, Any], path: Path | None = None) -> None:
    target = path or SNAPSHOT_FILE
    target.write_text(json.dumps(data, indent=2) + "\n")


def chart_series_tuples(chart: dict[str, Any]) -> list[SeriesSpec]:
    return [
        (s["weekly_row"], s["line_style"], s["axis"], s["end_column"])
        for s in chart["series"]
    ]


def charts_by_tab(snapshot: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for chart in snapshot["charts"]:
        grouped.setdefault(chart["tab"], []).append(chart)
    return grouped


def fetch_live_snapshot(client: SheetsClient) -> dict[str, Any]:
    meta = client.spreadsheet.fetch_sheet_metadata()
    snapshot: dict[str, Any] = {
        "worksheets": [s["properties"]["title"] for s in meta["sheets"]],
        "charts": [],
    }
    for sheet in meta["sheets"]:
        tab = sheet["properties"]["title"]
        for chart in sheet.get("charts", []):
            basic = chart["spec"].get("basicChart", {})
            domain = basic["domains"][0]["domain"]["sourceRange"]["sources"][0]
            entry: dict[str, Any] = {
                "tab": tab,
                "title": chart["spec"].get("title") or None,
                "domain_row": domain["startRowIndex"] + 1,
                "domain_end_col": domain["endColumnIndex"],
                "series": [],
            }
            for series in basic.get("series", []):
                src = series["series"]["sourceRange"]["sources"][0]
                entry["series"].append(
                    {
                        "weekly_row": src["startRowIndex"] + 1,
                        "line_style": series.get("lineStyle", {}).get("type", "SOLID"),
                        "axis": series.get("targetAxis", "LEFT_AXIS"),
                        "end_column": src["endColumnIndex"],
                    }
                )
            snapshot["charts"].append(entry)
    return snapshot


def compare_snapshots(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    if expected.get("worksheets") != actual.get("worksheets"):
        issues.append(
            "worksheets mismatch:\n"
            f"    expected: {expected.get('worksheets')}\n"
            f"    actual:   {actual.get('worksheets')}"
        )

    exp_charts = expected.get("charts", [])
    act_charts = actual.get("charts", [])
    if len(exp_charts) != len(act_charts):
        issues.append(f"chart count: expected {len(exp_charts)}, got {len(act_charts)}")

    for i, (exp, act) in enumerate(zip(exp_charts, act_charts, strict=False)):
        label = exp.get("title") or exp.get("tab")
        for key in ("tab", "title", "domain_row", "domain_end_col"):
            if exp.get(key) != act.get(key):
                issues.append(f"chart {i} ({label}): {key} expected {exp.get(key)!r}, got {act.get(key)!r}")
        if exp.get("series") != act.get("series"):
            issues.append(
                f"chart {i} ({label}): series mismatch\n"
                f"    expected: {exp.get('series')}\n"
                f"    actual:   {act.get('series')}"
            )

    return issues
