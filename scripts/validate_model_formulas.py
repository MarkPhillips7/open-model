#!/usr/bin/env python3
"""Verify model formulas reference rows that match current sheet labels."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.labels import WEEKLY, label_rows  # noqa: E402
from sheets.weekly_model_formulas import (  # noqa: E402
    MODEL_FORMULA_LABELS,
    UNIFORM_FORMULA_TEMPLATES,
    column_relative_formula,
    formula_row_dependencies,
    row_cells_for_label,
    uniform_formula_template,
)

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


def collect_template_issues(label_to_row: dict[str, int]) -> list[str]:
    issues: list[str] = []
    for label in MODEL_FORMULA_LABELS:
        deps = formula_row_dependencies(label)
        missing = deps - set(label_to_row)
        if missing:
            issues.append(f"{label!r}: missing labels on sheet: {sorted(missing)}")
        try:
            uniform_formula_template(label)
        except KeyError:
            pass
        else:
            tmpl = uniform_formula_template(label)
            unresolved = _labels_from_template(tmpl) - set(label_to_row)
            if unresolved:
                issues.append(f"{label!r}: template labels not on sheet: {sorted(unresolved)}")
    return issues


def collect_generated_formula_issues(
    label_to_row: dict[str, int],
    *,
    sample_col: str = "F",
) -> list[str]:
    issues: list[str] = []
    n_cols = ord(sample_col) - ord("B") + 1
    for label in MODEL_FORMULA_LABELS:
        cells = row_cells_for_label(label, n_cols, label_to_row=label_to_row)
        if not cells:
            continue
        formula = cells[-1]
        if not isinstance(formula, str) or not formula.startswith("="):
            continue
        deps = formula_row_dependencies(label)
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


def collect_hardcoded_template_rows() -> list[str]:
    """Flag numeric weekly row literals in templates (should use {Label} placeholders)."""
    issues: list[str] = []
    from sheets.weekly_model_formulas import COLUMN_RELATIVE_TEMPLATES

    for label, tmpl in COLUMN_RELATIVE_TEMPLATES.items():
        if ROW_REF_IN_COLUMN_TEMPLATE.search(tmpl):
            issues.append(
                f"COLUMN_RELATIVE[{label!r}] uses {{c}}<row> — use {{c}}{{Label}} instead"
            )
    for label, tmpl in UNIFORM_FORMULA_TEMPLATES.items():
        issues.extend(_weekly_row_literal_issues(f"UNIFORM[{label!r}]", tmpl))
    return issues


def validate(client: SheetsClient | None = None, *, offline: bool = False) -> list[str]:
    issues: list[str] = []
    issues.extend(collect_hardcoded_template_rows())
    if offline:
        return issues

    client = client or SheetsClient()
    label_to_row = label_rows(client, WEEKLY)
    issues.extend(collect_template_issues(label_to_row))
    issues.extend(collect_generated_formula_issues(label_to_row))
    return issues


def main() -> None:
    offline = "--offline" in sys.argv
    issues = validate(offline=offline)
    if issues:
        print("Model formula validation FAILED:")
        for item in issues:
            print(f"  - {item}")
        sys.exit(1)
    suffix = " (offline template checks only)" if offline else ""
    print(f"Model formula validation passed{suffix}.")


if __name__ == "__main__":
    main()
