"""Canonical Quarterly Financials * - Model formulas for EOSE."""

from __future__ import annotations

import re
from typing import Any

from sheets.formulas import col_letter as _col_letter

from models.EOSE.cogs import (
    ADJ_GM_MODEL_LABEL,
    DEFAULT_HAIRCUT_PCT,
    DEFAULT_TERMINAL_UNIT_COGS,
    Q2_2026_CASH_OPEX,
    Q2_2026_NONCASH_COGS,
    UNIT_COGS_MODEL_LABEL,
    qf_index_formula,
)
from models.EOSE.layout import FIRST_VALUE_COL, FIRST_VALUE_COL_INDEX, N_QUARTERS, QUARTERLY

FINANCIALS_TAB = QUARTERLY
FIRST_VALUE_COL = FIRST_VALUE_COL
FIRST_VALUE_COL_INDEX = FIRST_VALUE_COL_INDEX
COLUMN_RELATIVE_TEMPLATES: dict[str, str] = {}

_LABEL_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")


def col_letter(n: int) -> str:
    return _col_letter(n)


def apply_row_labels(template: str, label_to_row: dict[str, int]) -> str:
    out = template
    for label in sorted(label_to_row, key=len, reverse=True):
        out = out.replace("{" + label + "}", str(label_to_row[label]))
    return out


def _prior(label: str) -> str:
    return f"OFFSET({{c}}{{{label}}},0,-1)"


def _prefer(actual: str, model: str) -> str:
    return f'IF({actual}<>"",{actual},{model})'


def _first_q() -> str:
    return "COLUMN()=3"


