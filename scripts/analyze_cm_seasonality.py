#!/usr/bin/env python3
"""Print contribution margin seasonality from live model constants."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.cm_seasonality import CM_SEASONAL_ADJ_BY_MONTH  # noqa: E402

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

    print("Quarterly Contribution Margin (historical, data/contribution_margin_quarterly.json):")
    for year, quarter, cm in quarters:
        print(f"  {year} Q{quarter}: {cm * 100:+.1f}%")

    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    print("\nModel monthly adjustments (Seasonality row 6, from sheets/cm_seasonality.py):")
    for month, adj in enumerate(CM_SEASONAL_ADJ_BY_MONTH, 1):
        print(f"  {months[month - 1]}: {adj * 10000:+.0f} bps")

    print("\nQuarterly average of monthly adjustments:")
    for quarter in range(1, 5):
        vals = CM_SEASONAL_ADJ_BY_MONTH[(quarter - 1) * 3 : quarter * 3]
        print(f"  Q{quarter}: {sum(vals) / 3 * 10000:+.1f} bps")

    print("\nAt 6.0% core CM:")
    for month, adj in enumerate(CM_SEASONAL_ADJ_BY_MONTH, 1):
        print(f"  {months[month - 1]}: {(0.06 + adj) * 100:.2f}%")


if __name__ == "__main__":
    main()
