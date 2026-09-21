"""Valuation tab: sum of parts for LODE.

Why sum of parts rather than a multiple of earnings or a single DCF: Comstock is
one ramping operating business bolted to two lumpy asset stakes. A consolidated
multiple would blend a recycling plant, a half-share of a land fund, and a
pre-commercial fuels venture into one number that describes none of them. Valuing
them separately also means each pillar gets its own "achieved" lever, so you can
say "I believe the plant but not the land" and see what that is worth.

The mechanic is: pick a **reference quarter** far enough out that the recycling
plant is running at steady state, value the business as at that quarter, then
discount the resulting per-share figure back to today.

Double-counting guard
---------------------
``Cash - Model`` at the reference quarter already contains any asset sale that
closed before it — the contracted mining cash, plus whatever fraction of the SSOF
stake the ``SSOF stake sold for cash`` lever says was sold, if its monetization
quarter precedes the reference quarter. So the SSOF line below carries the stake
value **net of** that fraction. At the default (nothing sold for cash) the stake
is credited in full and the cash line is untouched; at the other extreme the value
sits entirely in net cash and the stake line is zero. Either way it is counted once.

The fuels stake is never in the cash line at all — the model assumes it is worth
something, not that it is ever sold — so it needs no such guard.
"""

from __future__ import annotations

from typing import Any

from models.LODE import layout as L
from models.LODE import levers as lv

VALUATION_SHEET = "Valuation"

HEADER = ["Line", "Units", "Value", "Notes"]
COL_WIDTHS_PX: dict[int, int] = {0: 330, 1: 80, 2: 118, 3: 820}

# Quarter whose run-rate is capitalized. 2029 Q4 is the first steady-state quarter
# in the default plan: utilization has plateaued at 85% and the uplift phase-in is
# essentially complete, so four times that quarter is a fair annual run-rate
# rather than a snapshot of a half-built ramp.
DEFAULT_REFERENCE_QUARTER = "2029 Q4"

REFERENCE_QUARTER = "Reference quarter"
REFERENCE_OFFSET = "Reference quarter column offset"
AS_OF = "As of date"
YEARS_TO_REFERENCE = "Years from present to reference quarter"

ANNUAL_CONTRIBUTION = "Annualized metals cash contribution"
ANNUAL_CORP_GA = "Annualized corporate cash G&A"
METALS_EBITDA = "Metals EBITDA proxy"
METALS_MULTIPLE = "Metals EV / EBITDA multiple"
METALS_VALUE = "Comstock Metals business value"

SSOF_GROSS = "SSOF gross asset value"
SSOF_SHARE = "Comstock ownership of SSOF"
SSOF_ACHIEVED = "SSOF value achieved"
SSOF_CASH_SOLD = "SSOF stake sold for cash"
SSOF_ALREADY_IN_CASH = "SSOF already monetized by reference quarter"
SSOF_VALUE = "SSOF stake value"

FUELS_VALUE = "Comstock Fuels stake value"

CASH_AT_REF = "Cash at reference quarter"
DEBT_AT_REF = "Total debt at reference quarter"
NET_CASH = "Net cash"
NET_CASH_CREDITED = "Net cash credited"

EQUITY_VALUE = "Equity value at reference quarter"
SHARES_AT_REF = "Shares outstanding at reference quarter"
VALUE_PER_SHARE = "Implied value per share at reference quarter"
CURRENT_PRICE = "Current share price"
PRESENT_VALUE_PER_SHARE = "Present value per share"
UPSIDE_TO_PRESENT = "Upside to present value"

SECTION_SETUP = "SETUP"
SECTION_METALS = "COMSTOCK METALS"
SECTION_SSOF = "SSOF — POWERED LAND"
SECTION_FUELS = "COMSTOCK FUELS"
SECTION_CASH = "NET CASH"
SECTION_RESULT = "RESULT"

SECTION_LABELS: frozenset[str] = frozenset(
    {
        SECTION_SETUP,
        SECTION_METALS,
        SECTION_SSOF,
        SECTION_FUELS,
        SECTION_CASH,
        SECTION_RESULT,
    }
)

USD_M = "$M"
PCT = "%"


