#!/usr/bin/env python3
"""Print contribution margin seasonality analysis from SEC supplements."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.cm_seasonality import (  # noqa: E402
    CM_SEASONAL_ADJ_BY_MONTH,
    CM_SEASONAL_ADJ_BY_QUARTER,
)

DATA_FILE = ROOT / "data" / "contribution_margin_quarterly.json"

def main() -> None:
    stored = json.loads(DATA_FILE.read_text())["quarters"]
    quarters = sorted(
        (
            (int(key.split()[0]), int(key.split()[1][1]), value)
            for key, value in stored.items()
        ),
        key=lambda x: (x[0], x[1]),
    )

    print("Quarterly Contribution Margin (stored):")
    for year, quarter, cm in quarters:
        print(f"  {year} Q{quarter}: {cm * 100:+.1f}%")

    ex_2023 = [(year, quarter, cm) for year, quarter, cm in quarters if year != 2023]
    annual = sum(cm for _, _, cm in ex_2023) / len(ex_2023)

    print(f"\nEx-2023 annual mean: {annual * 100:.2f}%")
    print("Quarterly seasonal deviation:")
    for q in range(1, 5):
        vals = [cm for y, qq, cm in ex_2023 if qq == q]
        avg = sum(vals) / len(vals)
        print(f"  Q{q}: {avg * 100:.2f}% ({(avg - annual) * 10000:+.0f} bps, n={len(vals)})")

    print("\nModel monthly adjustments (Seasonality row 6, smoothed within quarter):")
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    for month, adj in enumerate(CM_SEASONAL_ADJ_BY_MONTH, 1):
        print(f"  {months[month - 1]}: {adj * 10000:+.0f} bps")

    print("\nQuarterly check (monthly average vs target):")
    for quarter in range(1, 5):
        vals = CM_SEASONAL_ADJ_BY_MONTH[(quarter - 1) * 3 : quarter * 3]
        print(
            f"  Q{quarter}: {sum(vals) / 3 * 10000:+.1f} bps "
            f"(target {CM_SEASONAL_ADJ_BY_QUARTER[quarter] * 10000:+.0f})"
        )

    print("\nAt 6.0% core CM:")
    for month, adj in enumerate(CM_SEASONAL_ADJ_BY_MONTH, 1):
        print(f"  {months[month - 1]}: {(0.06 + adj) * 100:.2f}%")


if __name__ == "__main__":
    main()