UNIFORM_FORMULA_TEMPLATES: dict[str, str] = {
    "Quarter ending": (
        '=IF({c}{Year}="","",EOMONTH(DATE({c}{Year},{c}{Quarter}*3,1),0))'
    ),
    "Years from present": (
        '=IF({c}{Quarter ending}="","",({c}{Quarter ending}-$C${As of date})/365)'
    ),
    "Pipeline - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'{_prefer(_prior("Pipeline"), _prior("Pipeline - Model"))})'
    ),
    "Pipeline (GWh) - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'{_prefer(_prior("Pipeline (GWh)"), _prior("Pipeline (GWh) - Model"))})'
    ),
    "Booked orders - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'{_prefer(_prior("Booked orders"), _prior("Booked orders - Model"))})'
    ),
    "Backlog - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'IF(AND({_prior("Backlog")}="",{_prior("Backlog - Model")}=""),"",'
        + _prefer(_prior("Backlog"), _prior("Backlog - Model"))
        + "+"
        + _prefer("{c}{Booked orders}", "{c}{Booked orders - Model}")
        + "-"
        + _prefer("{c}{Revenue}", "{c}{Revenue - Model}")
        + "))"
    ),
    "Backlog (GWh) - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'IF(AND({_prior("Backlog (GWh)")}="",{_prior("Backlog (GWh) - Model")}=""),"",'
        + _prefer(_prior("Backlog (GWh)"), _prior("Backlog (GWh) - Model"))
        + "+IFERROR("
        + _prefer("{c}{Booked orders}", "{c}{Booked orders - Model}")
        + "/{c}{Z3 ASP - Model},0)-{c}{GWh shipped - Model}))"
    ),
    "GWh shipped - Model": (
        f'=IF({{c}}{{Quarter}}="","",MIN({{c}}{{Factory capacity - Model}},'
        f'IF({_first_q()},0,IFERROR('
        + _prefer(_prior("Backlog (GWh)"), _prior("Backlog (GWh) - Model"))
        + "/{c}{Backlog conversion lag},0))))"
    ),
    "Z3 module cycle time - Model": (
        f'=IF({{c}}{{Quarter}}="","",MAX($C${{Cycle time floor}},'
        f'IF(COLUMN()<=4,18,'
        f'{_prior("Z3 module cycle time - Model")}*(1-{{c}}{{Quarterly module cycle time reduction rate}}/100))))'
    ),
    "Z3 manufacturing lines utilized - Model": (
        "={c}{Z3 manufacturing lines - Model}*{c}{Capacity utilization}/100"
    ),
    "Full utilization weeks per year": "=365/7",
    "Module production count per line - Model": (
        "={c}{Full utilization weeks per year}*{c}{Full utilization days per week}"
        "*{c}{Full utilization hours per day}*3600/"
        f'{_prefer("{c}{Z3 module cycle time}","{c}{Z3 module cycle time - Model}")}'
        "/1000000"
    ),
    "Capacity per line - Model": (
        "={c}{Z3 Module Energy Capacity}*{c}{Module production count per line - Model}"
        "*{c}{Capacity utilization}/100"
    ),
    "Annualized module energy capacity - Model": (
        "={c}{Capacity per line - Model}*{c}{Z3 manufacturing lines - Model}"
    ),
    "Factory capacity - Model": (
        "={c}{Z3 Module Energy Capacity}*{c}{Module production count per line - Model}"
        "*{c}{Z3 manufacturing lines utilized - Model}/4"
    ),
    "Effective 45x credit - Model": (
        "={c}{45x & active electrode credits}*{c}{45x transfer rate}/100"
    ),
    "Government credits - Model": (
        "={c}{Effective 45x credit - Model}*{c}{GWh shipped - Model}"
    ),
    "Unit COGS w/ 45x - Model": (
        "={c}{Unit COGS - Model}-{c}{Effective 45x credit - Model}"
    ),
    "Revenue - Model": "={c}{GWh shipped - Model}*{c}{Z3 ASP - Model}",
    "COGS - Model": (
        "={c}{Unit COGS - Model}*{c}{GWh shipped - Model}-{c}{Government credits - Model}"
        "+$C${Non-cash COGS (D&A + SBC)}"
    ),
    "Gross profit - Model": "={c}{Revenue - Model}-{c}{COGS - Model}",
    "Gross margin": '=IF(N({c}{Revenue})=0,"",{c}{Gross profit}/{c}{Revenue}*100)',
    "Gross margin - Model": (
        '=IF(N({c}{Revenue - Model})=0,"",{c}{Gross profit - Model}/{c}{Revenue - Model}*100)'
    ),
    "Adjusted gross profit - Model": (
        "={c}{Revenue - Model}*{c}{Adjusted gross margin - Model}/100"
    ),
    "Adjusted gross margin": (
        '=IF(OR({c}{Adjusted gross profit}="",N({c}{Revenue})=0),"",'
        "{c}{Adjusted gross profit}/{c}{Revenue}*100)"
    ),
    "Adjusted gross margin - Model": qf_index_formula(ADJ_GM_MODEL_LABEL),
    "SG&A - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'{_prefer(_prior("SG&A"), _prior("SG&A - Model"))})'
    ),
    "R&D - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'{_prefer(_prior("R&D"), _prior("R&D - Model"))})'
    ),
    "OpEx - Model": "={c}{SG&A - Model}+{c}{R&D - Model}",
    "Adjusted EBITDA - Model": (
        "={c}{Adjusted gross profit - Model}-$C${Cash OpEx run-rate}"
    ),
    "Operating cash flow - Model": "={c}{Adjusted EBITDA - Model}",
    "Adjusted EBITDA margin": (
        '=IF(N({c}{Revenue})=0,"",{c}{Adjusted EBITDA}/{c}{Revenue}*100)'
    ),
    "Adjusted EBITDA margin - Model": (
        '=IF(N({c}{Revenue - Model})=0,"",'
        "{c}{Adjusted EBITDA - Model}/{c}{Revenue - Model}*100)"
    ),
    "Annualized EBITDA - Model": "={c}{Adjusted EBITDA - Model}*4",
    "GAAP net income - Model": (
        "={c}{Adjusted EBITDA - Model}-$C${Net interest run-rate}"
    ),
    "Capex - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),0,'
        f'MAX(0,{{c}}{{Z3 manufacturing lines - Model}}-{_prior("Z3 manufacturing lines - Model")})'
        "*$C${Capex per incremental line})"
    ),
    "Cash - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        + _prefer(_prior("Cash"), _prior("Cash - Model"))
        + "+{c}{Adjusted EBITDA - Model}-{c}{Capex - Model}-$C${Net interest run-rate})"
    ),
    "Total debt - Model": (
        f'=IF({{c}}{{Quarter}}="","",IF({_first_q()},1000,'
        f'IF({_prior("Total debt")}<>"",{_prior("Total debt")},'
        f'IF({_prior("Total debt - Model")}<>"",{_prior("Total debt - Model")},1000))))'
    ),
    "Net debt - Model": (
        "={c}{Total debt - Model}-"
        + _prefer("{c}{Cash}", "{c}{Cash - Model}")
    ),
    "Fully diluted shares - Model": (
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),"",'
        f'{_prefer(_prior("Fully diluted shares"), _prior("Fully diluted shares - Model"))})'
    ),
    "Stock price": (
        '=IF(OR({c}{Quarter ending}="",{c}{Quarter ending}>TODAY()),"",'
        "IFERROR(XLOOKUP({c}{Quarter ending},"
        "'Price History'!A:A,'Price History'!E:E,\"\",-1),\"\"))"
    ),
    "Market cap": (
        '=IF(OR({c}{Stock price}="",N({c}{Fully diluted shares})=0),"",'
        "{c}{Stock price}*{c}{Fully diluted shares}/1000)"
    ),
    "Enterprise value - Model": (
        '=IF(N({c}{Annualized EBITDA - Model})<=0,"",'
        "{c}{Annualized EBITDA - Model}*{c}{EV / EBITDA}/1000)"
    ),
    "Market cap - Model": (
        '=IF({c}{Enterprise value - Model}="","",'
        "{c}{Enterprise value - Model}-{c}{Net debt - Model}/1000)"
    ),
    "Implied future stock price - Model": (
        '=IF(OR({c}{Market cap - Model}="",N({c}{Fully diluted shares - Model})=0),"",'
        "{c}{Market cap - Model}/{c}{Fully diluted shares - Model}*1000)"
    ),
    "Present stock price discounted - Model": (
        '=IF(OR({c}{Implied future stock price - Model}="",{c}{Years from present}=""),"",'
        "-PV({c}{Discount rate}/100,{c}{Years from present},0,"
        "{c}{Implied future stock price - Model}))"
    ),
    "Backlog conversion lag": "=$C${Backlog conversion lag}",
    "Z3 Module Energy Capacity": "=$C${Z3 Module Energy Capacity}",
    "Z3 modules per cube": "=$C${Z3 modules per cube}",
    "Capacity utilization": "=$C${Capacity utilization}",
    "Full utilization days per week": "=$C${Full utilization days per week}",
    "Full utilization hours per day": "=$C${Full utilization hours per day}",
    "Quarterly module cycle time reduction rate": (
        "=$C${Quarterly module cycle time reduction rate}"
    ),
    "45x & active electrode credits": "=$C${45x & active electrode credits}",
    "45x transfer rate": "=$C${45x transfer rate}",
    "Percent of Guided Cost Cutting Achieved": (
        "=$C${Percent of Guided Cost Cutting Achieved}"
    ),
    "Terminal unit COGS": "=$C${Terminal unit COGS}",
    "Unit COGS - Model": qf_index_formula(UNIT_COGS_MODEL_LABEL),
    "Non-cash COGS (D&A + SBC)": "=$C${Non-cash COGS (D&A + SBC)}",
    "Cash OpEx run-rate": "=$C${Cash OpEx run-rate}",
    "EV / EBITDA": "=$C${EV / EBITDA}",
    "Discount rate": "=$C${Discount rate}",
}

