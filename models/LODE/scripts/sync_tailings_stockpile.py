#!/usr/bin/env python3
"""Push strong-2030 silver + tailings-stockpile model changes to the live LODE sheet.

- Inserts four Quarterly Financials rows if missing
- Rewrites Levers (full grid), QF labels A:B, model formulas, definitions, Welcome
- Re-baselines the manual-change fingerprint

Charts are not touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from sheets import SheetsClient  # noqa: E402
from sheets.formulas import col_letter  # noqa: E402
from sheets.labels import insert_rows_before_label  # noqa: E402
from models.LODE import levers as lv  # noqa: E402
from models.LODE import layout as L  # noqa: E402
from models.LODE import financials_definitions as DEF  # noqa: E402
from models.LODE import welcome as WEL  # noqa: E402
from models.LODE import manual_guard as guard  # noqa: E402
from models.LODE import quarterly_model_formulas as qmf  # noqa: E402
from models.LODE.scripts import setup_lode_workbook as setup  # noqa: E402

NEW_QF_LABELS = [
    L.TAILINGS_STOCKPILE_ADD,
    L.TAILINGS_INVENTORY,
    L.TAILINGS_STOCKPILE_DRAW,
    L.STOCKPILE_METAL_REVENUE,
]


def _ensure_qf_rows(client: SheetsClient) -> None:
    live = {row[0] for row in L.live_quarterly_ab(client) if row}
    missing = [lab for lab in NEW_QF_LABELS if lab not in live]
    if not missing:
        print("QF rows already present")
        return
    if missing != NEW_QF_LABELS:
        raise RuntimeError(
            f"Partial stockpile rows on sheet ({missing}); fix layout by hand before syncing"
        )
    insert_rows_before_label(
        client,
        tab=L.QUARTERLY,
        before_label=L.SECTION_METALS_ECON,
        labels=NEW_QF_LABELS,
    )
    print(f"Inserted {len(NEW_QF_LABELS)} rows before {L.SECTION_METALS_ECON!r}")


def _write_qf_labels(client: SheetsClient) -> None:
    ws = client.worksheet(L.QUARTERLY)
    ws.update(
        [[label, units] for label, units in L.ROWS],
        range_name=f"A1:B{len(L.ROWS)}",
        value_input_option="RAW",
    )
    print(f"QF A:B rewritten ({len(L.ROWS)} rows)")


def _restore_formulas(client: SheetsClient) -> None:
    qmf.assert_live_layout(client, action="sync tailings stockpile")
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
    # Editable plan paths (unchanged values, but re-assert uplift path from repo)
    for label, path in L.EDITABLE_PATHS.items():
        row = labels[label]
        batch.append(
            {
                "range": f"'{L.QUARTERLY}'!{L.FIRST_VALUE_COL}{row}:{end_col}{row}",
                "values": [list(path)],
            }
        )
    client.spreadsheet.values_batch_update(
        {"valueInputOption": "USER_ENTERED", "data": batch}
    )
    print(f"Wrote {len(batch)} QF formula/plan rows")


def _write_definitions(client: SheetsClient) -> None:
    ids = {ws.title: ws.id for ws in client.spreadsheet.worksheets()}
    setup.write_definitions(client, ids[DEF.DEFINITIONS_SHEET])


def _write_welcome(client: SheetsClient) -> None:
    ids = {ws.title: ws.id for ws in client.spreadsheet.worksheets()}
    setup.write_welcome(client, ids[WEL.WELCOME_SHEET])


# Levers whose Value+Default we intentionally reset to the new repo defaults.
RESET_LEVER_VALUES = {
    lv.MATERIAL_BASE_PER_TON,
    lv.TAILINGS_OFFTAKE_PER_TON,
    lv.TAILINGS_STOCKPILE_PCT,
    lv.TAILINGS_STOCKPILE_START,
    lv.GLASS_UPLIFT_PER_TON,
    lv.GLASS_UPLIFT_ACHIEVED,
    lv.METAL_UPLIFT_PER_TON,
    lv.METAL_UPLIFT_ACHIEVED,
    lv.TAILINGS_BACKLOG_DRAW,
}


def _write_levers(client: SheetsClient) -> None:
    """Rewrite Levers grid; keep prior Values except for the stockpile/silver set."""
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

    restores = []
    live_rows = lv.lever_rows()
    for label, value in prior_value_by_label.items():
        if label in RESET_LEVER_VALUES or label not in live_rows:
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
        f"Levers rewritten; preserved {len(restores)} unrelated Values; "
        f"reset {len(RESET_LEVER_VALUES)} silver/stockpile levers"
    )


def main() -> None:
    client = SheetsClient(ticker="LODE")
    _ensure_qf_rows(client)
    _write_qf_labels(client)
    _write_levers(client)
    _restore_formulas(client)
    _write_definitions(client)
    _write_welcome(client)
    guard.record(client)
    print(f"Fingerprint recorded → {guard.FINGERPRINT_PATH}")
    print("Done. Verify chart series manually if lines look shifted after the row insert.")


if __name__ == "__main__":
    main()
