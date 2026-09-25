"""Reported quarterly actuals, in millions of USD except GW, GWh, percent, and shares.

Blank means the company has not published the figure. Nothing here is reverse-engineered
from a rounded percent. Q1 2025 product lines are H1 2025 minus Q2 2025 from the
Q2 2026 earnings release, which is exact.

Sources: Q2 2026 earnings release (2026-08-27) and Q1 2026 earnings release (2026-05-14).
"""

from __future__ import annotations

from models.CSIQ.layout import (
    ASSET_SALES_ACTUAL,
    CAPEX_ACTUAL,
    CASH_ACTUAL,
    CASH_RESTRICTED_ACTUAL,
    CONVERTS_ACTUAL,
    DEBT_ACTUAL,
    ELECTRICITY_ACTUAL,
    EPS_ACTUAL,
    GM_ACTUAL,
    GP_ACTUAL,
    MFG_GP_ACTUAL,
    MFG_OI_ACTUAL,
    MFG_REV_ACTUAL,
    MODULE_GW_ACTUAL,
    MODULE_REV_ACTUAL,
    NI_ACTUAL,
    NONRECOURSE_ACTUAL,
    OCF_ACTUAL,
    OI_ACTUAL,
    OPEX_ACTUAL,
    OTHER_MFG_REV_ACTUAL,
    POWER_ACTUAL,
    RECURRENT_GP_ACTUAL,
    RECURRENT_OI_ACTUAL,
    RECURRENT_REV_ACTUAL,
    RESTRICTED_ACTUAL,
    SHARES_ACTUAL,
    STORAGE_GWH_ACTUAL,
    STORAGE_REV_ACTUAL,
    TOTAL_REV_ACTUAL,
)


def _series(*pairs: tuple[str, float]) -> dict[str, float]:
    return dict(pairs)


def quarterly_actuals() -> dict[str, dict[str, float]]:
    return {
        MODULE_GW_ACTUAL: _series(("2026 Q1", 2.5), ("2026 Q2", 3.1)),
        STORAGE_GWH_ACTUAL: _series(("2026 Q1", 2.1), ("2026 Q2", 3.7)),
        MODULE_REV_ACTUAL: _series(
            ("2025 Q1", 797.422),
            ("2025 Q2", 1022.266),
            ("2026 Q1", 455.117),
            ("2026 Q2", 589.377),
        ),
        STORAGE_REV_ACTUAL: _series(
            ("2025 Q1", 155.310),
            ("2025 Q2", 432.399),
            ("2026 Q1", 382.758),
            ("2026 Q2", 425.922),
        ),
        # Kits + EPC and others.
        OTHER_MFG_REV_ACTUAL: _series(
            ("2025 Q1", 120.563),
            ("2025 Q2", 135.425),
            ("2026 Q1", 102.589),
            ("2026 Q2", 78.545),
        ),
        MFG_REV_ACTUAL: _series(("2026 Q1", 949.662), ("2026 Q2", 1097.535)),
        MFG_GP_ACTUAL: _series(("2026 Q1", 276.346), ("2026 Q2", 130.558)),
        MFG_OI_ACTUAL: _series(("2026 Q1", 126.817), ("2026 Q2", -49.374)),
        ASSET_SALES_ACTUAL: _series(
            ("2025 Q1", 72.151),
            ("2025 Q2", 48.091),
            ("2026 Q1", 88.541),
            ("2026 Q2", 61.114),
        ),
        POWER_ACTUAL: _series(
            ("2025 Q1", 16.499),
            ("2025 Q2", 18.809),
            ("2026 Q1", 22.416),
            ("2026 Q2", 20.053),
        ),
        ELECTRICITY_ACTUAL: _series(
            ("2025 Q1", 34.680),
            ("2025 Q2", 36.881),
            ("2026 Q1", 26.457),
            ("2026 Q2", 32.703),
        ),
        RECURRENT_REV_ACTUAL: _series(("2026 Q1", 139.232), ("2026 Q2", 117.306)),
        RECURRENT_GP_ACTUAL: _series(("2026 Q1", -14.517), ("2026 Q2", 35.971)),
        RECURRENT_OI_ACTUAL: _series(("2026 Q1", -60.253), ("2026 Q2", -19.370)),
        TOTAL_REV_ACTUAL: _series(
            ("2025 Q1", 1196.625),
            ("2025 Q2", 1693.871),
            ("2026 Q1", 1077.878),
            ("2026 Q2", 1207.714),
        ),
        GP_ACTUAL: _series(
            ("2025 Q1", 140.494),
            ("2025 Q2", 505.030),
            ("2025 Q4", 124),
            ("2026 Q1", 270.820),
            ("2026 Q2", 168.475),
        ),
        GM_ACTUAL: _series(
            ("2025 Q1", 11.7),
            ("2025 Q2", 29.8),
            ("2025 Q4", 10.2),
            ("2026 Q1", 25.1),
            ("2026 Q2", 13.9),
        ),
        OPEX_ACTUAL: _series(
            ("2025 Q1", 195.299),
            ("2025 Q2", 377.597),
            ("2025 Q4", 188),
            ("2026 Q1", 197.954),
            ("2026 Q2", 239.534),
        ),
        OI_ACTUAL: _series(
            ("2025 Q1", -54.805),
            ("2025 Q2", 127.433),
            ("2026 Q1", 72.866),
            ("2026 Q2", -71.059),
        ),
        NI_ACTUAL: _series(
            ("2025 Q1", -33.971),
            ("2025 Q2", 7.197),
            ("2025 Q4", -86),
            ("2026 Q1", -32.093),
            ("2026 Q2", -76.859),
        ),
        EPS_ACTUAL: _series(
            ("2025 Q1", -0.69),
            ("2025 Q2", -0.08),
            ("2025 Q4", -1.66),
            ("2026 Q1", -0.71),
            ("2026 Q2", -1.40),
        ),
        CASH_ACTUAL: _series(("2025 Q4", 1370.418), ("2026 Q2", 1461.248)),
        RESTRICTED_ACTUAL: _series(("2025 Q4", 570.017), ("2026 Q2", 389.108)),
        CASH_RESTRICTED_ACTUAL: _series(
            ("2025 Q2", 2264.209),
            ("2025 Q4", 1940.435),
            ("2026 Q1", 1883.291),
            ("2026 Q2", 1850.356),
        ),
        OCF_ACTUAL: _series(
            ("2025 Q1", -264),
            ("2025 Q2", 188.556),
            ("2025 Q4", -65),
            ("2026 Q1", -208.658),
            ("2026 Q2", -180.761),
        ),
        CAPEX_ACTUAL: _series(
            ("2026 Q1", 173.210),
            ("2026 Q2", 171.840),
        ),
        DEBT_ACTUAL: _series(
            ("2025 Q4", 6500),
            ("2026 Q1", 6800),
            ("2026 Q2", 7100),
        ),
        CONVERTS_ACTUAL: _series(("2025 Q4", 195.313), ("2026 Q2", 420.063)),
        NONRECOURSE_ACTUAL: _series(("2026 Q1", 2300), ("2026 Q2", 2622.080)),
        SHARES_ACTUAL: _series(
            ("2025 Q2", 67.167),
            ("2026 Q1", 67.818),
            ("2026 Q2", 67.908),
        ),
    }
