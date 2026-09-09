"""COGS tab: unit-cost path from the Q2 2026 cost-out plan, with an execution haircut.

The near-term engine is management's Slide 11 waterfall (materials / conversion /
projects / scrap) phased in over four quarters. Because Eos has repeatedly missed
cost-out timelines, **Percent of Guided Cost Cutting Achieved** (default 70%)
scales the guided points. After the plan completes, remaining gap to terminal
unit COGS is absorbed as Lines 3–4 come in (Indensity / single-piece flow).

Quarterly Financials pulls **Unit COGS - Model** and **Adjusted gross margin - Model**
from this tab via INDEX/MATCH (column-aligned with 2025 Q1 – 2030 Q4).
"""

from __future__ import annotations

from typing import Any

from models.EOSE.layout import (
    FIRST_VALUE_COL_INDEX,
    N_QUARTERS,
    QUARTERLY,
    quarters,
)
from sheets.formulas import col_letter

COGS_SHEET = "COGS"
THREAD_URL = "https://x.com/bert_gilfoyle/status/2096422051376742414"
SLIDE_URL = "https://investors.eose.com/static-files/89d12692-901b-42a8-9872-df44057ac479"

# Labels QF INDEX/MATCHes. Do not rename without updating quarterly_model_formulas.py.
UNIT_COGS_MODEL_LABEL = "Unit COGS - Model"
ADJ_GM_MODEL_LABEL = "Adjusted gross margin - Model"
GUIDED_ADJ_GM_MODEL_LABEL = "Guided adjusted gross margin - Model"
COST_OUT_PROGRESS_LABEL = "Cost-out progress"
SCALE_BLEND_LABEL = "Scale absorption blend"

# Q2 2026 prints used as the cost-out starting point (8-K recon / Slide 11).
Q2_2026_REVENUE = 68.775
Q2_2026_ADJ_GP = -42.869
Q2_2026_ADJ_GM = round(Q2_2026_ADJ_GP / Q2_2026_REVENUE * 100, 1)  # -62.3
Q2_2026_ADJ_EBITDA = -71.355
Q2_2026_CASH = 364.070
Q2_2026_COGS_SBC = 0.516
Q2_2026_COGS_DA = 5.416
Q2_2026_NONCASH_COGS = round(Q2_2026_COGS_SBC + Q2_2026_COGS_DA, 3)  # 5.932
Q2_2026_CASH_OPEX = round(Q2_2026_ADJ_GP - Q2_2026_ADJ_EBITDA, 3)  # 28.486

GUIDED_MATERIALS_PTS = 25
GUIDED_CONVERSION_PTS = 20
GUIDED_PROJECTS_PTS = 20
GUIDED_SCRAP_PTS = 8
GUIDED_TOTAL_PTS = (
    GUIDED_MATERIALS_PTS
    + GUIDED_CONVERSION_PTS
    + GUIDED_PROJECTS_PTS
    + GUIDED_SCRAP_PTS
)  # 73

DEFAULT_HAIRCUT_PCT = 70
DEFAULT_TERMINAL_UNIT_COGS = 160
COST_OUT_START_YEAR = 2026
COST_OUT_START_QUARTER = 2  # progress 0 at Q2 2026
COST_OUT_END_YEAR = 2027
COST_OUT_END_QUARTER = 2  # progress 1 at Q2 2027 (12 months)
SCALE_START_LINES = 2
SCALE_END_LINES = 4  # Lines 3 and 4: fixed-cost absorption / Indensity
ILLUSTRATION_REVENUE = 200  # bert: $200M/qtr ops-cash illustration
END_COL = col_letter(FIRST_VALUE_COL_INDEX + N_QUARTERS - 1)
N_COLS = 2 + N_QUARTERS  # A, B, C–Z


def _empty_row() -> list[Any]:
    return [""] * N_COLS


