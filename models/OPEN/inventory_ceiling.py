"""Inventory ceiling (homes) and utilization vs facility vs committed capacity.

Utilization of a dollar capacity is warehouse debt / capacity, which equals
homes / (capacity × homes / debt). That is the % on Opendoor Homes Inventory.
Committed capacity is the 10-Q promised amount (~$1.5B at Q2 2026); facility
capacity is the modeled operating ceiling (default senior $4.2B). Above 100%
of committed means lenders are funding at their discretion.
"""

from __future__ import annotations

from sheets.warehouse_financing import (
    MEZZ_DEBT_LABEL,
    MEZZ_DEBT_MODEL_LABEL,
    SENIOR_DEBT_LABEL,
    SENIOR_DEBT_MODEL_LABEL,
    SENIOR_INTEREST_RATE_LABEL,
    carry_forward_rate_formula,
)

FACILITY_CAPACITY_LABEL = "Warehouse Facility Capacity"
COMMITTED_CAPACITY_LABEL = "Warehouse Committed Capacity"
INVENTORY_CEILING_MODEL_LABEL = "Inventory Ceiling - Model"
COMMITTED_CEILING_MODEL_LABEL = "Committed Inventory Ceiling - Model"
UTILIZATION_LABEL = "Inventory Utilization %"
UTILIZATION_MODEL_LABEL = "Inventory Utilization % - Model"
UTILIZATION_COMMITTED_LABEL = "Inventory Utilization % of Committed"
UTILIZATION_COMMITTED_MODEL_LABEL = "Inventory Utilization % of Committed - Model"

# Senior revolving + senior term capacity from Q2 2026 10-Q ($2.8B + $1.4B).
# Switch B to 7_450_000_000 for headline (incl. uncommitted + mezz) or 1_500_000_000
# to make ceiling = committed.
FACILITY_CAPACITY = 4_200_000_000
# Q2 2026 committed borrowing capacity (revolvers $400M + senior term $725M + mezz $350M).
# Q3 2025 10-Q cited $1.8B committed; overwrite early weeks if you want that history.
COMMITTED_CAPACITY = 1_500_000_000

INVENTORY_CEILING_LABELS: tuple[str, ...] = (
    FACILITY_CAPACITY_LABEL,
    COMMITTED_CAPACITY_LABEL,
    INVENTORY_CEILING_MODEL_LABEL,
    COMMITTED_CEILING_MODEL_LABEL,
    UTILIZATION_LABEL,
    UTILIZATION_MODEL_LABEL,
    UTILIZATION_COMMITTED_LABEL,
    UTILIZATION_COMMITTED_MODEL_LABEL,
)

CAPACITY_LABELS: tuple[str, ...] = (
    FACILITY_CAPACITY_LABEL,
    COMMITTED_CAPACITY_LABEL,
)
UTILIZATION_LABELS: tuple[str, ...] = (
    UTILIZATION_LABEL,
    UTILIZATION_MODEL_LABEL,
    UTILIZATION_COMMITTED_LABEL,
    UTILIZATION_COMMITTED_MODEL_LABEL,
)
HOMES_CEILING_LABELS: tuple[str, ...] = (
    INVENTORY_CEILING_MODEL_LABEL,
    COMMITTED_CEILING_MODEL_LABEL,
)

INSERT_BEFORE_LABEL = SENIOR_INTEREST_RATE_LABEL

MODEL_FORMULA_LABELS: tuple[str, ...] = INVENTORY_CEILING_LABELS


def capacity_seed(label: str) -> int:
    if label == FACILITY_CAPACITY_LABEL:
        return FACILITY_CAPACITY
    if label == COMMITTED_CAPACITY_LABEL:
        return COMMITTED_CAPACITY
    raise KeyError(label)


def _debt_model_sum(col: str, label_to_row: dict[str, int]) -> str:
    senior = label_to_row[SENIOR_DEBT_MODEL_LABEL]
    mezz = label_to_row[MEZZ_DEBT_MODEL_LABEL]
    return f"({col}{senior}+{col}{mezz})"


def inventory_ceiling_model_formula(
    col: str,
    *,
    committed: bool,
    label_to_row: dict[str, int],
) -> str:
    """Homes at 100% of this dollar capacity, at this week's debt per home."""
    cap_label = COMMITTED_CAPACITY_LABEL if committed else FACILITY_CAPACITY_LABEL
    cap = label_to_row[cap_label]
    inv = label_to_row["Homes in Inventory - Model"]
    debt = _debt_model_sum(col, label_to_row)
    return (
        f"=IF(OR({col}{cap}=0,{col}{inv}=0,{debt}=0),\"\","
        f"{col}{cap}*{col}{inv}/{debt})"
    )


def utilization_formula(
    col: str,
    *,
    committed: bool,
    modeled: bool,
    label_to_row: dict[str, int],
) -> str:
    """Warehouse debt / capacity. Equals homes / homes-ceiling when debt per home is stable."""
    cap_label = COMMITTED_CAPACITY_LABEL if committed else FACILITY_CAPACITY_LABEL
    cap = label_to_row[cap_label]
    if modeled:
        debt = _debt_model_sum(col, label_to_row)
        return f"=IF(OR({col}{cap}=0,{debt}=0),\"\",{debt}/{col}{cap})"
    senior = label_to_row[SENIOR_DEBT_LABEL]
    mezz = label_to_row[MEZZ_DEBT_LABEL]
    return (
        f"=IF(OR({col}{cap}=0,NOT(ISNUMBER({col}{senior})),NOT(ISNUMBER({col}{mezz}))),"
        f"\"\",({col}{senior}+{col}{mezz})/{col}{cap})"
    )


# Re-export so restore can use the same carry-forward helper.
capacity_carry_forward_formula = carry_forward_rate_formula
