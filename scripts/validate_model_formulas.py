#!/usr/bin/env python3
"""Verify model formulas reference rows that match current sheet labels."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sheets.registry import load_pack_module, parse_ticker_argv, pack_dir, resolve_ticker  # noqa: E402

# Placeholders that are not Weekly Financials row labels.
NON_LABEL_PLACEHOLDERS = frozenset(
    {
        "c",
        "cp",
        "opex",
        "sbc",
        "interest",
        "da",
        "tax",
        "gaap_row",
        "shares_row",
        "adj_ni",
        "debt",
        "interest_gaap",
        "other_income",
        "net_interest",
    }
)

ROW_REF_IN_COLUMN_TEMPLATE = re.compile(r"\{c\}\d+")
# Weekly row refs like $9: or INDEX($11: but not Transitions!$B$2
WEEKLY_DOLLAR_ROW = re.compile(r"(?<!Transitions!)\$(\d+)(?=:)")
INDEX_DOLLAR_ROW = re.compile(r"INDEX\(\$(\d+):")


def _labels_from_template(template: str) -> set[str]:
    return {
        m.group(1)
        for m in re.finditer(r"\{([^{}]+)\}", template)
        if m.group(1) not in NON_LABEL_PLACEHOLDERS
    }


def normalize_formula(value: object) -> str:
    if not isinstance(value, str):
        return str(value)
    return re.sub(r"\s+", "", value.strip())


def collect_template_issues(wfm: ModuleType, label_to_row: dict[str, int]) -> list[str]:
    issues: list[str] = []
    for label in wfm.MODEL_FORMULA_LABELS:
        deps = wfm.formula_row_dependencies(label)
        missing = deps - set(label_to_row)
        if missing:
            issues.append(f"{label!r}: missing labels on sheet: {sorted(missing)}")
        try:
            wfm.uniform_formula_template(label)
        except KeyError:
            pass
        else:
            tmpl = wfm.uniform_formula_template(label)
            unresolved = _labels_from_template(tmpl) - set(label_to_row)
            if unresolved:
                issues.append(f"{label!r}: template labels not on sheet: {sorted(unresolved)}")
    return issues


def collect_generated_formula_issues(
    wfm: ModuleType,
    label_to_row: dict[str, int],
    *,
    sample_col: str = "F",
) -> list[str]:
    issues: list[str] = []
    n_cols = ord(sample_col) - ord("B") + 1
    for label in wfm.MODEL_FORMULA_LABELS:
        cells = wfm.row_cells_for_label(label, n_cols, label_to_row=label_to_row)
        if not cells:
            continue
        formula = cells[-1]
        if not isinstance(formula, str) or not formula.startswith("="):
            continue
        deps = wfm.formula_row_dependencies(label)
        if not deps:
            continue
        for dep_label in deps:
            expected = label_to_row[dep_label]
            cell_ref = f"{sample_col}{expected}"
            if cell_ref not in formula and f"${expected}" not in formula:
                issues.append(
                    f"{label!r}: generated formula for col {sample_col} "
                    f"does not reference {cell_ref} ({dep_label!r})"
                )
    return issues


def collect_live_formula_drift(
    wfm: ModuleType,
    client: SheetsClient,
    label_to_row: dict[str, int],
    *,
    max_row: int = 120,
) -> list[str]:
    """Compare live * - Model formulas to repo templates (catches un-synced manual edits)."""
    del max_row  # kept for call-site compatibility
    n_cols = 128  # B:DY
    end_col = wfm.col_letter(n_cols + 1)
    model_labels = [label for label in wfm.MODEL_FORMULA_LABELS if label in label_to_row]
    ranges = [f"{WEEKLY}!B{label_to_row[label]}:{end_col}{label_to_row[label]}" for label in model_labels]
    if not ranges:
        return []
    live_rows = client.batch_get(ranges, as_formulas=True)
    issues: list[str] = []

    for label, live_grid in zip(model_labels, live_rows, strict=True):
        cells = wfm.row_cells_for_label(label, n_cols, label_to_row=label_to_row)
        if cells is None:
            continue
        row_num = label_to_row[label]
        live_row = live_grid[0] if live_grid else []
        for col_idx, expected in enumerate(cells):
            live = live_row[col_idx] if col_idx < len(live_row) else ""
            if isinstance(expected, str) and expected.startswith("="):
                if normalize_formula(expected) != normalize_formula(live):
                    col = wfm.col_letter(col_idx + 2)
                    issues.append(
                        f"{label!r} row {row_num} col {col}: live sheet differs from "
                        f"repo template (update models/{{TICKER}}/*.py or run restore after fixing repo)"
                    )
                    break
            elif expected != "" and expected != live:
                col = wfm.col_letter(col_idx + 2)
                issues.append(
                    f"{label!r} row {row_num} col {col}: live value {live!r} != repo {expected!r}"
                )
                break
    return issues


def _weekly_row_literal_issues(label: str, tmpl: str) -> list[str]:
    """Find $N weekly row literals outside Transitions! references."""
    issues: list[str] = []
    for part in re.split(r"Transitions![^)\s]*", tmpl):
        for pat in (WEEKLY_DOLLAR_ROW, INDEX_DOLLAR_ROW):
            for match in pat.finditer(part):
                issues.append(
                    f"{label}: hardcoded weekly row ${match.group(1)} "
                    f"(use {{Label Name}} placeholder)"
                )
    return issues


def collect_hardcoded_template_rows(wfm: ModuleType) -> list[str]:
    """Flag numeric weekly row literals in templates (should use {Label} placeholders)."""
    issues: list[str] = []
    for label, tmpl in wfm.COLUMN_RELATIVE_TEMPLATES.items():
        if ROW_REF_IN_COLUMN_TEMPLATE.search(tmpl):
            issues.append(
                f"COLUMN_RELATIVE[{label!r}] uses {{c}}<row> — use {{c}}{{Label}} instead"
            )
    for label, tmpl in wfm.UNIFORM_FORMULA_TEMPLATES.items():
        issues.extend(_weekly_row_literal_issues(f"UNIFORM[{label!r}]", tmpl))
    return issues


def validate(
    client: SheetsClient | None = None,
    *,
    ticker: str | None = None,
    offline: bool = False,
    check_live_drift: bool = True,
) -> list[str]:
    resolved = resolve_ticker(ticker or (client.ticker if client else None))
    wfm = load_pack_module(resolved, "weekly_model_formulas")
    issues: list[str] = []
    issues.extend(collect_hardcoded_template_rows(wfm))
    if offline:
        return issues

    client = client or SheetsClient(ticker=resolved)
    label_to_row = label_rows(client, WEEKLY, max_row=120)
    issues.extend(collect_template_issues(wfm, label_to_row))
    issues.extend(collect_generated_formula_issues(wfm, label_to_row))
    if check_live_drift:
        issues.extend(collect_live_formula_drift(wfm, client, label_to_row))
    return issues


def main() -> None:
    ticker_arg, rest = parse_ticker_argv()
    ticker = resolve_ticker(ticker_arg)
    if not (pack_dir(ticker) / "weekly_model_formulas.py").is_file():
        print(f"No weekly_model_formulas.py in {ticker} pack — skip.")
        return
    offline = "--offline" in rest
    check_live_drift = "--skip-drift" not in rest
    unknown = [a for a in rest if a not in {"--offline", "--skip-drift"}]
    if unknown:
        print(f"Unknown arguments: {unknown}")
        sys.exit(2)
    issues = validate(ticker=ticker, offline=offline, check_live_drift=check_live_drift)
    if issues:
        print("Model formula validation FAILED:")
        for item in issues:
            print(f"  - {item}")
        sys.exit(1)
    suffix = " (offline template checks only)" if offline else ""
    if not check_live_drift:
        suffix += " (live drift check skipped)"
    print(f"Model formula validation passed for {ticker}{suffix}.")


if __name__ == "__main__":
    main()