def _qf(label: str) -> str:
    """Column-aligned INDEX/MATCH into Quarterly Financials C:Z."""
    return (
        f"INDEX('{QUARTERLY}'!$C:$Z,"
        f"MATCH(\"{label}\",'{QUARTERLY}'!$A:$A,0),"
        "COLUMN()-2)"
    )


def _cogs_c(label: str) -> str:
    return f"INDEX($C:$C,MATCH(\"{label}\",$A:$A,0))"


def _qf_c(label: str) -> str:
    return (
        f"INDEX('{QUARTERLY}'!$C:$C,"
        f"MATCH(\"{label}\",'{QUARTERLY}'!$A:$A,0))"
    )


def _progress_formula() -> str:
    """0 at cost-out start quarter, 1 at complete, held after. Linear in between."""
    y = _cogs_c("Cost-out start year")
    q = _cogs_c("Cost-out start quarter")
    ey = _cogs_c("Cost-out complete year")
    eq = _cogs_c("Cost-out complete quarter")
    return (
        f'=IF(OR(C{{year}}="",{y}=""),"",'
        f"MIN(1,MAX(0,((C{{year}}-{y})*4+C{{quarter}}-{q})"
        f"/MAX(1,({ey}-{y})*4+({eq}-{q})))))"
    )


def _adj_gm_formula(*, guided: bool) -> str:
    start = _cogs_c("Starting adjusted gross margin")
    total = _cogs_c("Total guided cost-out")
    haircut = _cogs_c("Percent of Guided Cost Cutting Achieved")
    progress = f"C{{progress}}"
    pts = total if guided else f"({total}*{haircut}/100)"
    return f'=IF({progress}="","",{start}+{progress}*{pts})'


def _scale_blend_formula() -> str:
    start = _cogs_c("Scale absorption start lines")
    end = _cogs_c("Scale absorption complete lines")
    lines = _qf("Z3 manufacturing lines - Model")
    progress = "C{progress}"
    return (
        f'=IF({progress}="","",'
        f"IF({progress}<1,0,MIN(1,MAX(0,({lines}-{start})"
        f"/MAX(0.001,{end}-{start})))))"
    )


def _unit_cogs_formula() -> str:
    """Pre-45X unit COGS. During the plan: ASP × (1 − adj GM) + 45X.
    After the plan: blend that level toward Terminal unit COGS as lines 3–4 ramp.
    """
    asp = _qf("Z3 ASP - Model")
    credit = _qf("Effective 45x credit - Model")
    terminal = _cogs_c("Terminal unit COGS")
    gm = "C{adj_gm}"
    blend = "C{blend}"
    raw = f"({asp}*(1-{gm}/100)+{credit})"
    return (
        f'=IF(OR({gm}="",{asp}=""),"",'
        f"IF(C{{progress}}<1,{raw},{raw}*(1-{blend})+{terminal}*{blend}))"
    )


def _ebitda_at_200m(gm_label: str) -> str:
    rev = _cogs_c("$200M quarterly revenue (illustration)")
    opex = _cogs_c("Cash OpEx run-rate")
    return f'=IF(C{{{gm_label}}}="","",{rev}*C{{{gm_label}}}/100-{opex})'


