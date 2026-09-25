"""Canonical ``- Model`` formulas for CSIQ Quarterly Financials.

``{c}`` is the current column, ``{cp}`` the prior column, ``{Row Label}`` a row on
this tab. Scalars come from the Levers tab. No magic numbers.
"""

from __future__ import annotations

import re
from typing import Any

from sheets.formulas import col_letter as _col_letter

from models.CSIQ import levers as lv
from models.CSIQ.layout import (
    ASSET_SALES_ACTUAL,
    ASSET_SALES_MODEL,
    ASSET_SALES_PLAN,
    AS_OF_DATE,
    CONVERTS_ACTUAL,
    CONVERTS_MODEL,
    CSI_CROSSCHECK,
    CSI_STAKE,
    DILUTED_PRICE,
    ELECTRICITY_ACTUAL,
    ELECTRICITY_MODEL,
    ELECTRICITY_PLAN,
    EQUITY_VALUE,
    EXUS_MODULE_PLAN,
    EXUS_STORAGE_PLAN,
    FIRST_VALUE_COL,
    FIRST_VALUE_COL_INDEX,
    FLOOR_EQUITY,
    GP_ACTUAL,
    GP_MODEL,
    HOLDCO_NET_DEBT,
    IMPLIED_PRICE,
    MARKET_CAP,
    MFG_REV_ACTUAL,
    MFG_REV_MODEL,
    MODULE_GW_ACTUAL,
    MODULE_GW_MODEL,
    MODULE_REV_ACTUAL,
    MODULE_REV_MODEL,
    N_QUARTERS,
    OI_ACTUAL,
    OI_MODEL,
    OPEX_ACTUAL,
    OPEX_MODEL,
    OTHER_MFG_REV_ACTUAL,
    OTHER_MFG_REV_MODEL,
    POWER_ACTUAL,
    POWER_MODEL,
    POWER_PLAN,
    PRESENT_PRICE,
    QUARTER_ENDING,
    QUARTERLY,
    RECURRENT_REV_ACTUAL,
    RECURRENT_REV_MODEL,
    RECURRENT_STAKE,
    SHARES_ACTUAL,
    SHARES_MODEL,
    STOCK_PRICE,
    STORAGE_GWH_ACTUAL,
    STORAGE_GWH_MODEL,
    STORAGE_REV_ACTUAL,
    STORAGE_REV_MODEL,
    TOTAL_REV_ACTUAL,
    TOTAL_REV_MODEL,
    US_MODULE_EBITDA,
    US_MODULE_EQUITY,
    US_MODULE_PHASE,
    US_MODULE_PLAN,
    US_STORAGE_EBITDA,
    US_STORAGE_EQUITY,
    US_STORAGE_PHASE,
    US_STORAGE_PLAN,
    YEAR,
    YEARS_FROM_PRESENT,
    label_map_from_ab,
    live_quarterly_ab,
    require_live_layout_match,
)

FINANCIALS_TAB = QUARTERLY
FIRST_VALUE_COL = FIRST_VALUE_COL
FIRST_VALUE_COL_INDEX = FIRST_VALUE_COL_INDEX
COLUMN_RELATIVE_TEMPLATES: dict[str, str] = {}

_LABEL_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
PRICE_HISTORY_SHEET = "Price History"


def col_letter(n: int) -> str:
    return _col_letter(n)


def apply_row_labels(template: str, label_to_row: dict[str, int]) -> str:
    out = template
    for label in sorted(label_to_row, key=len, reverse=True):
        out = out.replace("{" + label + "}", str(label_to_row[label]))
    return out


def sheet_label_map(client: Any) -> dict[str, int]:
    return label_map_from_ab(live_quarterly_ab(client))


def assert_live_layout(client: Any, *, action: str = "restore model formulas") -> None:
    require_live_layout_match(client, action=action)


def _cur(label: str) -> str:
    return f"{{c}}{{{label}}}"


def _prev(label: str) -> str:
    return f"{{cp}}{{{label}}}"


def _prefer(actual: str, model: str) -> str:
    return f'IF({actual}<>"",{actual},{model})'


def _blank(body: str) -> str:
    return f'=IF({_cur(YEAR)}="","",{body})'


def _lever(label: str) -> str:
    return lv.lever_ref(label)


def _pct(label: str) -> str:
    return f"{_lever(label)}/100"


def _us_module_gw() -> str:
    return f"{_cur(US_MODULE_PLAN)}*{_pct(lv.US_MODULE_VOL_ACH)}"


def _exus_module_gw() -> str:
    return f"{_cur(EXUS_MODULE_PLAN)}*{_pct(lv.EXUS_MODULE_VOL_ACH)}"


def _us_storage_gwh() -> str:
    return f"{_cur(US_STORAGE_PLAN)}*{_pct(lv.US_STORAGE_VOL_ACH)}"