# (label, units, note). Section headings have empty units and note.
ROWS: list[tuple[str, str, str]] = [
    (SECTION_SETUP, "", ""),
    (
        REFERENCE_QUARTER,
        "quarter",
        "Quarter whose results are annualized and capitalized below. Must be a quarter in the "
        "Quarterly Financials spine (2025 Q1 – 2030 Q4). Push it later for a more mature run-rate "
        "but a longer discount; pull it earlier for the opposite. This is an input — edit it.",
    ),
    (
        REFERENCE_OFFSET,
        "columns",
        "Helper: how many columns right of C the reference quarter sits. Derived from the quarter "
        "above; every lookup on this tab uses it. Not an input.",
    ),
    (
        AS_OF,
        "date",
        "Valuation date, taken from the Levers tab. The present-value line discounts back to here.",
    ),
    (
        YEARS_TO_REFERENCE,
        "years",
        "Years between the As of date and the end of the reference quarter, used as the discounting "
        "period.",
    ),
    (SECTION_METALS, "", ""),
    (
        ANNUAL_CONTRIBUTION,
        USD_M,
        "Four times 'Metals cash contribution - Model' in the reference quarter: recycling revenue "
        "less the fixed cost of running the lines and the gas-and-electricity variable cost. It sits "
        "above depreciation and stock compensation, so treat it as a cash EBITDA for the segment.",
    ),
    (
        ANNUAL_CORP_GA,
        USD_M,
        "Four times 'Corporate cash G&A - Model' in the reference quarter. That model row is "
        "Corporate/Other SEGMENT cash G&A only (~$2.25M/qtr default on Levers — not consolidated "
        "G&A of ~$7M, which would double-count Bioleum against the fuels bridge). Deducted because "
        "a shareholder cannot buy the plant without also funding the public company around it.",
    ),
    (
        METALS_EBITDA,
        USD_M,
        "Annual segment contribution less corporate overhead — the consolidated cash earnings the "
        "multiple is applied to.",
    ),
    (
        METALS_MULTIPLE,
        "x",
        "From the Levers tab. Applied to the cash earnings figure above.",
    ),
    (
        METALS_VALUE,
        USD_M,
        "EBITDA proxy × multiple × 'Metals business value achieved'. Floored at zero: if the plant "
        "is still loss-making at the reference quarter the business is worth nothing in this frame, "
        "not a negative number — the cash drain already shows up in the net cash line.",
    ),
    (SECTION_SSOF, "", ""),
    (SSOF_GROSS, USD_M, "From the Levers tab — whole-asset value of the land, water, and power."),
    (SSOF_SHARE, PCT, "From the Levers tab — Comstock's equity interest in the fund."),
    (SSOF_ACHIEVED, PCT, "From the Levers tab — how much of the gross value reaches shareholders."),
    (
        SSOF_CASH_SOLD,
        PCT,
        "From the Levers tab — percentage of the haircut stake sold for cash inside the forecast "
        "(not a dollar amount). Defaults to zero because nothing is signed and every SSOF "
        "transaction to date is Comstock paying in (~$37M cumulative). Raise it only as a "
        "scenario test. Whatever is sold shows up in 'Cash - Model' instead of as a stake, and "
        "gets deducted below so it is never counted twice.",
    ),
    (
        SSOF_ALREADY_IN_CASH,
        "yes / no",
        "Yes when the SSOF monetization quarter is at or before the reference quarter, which means "
        "any sold portion is already sitting in 'Cash - Model'. Only then does the deduction below "
        "apply — a sale scheduled after the reference quarter has not hit cash yet.",
    ),
    (
        SSOF_VALUE,
        USD_M,
        "Comstock's haircut share of SSOF, less whatever has already been converted to cash by the "
        "reference quarter. At the default zero-cash-sold setting this is the full stake value and "
        "the cash line is untouched; at 100% sold before the reference quarter it is zero and the "
        "value lives entirely in net cash. In between it splits, with no double-count either way.",
    ),
    (SECTION_FUELS, "", ""),
    (
        FUELS_VALUE,
        USD_M,
        "From the Levers tab: value × achieved. Never appears in the cash line, because the model "
        "does not assume the fuels stake is ever sold — only that it is worth something. The "
        "default is management's stated liquidation-preference floor, not a growth valuation.",
    ),
    (SECTION_CASH, "", ""),
    (
        CASH_AT_REF,
        USD_M,
        "'Cash - Model' at the reference quarter. Already reflects every modelled flow up to that "
        "point: operating burn, capex on new lines, the mining sale, the fuels bridge loan, and SSOF "
        "proceeds if they landed before then. A negative number here is a funding gap, not a "
        "forecast of insolvency — read it as the equity the company still has to raise.",
    ),
    (DEBT_AT_REF, USD_M, "'Total debt - Model' at the reference quarter. Comstock has run debt-free."),
    (
        NET_CASH,
        USD_M,
        "Cash less debt at the reference quarter. Sanity check near today (not a lever input): "
        "$31.4M cash at 6/30/26 + $20.0M Mackay Initial Payment received 8/24/26 ≈ $51M before "
        "Q3 burn; ~$35–43M after a quarter of ~$8M operating burn and ~$3.5M capex is a "
        "reasonable ballpark. Do not credit the $4.3M reclamation bond deposit — it transferred "
        "with the mining sale. The Levers 'Net cash credited to equity value' cell is a "
        "percentage haircut on this modelled figure, not a dollar override.",
    ),
    (
        NET_CASH_CREDITED,
        USD_M,
        "Net cash × 'Net cash credited to equity value' (a % lever, default 100%). Lower the "
        "percentage if you think cash gets consumed before shareholders see the benefit — do not "
        "paste a dollar target into that lever cell.",
    ),
    (SECTION_RESULT, "", ""),
    (
        EQUITY_VALUE,
        USD_M,
        "Metals business + SSOF stake + fuels stake + credited net cash. The 1.5% NSR on the sold "
        "mining district is deliberately carried at zero here — it pays on an unknowable schedule. "
        "Contract buyout floor if you want to credit it elsewhere (not by editing the rate lever): "
        "$3.5M anytime, rising to $7.0M if the 7-year contingent window lapses unpaid.",
    ),
    (
        SHARES_AT_REF,
        "M shares",
        "'Shares outstanding - Model' at the reference quarter, which includes the modelled dilution "
        "drip. If you expect a large raise, add it on the Shares tab rather than editing this.",
    ),
    (
        VALUE_PER_SHARE,
        "$",
        "Equity value ÷ shares, both as at the reference quarter. A future price, not today's.",
    ),
    (
        CURRENT_PRICE,
        "$",
        "Latest close from the Price History tab, for comparison against the present value below.",
    ),
    (
        PRESENT_VALUE_PER_SHARE,
        "$",
        "The reference-quarter price discounted back to the As of date at the Levers discount rate. "
        "This is the number to compare with the current share price.",
    ),
    (
        UPSIDE_TO_PRESENT,
        PCT,
        "Present value per share versus the current price. Blank until both are available.",
    ),
]


