#!/usr/bin/env python3
"""Push Quarterly Financials valuation series + SSOF/Fuels growth levers to the live LODE sheet.

- Inserts the VALUATION block after Market cap if missing
- Rewrites Levers (preserves prior Values; new growth levers get repo defaults)
- Rewrites QF A:B labels, all *-Model formulas, Valuation tab, definitions, Welcome
- Re-baselines the manual-change fingerprint

Charts are not touched — add or point series at Implied / Present stock price in the UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.labels import insert_rows_after_label, sheet_id  # noqa: E402
from models.LODE import levers as lv  # noqa: E402
from models.LODE import layout as L  # noqa: E402
from models.LODE import financials_definitions as DEF  # noqa: E402
from models.LODE import welcome as WEL  # noqa: E402
from models.LODE import valuation as VAL  # noqa: E402
from models.LODE import manual_guard as guard  # noqa: E402
from models.LODE import quarterly_model_formulas as qmf  # noqa: E402
from models.LODE.scripts import setup_lode_workbook as setup  # noqa: E402

# Spacer + section + SoP series, in layout order after Market cap.
VALUATION_BLOCK: list[tuple[str, str]] = []
_seen_market = False
for _label, _units in L.ROWS:
    if _label == L.MARKET_CAP:
        _seen_market = True
        continue
    if _seen_market:
        VALUATION_BLOCK.append((_label, _units))

NEW_QF_LABELS = [lab for lab, _u in VALUATION_BLOCK]


def _ensure_qf_rows(client: SheetsClient) -> None:
    live = {row[0] for row in L.live_quarterly_ab(client) if row}
    if L.SECTION_VALUATION in live and L.IMPLIED_STOCK_PRICE_MODEL in live:
        print("QF valuation block already present")
        return
    missing = [lab for lab in NEW_QF_LABELS if lab and lab not in live]
    # Spacer "" may already exist elsewhere; only require named rows.
    required = [lab for lab in NEW_QF_LABELS if lab]
    if any(lab in live for lab in required) and L.SECTION_VALUATION not in live:
        raise RuntimeError(
            f"Partial valuation rows on sheet ({missing}); fix layout by hand before syncing"
        )
    insert_rows_after_label(
        client,
        tab=L.QUARTERLY,
        after_label=L.MARKET_CAP,
        labels=NEW_QF_LABELS,
    )
    print(f"Inserted {len(NEW_QF_LABELS)} rows after {L.MARKET_CAP!r}")


def _write_qf_labels(client: SheetsClient) -> None:
    ws = client.worksheet(L.QUARTERLY)
    ws.update(
        [[label, units] for label, units in L.ROWS],
        range_name=f"A1:B{len(L.ROWS)}",
        value_input_option="RAW",
    )
    print(f"QF A:B rewritten ({len(L.ROWS)} rows)")


def _restore_formulas(client: SheetsClient) -> None:
    qmf.assert_live_layout(client, action="sync quarterly valuation")
    labels = qmf.sheet_label_map(client)
    end_col = col_letter(L.FIRST_VALUE_COL_INDEX + L.N_QUARTERS - 1)
    batch = []
    for label in qmf.MODEL_FORMULA_LABELS:
        cells = qmf.row_cells_for_label(label, L.N_QUARTERS, label_to_row=labels)
        if cells is None:
            continue
        row = labels[label]
        batch.append(
            {
                "range": f"'{L.QUARTERLY}'!{L.FIRST_VALUE_COL}{row}:{end_col}{row}",
                "values": [cells],
            }
        )
    client.spreadsheet.values_batch_update(
        {"valueInputOption": "USER_ENTERED", "data": batch}
    )
    print(f"Wrote {len(batch)} QF formula rows")


def _format_valuation_block(client: SheetsClient) -> None:
    """Section band + number formats for the new rows (setup-equivalent, local only)."""
    labels = L.label_row_numbers()
    sid = sheet_id(client, L.QUARTERLY)
    n = L.N_QUARTERS
    last_col_idx = L.FIRST_VALUE_COL_INDEX + n - 1
    requests: list[dict] = []

    sec = labels[L.SECTION_VALUATION] - 1
    requests.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": sec,
                    "endRowIndex": sec + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": last_col_idx,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.87,
                            "green": 0.90,
                            "blue": 0.94,
                        },
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        }
    )

    for label, fmt in L.NUMBER_FORMAT_BY_LABEL.items():
        if label not in {
            L.ANNUAL_METALS_CONTRIB_MODEL,
            L.ANNUAL_CORP_GA_MODEL,
            L.METALS_EBITDA_PROXY_MODEL,
            L.METALS_BUSINESS_VALUE_MODEL,
            L.SSOF_GROSS_MODEL,
            L.SSOF_STAKE_VALUE_MODEL,
            L.FUELS_STAKE_VALUE_MODEL,
            L.NET_CASH_MODEL,
            L.NET_CASH_CREDITED_MODEL,
            L.EQUITY_VALUE_MODEL,
            L.IMPLIED_STOCK_PRICE_MODEL,
            L.PRESENT_STOCK_PRICE_MODEL,
        }:
            continue
        r = labels[label] - 1
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": r,
                        "endRowIndex": r + 1,
                        "startColumnIndex": L.FIRST_VALUE_COL_INDEX - 1,
                        "endColumnIndex": last_col_idx,
                    },
                    "cell": {
                        "userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": fmt}}
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    client.spreadsheet.batch_update({"requests": requests})
    print(f"Formatted valuation block ({len(requests)} requests)")


def _write_levers(client: SheetsClient) -> None:
    """Rewrite Levers grid; keep prior Values for existing levers."""
    ws = client.worksheet(lv.LEVERS_SHEET)
    prior = ws.get("A1:G200")
    prior_value_by_label: dict[str, object] = {}
    for row in prior[1:]:
        if not row or not row[0]:
            continue
        if len(row) > 2 and row[2] != "":
            prior_value_by_label[str(row[0])] = row[2]

    ids = {ws.title: ws.id for ws in client.spreadsheet.worksheets()}
    setup.write_levers(client, ids[lv.LEVERS_SHEET])

    # New growth levers should keep repo defaults (do not restore stale blanks).
    new_defaults = {lv.SSOF_VALUE_GROWTH, lv.FUELS_VALUE_GROWTH}

    restores = []
    live_rows = lv.lever_rows()
    for label, value in prior_value_by_label.items():
        if label in new_defaults or label not in live_rows:
            continue
        restores.append(
            {
                "range": f"'{lv.LEVERS_SHEET}'!C{live_rows[label]}",
                "values": [[value]],
            }
        )
    if restores:
        client.spreadsheet.values_batch_update(
            {"valueInputOption": "USER_ENTERED", "data": restores}
        )
    print(
        f"Levers rewritten; preserved {len(restores)} Values; "
        f"new defaults for {sorted(new_defaults)}"
    )


def _write_valuation(client: SheetsClient) -> None:
    ids = {ws.title: ws.id for ws in client.spreadsheet.worksheets()}
    setup.write_valuation(client, ids[VAL.VALUATION_SHEET])


def _write_definitions(client: SheetsClient) -> None:
    ids = {ws.title: ws.id for ws in client.spreadsheet.worksheets()}
    setup.write_definitions(client, ids[DEF.DEFINITIONS_SHEET])


def _write_welcome(client: SheetsClient) -> None:
    ids = {ws.title: ws.id for ws in client.spreadsheet.worksheets()}
    setup.write_welcome(client, ids[WEL.WELCOME_SHEET])


def main() -> None:
    client = SheetsClient(ticker="LODE")
    _ensure_qf_rows(client)
    _write_qf_labels(client)
    _write_levers(client)
    _restore_formulas(client)
    _format_valuation_block(client)
    _write_valuation(client)
    _write_definitions(client)
    _write_welcome(client)
    guard.record(client)
    print(f"Fingerprint recorded → {guard.FINGERPRINT_PATH}")
    print(
        "Done. Chart 'Implied stock price - Model' (and optionally "
        "'Present stock price discounted - Model') manually in the Sheets UI."
    )


if __name__ == "__main__":
    main()
