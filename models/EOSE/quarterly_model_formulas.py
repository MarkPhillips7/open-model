"""Canonical Quarterly Financials * - Model formulas for EOSE."""

from __future__ import annotations

import re
from typing import Any

from sheets.formulas import col_letter as _col_letter

from models.EOSE.cogs import (
    DEFAULT_HAIRCUT_PCT,
    Q2_2026_CASH_OPEX,
    Q2_2026_NONCASH_COGS,
    cogs_c_ref,
)
from models.EOSE.layout import (
    ADJ_GM_MODEL_ADD_PTS,
    ADJ_GM_MODEL_CAP,
    ASP_MODEL_HOLD_FROM_COL,
    ASP_MODEL_QOQ,
    ASP_MODEL_START,
    BACKLOG_GWH_2024,
    BOOKED_ORDERS_GWH_KEY,
    BOOKED_ORDERS_M_KEY,
    CAPACITY_UTILIZATION_COMPLETED,
    CELL_MODULE_CREDIT_LABEL,
    CELL_MODULE_CREDIT_PER_KWH,
    COST_OUT_PROGRESS_LABEL,
    DILUTION_PROCEEDS_FRACTION,
    EBITDA_200M_GUIDED_LABEL,
    EBITDA_200M_MODEL_LABEL,
    FD_SHARES_MODEL_QOQ,
    FIRST_VALUE_COL,
    FIRST_VALUE_COL_INDEX,
    GUIDED_ADJ_GM_MODEL_LABEL,
    MWH_SHIPPED_BACKLOG_LAG_LABEL,
    MWH_SHIPPED_MAX_FACTORY_LABEL,
    MWH_SHIPPED_MODEL_LABEL,
    MWH_SHIPPED_PTC_LABEL,
    N_QUARTERS,
    PTC_LABEL,
    QUARTERLY,
    SCALE_BLEND_LABEL,
    STATUTORY_PTC_LABEL,
    TOTAL_DEBT_MODEL_QOQ,
    label_map_from_ab,
    live_quarterly_ab,
    require_live_layout_match,
)

CAPACITY_UTILIZATION_LABEL = "Capacity utilization"

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


def sheet_label_map(client: Any) -> dict[str, int]:
    """Live A:B map with first-match bare labels plus ``label [units]`` keys."""
    return label_map_from_ab(live_quarterly_ab(client))


def assert_live_layout(client: Any, *, action: str = "restore model formulas") -> None:
    require_live_layout_match(client, action=action)


def _prior(label: str) -> str:
    return f"OFFSET({{c}}{{{label}}},0,-1)"


def _prefer(actual: str, model: str) -> str:
    return f'IF({actual}<>"",{actual},{model})'


def _first_q() -> str:
    return "COLUMN()=3"


def _cost_out_progress_formula() -> str:
    y = cogs_c_ref("Cost-out start year")
    q = cogs_c_ref("Cost-out start quarter")
    ey = cogs_c_ref("Cost-out complete year")
    eq = cogs_c_ref("Cost-out complete quarter")
    return (
        f'=IF(OR({{c}}{{Year}}="",{y}=""),"",'
        f"MIN(1,MAX(0,(({{c}}{{Year}}-{y})*4+{{c}}{{Quarter}}-{q})"
        f"/MAX(1,({ey}-{y})*4+({eq}-{q})))))"
    )


def _adj_gm_formula(*, guided: bool) -> str:
    start = cogs_c_ref("Starting adjusted gross margin")
    total = cogs_c_ref("Total guided cost-out")
    progress = f"{{c}}{{{COST_OUT_PROGRESS_LABEL}}}"
    pts = total if guided else (
        f"({total}*$C${{Percent of Guided Cost Cutting Achieved}}/100)"
    )
    return f'=IF({progress}="","",{start}+{progress}*{pts})'


def _adj_gm_model_formula() -> str:
    """Copy actual adj. GM through 2026 Q2; after cost-out complete +5 pts/q (cap 30%); else haircut path."""
    start = cogs_c_ref("Starting adjusted gross margin")
    total = cogs_c_ref("Total guided cost-out")
    progress = f"{{c}}{{{COST_OUT_PROGRESS_LABEL}}}"
    prior_progress = f"{{cp}}{{{COST_OUT_PROGRESS_LABEL}}}"
    haircut = (
        f"{start}+{progress}*({total}*$C${{Percent of Guided Cost Cutting Achieved}}/100)"
    )
    grown = (
        f"min({ADJ_GM_MODEL_CAP},"
        f"{{cp}}{{Adjusted gross margin - Model}}+{ADJ_GM_MODEL_ADD_PTS})"
    )
    return (
        f'=IF({progress}="","",'
        f"if(column()<{ASP_MODEL_HOLD_FROM_COL},{{c}}{{Adjusted gross margin}},"
        f"if({prior_progress}=1,{grown},{haircut})))"
    )


