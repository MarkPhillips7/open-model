#!/usr/bin/env python3
"""Pull CM seasonality + stack constants from the live spreadsheet into git.

The spreadsheet is the source of truth. Run this after manual sheet edits to
refresh sheets/cm_seasonality.py and the CM_* constants in weekly_model_formulas.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.cm_seasonality import CM_SEASONALITY_ROW_LABEL, CM_SEASONALITY_SHEET  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sheets.weekly_model_formulas import col_letter  # noqa: E402

WEEKLY_FORMULAS = ROOT / "sheets" / "weekly_model_formulas.py"
CM_SEASONALITY = ROOT / "sheets" / "cm_seasonality.py"


def _format_float(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        return "0.0"
    return text


def _format_monthly_tuple(values: list[float]) -> str:
    lines = ["CM_SEASONAL_ADJ_BY_MONTH: tuple[float, ...] = ("]
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


def pull_seasonality_monthly(client: SheetsClient) -> list[float]:
    ws = client.worksheet(CM_SEASONALITY_SHEET)
    label_cell = ws.get("A6", value_render_option="UNFORMATTED_VALUE")[0][0]
    if label_cell != CM_SEASONALITY_ROW_LABEL:
        raise ValueError(f"Expected {CM_SEASONALITY_ROW_LABEL!r} in Seasonality!A6, got {label_cell!r}")
    row = ws.get("B6:M6", value_render_option="UNFORMATTED_VALUE")[0]
    return [float(v) for v in row]


def pull_weekly_cm_stack(client: SheetsClient) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    labels = label_rows(client, WEEKLY, max_row=65)
    ws = client.worksheet(WEEKLY)
    n_cols = 128  # B:DY

    def row_values(label: str) -> list:
        row = labels[label]
        return ws.get(
            f"B{row}:{col_letter(n_cols + 1)}{row}",
            value_render_option="UNFORMATTED_VALUE",
        )[0]

    def row_formulas(label: str) -> list:
        row = labels[label]
        return ws.get(
            f"B{row}:{col_letter(n_cols + 1)}{row}",
            value_render_option="FORMULA",
        )[0]

    core: dict[str, float] = {}
    core_f = row_formulas("Contribution Margin - Core")
    core_v = row_values("Contribution Margin - Core")
    for idx, (formula, value) in enumerate(zip(core_f, core_v)):
        if isinstance(formula, (int, float)) or (isinstance(formula, str) and formula and not formula.startswith("=")):
            core[col_letter(idx + 2)] = float(value)

    adjustments: dict[str, float] = {}
    adj_f = row_formulas("Contribution Margin - Adjustments")
    adj_v = row_values("Contribution Margin - Adjustments")
    for idx, (formula, value) in enumerate(zip(adj_f, adj_v)):
        if formula == "" and value == "":
            continue
        if isinstance(formula, (int, float)) or (isinstance(formula, str) and formula and not formula.startswith("=")):
            adjustments[col_letter(idx + 2)] = float(value)

    anchors: dict[str, float] = {}
    imp_f = row_formulas("Contribution Margin Improvement - Core")
    imp_v = row_values("Contribution Margin Improvement - Core")
    for idx, (formula, value) in enumerate(zip(imp_f, imp_v)):
        if isinstance(formula, (int, float)) or (isinstance(formula, str) and formula and not formula.startswith("=")):
            anchors[col_letter(idx + 2)] = float(value)

    return core, adjustments, anchors


def write_cm_seasonality(monthly: list[float]) -> None:
    _replace_block(
        CM_SEASONALITY,
        "CM_SEASONAL_ADJ_BY_MONTH: tuple[float, ...] = (",
        ")",
        _format_monthly_tuple(monthly),
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
    client = SheetsClient()
    monthly = pull_seasonality_monthly(client)
    core, adjustments, anchors = pull_weekly_cm_stack(client)
    write_cm_seasonality(monthly)
    write_weekly_constants(core, adjustments, anchors)
    print(f"Updated {CM_SEASONALITY.name} ({len(monthly)} monthly values)")
    print(
        f"Updated {WEEKLY_FORMULAS.name}: "
        f"{len(core)} core anchor(s), {len(adjustments)} adjustment cell(s), "
        f"{len(anchors)} improvement anchor(s)"
    )


if __name__ == "__main__":
    main()