def _exus_storage_gwh() -> str:
    return f"{_cur(EXUS_STORAGE_PLAN)}*{_pct(lv.EXUS_STORAGE_VOL_ACH)}"


def _years_from_present() -> str:
    return (
        f'=IF({_cur(QUARTER_ENDING)}="","",'
        f"({_cur(QUARTER_ENDING)}-{_cur(AS_OF_DATE)})/365)"
    )


def _module_gw_model() -> str:
    model = f"{_us_module_gw()}+{_exus_module_gw()}"
    return _blank(_prefer(_cur(MODULE_GW_ACTUAL), model))


def _storage_gwh_model() -> str:
    model = f"{_us_storage_gwh()}+{_exus_storage_gwh()}"
    return _blank(_prefer(_cur(STORAGE_GWH_ACTUAL), model))


def _module_rev_model() -> str:
    # GW × $/W × 1,000 = $M.
    model = (
        f"{_us_module_gw()}*{_lever(lv.US_MODULE_ASP)}*1000"
        f"+{_exus_module_gw()}*{_lever(lv.EXUS_MODULE_ASP)}*1000"
    )
    return _blank(_prefer(_cur(MODULE_REV_ACTUAL), model))


def _storage_rev_model() -> str:
    # GWh × $/kWh = $M.
    model = (
        f"{_us_storage_gwh()}*{_lever(lv.US_STORAGE_ASP)}"
        f"+{_exus_storage_gwh()}*{_lever(lv.EXUS_STORAGE_ASP)}"
    )
    return _blank(_prefer(_cur(STORAGE_REV_ACTUAL), model))


def _other_mfg_rev_model() -> str:
    return _blank(_prefer(_cur(OTHER_MFG_REV_ACTUAL), _lever(lv.OTHER_MFG_REV)))


def _mfg_rev_model() -> str:
    model = (
        f"N({_cur(MODULE_REV_MODEL)})+N({_cur(STORAGE_REV_MODEL)})"
        f"+N({_cur(OTHER_MFG_REV_MODEL)})"
    )
    return _blank(_prefer(_cur(MFG_REV_ACTUAL), model))


def _us_module_ebitda() -> str:
    """Quarterly US module cash EBITDA. Can be negative while the lease is ahead of margin."""
    volume = _us_module_gw()
    margin = (
        f"{_lever(lv.US_MODULE_MARGIN)}*{_cur(US_MODULE_PHASE)}/100"
        f"*{_pct(lv.US_MODULE_MARGIN_ACH)}"
    )
    gross = f"{volume}*{margin}*1000"
    full_quarter_gw = f"({_lever(lv.US_LEASE_GW)}/4)"
    lease = (
        f"({_lever(lv.US_LEASE)}/4)*"
        f'IF({full_quarter_gw}<=0,0,MIN(1,{volume}/({full_quarter_gw})))'
    )
    return _blank(f"{gross}-({lease})")


def _us_storage_ebitda() -> str:
    return _blank(
        f"{_us_storage_gwh()}*{_lever(lv.US_STORAGE_ASP)}"
        f"*{_pct(lv.US_STORAGE_MARGIN)}*{_cur(US_STORAGE_PHASE)}/100"
        f"*{_pct(lv.US_STORAGE_MARGIN_ACH)}"
    )


def _asset_sales_model() -> str:
    return _blank(_prefer(_cur(ASSET_SALES_ACTUAL), _cur(ASSET_SALES_PLAN)))


def _power_model() -> str:
    return _blank(_prefer(_cur(POWER_ACTUAL), _cur(POWER_PLAN)))


def _electricity_model() -> str:
    return _blank(_prefer(_cur(ELECTRICITY_ACTUAL), _cur(ELECTRICITY_PLAN)))


def _recurrent_rev_model() -> str:
    model = (
        f"N({_cur(ASSET_SALES_MODEL)})+N({_cur(POWER_MODEL)})"
        f"+N({_cur(ELECTRICITY_MODEL)})"
    )
    return _blank(_prefer(_cur(RECURRENT_REV_ACTUAL), model))


def _total_rev_model() -> str:
    model = f"N({_cur(MFG_REV_MODEL)})+N({_cur(RECURRENT_REV_MODEL)})"
    return _blank(_prefer(_cur(TOTAL_REV_ACTUAL), model))


def _gp_model() -> str:
    model = f"N({_cur(TOTAL_REV_MODEL)})*{_pct(lv.GROSS_MARGIN)}"
    return _blank(_prefer(_cur(GP_ACTUAL), model))


def _opex_model() -> str:
    return _blank(_prefer(_cur(OPEX_ACTUAL), _lever(lv.OPEX_Q)))