def _scale_blend_formula() -> str:
    start = cogs_c_ref("Scale absorption start lines")
    end = cogs_c_ref("Scale absorption complete lines")
    lines = "{c}{Z3 manufacturing lines - Model}"
    progress = f"{{c}}{{{COST_OUT_PROGRESS_LABEL}}}"
    return (
        f'=IF({progress}="","",'
        f"IF({progress}<1,0,MIN(1,MAX(0,({lines}-{start})"
        f"/MAX(0.001,{end}-{start})))))"
    )


def _unit_cogs_formula() -> str:
    asp = "{c}{Z3 ASP - Model}"
    credit = "{c}{Effective 45x credit - Model}"
    terminal = cogs_c_ref("Terminal unit COGS")
    gm = "{c}{Adjusted gross margin - Model}"
    blend = f"{{c}}{{{SCALE_BLEND_LABEL}}}"
    progress = f"{{c}}{{{COST_OUT_PROGRESS_LABEL}}}"
    raw = f"({asp}*(1-{gm}/100)+{credit})"
    return (
        f'=IF(OR({gm}="",{asp}=""),"",'
        f"IF({progress}<1,{raw},{raw}*(1-{blend})+{terminal}*{blend}))"
    )


def _ebitda_at_200m(gm_label: str) -> str:
    rev = cogs_c_ref("$200M quarterly revenue (illustration)")
    opex = "$C${Cash OpEx run-rate}"
    return f'=IF({{c}}{{{gm_label}}}="","",{rev}*{{c}}{{{gm_label}}}/100-{opex})'