# (label, units) for the lever / documentation block. C is value or formula.
# Spacers use empty label.
LEVER_ROWS: list[tuple[str, str, Any]] = [
    ("COGS & cost-out plan", "", ""),
    ("", "", ""),
    (
        "Source",
        "",
        f'=HYPERLINK("{THREAD_URL}","bert_gilfoyle cost-out thread (6 Sep 2026)")',
    ),
    (
        "Management slide",
        "",
        f'=HYPERLINK("{SLIDE_URL}","Q2 2026 earnings Slide 11 — Roadmap to Positive Adj. GM")',
    ),
    (
        "Notes",
        "",
        "Not a prediction. The CFO's 12-month cost-out is the guided case; "
        "the haircut is the model's default because Eos has repeatedly missed "
        "cost-out timelines and has funded the gap with dilution. Operational "
        "cash use ≈ Adjusted EBITDA (CFO; Q2 2026). CapEx continues on top of that.",
    ),
    ("", "", ""),
    ("Levers", "", "Edit the yellow cells. Haircut and terminal also live on Quarterly Financials."),
    (
        "Percent of Guided Cost Cutting Achieved",
        "%",
        f"={_qf_c('Percent of Guided Cost Cutting Achieved')}",
    ),
    (
        "Terminal unit COGS",
        "$ / kWh",
        f"={_qf_c('Terminal unit COGS')}",
    ),
    ("Cost-out start year", "year", COST_OUT_START_YEAR),
    ("Cost-out start quarter", "q", COST_OUT_START_QUARTER),
    ("Cost-out complete year", "year", COST_OUT_END_YEAR),
    ("Cost-out complete quarter", "q", COST_OUT_END_QUARTER),
    ("Scale absorption start lines", "count", SCALE_START_LINES),
    ("Scale absorption complete lines", "count", SCALE_END_LINES),
    ("Starting adjusted gross margin", "%", Q2_2026_ADJ_GM),
    ("Cash OpEx run-rate", "$M", f"={_qf_c('Cash OpEx run-rate')}"),
    ("$200M quarterly revenue (illustration)", "$M", ILLUSTRATION_REVENUE),
    ("", "", ""),
    (
        "Guided cost-out (pts of adj. GM)",
        "",
        "Slide 11 / Q2 2026 call. 72+ pts over 12 months; drivers sum to 73.",
    ),
    (
        "Materials cost-out",
        "pts",
        GUIDED_MATERIALS_PTS,
    ),
    (
        "Conversion cost-out",
        "pts",
        GUIDED_CONVERSION_PTS,
    ),
    (
        "Projects cost-out",
        "pts",
        GUIDED_PROJECTS_PTS,
    ),
    (
        "Scrap cost-out",
        "pts",
        GUIDED_SCRAP_PTS,
    ),
    (
        "Total guided cost-out",
        "pts",
        f"={_cogs_c('Materials cost-out')}+{_cogs_c('Conversion cost-out')}"
        f"+{_cogs_c('Projects cost-out')}+{_cogs_c('Scrap cost-out')}",
    ),
    (
        "Achieved cost-out",
        "pts",
        f"={_cogs_c('Total guided cost-out')}*"
        f"{_cogs_c('Percent of Guided Cost Cutting Achieved')}/100",
    ),
    (
        "Implied adj. GM at completion — guided",
        "%",
        f"={_cogs_c('Starting adjusted gross margin')}+{_cogs_c('Total guided cost-out')}",
    ),
    (
        "Implied adj. GM at completion — haircut",
        "%",
        f"={_cogs_c('Starting adjusted gross margin')}+{_cogs_c('Achieved cost-out')}",
    ),
    ("", "", ""),
    (
        "Q2 2026 anchor",
        "",
        "Starting cost structure. Adj. GM recon is GP + SBC in COGS + D&A in COGS.",
    ),
    ("Q2 2026 revenue", "$M", Q2_2026_REVENUE),
    ("Q2 2026 adj. gross profit", "$M", Q2_2026_ADJ_GP),
    ("Q2 2026 adj. EBITDA", "$M", Q2_2026_ADJ_EBITDA),
    ("Q2 2026 cash", "$M", Q2_2026_CASH),
    ("Q2 2026 monthly burn (adj. EBITDA / 3)", "$M / mo", round(Q2_2026_ADJ_EBITDA / 3, 2)),
    ("Q2 2026 implied cash OpEx", "$M", Q2_2026_CASH_OPEX),
    ("Q2 2026 non-cash COGS (SBC + D&A)", "$M", Q2_2026_NONCASH_COGS),
    ("", "", ""),
    (
        "Driver notes",
        "",
        "Materials (~25 pts): supplier volume agreements + 90 cost-out initiatives. "
        "A 25-pt cut on 100% of materials in <12 months is aggressive — the haircut "
        "is partly for this. Conversion (~20 pts): one overhead at Thorn Hill, "
        "automation replacing temp labor between buildings. Projects (~20 pts): "
        "finish DawnOS upgrades, insource third-party field labor. Scrap (~8 pts): "
        "sub-assembly yield, tighter tolerances. After break-even: Lines 3–4, "
        "Indensity single-piece flow, nameplate exceeded via cycle time.",
    ),
    (
        "$200M / quarter illustration",
        "",
        "bert: at ~$200M quarterly revenue and the cost-out, ops cash can turn "
        "positive. That needs adj. GP > cash OpEx. At 70% haircut (~−11% adj. GM) "
        "it does not; at 100% (~+11% adj. GM) it is close but still shy of $28.5M "
        "cash OpEx unless volume or opex leverage helps. FY2026 $325M is the "
        "guide midpoint ($300–350M), not a separate forecast.",
    ),
    ("", "", ""),
    ("Quarterly path", "", "C–Z aligned with Quarterly Financials (2025 Q1 – 2030 Q4)."),
]