def label_rows() -> dict[str, int]:
    """Label → 1-based row on the Valuation tab (row 1 is the header)."""
    out: dict[str, int] = {}
    for i, (label, _units, _note) in enumerate(ROWS, start=2):
        out.setdefault(label, i)
    return out


def _ref(label: str) -> str:
    return f"$C${label_rows()[label]}"


def _qf_at_ref(qf_label: str, qf_rows: dict[str, int]) -> str:
    """Value of a Quarterly Financials row at the reference quarter."""
    row = qf_rows[qf_label]
    return (
        f"OFFSET('{L.QUARTERLY}'!${L.FIRST_VALUE_COL}${row},0,{_ref(REFERENCE_OFFSET)})"
    )


def _quarter_index_of(cell: str) -> str:
    return f"(VALUE(LEFT({cell},4))*4+VALUE(RIGHT({cell},1)))"


def value_formulas(qf_rows: dict[str, int]) -> dict[str, Any]:
    """Label → value or formula for column C, resolved against the live QF row map."""
    ref_q = _ref(REFERENCE_QUARTER)
    first_q = f"{L.YEARS[0]}*4+1"

    ssof_already = (
        f"=IF({_quarter_index_of(lv.lever_ref(lv.SSOF_PROCEEDS_QUARTER))}"
        f'<={_quarter_index_of(ref_q)},"yes","no")'
    )

    return {
        REFERENCE_QUARTER: DEFAULT_REFERENCE_QUARTER,
        REFERENCE_OFFSET: f"={_quarter_index_of(ref_q)}-({first_q})",
        AS_OF: f"={lv.lever_ref(lv.AS_OF_DATE)}",
        YEARS_TO_REFERENCE: (
            f"=({_qf_at_ref(L.QUARTER_ENDING, qf_rows)}-{_ref(AS_OF)})/365"
        ),
        ANNUAL_CONTRIBUTION: f"=4*N({_qf_at_ref(L.METALS_CONTRIBUTION_MODEL, qf_rows)})",
        ANNUAL_CORP_GA: f"=4*N({_qf_at_ref(L.CORP_GA_MODEL, qf_rows)})",
        METALS_EBITDA: f"={_ref(ANNUAL_CONTRIBUTION)}-{_ref(ANNUAL_CORP_GA)}",
        METALS_MULTIPLE: f"={lv.lever_ref(lv.METALS_MULTIPLE)}",
        METALS_VALUE: (
            f"=MAX(0,{_ref(METALS_EBITDA)}*{_ref(METALS_MULTIPLE)}"
            f"*{lv.lever_ref(lv.METALS_ACHIEVED)}/100)"
        ),
        SSOF_GROSS: f"={lv.lever_ref(lv.SSOF_GROSS_VALUE)}",
        SSOF_SHARE: f"={lv.lever_ref(lv.SSOF_OWNERSHIP)}",
        SSOF_ACHIEVED: f"={lv.lever_ref(lv.SSOF_ACHIEVED)}",
        SSOF_CASH_SOLD: f"={lv.lever_ref(lv.SSOF_CASH_SOLD)}",
        SSOF_ALREADY_IN_CASH: ssof_already,
        SSOF_VALUE: (
            f"={_ref(SSOF_GROSS)}*{_ref(SSOF_SHARE)}/100*{_ref(SSOF_ACHIEVED)}/100"
            f'*(1-IF({_ref(SSOF_ALREADY_IN_CASH)}="yes",{_ref(SSOF_CASH_SOLD)}/100,0))'
        ),
        FUELS_VALUE: (
            f"={lv.lever_ref(lv.FUELS_VALUE)}*{lv.lever_ref(lv.FUELS_ACHIEVED)}/100"
        ),
        CASH_AT_REF: f"=N({_qf_at_ref(L.CASH_MODEL, qf_rows)})",
        DEBT_AT_REF: f"=N({_qf_at_ref(L.TOTAL_DEBT_MODEL, qf_rows)})",
        NET_CASH: f"={_ref(CASH_AT_REF)}-{_ref(DEBT_AT_REF)}",
        NET_CASH_CREDITED: (
            f"={_ref(NET_CASH)}*{lv.lever_ref(lv.NET_CASH_CREDIT)}/100"
        ),
        EQUITY_VALUE: (
            f"={_ref(METALS_VALUE)}+{_ref(SSOF_VALUE)}+{_ref(FUELS_VALUE)}"
            f"+{_ref(NET_CASH_CREDITED)}"
        ),
        SHARES_AT_REF: f"=N({_qf_at_ref(L.SHARES_MODEL, qf_rows)})",
        VALUE_PER_SHARE: (
            f'=IF({_ref(SHARES_AT_REF)}<=0,"",{_ref(EQUITY_VALUE)}/{_ref(SHARES_AT_REF)})'
        ),
        CURRENT_PRICE: (
            "=LET(d,'Price History'!$A$2:$E,"
            'IFERROR(INDEX(SORT(FILTER(d,INDEX(d,0,1)<>""),1,FALSE),1,5),""))'
        ),
        PRESENT_VALUE_PER_SHARE: (
            f'=IF(OR({_ref(VALUE_PER_SHARE)}="",{_ref(YEARS_TO_REFERENCE)}<=0),"",'
            f"-PV({lv.lever_ref(lv.DISCOUNT_RATE)}/100,{_ref(YEARS_TO_REFERENCE)},0,"
            f"{_ref(VALUE_PER_SHARE)}))"
        ),
        UPSIDE_TO_PRESENT: (
            f'=IF(OR(N({_ref(CURRENT_PRICE)})=0,{_ref(PRESENT_VALUE_PER_SHARE)}=""),"",'
            f"({_ref(PRESENT_VALUE_PER_SHARE)}/{_ref(CURRENT_PRICE)}-1)*100)"
        ),
    }


