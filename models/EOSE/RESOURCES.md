# Resources

Sources and references used in the **EOSE Model** spreadsheet (and related comments). Not investment advice; citations are for transparency about where numbers and assumptions come from.

Spreadsheet (view or comment): [EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)

---

## Official Eos Energy

| Resource | Role |
| --- | --- |
| [Investor relations](https://investors.eose.com/) | Earnings releases, SEC filings, presentations |
| [eose.com / technology](https://www.eose.com/technology/) | Z3 zinc hybrid cathode, duration, manufacturing claims |
| [Z3 product sheet (Jan 2024)](https://www.eose.com/wp-content/uploads/2024/02/eos_Z3_productsheet_013124_V2-2.pdf) | Module energy (~1.2 kWh) used to sanity-check **Z3 Module Energy Capacity** |

---

## In-sheet Reference tab

Copied from **Reference** on the live workbook:

| Information | Source | Notes |
| --- | --- | --- |
| Average sale price higher in 2025 Q3 than Q2 | [Yahoo Finance Q3 2025 earnings call](https://finance.yahoo.com/quote/EOSE/earnings/EOSE-Q3-2025-earnings_call-369182.html) | Search for "Average selling price" |
| Derive average selling price from PTC credits | [x.com/x_times_1](https://x.com/x_times_1/status/1950885635100717222) | |
| Tax credits are not recorded as revenue. They are recorded as negative cost of goods sold. | [x.com/x_times_1](https://x.com/x_times_1/status/2006569905122898296) | Modeled **COGS derived** subtracts **Government credits**; modeled **Revenue** still adds the same credits — see the pack README |
| Feltonomics | [x.com/philroberts](https://x.com/philroberts/status/2006725760514453566) | Independent model; **Feltonomics** tab is currently empty |
| Module and cell are interchangeable words with respect to Z3 | (model note) | |

---

## Suggested refresh checklist

When updating the model after an earnings release:

1. Pull reported revenue, COGS, SG&A, R&D, debt, diluted shares, and any ASP / kWh shipped commentary.
2. Reconcile 45X / PTC credit treatment with the latest 10-Q (COGS offset vs revenue).
3. Update manufacturing-line ramp and cycle-time assumptions if management changes the outlook.
4. Refresh **Stock price - actual** / **Market cap - actual** if you still want a single actuals column.
5. Append sheet edits to [CHANGELOG.md](CHANGELOG.md).
