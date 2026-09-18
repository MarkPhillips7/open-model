"""COGS tab: cost-out levers and notes (Units / Value / Notes).

The near-term plan is management's Slide 11 waterfall (materials / conversion /
projects / scrap) phased in over four quarters. Because Eos has repeatedly missed
cost-out timelines, **Percent of Guided Cost Cutting Achieved** (default 70%)
scales the guided points. After the plan completes, remaining gap to terminal
unit COGS is absorbed as Lines 3–4 come in (Indensity / single-piece flow).

Quarterly Financials owns the time series (progress, adj. GM, unit COGS, $200M
illustration) and INDEX/MATCHes the yellow column-C scalars on this tab.
"""

from __future__ import annotations

from typing import Any

from models.EOSE.layout import COGS_COL_WIDTHS_PX, QUARTERLY, column_width_requests

COGS_SHEET = "COGS"
THREAD_URL = "https://x.com/bert_gilfoyle/status/2096422051376742414"
SLIDE_URL = "https://investors.eose.com/static-files/89d12692-901b-42a8-9872-df44057ac479"

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

DEFAULT_HAIRCUT_PCT = 70  # note / Welcome copy; live Quarterly Financials C is 100
DEFAULT_TERMINAL_UNIT_COGS = 181
COST_OUT_START_YEAR = 2026
COST_OUT_START_QUARTER = 2  # progress 0 at Q2 2026
COST_OUT_END_YEAR = 2027
COST_OUT_END_QUARTER = 2  # progress 1 at Q2 2027 (12 months)
SCALE_START_LINES = 2
SCALE_END_LINES = 4  # Lines 3 and 4: fixed-cost absorption / Indensity
ILLUSTRATION_REVENUE = 200  # bert: $200M/qtr ops-cash illustration

N_COLS = 4  # A label, B units, C value, D notes
END_COL = "D"


def cogs_c_ref(label: str) -> str:
    """INDEX/MATCH a COGS tab column-C scalar by label (for Quarterly Financials)."""
    return f'INDEX({COGS_SHEET}!$C:$C,MATCH("{label}",{COGS_SHEET}!$A:$A,0))'


def _cogs_c(label: str) -> str:
    return cogs_c_ref(label)


def _qf_c(label: str) -> str:
    return (
        f"INDEX('{QUARTERLY}'!$C:$C,"
        f"MATCH(\"{label}\",'{QUARTERLY}'!$A:$A,0))"
    )