# Driver commentary in column D (index 3) for selected lever labels.
LEVER_COL_D: dict[str, str] = {
    "Percent of Guided Cost Cutting Achieved": (
        "Default 70%. 100% = take the CFO's 73 pts at face value. 0% = freeze Q2 2026 costs."
    ),
    "Terminal unit COGS": "Floor after Lines 3–4 scale absorption. Explicit thesis, not a print.",
    "Cost-out start year": "Progress is 0 in this quarter (Q2 2026 actuals are the base).",
    "Cost-out complete year": "12 months after start — Slide 11 Q2 '27 10%+ adj. GM target.",
    "Scale absorption start lines": "Line 2 is already in the conversion-cost plan. Extra blend starts after 2.",
    "Scale absorption complete lines": (
        "bert: the real magic is Lines 3 and 4 + Indensity single-piece flow."
    ),
    "Starting adjusted gross margin": "Q2 2026 adj. GP −$42.869M / revenue $68.775M = −62.3%.",
    "Materials cost-out": "Supplier volume agreements + cost-out initiative funnel.",
    "Conversion cost-out": "Higher volume across optimized Thorn Hill footprint (one overhead).",
    "Projects cost-out": "Complete DawnOS upgrades; insource third-party field labor.",
    "Scrap cost-out": "Sub-assembly yield improvement with equipment / tolerance upgrades.",
    "Cash OpEx run-rate": "Q2 implied: adj. GP − adj. EBITDA. Held flat (opex was sequentially flat).",
    "$200M quarterly revenue (illustration)": "Scenario only — does not drive Quarterly Financials revenue.",
}


def lever_label_rows() -> dict[str, int]:
    """1-based row index for non-empty lever labels."""
    found: dict[str, int] = {}
    for i, (label, _units, _val) in enumerate(LEVER_ROWS, start=1):
        if label:
            found[label] = i
    return found


def quarterly_block_start_row() -> int:
    return len(LEVER_ROWS) + 1


def quarterly_engine_labels() -> list[tuple[str, str]]:
    """Labels written in the quarterly block (row order)."""
    return [
        ("Year", ""),
        ("Quarter", ""),
        (COST_OUT_PROGRESS_LABEL, "0–1"),
        (GUIDED_ADJ_GM_MODEL_LABEL, "%"),
        (ADJ_GM_MODEL_LABEL, "%"),
        (SCALE_BLEND_LABEL, "0–1"),
        (UNIT_COGS_MODEL_LABEL, "$ / kWh"),
        ("Adj. EBITDA at $200M revenue — guided", "$M"),
        ("Adj. EBITDA at $200M revenue — haircut", "$M"),
    ]


