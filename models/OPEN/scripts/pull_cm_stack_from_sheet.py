#!/usr/bin/env python3
"""Pull Seasonality tab + CM stack constants from the live spreadsheet into git.

The spreadsheet is the source of truth. Run this after manual sheet edits to
refresh models/OPEN/seasonality.py, models/OPEN/cm_seasonality.py, and the CM_* constants
in weekly_model_formulas.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from sheets import SheetsClient  # noqa: E402
from models.OPEN.cm_seasonality import CM_SEASONALITY_ROW_LABEL, CM_SEASONALITY_SHEET  # noqa: E402
from sheets.labels import WEEKLY  # noqa: E402
from models.OPEN.seasonality import ACQUISITION_PERCENT_LABEL  # noqa: E402
from models.OPEN.weekly_model_formulas import col_letter  # noqa: E402

WEEKLY_FORMULAS = PACK / "weekly_model_formulas.py"
CM_SEASONALITY = PACK / "cm_seasonality.py"
ACQUISITION_SEASONALITY = PACK / "seasonality.py"
N_COLS = 128  # B:DY


def _format_float(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        return "0.0"
    return text


def _format_monthly_tuple(name: str, values: list[float]) -> str:
    lines = [f"{name}: tuple[float, ...] = ("]
    for value in values:
        lines.append(f"    {_format_float(value)},")
    lines.append(")")
    return "\n".join(lines)


def _format_col_dict(name: str, mapping: dict[str, float]) -> str:
    lines = [f"{name}: dict[str, float] = {{"]
    for col, value in mapping.items():
        lines.append(f'    "{col}": {_format_float(value)},')
    lines.append("}")
    return "\n".join(lines)


def _replace_block(path: Path, start_marker: str, end_marker: str, new_block: str) -> None:
    text = path.read_text()
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    if not pattern.search(text):
        raise ValueError(f"Block not found in {path}: {start_marker!r}")
    path.write_text(pattern.sub(new_block, text, count=1))


def _label_rows_from_column(rows: list[list]) -> dict[str, int]:
    found: dict[str, int] = {}
    for idx, row in enumerate(rows, start=1):
        if row and row[0]:
            found[row[0]] = idx
    return found


def pull_seasonality_monthly(client: SheetsClient) -> list[float]:
    seasonality, monthly = client.batch_get(
        [f"{CM_SEASONALITY_SHEET}!A6", f"{CM_SEASONALITY_SHEET}!B6:M6"],
    )
    label_cell = seasonality[0][0] if seasonality and seasonality[0] else ""
    if label_cell != CM_SEASONALITY_ROW_LABEL:
        raise ValueError(f"Expected {CM_SEASONALITY_ROW_LABEL!r} in Seasonality!A6, got {label_cell!r}")
    row = monthly[0] if monthly else []
    return [float(v) for v in row]


def pull_acquisition_percent_monthly(client: SheetsClient) -> list[float]:
    seasonality, monthly = client.batch_get(
        [f"{CM_SEASONALITY_SHEET}!A2", f"{CM_SEASONALITY_SHEET}!B2:M2"],
    )
    label_cell = seasonality[0][0] if seasonality and seasonality[0] else ""
    if label_cell != ACQUISITION_PERCENT_LABEL:
        raise ValueError(
            f"Expected {ACQUISITION_PERCENT_LABEL!r} in Seasonality!A2, got {label_cell!r}"
        )
    row = monthly[0] if monthly else []
    return [float(v) for v in row]


def pull_weekly_cm_stack(client: SheetsClient) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    label_rows = client.batch_get([f"{WEEKLY}!A1:A65"])[0]
    labels = _label_rows_from_column(label_rows)
    end_col = col_letter(N_COLS + 1)

    def row_range(label: str) -> str:
        row = labels[label]
        return f"{WEEKLY}!B{row}:{end_col}{row}"

    cm_labels = (
        "Contribution Margin - Core",
        "Contribution Margin - Adjustments",
        "Contribution Margin Improvement - Core",
    )
    value_ranges = [row_range(label) for label in cm_labels]
    formula_ranges = value_ranges[:]
    value_rows = client.batch_get(value_ranges)
    formula_rows = client.batch_get(formula_ranges, as_formulas=True)

    def hardcoded_cells(values: list[list], formulas: list[list]) -> dict[str, float]:
        out: dict[str, float] = {}
        vals = values[0] if values else []
        forms = formulas[0] if formulas else []
        for idx, (formula, value) in enumerate(zip(forms, vals, strict=False)):
            if formula == "" and value == "":
                continue
            if isinstance(formula, (int, float)) or (
                isinstance(formula, str) and formula and not formula.startswith("=")
            ):
                out[col_letter(idx + 2)] = float(value)
        return out

    core = hardcoded_cells([value_rows[0]], [formula_rows[0]])
    adjustments = hardcoded_cells([value_rows[1]], [formula_rows[1]])
    anchors = hardcoded_cells([value_rows[2]], [formula_rows[2]])
    return core, adjustments, anchors


def write_cm_seasonality(monthly: list[float]) -> None:
    _replace_block(
        CM_SEASONALITY,
        "CM_SEASONAL_ADJ_BY_MONTH: tuple[float, ...] = (",
        ")",
        _format_monthly_tuple("CM_SEASONAL_ADJ_BY_MONTH", monthly),
    )


def write_acquisition_seasonality(monthly: list[float]) -> None:
    _replace_block(
        ACQUISITION_SEASONALITY,
        "ACQUISITION_PERCENT_BY_MONTH: tuple[float, ...] = (",
        ")",
        _format_monthly_tuple("ACQUISITION_PERCENT_BY_MONTH", monthly),
    )


def write_weekly_constants(
    core: dict[str, float],
    adjustments: dict[str, float],
    anchors: dict[str, float],
) -> None:
    _replace_block(
        WEEKLY_FORMULAS,
        "CM_CORE_VALUES: dict[str, float] = {",
        "}",
        _format_col_dict("CM_CORE_VALUES", core),
    )
    _replace_block(
        WEEKLY_FORMULAS,
        "CM_ADJUSTMENTS_VALUES: dict[str, float] = {",
        "}",
        _format_col_dict("CM_ADJUSTMENTS_VALUES", adjustments),
    )
    _replace_block(
        WEEKLY_FORMULAS,
        "CM_IMPROVEMENT_ANCHORS: dict[str, float] = {",
        "}",
        _format_col_dict("CM_IMPROVEMENT_ANCHORS", anchors),
    )


def main() -> None:
    client = SheetsClient(ticker="OPEN")
    acquisition = pull_acquisition_percent_monthly(client)
    monthly = pull_seasonality_monthly(client)
    core, adjustments, anchors = pull_weekly_cm_stack(client)
    write_acquisition_seasonality(acquisition)
    write_cm_seasonality(monthly)
    print(f"Updated {ACQUISITION_SEASONALITY.name} ({len(acquisition)} monthly values)")
    print(f"Updated {CM_SEASONALITY.name} ({len(monthly)} monthly values)")
    if not core and not adjustments and not anchors:
        print(
            "No hardcoded CM stack cells found on Weekly Financials — "
            "preserving repo CM_* constants"
        )
        return
    write_weekly_constants(core, adjustments, anchors)
    print(
        f"Updated {WEEKLY_FORMULAS.name}: "
        f"{len(core)} core anchor(s), {len(adjustments)} adjustment cell(s), "
        f"{len(anchors)} improvement anchor(s)"
    )


if __name__ == "__main__":
    main()
