# Canadian Solar (CSIQ)

Investment model for **Canadian Solar Inc.** (`CSIQ`). The workbook follows the Comstock pack's shape — levers, reported actuals next to model rows, yellow plan trajectories, and a sum of parts — because Canadian Solar is also several businesses in one ticker. The operating math is Canadian Solar's, not Comstock's.

Live sheet: [CSIQ Model](https://docs.google.com/spreadsheets/d/1kCYZnwJyOKNRnyDPlyQyGCYOwkelu944fJ7yEEKyEeo/edit).

Sources: [RESOURCES.md](RESOURCES.md). Sheet edits: [CHANGELOG.md](CHANGELOG.md).

Not investment advice.

## What is being valued

Three stakes, not a multiple on the consolidated loss:

1. **CSI Solar** — Shanghai-listed manufacturer. Canadian Solar owns about 64%. Default value is a 30% discount to the thesis's $7B market cap. Update that market cap; it is not a live quote.
2. **CS PowerTech** — US modules and storage. Canadian Solar holds 75.1% directly. The default economics are the [2026-04-28 thesis](https://www.youtube.com/watch?v=egSupfYmkVE): 7.5¢/W on 6 GW of modules after a $250M lease, and 5 GWh of storage at $200/kWh and a 15% margin. The yellow phase-in rows keep 2026 from being credited with that steady state, because Jeffersonville opened in July 2026 and management said ramp costs run through year-end.
3. **Recurrent Energy** — projects, electricity, and O&M. Default equity value is BlackRock's early-2024 $2.5B post-money mark, times Canadian Solar's 80%.

Ex-US volume is in the revenue bridge so quarterly guidance can be checked. It is not given a second multiple. Backlog, early-stage pipeline, and tax credits are not added on top of those stakes. Only holdco converts, net of unallocated cash, are subtracted.

## Tabs

Welcome, Levers, Quarterly Financials (2025 Q1–2030 Q4), Financials Definitions, Pillars, Valuation, Shares, Price History, Reference.

Charts are manual. A useful one is Present stock price and Stock price on the left axis, US module EBITDA on the right.

## Rebuild

```bash
python models/CSIQ/scripts/setup_csiq_workbook.py --force-rebuild
python scripts/validate_model_formulas.py --ticker CSIQ --offline
```

`--force-rebuild` replaces tab contents from this pack.