def engine_label_rows() -> dict[str, int]:
    start = quarterly_block_start_row()
    return {label: start + i for i, (label, _u) in enumerate(quarterly_engine_labels())}


def build_cogs_grid() -> list[list[Any]]:
    """Full A1:Z grid for the COGS tab."""
    grid = [_empty_row() for _ in range(len(LEVER_ROWS) + len(quarterly_engine_labels()))]
    for r, (label, units, value) in enumerate(LEVER_ROWS):
        grid[r][0] = label
        grid[r][1] = units
        grid[r][2] = value
        if label in LEVER_COL_D:
            grid[r][3] = LEVER_COL_D[label]

    engine = engine_label_rows()
    year_row = engine["Year"]
    q_row = engine["Quarter"]
    progress_row = engine[COST_OUT_PROGRESS_LABEL]
    guided_gm_row = engine[GUIDED_ADJ_GM_MODEL_LABEL]
    adj_gm_row = engine[ADJ_GM_MODEL_LABEL]
    blend_row = engine[SCALE_BLEND_LABEL]
    unit_row = engine[UNIT_COGS_MODEL_LABEL]
    ebitda_g_row = engine["Adj. EBITDA at $200M revenue — guided"]
    ebitda_h_row = engine["Adj. EBITDA at $200M revenue — haircut"]

    progress_tmpl = _progress_formula()
    guided_gm_tmpl = _adj_gm_formula(guided=True)
    adj_gm_tmpl = _adj_gm_formula(guided=False)
    blend_tmpl = _scale_blend_formula()
    unit_tmpl = _unit_cogs_formula()
    ebitda_g_tmpl = _ebitda_at_200m("guided_gm")
    ebitda_h_tmpl = _ebitda_at_200m("adj_gm")

    for r, (label, units) in enumerate(quarterly_engine_labels()):
        idx = quarterly_block_start_row() - 1 + r
        grid[idx][0] = label
        grid[idx][1] = units

    for i, (year, q) in enumerate(quarters()):
        c = 2 + i
        col = col_letter(FIRST_VALUE_COL_INDEX + i)
        grid[year_row - 1][c] = f"='{QUARTERLY}'!{col}{2}"  # filled after QF Year row known
        grid[q_row - 1][c] = f"='{QUARTERLY}'!{col}{3}"

        def _sub(tmpl: str) -> str:
            return (
                tmpl.replace("C{year}", f"{col}{year_row}")
                .replace("C{quarter}", f"{col}{q_row}")
                .replace("C{progress}", f"{col}{progress_row}")
                .replace("C{adj_gm}", f"{col}{adj_gm_row}")
                .replace("C{guided_gm}", f"{col}{guided_gm_row}")
                .replace("C{blend}", f"{col}{blend_row}")
                .replace("{year}", str(year_row))
                .replace("{quarter}", str(q_row))
                .replace("{progress}", str(progress_row))
                .replace("{adj_gm}", str(adj_gm_row))
                .replace("{guided_gm}", str(guided_gm_row))
                .replace("{blend}", str(blend_row))
            )

        grid[progress_row - 1][c] = _sub(progress_tmpl)
        grid[guided_gm_row - 1][c] = _sub(guided_gm_tmpl)
        grid[adj_gm_row - 1][c] = _sub(adj_gm_tmpl)
        grid[blend_row - 1][c] = _sub(blend_tmpl)
        grid[unit_row - 1][c] = _sub(unit_tmpl)
        grid[ebitda_g_row - 1][c] = _sub(ebitda_g_tmpl)
        grid[ebitda_h_row - 1][c] = _sub(ebitda_h_tmpl)

    return grid