def _oi_model() -> str:
    model = f"N({_cur(GP_MODEL)})-N({_cur(OPEX_MODEL)})"
    return _blank(_prefer(_cur(OI_ACTUAL), model))


def _converts_model() -> str:
    """Actual, else the lever once the quarter is still ahead, else carry the prior print.

    Quarters before the first reported balance stay blank instead of being filled
    with today's convert balance.
    """
    carried = f'IF({_prev(CONVERTS_MODEL)}="","",{_prev(CONVERTS_MODEL)})'
    return _blank(
        f'IF({_cur(CONVERTS_ACTUAL)}<>"",{_cur(CONVERTS_ACTUAL)},'
        f'IF(N({_cur(YEARS_FROM_PRESENT)})>0,{_lever(lv.CONVERTS)},{carried}))'
    )


def _converts_model_first() -> str:
    return _blank(
        f'IF({_cur(CONVERTS_ACTUAL)}<>"",{_cur(CONVERTS_ACTUAL)},'
        f'IF(N({_cur(YEARS_FROM_PRESENT)})>0,{_lever(lv.CONVERTS)},""))'
    )


def _shares_model() -> str:
    grown = (
        f'IF({_prev(SHARES_MODEL)}="","",'
        f"{_prev(SHARES_MODEL)}*(1+{_pct(lv.SHARE_DRIP)}))"
    )
    return _blank(_prefer(_cur(SHARES_ACTUAL), grown))


def _shares_model_first() -> str:
    return _blank(_prefer(_cur(SHARES_ACTUAL), '""'))


def _stock_price() -> str:
    qe = _cur(QUARTER_ENDING)
    return (
        f"=LET(d,'{PRICE_HISTORY_SHEET}'!$A$2:$E,"
        f'IF(OR({qe}="",{qe}>TODAY()),"",'
        f'IFERROR(XLOOKUP({qe},INDEX(d,0,1),INDEX(d,0,5),"",-1),"")))'
    )


def _market_cap() -> str:
    return (
        f'=IF(OR(N({_cur(SHARES_MODEL)})=0,N({_cur(STOCK_PRICE)})=0),"",'
        f"{_cur(SHARES_MODEL)}*{_cur(STOCK_PRICE)})"
    )


def _csi_stake() -> str:
    listed = (
        f"{_lever(lv.CSI_MKTCAP)}*{_pct(lv.CSI_OWNED)}"
        f"*(1-{_pct(lv.CSI_DISCOUNT)})*{_pct(lv.CSI_ACH)}"
    )
    return _blank(listed)


def _csi_crosscheck() -> str:
    equity = (
        f"({_lever(lv.CSI_EBITDA)}*{_lever(lv.CSI_MULTIPLE)}-{_lever(lv.CSI_NET_DEBT)})"
        f"*{_pct(lv.CSI_OWNED)}"
    )
    return _blank(equity)


def _recurrent_stake() -> str:
    return _blank(
        f"{_lever(lv.RECURRENT_EQUITY)}*{_pct(lv.RECURRENT_OWNED)}*{_pct(lv.RECURRENT_ACH)}"
    )


def _us_module_equity() -> str:
    annual = f"4*N({_cur(US_MODULE_EBITDA)})"
    return _blank(
        f"MAX(0,{annual})*{_lever(lv.US_MODULE_MULTIPLE)}"
        f"*{_pct(lv.POWERTECH_OWNED)}*{_pct(lv.US_VALUE_ACH)}"
    )


def _us_storage_equity() -> str:
    annual = f"4*N({_cur(US_STORAGE_EBITDA)})"
    return _blank(
        f"MAX(0,{annual}*{_lever(lv.US_STORAGE_MULTIPLE)}-{_lever(lv.US_STORAGE_DEBT)})"
        f"*{_pct(lv.POWERTECH_OWNED)}*{_pct(lv.US_VALUE_ACH)}"
    )


def _holdco_net_debt() -> str:
    cash = f"{_lever(lv.HOLDCO_CASH)}*{_pct(lv.HOLDCO_CASH_CREDIT)}"
    return _blank(f"N({_cur(CONVERTS_MODEL)})-({cash})")


def _floor_equity() -> str:
    return _blank(
        f"N({_cur(CSI_STAKE)})+N({_cur(RECURRENT_STAKE)})-N({_cur(HOLDCO_NET_DEBT)})"
    )


def _equity_value() -> str:
    return _blank(
        f"N({_cur(FLOOR_EQUITY)})+N({_cur(US_MODULE_EQUITY)})+N({_cur(US_STORAGE_EQUITY)})"
    )


def _price(numerator: str) -> str:
    return _blank(
        f'IF(N({_cur(SHARES_MODEL)})=0,"",{numerator}/N({_cur(SHARES_MODEL)}))'
    )


def _implied_price() -> str:
    return _price(f"N({_cur(EQUITY_VALUE)})")