UNIFORM_FORMULA_TEMPLATES: dict[str, str] = {
    "Quarter ending": (
        '=IF({c}{Year}="","",EOMONTH(DATE({c}{Year},{c}{Quarter}*3,1),0))'
    ),
    "Years from present": (
        '=IF({c}{Quarter ending}="","",({c}{Quarter ending}-$C${As of date})/365)'
    ),
    "Pipeline - Model": (
        f'=IF({{c}}{{Quarter}}="","",'
        f"IF(COLUMN()=3,{{c}}{{Pipeline}},"
        f'{_prior("Pipeline - Model")}*(1+{{c}}{{Pipeline quarterly growth rate}}/100)))'
    ),
    "Pipeline (GWh) - Model": (
        '=IF({c}{Quarter}="","",IFERROR(1000*{c}{Pipeline - Model}/{c}{Z3 ASP - Model},""))'
    ),
    "Booked orders - Model": (
        "=IF({c}{" + BOOKED_ORDERS_M_KEY + '}="",'
        "{cp}{Booked orders - Model}*1.2,"
        "{c}{" + BOOKED_ORDERS_M_KEY + "})"
    ),
    "Backlog - Model": (
        "=IF(column()=3,$C${Backlog},{cp}{Backlog - Model}*1.03)"
    ),
    "Backlog (GWh) - Model": "={c}{Backlog - Model}/{c}{Z3 ASP - Model}",
    "Z3 ASP - Derived": (
        "=if(n({c}{" + BOOKED_ORDERS_GWH_KEY + "})=0,"
        'if(n({c}{Pipeline (GWh)})=0,"",'
        "{c}{Pipeline}*1000/{c}{Pipeline (GWh)}),"
        "{c}{" + BOOKED_ORDERS_M_KEY + "}/{c}{" + BOOKED_ORDERS_GWH_KEY + "})"
    ),
    "Z3 ASP - Model": (
        f"=if(column()=3,{ASP_MODEL_START},"
        f"if(column()<{ASP_MODEL_HOLD_FROM_COL},"
        f"{{cp}}{{Z3 ASP - Model}}*{ASP_MODEL_QOQ},"
        f"{{cp}}{{Z3 ASP - Model}}))"
    ),
    "Z3 module cycle time - Model": (
        f'=IF({{c}}{{Quarter}}="","",MAX($C${{Cycle time floor}},'
        f"IF(COLUMN()<=4,18,"
        f'{_prior("Z3 module cycle time - Model")}*(1-{{c}}{{Quarterly module cycle time reduction rate}}/100))))'
    ),
    "Z3 manufacturing lines utilized - Model": (
        "={c}{Z3 manufacturing lines - Model}*{c}{Capacity utilization}/100"
    ),
    "Full utilization weeks per year": "=365/7",
    "Module production count per line - Model": (
        "={c}{Full utilization weeks per year}*{c}{Full utilization days per week}"
        "*{c}{Full utilization hours per day}*3600/"
        'IF({c}{Z3 module cycle time}<>"",{c}{Z3 module cycle time},'
        "{c}{Z3 module cycle time - Model})/1000000"
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
        f'=IF({{c}}{{{PTC_LABEL}}}<>"",{{c}}{{{PTC_LABEL}}},'
        f'IF(OR({{c}}{{{MWH_SHIPPED_MODEL_LABEL}}}="",'
        f'N({{c}}{{{MWH_SHIPPED_MODEL_LABEL}}})=0),"",'
        f"{{c}}{{Effective 45x credit - Model}}*{{c}}{{{MWH_SHIPPED_MODEL_LABEL}}}/1000))"
    ),
    STATUTORY_PTC_LABEL: (
        f'=IF(OR({{c}}{{{PTC_LABEL}}}="",N({{c}}{{{PTC_LABEL}}})=0),"",'
        f"{{c}}{{{PTC_LABEL}}}/({{c}}{{45x transfer rate}}/100))"
    ),
    MWH_SHIPPED_PTC_LABEL: (
        f'=IF(OR({{c}}{{{STATUTORY_PTC_LABEL}}}="",'
        f'N({{c}}{{{STATUTORY_PTC_LABEL}}})=0),"",'
        f"{{c}}{{{STATUTORY_PTC_LABEL}}}*1000/{{c}}{{{CELL_MODULE_CREDIT_LABEL}}})"
    ),
    MWH_SHIPPED_BACKLOG_LAG_LABEL: (
        # Look back *lag* quarters (not 1); divide by lag so that vintage is
        # spread across the conversion window. Pre-C columns use 2024 prints.
        f'=IF({{c}}{{Quarter}}="","",'
        f"IFERROR("
        f"IF(COLUMN()-{{c}}{{Backlog conversion lag}}<{FIRST_VALUE_COL_INDEX},"
        f"CHOOSE(COLUMN()-{{c}}{{Backlog conversion lag}}+2,"
        f"{','.join(str(g) for g in BACKLOG_GWH_2024)}),"
        f'IF(OFFSET({{c}}{{Backlog (GWh)}},0,-{{c}}{{Backlog conversion lag}})<>"",'
        f"OFFSET({{c}}{{Backlog (GWh)}},0,-{{c}}{{Backlog conversion lag}}),"
        f"OFFSET({{c}}{{Backlog (GWh) - Model}},0,-{{c}}{{Backlog conversion lag}}))"
        f")/{{c}}{{Backlog conversion lag}}*1000,0))"
    ),
    MWH_SHIPPED_MAX_FACTORY_LABEL: (
        '=IF({c}{Quarter}="","",{c}{Factory capacity - Model}*1000)'
    ),
    MWH_SHIPPED_MODEL_LABEL: (
        f'=IF({{c}}{{Quarter}}="","",'
        f"MIN({{c}}{{{MWH_SHIPPED_BACKLOG_LAG_LABEL}}},"
        f"{{c}}{{{MWH_SHIPPED_MAX_FACTORY_LABEL}}}))"
    ),
    "Unit COGS - Derived": (
        f'=IF(OR({{c}}{{{MWH_SHIPPED_PTC_LABEL}}}="",'
        f'N({{c}}{{{MWH_SHIPPED_PTC_LABEL}}})=0),"",'
        f"{{c}}{{COGS}}*1000/{{c}}{{{MWH_SHIPPED_PTC_LABEL}}})"
    ),
    "Unit COGS w/ 45x - Model": (
        "={c}{Unit COGS - Model}-{c}{Effective 45x credit - Model}"
    ),
    "Revenue - Model": (
        f'=IF(OR({{c}}{{{MWH_SHIPPED_MODEL_LABEL}}}="",'
        f'N({{c}}{{{MWH_SHIPPED_MODEL_LABEL}}})=0),"",'
        f"{{c}}{{{MWH_SHIPPED_MODEL_LABEL}}}/1000*{{c}}{{Z3 ASP - Model}})"
    ),
    "COGS - Model": (
        f'=IF(OR({{c}}{{{MWH_SHIPPED_MODEL_LABEL}}}="",'
        f'N({{c}}{{{MWH_SHIPPED_MODEL_LABEL}}})=0),"",'
        f"{{c}}{{Unit COGS - Model}}*{{c}}{{{MWH_SHIPPED_MODEL_LABEL}}}/1000"
        "-{c}{Government credits - Model}+$C${Non-cash COGS (D&A + SBC)})"
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
    "Adjusted gross margin - Model": _adj_gm_model_formula(),
    COST_OUT_PROGRESS_LABEL: _cost_out_progress_formula(),
    GUIDED_ADJ_GM_MODEL_LABEL: _adj_gm_formula(guided=True),
    SCALE_BLEND_LABEL: _scale_blend_formula(),
    EBITDA_200M_GUIDED_LABEL: _ebitda_at_200m(GUIDED_ADJ_GM_MODEL_LABEL),
    EBITDA_200M_MODEL_LABEL: _ebitda_at_200m("Adjusted gross margin - Model"),
    "SG&A - Model": (
        "=IF(n({c}{SG&A})=0,{cp}{SG&A - Model},{c}{SG&A})"
    ),
    "R&D - Model": (
        "=IF(n({c}{R&D})=0,{cp}{R&D - Model},{c}{R&D})"
    ),
    "OpEx - Model": (
        "=IF(n({c}{OpEx})=0,{cp}{OpEx - Model},{c}{OpEx})"
    ),
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
        f'=IF(OR({{c}}{{Quarter}}="",{_first_q()}),{{c}}{{Cash}},'
        + _prefer(_prior("Cash"), _prior("Cash - Model"))
        + "+{c}{Adjusted EBITDA - Model}-{c}{Capex - Model}-$C${Net interest run-rate}"
        + "+{c}{Total debt - Model}-{cp}{Total debt - Model}"
        + "+({c}{Fully diluted shares - Model}-{cp}{Fully diluted shares - Model})"
        f"*{{cp}}{{Stock price}}*{DILUTION_PROCEEDS_FRACTION})"
    ),
    "Total debt - Model": (
        "=IF(n({c}{Total debt})=0,"
        f"{{cp}}{{Total debt - Model}}*{TOTAL_DEBT_MODEL_QOQ},"
        "{c}{Total debt})"
    ),
    "Net debt - Model": (
        "={c}{Total debt - Model}-"
        + _prefer("{c}{Cash}", "{c}{Cash - Model}")
    ),
    "Fully diluted shares - Model": (
        "=IF(n({c}{Fully diluted shares})=0,"
        f"{{cp}}{{Fully diluted shares - Model}}*{FD_SHARES_MODEL_QOQ},"
        "{c}{Fully diluted shares})"
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
    # Completed prints are hardcoded; later columns copy prior (see row_cells_for_label).
    CAPACITY_UTILIZATION_LABEL: "={cp}{" + CAPACITY_UTILIZATION_LABEL + "}",
    "Full utilization days per week": "=$C${Full utilization days per week}",
    "Full utilization hours per day": "=$C${Full utilization hours per day}",
    "Quarterly module cycle time reduction rate": (
        "=$C${Quarterly module cycle time reduction rate}"
    ),
    CELL_MODULE_CREDIT_LABEL: "=$C${" + CELL_MODULE_CREDIT_LABEL + "}",
    "45x & active electrode credits": "=$C${45x & active electrode credits}",
    "45x transfer rate": "=$C${45x transfer rate}",
    "Percent of Guided Cost Cutting Achieved": (
        "=$C${Percent of Guided Cost Cutting Achieved}"
    ),
    "Unit COGS - Model": _unit_cogs_formula(),
    "Non-cash COGS (D&A + SBC)": "=$C${Non-cash COGS (D&A + SBC)}",
    "Cash OpEx run-rate": "=$C${Cash OpEx run-rate}",
    "EV / EBITDA": "=$C${EV / EBITDA}",
    "Discount rate": "=$C${Discount rate}",
    "Pipeline quarterly growth rate": "=$C${Pipeline quarterly growth rate}",
}

MODEL_FORMULA_LABELS: tuple[str, ...] = tuple(UNIFORM_FORMULA_TEMPLATES)


def formula_row_dependencies(label: str) -> frozenset[str]:
    tmpl = UNIFORM_FORMULA_TEMPLATES.get(label, "")
    return frozenset(
        m.group(1)
        for m in _LABEL_PLACEHOLDER_RE.finditer(tmpl)
        if m.group(1) not in {"c", "cp"}
    )


def uniform_formula_template(label: str) -> str:
    return UNIFORM_FORMULA_TEMPLATES[label]


# Seed in C; D:Z copy `=$C$row`. Column C must stay the number (not a self-ref).
COPY_FROM_C_LABELS: frozenset[str] = frozenset(
    {
        "Backlog conversion lag",
        "Z3 Module Energy Capacity",
        "Z3 modules per cube",
        "Full utilization days per week",
        "Full utilization hours per day",
        "Quarterly module cycle time reduction rate",
        CELL_MODULE_CREDIT_LABEL,
        "45x & active electrode credits",
        "45x transfer rate",
        "Percent of Guided Cost Cutting Achieved",
        "Non-cash COGS (D&A + SBC)",
        "Cash OpEx run-rate",
        "EV / EBITDA",
        "Discount rate",
        "Pipeline quarterly growth rate",
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
    if label == CAPACITY_UTILIZATION_LABEL:
        row = label_to_row.get(label)
        if not row:
            raise KeyError(
                f"{CAPACITY_UTILIZATION_LABEL!r} row required to build prior-copy formulas"
            )
        cells: list[Any] = []
        for i in range(n_cols):
            if i < len(CAPACITY_UTILIZATION_COMPLETED):
                cells.append(CAPACITY_UTILIZATION_COMPLETED[i])
            else:
                prior = col_letter(FIRST_VALUE_COL_INDEX + i - 1)
                cells.append(f"={prior}{row}")
        return cells
    if label == "Z3 ASP - Model":
        # Column C uses a shorter else-branch (never taken when column()=3); D:Z keep
        # the hold-flat nest. Matches the live sheet after a manual C edit.
        row = label_to_row.get(label)
        if not row:
            raise KeyError("'Z3 ASP - Model' row required to build ASP formulas")
        cells = []
        for i in range(n_cols):
            prior = col_letter(FIRST_VALUE_COL_INDEX + i - 1)
            if i == 0:
                cells.append(
                    f"=if(column()=3,{ASP_MODEL_START},{prior}{row}*{ASP_MODEL_QOQ})"
                )
            else:
                cells.append(
                    f"=if(column()=3,{ASP_MODEL_START},"
                    f"if(column()<{ASP_MODEL_HOLD_FROM_COL},"
                    f"{prior}{row}*{ASP_MODEL_QOQ},"
                    f"{prior}{row}))"
                )
        return cells
    resolved = apply_row_labels(UNIFORM_FORMULA_TEMPLATES[label], label_to_row)
    if label in COPY_FROM_C_LABELS:
        return [None] + [resolved] * max(0, n_cols - 1)
    cells = []
    for i in range(n_cols):
        col = col_letter(FIRST_VALUE_COL_INDEX + i)
        prior = col_letter(FIRST_VALUE_COL_INDEX + i - 1)
        cells.append(resolved.replace("{c}", col).replace("{cp}", prior))
    return cells


# Default assumption values written to column C (column B is units only).
COLUMN_C_DEFAULTS: dict[str, Any] = {
    "Backlog conversion lag": 4,
    "Z3 Module Energy Capacity": 1.19047619,
    "Z3 modules per cube": 672,
    "Full utilization days per week": 7,
    "Full utilization hours per day": 24,
    "Quarterly module cycle time reduction rate": 2.9,
    CELL_MODULE_CREDIT_LABEL: CELL_MODULE_CREDIT_PER_KWH,
    "45x & active electrode credits": 47,
    "45x transfer rate": 90,
    "Percent of Guided Cost Cutting Achieved": DEFAULT_HAIRCUT_PCT,
    "Non-cash COGS (D&A + SBC)": Q2_2026_NONCASH_COGS,
    "Cash OpEx run-rate": Q2_2026_CASH_OPEX,
    "EV / EBITDA": 30,
    "Discount rate": 20,
    "Pipeline quarterly growth rate": 10,
}

assert COPY_FROM_C_LABELS == frozenset(COLUMN_C_DEFAULTS)
assert N_QUARTERS == 24
assert len(CAPACITY_UTILIZATION_COMPLETED) == 9