MODEL_FORMULA_LABELS: tuple[str, ...] = tuple(UNIFORM_FORMULA_TEMPLATES)


def formula_row_dependencies(label: str) -> frozenset[str]:
    tmpl = UNIFORM_FORMULA_TEMPLATES.get(label, "")
    return frozenset(
        m.group(1)
        for m in _LABEL_PLACEHOLDER_RE.finditer(tmpl)
        if m.group(1) != "c"
    )


def uniform_formula_template(label: str) -> str:
    return UNIFORM_FORMULA_TEMPLATES[label]


# Seed in C; D:Z copy `=$C$row`. Column C must stay the number (not a self-ref).
COPY_FROM_C_LABELS: frozenset[str] = frozenset(
    {
        "Backlog conversion lag",
        "Z3 Module Energy Capacity",
        "Z3 modules per cube",
        "Capacity utilization",
        "Full utilization days per week",
        "Full utilization hours per day",
        "Quarterly module cycle time reduction rate",
        "45x & active electrode credits",
        "45x transfer rate",
        "Percent of Guided Cost Cutting Achieved",
        "Terminal unit COGS",
        "Non-cash COGS (D&A + SBC)",
        "Cash OpEx run-rate",
        "EV / EBITDA",
        "Discount rate",
    }
)


def row_cells_for_label(
    label: str,
    n_cols: int,
    *,
    label_to_row: dict[str, int] | None = None,
) -> list[Any] | None:
    if label not in UNIFORM_FORMULA_TEMPLATES:
        return None
    label_to_row = label_to_row or {}
    resolved = apply_row_labels(UNIFORM_FORMULA_TEMPLATES[label], label_to_row)
    if label in COPY_FROM_C_LABELS:
        return [None] + [resolved] * max(0, n_cols - 1)
    cells: list[Any] = []
    for i in range(n_cols):
        col = col_letter(FIRST_VALUE_COL_INDEX + i)
        cells.append(resolved.replace("{c}", col))
    return cells


# Default assumption values written to column C (column B is units only).
COLUMN_C_DEFAULTS: dict[str, Any] = {
    "Backlog conversion lag": 4,
    "Z3 Module Energy Capacity": 1.19047619,
    "Z3 modules per cube": 672,
    "Capacity utilization": 85,
    "Full utilization days per week": 7,
    "Full utilization hours per day": 24,
    "Quarterly module cycle time reduction rate": 2.9,
    "45x & active electrode credits": 47,
    "45x transfer rate": 90,
    "Percent of Guided Cost Cutting Achieved": DEFAULT_HAIRCUT_PCT,
    "Terminal unit COGS": DEFAULT_TERMINAL_UNIT_COGS,
    "Non-cash COGS (D&A + SBC)": Q2_2026_NONCASH_COGS,
    "Cash OpEx run-rate": Q2_2026_CASH_OPEX,
    "EV / EBITDA": 30,
    "Discount rate": 20,
}

assert COPY_FROM_C_LABELS == frozenset(COLUMN_C_DEFAULTS)
assert N_QUARTERS == 24
