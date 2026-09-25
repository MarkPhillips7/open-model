"""Reported quarterly actuals, in millions of USD except GW, GWh, percent, and shares.

Blank means the company has not published the figure. Segment gross margin is gross
profit divided by segment revenue from the same table, to one decimal.

2025 manufacturing rows are the CSI Solar segment through Q3 and the Manufacturing
segment in Q4, after the December 2025 reorganization. The line is continuous.

Storage GWh: Q1 2025 is the 0.8 GWh in the Q1 release materials. Q3 2025 is the
stated 2.7 GWh. Q4 2025 is 2.0 because Q1 2026's 2.1 GWh was "up 5%" from it
(2.1 / 1.05 = 2.0). Q2 2025 is 2.3, the residual of the stated 7.8 GWh full year
(0.8 + 2.3 + 2.7 + 2.0 = 7.8) and of the 5.8 GWh nine-month utility-scale total.

Sources: Q1, Q2, Q3, and Q4 2025 earnings releases, and the Q1 and Q2 2026 releases.
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
    MFG_GM_ACTUAL,
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
        MODULE_GW_ACTUAL: _series(
            ("2025 Q1", 6.9),
            ("2025 Q2", 7.9),
            ("2025 Q3", 5.1),
            ("2025 Q4", 4.3),
            ("2026 Q1", 2.5),
            ("2026 Q2", 3.1),
        ),
        STORAGE_GWH_ACTUAL: _series(
            ("2025 Q1", 0.8),
            ("2025 Q2", 2.3),
            ("2025 Q3", 2.7),
            ("2025 Q4", 2.0),
            ("2026 Q1", 2.1),
            ("2026 Q2", 3.7),
        ),
        MODULE_REV_ACTUAL: _series(
            ("2025 Q1", 797.422),
            ("2025 Q2", 1022.266),
            ("2025 Q3", 839.421),
            ("2025 Q4", 718.597),
            ("2026 Q1", 455.117),
            ("2026 Q2", 589.377),
        ),
        STORAGE_REV_ACTUAL: _series(
            ("2025 Q1", 155.310),
            ("2025 Q2", 432.399),
            ("2025 Q3", 486.033),
            ("2025 Q4", 296.848),
            ("2026 Q1", 382.758),
            ("2026 Q2", 425.922),
        ),
        # Kits + EPC and others.
        OTHER_MFG_REV_ACTUAL: _series(
            ("2025 Q1", 120.563),
            ("2025 Q2", 135.425),
            ("2025 Q3", 59.667),
            ("2025 Q4", 136.821),
            ("2026 Q1", 102.589),
            ("2026 Q2", 78.545),
        ),
        MFG_REV_ACTUAL: _series(
            ("2025 Q1", 1190.258),
            ("2025 Q2", 1731.803),
            ("2025 Q3", 1426.491),
            ("2025 Q4", 1263.572),
            ("2026 Q1", 949.662),
            ("2026 Q2", 1097.535),
        ),
        MFG_GP_ACTUAL: _series(
            ("2025 Q1", 159.538),
            ("2025 Q2", 385.555),
            ("2025 Q3", 214.363),
            ("2025 Q4", 183.060),
            ("2026 Q1", 276.346),
            ("2026 Q2", 130.558),
        ),
        MFG_GM_ACTUAL: _series(
            ("2025 Q1", 13.4),
            ("2025 Q2", 22.3),
            ("2025 Q3", 15.0),
            ("2025 Q4", 14.5),
            ("2026 Q1", 29.1),
            ("2026 Q2", 11.9),
        ),
        MFG_OI_ACTUAL: _series(
            ("2025 Q1", 1.837),
            ("2025 Q2", 120.740),
            ("2025 Q3", 38.712),
            ("2025 Q4", 37.268),
            ("2026 Q1", 126.817),
            ("2026 Q2", -49.374),
        ),
        ASSET_SALES_ACTUAL: _series(
            ("2025 Q1", 72.151),
            ("2025 Q2", 48.091),
            ("2025 Q3", 39.770),
            ("2025 Q4", 15.975),
            ("2026 Q1", 88.541),
            ("2026 Q2", 61.114),
        ),
        POWER_ACTUAL: _series(
            ("2025 Q1", 16.499),
            ("2025 Q2", 18.809),
            ("2025 Q3", 19.892),
            ("2025 Q4", 20.286),
            ("2026 Q1", 22.416),
            ("2026 Q2", 20.053),
        ),
        ELECTRICITY_ACTUAL: _series(
            ("2025 Q1", 34.680),
            ("2025 Q2", 36.881),
            ("2025 Q3", 42.619),
            ("2025 Q4", 28.682),
            ("2026 Q1", 26.457),
            ("2026 Q2", 32.703),
        ),
        RECURRENT_REV_ACTUAL: _series(
            ("2025 Q1", 125.242),
            ("2025 Q2", 106.135),
            ("2025 Q3", 105.200),
            ("2025 Q4", 67.043),
            ("2026 Q1", 139.232),
            ("2026 Q2", 117.306),
        ),
        RECURRENT_GP_ACTUAL: _series(
            ("2025 Q1", 23.284),
            ("2025 Q2", 34.378),
            ("2025 Q3", 48.490),
            ("2025 Q4", -22.698),
            ("2026 Q1", -14.517),
            ("2026 Q2", 35.971),
        ),
        RECURRENT_OI_ACTUAL: _series(
            ("2025 Q1", -11.997),
            ("2025 Q2", -74.437),
            ("2025 Q3", 2.757),
            ("2025 Q4", -68.980),
            ("2026 Q1", -60.253),
            ("2026 Q2", -19.370),
        ),
        TOTAL_REV_ACTUAL: _series(
            ("2025 Q1", 1196.625),
            ("2025 Q2", 1693.871),
            ("2025 Q3", 1487.402),
            ("2025 Q4", 1217.209),
            ("2026 Q1", 1077.878),
            ("2026 Q2", 1207.714),
        ),
        GP_ACTUAL: _series(
            ("2025 Q1", 140.494),
            ("2025 Q2", 505.030),
            ("2025 Q3", 256.301),
            ("2025 Q4", 124.401),
            ("2026 Q1", 270.820),
            ("2026 Q2", 168.475),
        ),
        GM_ACTUAL: _series(
            ("2025 Q1", 11.7),
            ("2025 Q2", 29.8),
            ("2025 Q3", 17.2),
            ("2025 Q4", 10.2),
            ("2026 Q1", 25.1),
            ("2026 Q2", 13.9),
        ),
        OPEX_ACTUAL: _series(
            ("2025 Q1", 195.299),
            ("2025 Q2", 377.597),
            ("2025 Q3", 221.712),
            ("2025 Q4", 188.462),
            ("2026 Q1", 197.954),
            ("2026 Q2", 239.534),
        ),
        OI_ACTUAL: _series(
            ("2025 Q1", -54.805),
            ("2025 Q2", 127.433),
            ("2025 Q3", 34.589),
            ("2025 Q4", -64.061),
            ("2026 Q1", 72.866),
            ("2026 Q2", -71.059),
        ),
        NI_ACTUAL: _series(
            ("2025 Q1", -33.971),
            ("2025 Q2", 7.197),
            ("2025 Q3", 8.986),
            ("2025 Q4", -86.338),
            ("2026 Q1", -32.093),
            ("2026 Q2", -76.859),
        ),
        EPS_ACTUAL: _series(
            ("2025 Q1", -0.69),
            ("2025 Q2", -0.08),
            ("2025 Q3", -0.07),
            ("2025 Q4", -1.66),
            ("2026 Q1", -0.71),
            ("2026 Q2", -1.40),
        ),
        CASH_ACTUAL: _series(
            ("2025 Q1", 1577.275),
            ("2025 Q2", 1856.034),
            ("2025 Q3", 1763.311),
            ("2025 Q4", 1370.418),
            ("2026 Q1", 1441.110),
            ("2026 Q2", 1461.248),
        ),
        RESTRICTED_ACTUAL: _series(
            ("2025 Q1", 456.644),
            ("2025 Q2", 408.175),
            ("2025 Q3", 416.620),
            ("2025 Q4", 570.017),
            ("2026 Q1", 442.181),
            ("2026 Q2", 389.108),
        ),
        CASH_RESTRICTED_ACTUAL: _series(
            ("2025 Q1", 2033.919),
            ("2025 Q2", 2264.209),
            ("2025 Q3", 2179.931),
            ("2025 Q4", 1940.435),
            ("2026 Q1", 1883.291),
            ("2026 Q2", 1850.356),
        ),
        OCF_ACTUAL: _series(
            ("2025 Q1", -264.203),
            ("2025 Q2", 188.556),
            ("2025 Q3", -112.060),
            ("2025 Q4", -65.034),
            ("2026 Q1", -208.658),
            ("2026 Q2", -180.761),
        ),
        CAPEX_ACTUAL: _series(
            ("2025 Q1", 256.380),
            ("2025 Q2", 172.729),
            ("2025 Q3", 266.768),
            ("2025 Q4", 266.377),
            ("2026 Q1", 173.210),
            ("2026 Q2", 171.840),
        ),
        DEBT_ACTUAL: _series(
            ("2025 Q1", 5700),
            ("2025 Q2", 6300),
            ("2025 Q3", 6400),
            ("2025 Q4", 6500),
            ("2026 Q1", 6800),
            ("2026 Q2", 7100),
        ),
        CONVERTS_ACTUAL: _series(
            ("2025 Q2", 274.510),
            ("2025 Q3", 194.751),
            ("2025 Q4", 195.313),
            ("2026 Q2", 420.063),
        ),
        NONRECOURSE_ACTUAL: _series(
            ("2025 Q1", 1262.822),
            ("2025 Q2", 1809.269),
            ("2025 Q3", 1952.303),
            ("2025 Q4", 2168.485),
            ("2026 Q1", 2300),
            ("2026 Q2", 2622.080),
        ),
        SHARES_ACTUAL: _series(
            ("2025 Q1", 66.963),
            ("2025 Q2", 67.167),
            ("2025 Q3", 67.620),
            ("2025 Q4", 67.713),
            ("2026 Q1", 67.818),
            ("2026 Q2", 67.908),
        ),
    }