def _discounted_equity() -> str:
    """Floor today; US ramp discounted when the quarter is still in the future."""
    t = f"N({_cur(YEARS_FROM_PRESENT)})"
    rate = f"(1+{_pct(lv.DISCOUNT_RATE)})"
    us = f"N({_cur(US_MODULE_EQUITY)})+N({_cur(US_STORAGE_EQUITY)})"
    floor = f"N({_cur(FLOOR_EQUITY)})"
    return f'IF({t}<=0,{floor}+{us},{floor}+{us}/({rate}^{t}))'


def _present_price() -> str:
    return _price(_discounted_equity())


def _diluted_price() -> str:
    """Adds converts back, then divides by the diluted count, with the same US discount."""
    equity = _discounted_equity()
    diluted = f"N({_lever(lv.DILUTED_SHARES)})"
    return _blank(
        f'IF({diluted}=0,"",({equity}+N({_cur(CONVERTS_MODEL)}))/{diluted})'
    )


UNIFORM_FORMULA_TEMPLATES: dict[str, str] = {
    AS_OF_DATE: f"={_lever(lv.AS_OF_DATE)}",
    YEARS_FROM_PRESENT: _years_from_present(),
    MODULE_GW_MODEL: _module_gw_model(),
    STORAGE_GWH_MODEL: _storage_gwh_model(),
    MODULE_REV_MODEL: _module_rev_model(),
    STORAGE_REV_MODEL: _storage_rev_model(),
    OTHER_MFG_REV_MODEL: _other_mfg_rev_model(),
    MFG_REV_MODEL: _mfg_rev_model(),
    US_MODULE_EBITDA: _us_module_ebitda(),
    US_STORAGE_EBITDA: _us_storage_ebitda(),
    ASSET_SALES_MODEL: _asset_sales_model(),
    POWER_MODEL: _power_model(),
    ELECTRICITY_MODEL: _electricity_model(),
    RECURRENT_REV_MODEL: _recurrent_rev_model(),
    TOTAL_REV_MODEL: _total_rev_model(),
    GP_MODEL: _gp_model(),
    OPEX_MODEL: _opex_model(),
    OI_MODEL: _oi_model(),
    CONVERTS_MODEL: _converts_model(),
    SHARES_MODEL: _shares_model(),
    STOCK_PRICE: _stock_price(),
    MARKET_CAP: _market_cap(),
    CSI_STAKE: _csi_stake(),
    CSI_CROSSCHECK: _csi_crosscheck(),
    RECURRENT_STAKE: _recurrent_stake(),
    US_MODULE_EQUITY: _us_module_equity(),
    US_STORAGE_EQUITY: _us_storage_equity(),
    HOLDCO_NET_DEBT: _holdco_net_debt(),
    FLOOR_EQUITY: _floor_equity(),
    EQUITY_VALUE: _equity_value(),
    IMPLIED_PRICE: _implied_price(),
    DILUTED_PRICE: _diluted_price(),
    PRESENT_PRICE: _present_price(),
}

FIRST_COL_TEMPLATES: dict[str, str] = {
    CONVERTS_MODEL: _converts_model_first(),
    SHARES_MODEL: _shares_model_first(),
}

MODEL_FORMULA_LABELS: tuple[str, ...] = tuple(UNIFORM_FORMULA_TEMPLATES)


def formula_row_dependencies(label: str) -> frozenset[str]:
    tmpl = UNIFORM_FORMULA_TEMPLATES.get(label, "") + FIRST_COL_TEMPLATES.get(label, "")
    return frozenset(
        m.group(1)
        for m in _LABEL_PLACEHOLDER_RE.finditer(tmpl)
        if m.group(1) not in {"c", "cp"}
    )


def uniform_formula_template(label: str) -> str:
    return UNIFORM_FORMULA_TEMPLATES[label]


def row_cells_for_label(
    label: str,
    n_cols: int,
    *,
    label_to_row: dict[str, int] | None = None,
) -> list[Any] | None:
    if label not in UNIFORM_FORMULA_TEMPLATES:
        return None
    label_to_row = label_to_row or {}
    general = apply_row_labels(UNIFORM_FORMULA_TEMPLATES[label], label_to_row)
    first = (
        apply_row_labels(FIRST_COL_TEMPLATES[label], label_to_row)
        if label in FIRST_COL_TEMPLATES
        else general
    )
    cells: list[Any] = []
    for i in range(n_cols):
        col = col_letter(FIRST_VALUE_COL_INDEX + i)
        prior = col_letter(FIRST_VALUE_COL_INDEX + i - 1)
        tmpl = first if i == 0 else general
        cells.append(tmpl.replace("{c}", col).replace("{cp}", prior))
    return cells


assert N_QUARTERS == 24