def bind_year_quarter_to_qf(
    grid: list[list[Any]],
    *,
    year_row_qf: int,
    quarter_row_qf: int,
) -> list[list[Any]]:
    """Point COGS Year/Quarter at the live Quarterly Financials row numbers."""
    engine = engine_label_rows()
    year_i = engine["Year"] - 1
    q_i = engine["Quarter"] - 1
    for i in range(N_QUARTERS):
        col = col_letter(FIRST_VALUE_COL_INDEX + i)
        grid[year_i][2 + i] = f"='{QUARTERLY}'!{col}{year_row_qf}"
        grid[q_i][2 + i] = f"='{QUARTERLY}'!{col}{quarter_row_qf}"
    return grid


def qf_index_formula(cogs_label: str) -> str:
    """Quarterly Financials template: pull a COGS engine row, column-aligned."""
    return (
        f'=IF({{c}}{{Quarter}}="","",'
        f'IFERROR(INDEX({COGS_SHEET}!$C:$Z,'
        f'MATCH("{cogs_label}",{COGS_SHEET}!$A:$A,0),COLUMN()-2),""))'
    )


# Lever C cells that are inputs (not formulas pulled from Quarterly Financials).
EDITABLE_LEVER_LABELS: frozenset[str] = frozenset(
    {
        "Cost-out start year",
        "Cost-out start quarter",
        "Cost-out complete year",
        "Cost-out complete quarter",
        "Scale absorption start lines",
        "Scale absorption complete lines",
        "Starting adjusted gross margin",
        "Materials cost-out",
        "Conversion cost-out",
        "Projects cost-out",
        "Scrap cost-out",
        "$200M quarterly revenue (illustration)",
    }
)


def write_cogs_sheet(client: Any, qf_label_to_row: dict[str, int]) -> None:
    """Clear and rewrite the COGS tab. Does not create charts."""
    from sheets.labels import sheet_id

    grid = bind_year_quarter_to_qf(
        build_cogs_grid(),
        year_row_qf=qf_label_to_row["Year"],
        quarter_row_qf=qf_label_to_row["Quarter"],
    )
    titles = client.list_worksheets()
    if COGS_SHEET not in titles:
        client.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": COGS_SHEET,
                                "gridProperties": {
                                    "rowCount": max(80, len(grid) + 5),
                                    "columnCount": 28,
                                },
                            }
                        }
                    }
                ]
            }
        )
    sid = sheet_id(client, COGS_SHEET)
    client.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sid,
                            "gridProperties": {
                                "rowCount": max(80, len(grid) + 5),
                                "columnCount": 28,
                            },
                        },
                        "fields": "gridProperties.rowCount,gridProperties.columnCount",
                    }
                }
            ]
        }
    )
    ws = client.worksheet(COGS_SHEET)
    ws.clear()
    ws.update(
        grid,
        range_name=f"A1:{END_COL}{len(grid)}",
        value_input_option="USER_ENTERED",
    )

    lever_rows = lever_label_rows()
    yellow_rows = [lever_rows[lab] for lab in EDITABLE_LEVER_LABELS if lab in lever_rows]
    requests: list[dict] = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                },
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 14}}},
                "fields": "userEnteredFormat.textFormat",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 0,
                    "endRowIndex": len(grid),
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                },
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 0,
                    "endRowIndex": len(grid),
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "wrapStrategy": "WRAP",
                        "verticalAlignment": "TOP",
                    }
                },
                "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sid,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 320},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sid,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 2,
                },
                "properties": {"pixelSize": 80},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sid,
                    "dimension": "COLUMNS",
                    "startIndex": 3,
                    "endIndex": 4,
                },
                "properties": {"pixelSize": 420},
                "fields": "pixelSize",
            }
        },
    ]
    for row_1based in yellow_rows:
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": row_1based - 1,
                        "endRowIndex": row_1based,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 1, "green": 0.95, "blue": 0.8}
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )
    client.spreadsheet.batch_update({"requests": requests})
    print(f"Wrote {len(grid)} rows × {N_COLS} cols to {COGS_SHEET!r}")
