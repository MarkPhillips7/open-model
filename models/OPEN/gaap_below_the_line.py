"""GAAP below-the-line income statement items (quarterly actuals from 10-Q / earnings supplement)."""

from __future__ import annotations

DEBT_EXTINGUISHMENT_LABEL = "(Loss) Gain on Extinguishment of Debt"
INTEREST_EXPENSE_LABEL = "Interest Expense"
OTHER_INCOME_LABEL = "Other Income - Net"
ADJ_EBITDA_MODEL_LABEL = "Adjusted EBITDA - Model"
ADJ_NET_INCOME_MODEL_LABEL = "Adjusted Net Income - Model"

DEBT_EXTINGUISHMENT_MODEL_LABEL = "(Loss) Gain on Extinguishment of Debt - Model"
INTEREST_EXPENSE_MODEL_LABEL = "Interest Expense - Model"
OTHER_INCOME_MODEL_LABEL = "Other Income - Net - Model"

# Adj → GAAP reconciliation add-backs (earnings supplement signs: positive = added to GAAP net
# loss to reach Adjusted Net Loss). Prior-period inventory lines are negative in the supplement.
INV_VAL_CURRENT_LABEL = "Inventory Valuation Adjustment - Current Period"
INV_VAL_PRIOR_LABEL = "Inventory Valuation Adjustment - Prior Periods"
RESTRUCTURING_LABEL = "Restructuring"
CEO_MAKE_WHOLE_LABEL = "CEO Make-Whole Provision"
OTHER_GAAP_ADJ_LABEL = "Other GAAP Adjustments"

INV_VAL_CURRENT_MODEL_LABEL = "Inventory Valuation Adjustment - Current Period - Model"
INV_VAL_PRIOR_MODEL_LABEL = "Inventory Valuation Adjustment - Prior Periods - Model"
RESTRUCTURING_MODEL_LABEL = "Restructuring - Model"
CEO_MAKE_WHOLE_MODEL_LABEL = "CEO Make-Whole Provision - Model"
OTHER_GAAP_ADJ_MODEL_LABEL = "Other GAAP Adjustments - Model"

# Forward run-rates when no quarterly actual is spread (weekly $, not cumulative).
INTEREST_EXPENSE_GUIDANCE_QUARTERLY = -27_000_000
OTHER_INCOME_GUIDANCE_QUARTERLY = 10_500_000
# Match live sheet literals (quarterly guidance ÷ 13 as stored in Sheets).
INTEREST_EXPENSE_WEEKLY_RUN_RATE = -2_076_923.07692307
OTHER_INCOME_WEEKLY_RUN_RATE = 807_692.307692307

# Recent-quarter averages for forward GAAP-bridge rows (2025 Q3–2026 Q2 supplements).
INV_VAL_CURRENT_GUIDANCE_QUARTERLY = 12_000_000
INV_VAL_PRIOR_GUIDANCE_QUARTERLY = -15_000_000
INV_VAL_CURRENT_WEEKLY_RUN_RATE = 923_076.923076923
INV_VAL_PRIOR_WEEKLY_RUN_RATE = -1_153_846.15384615

BELOW_THE_LINE_MODEL_LABELS: tuple[str, ...] = (
    DEBT_EXTINGUISHMENT_MODEL_LABEL,
    INTEREST_EXPENSE_MODEL_LABEL,
    OTHER_INCOME_MODEL_LABEL,
)

ADJ_TO_GAAP_MODEL_LABELS: tuple[str, ...] = (
    INV_VAL_CURRENT_MODEL_LABEL,
    INV_VAL_PRIOR_MODEL_LABEL,
    RESTRUCTURING_MODEL_LABEL,
    CEO_MAKE_WHOLE_MODEL_LABEL,
    OTHER_GAAP_ADJ_MODEL_LABEL,
)

# Values in dollars; losses stored as negative (matches GAAP statement presentation).
BELOW_THE_LINE_BY_COL: dict[str, dict[str, int]] = {
    # 2025 Q3 — Sep 30, 2025 (10-Q / Q4 2025 earnings supplement)
    "B": {
        DEBT_EXTINGUISHMENT_LABEL: -1_000_000,
        INTEREST_EXPENSE_LABEL: -34_000_000,
        OTHER_INCOME_LABEL: 14_000_000,
    },
    # 2025 Q4 — Dec 31, 2025
    "C": {
        DEBT_EXTINGUISHMENT_LABEL: -933_000_000,
        INTEREST_EXPENSE_LABEL: -28_000_000,
        OTHER_INCOME_LABEL: 14_000_000,
    },
    # 2026 Q1 — Mar 31, 2026
    "D": {
        DEBT_EXTINGUISHMENT_LABEL: -1_000_000,
        INTEREST_EXPENSE_LABEL: -23_000_000,
        OTHER_INCOME_LABEL: 10_000_000,
    },
    # 2026 Q2 — Jun 30, 2026
    "E": {
        DEBT_EXTINGUISHMENT_LABEL: 0,
        INTEREST_EXPENSE_LABEL: -29_000_000,
        OTHER_INCOME_LABEL: 11_000_000,
    },
}

# Reconciliation add-backs: GAAP net loss + these adjustments = Adjusted Net Loss.
ADJ_TO_GAAP_BY_COL: dict[str, dict[str, int]] = {
    "B": {
        INV_VAL_CURRENT_LABEL: 15_000_000,
        INV_VAL_PRIOR_LABEL: -17_000_000,
        RESTRUCTURING_LABEL: 1_000_000,
        CEO_MAKE_WHOLE_LABEL: 0,
        OTHER_GAAP_ADJ_LABEL: -2_000_000,
    },
    "C": {
        INV_VAL_CURRENT_LABEL: 9_000_000,
        INV_VAL_PRIOR_LABEL: -21_000_000,
        RESTRUCTURING_LABEL: 0,
        CEO_MAKE_WHOLE_LABEL: 5_000_000,
        OTHER_GAAP_ADJ_LABEL: 0,
    },
    "D": {
        INV_VAL_CURRENT_LABEL: 9_000_000,
        INV_VAL_PRIOR_LABEL: -14_000_000,
        RESTRUCTURING_LABEL: 0,
        CEO_MAKE_WHOLE_LABEL: 5_000_000,
        OTHER_GAAP_ADJ_LABEL: 0,
    },
    "E": {
        INV_VAL_CURRENT_LABEL: 14_000_000,
        INV_VAL_PRIOR_LABEL: -9_000_000,
        RESTRUCTURING_LABEL: 3_000_000,
        CEO_MAKE_WHOLE_LABEL: 4_000_000,
        OTHER_GAAP_ADJ_LABEL: -2_000_000,
    },
}

BELOW_THE_LINE_LABELS: tuple[str, ...] = (
    DEBT_EXTINGUISHMENT_LABEL,
    INTEREST_EXPENSE_LABEL,
    OTHER_INCOME_LABEL,
    ADJ_NET_INCOME_MODEL_LABEL,
)

ADJ_TO_GAAP_LABELS: tuple[str, ...] = (
    INV_VAL_CURRENT_LABEL,
    INV_VAL_PRIOR_LABEL,
    RESTRUCTURING_LABEL,
    CEO_MAKE_WHOLE_LABEL,
    OTHER_GAAP_ADJ_LABEL,
)