# (label, units, value, notes). Spacers and the header use empty labels.
LEVER_ROWS: list[tuple[str, str, Any, str]] = [
    ("", "Units", "Value", "Notes"),
    ("", "", "", ""),
    (
        "Source",
        "",
        "",
        f'=HYPERLINK("{THREAD_URL}","bert_gilfoyle cost-out thread (6 Sep 2026)")',
    ),
    (
        "Management slide",
        "",
        "",
        f'=HYPERLINK("{SLIDE_URL}","Q2 2026 earnings Slide 11 — Roadmap to Positive Adj. GM")',
    ),
    (
        "Notes",
        "",
        "",
        "Not a prediction. The CFO's 12-month cost-out is the guided case; "
        "the haircut is the model's default because Eos has repeatedly missed "
        "cost-out timelines and has funded the gap with dilution. Operational "
        "cash use ≈ Adjusted EBITDA (CFO; Q2 2026). CapEx continues on top of that.",
    ),
    ("", "", "", ""),
    (
        "Levers",
        "",
        "",
        "Edit the yellow cells. Haircut also lives on Quarterly Financials; "
        "terminal $/kWh is edited here.",
    ),
    (
        "Percent of Guided Cost Cutting Achieved",
        "%",
        f"={_qf_c('Percent of Guided Cost Cutting Achieved')}",
        "Default 70%. 100% = take the CFO's 73 pts at face value. 0% = freeze Q2 2026 costs.",
    ),
    (
        "Terminal unit COGS",
        "$ / kWh",
        DEFAULT_TERMINAL_UNIT_COGS,
        "Floor after Lines 3–4 scale absorption. Explicit thesis, not a print.",
    ),
    (
        "Cost-out start year",
        "year",
        COST_OUT_START_YEAR,
        "Progress is 0 in this quarter (Q2 2026 actuals are the base).",
    ),
    ("Cost-out start quarter", "q", COST_OUT_START_QUARTER, ""),
    (
        "Cost-out complete year",
        "year",
        COST_OUT_END_YEAR,
        "12 months after start — Slide 11 Q2 '27 10%+ adj. GM target.",
    ),
    ("Cost-out complete quarter", "q", COST_OUT_END_QUARTER, ""),
    (
        "Scale absorption start lines",
        "count",
        SCALE_START_LINES,
        "Line 2 is already in the conversion-cost plan. Extra blend starts after 2.",
    ),
    (
        "Scale absorption complete lines",
        "count",
        SCALE_END_LINES,
        "bert: the real magic is Lines 3 and 4 + Indensity single-piece flow.",
    ),
    (
        "Starting adjusted gross margin",
        "%",
        Q2_2026_ADJ_GM,
        "Q2 2026 adj. GP −$42.869M / revenue $68.775M = −62.3%.",
    ),
    (
        "Cash OpEx run-rate",
        "$M",
        f"={_qf_c('Cash OpEx run-rate')}",
        "Q2 implied: adj. GP − adj. EBITDA. Held flat (opex was sequentially flat).",
    ),
    (
        "$200M quarterly revenue (illustration)",
        "$M",
        ILLUSTRATION_REVENUE,
        "Scenario only — does not drive Quarterly Financials revenue.",
    ),
    ("", "", "", ""),
    (
        "Guided cost-out (pts of adj. GM)",
        "",
        "",
        "Slide 11 / Q2 2026 call. 72+ pts over 12 months; drivers sum to 73.",
    ),
    (
        "Materials cost-out",
        "pts",
        GUIDED_MATERIALS_PTS,
        "Supplier volume agreements + cost-out initiative funnel.",
    ),
    (
        "Conversion cost-out",
        "pts",
        GUIDED_CONVERSION_PTS,
        "Higher volume across optimized Thorn Hill footprint (one overhead).",
    ),
    (
        "Projects cost-out",
        "pts",
        GUIDED_PROJECTS_PTS,
        "Complete DawnOS upgrades; insource third-party field labor.",
    ),
    (
        "Scrap cost-out",
        "pts",
        GUIDED_SCRAP_PTS,
        "Sub-assembly yield improvement with equipment / tolerance upgrades.",
    ),
    (
        "Total guided cost-out",
        "pts",
        f"={_cogs_c('Materials cost-out')}+{_cogs_c('Conversion cost-out')}"
        f"+{_cogs_c('Projects cost-out')}+{_cogs_c('Scrap cost-out')}",
        "",
    ),
    (
        "Achieved cost-out",
        "pts",
        f"={_cogs_c('Total guided cost-out')}*"
        f"{_cogs_c('Percent of Guided Cost Cutting Achieved')}/100",
        "",
    ),
    (
        "Implied adj. GM at completion — guided",
        "%",
        f"={_cogs_c('Starting adjusted gross margin')}+{_cogs_c('Total guided cost-out')}",
        "",
    ),
    (
        "Implied adj. GM at completion — haircut",
        "%",
        f"={_cogs_c('Starting adjusted gross margin')}+{_cogs_c('Achieved cost-out')}",
        "",
    ),
    ("", "", "", ""),
    (
        "Q2 2026 anchor",
        "",
        "",
        "Starting cost structure. Adj. GM recon is GP + SBC in COGS + D&A in COGS.",
    ),
    ("Q2 2026 revenue", "$M", Q2_2026_REVENUE, ""),
    ("Q2 2026 adj. gross profit", "$M", Q2_2026_ADJ_GP, ""),
    ("Q2 2026 adj. EBITDA", "$M", Q2_2026_ADJ_EBITDA, ""),
    ("Q2 2026 cash", "$M", Q2_2026_CASH, ""),
    (
        "Q2 2026 monthly burn (adj. EBITDA / 3)",
        "$M / mo",
        round(Q2_2026_ADJ_EBITDA / 3, 2),
        "",
    ),
    ("Q2 2026 implied cash OpEx", "$M", Q2_2026_CASH_OPEX, ""),
    ("Q2 2026 non-cash COGS (SBC + D&A)", "$M", Q2_2026_NONCASH_COGS, ""),
    ("", "", "", ""),
    (
        "Driver notes",
        "",
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
        "",
        "bert: at ~$200M quarterly revenue and the cost-out, ops cash can turn "
        "positive. That needs adj. GP > cash OpEx. At 70% haircut (~−11% adj. GM) "
        "it does not; at 100% (~+11% adj. GM) it is close but still shy of $28.5M "
        "cash OpEx unless volume or opex leverage helps. FY2026 $325M is the "
        "guide midpoint ($300–350M), not a separate forecast.",
    ),
]


def lever_label_rows() -> dict[str, int]:
    """1-based row index for non-empty lever labels."""
    found: dict[str, int] = {}
    for i, (label, _units, _val, _notes) in enumerate(LEVER_ROWS, start=1):
        if label:
            found[label] = i
    return found


def build_cogs_grid() -> list[list[Any]]:
    """Full A1:D grid for the COGS tab (no quarterly time series)."""
    grid = [[""] * N_COLS for _ in range(len(LEVER_ROWS))]
    for r, (label, units, value, notes) in enumerate(LEVER_ROWS):
        grid[r][0] = label
        grid[r][1] = units
        grid[r][2] = value
        grid[r][3] = notes
    return grid


# Lever C cells that are inputs (not formulas pulled from Quarterly Financials).
EDITABLE_LEVER_LABELS: frozenset[str] = frozenset(
    {
        "Cost-out start year",
        "Cost-out start quarter",
        "Cost-out complete year",
        "Cost-out complete quarter",
        "Scale absorption start lines",
        "Scale absorption complete lines",
        "Terminal unit COGS",
        "Starting adjusted gross margin",
        "Materials cost-out",
        "Conversion cost-out",
        "Projects cost-out",
        "Scrap cost-out",
        "$200M quarterly revenue (illustration)",
    }
)


def write_cogs_sheet(client: Any) -> None:
    """Clear and rewrite the COGS tab. Does not create charts."""
    from sheets.labels import sheet_id

    grid = build_cogs_grid()
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
                                    "rowCount": max(50, len(grid) + 5),
                                    "columnCount": 6,
                                    "frozenRowCount": 1,
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
                                "rowCount": max(50, len(grid) + 5),
                                "columnCount": 6,
                                "frozenRowCount": 1,
                            },
                        },
                        "fields": (
                            "gridProperties.rowCount,gridProperties.columnCount,"
                            "gridProperties.frozenRowCount"
                        ),
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
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True},
                        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True, "fontSize": 14},
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.textFormat.fontSize",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 1,
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
    ]
    requests.extend(column_width_requests(sid, COGS_COL_WIDTHS_PX))
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