NUMBER_FORMAT_BY_LABEL: dict[str, str] = {
    REFERENCE_OFFSET: "#,##0",
    YEARS_TO_REFERENCE: "#,##0.00",
    ANNUAL_CONTRIBUTION: "#,##0.00",
    ANNUAL_CORP_GA: "#,##0.00",
    METALS_EBITDA: "#,##0.00",
    METALS_MULTIPLE: "#,##0.0",
    METALS_VALUE: "#,##0.00",
    SSOF_GROSS: "#,##0.00",
    SSOF_SHARE: "#,##0.00",
    SSOF_ACHIEVED: "#,##0.00",
    SSOF_CASH_SOLD: "#,##0.00",
    SSOF_VALUE: "#,##0.00",
    FUELS_VALUE: "#,##0.00",
    CASH_AT_REF: "#,##0.00",
    DEBT_AT_REF: "#,##0.00",
    NET_CASH: "#,##0.00",
    NET_CASH_CREDITED: "#,##0.00",
    EQUITY_VALUE: "#,##0.00",
    SHARES_AT_REF: "#,##0.00",
    VALUE_PER_SHARE: "#,##0.00",
    CURRENT_PRICE: "#,##0.00",
    PRESENT_VALUE_PER_SHARE: "#,##0.00",
    UPSIDE_TO_PRESENT: "#,##0.0",
}

# Only the reference quarter is a human input on this tab; everything else derives.
INPUT_LABELS: tuple[str, ...] = (REFERENCE_QUARTER,)
