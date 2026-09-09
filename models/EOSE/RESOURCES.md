# Resources

Sources and references used in the **EOSE Model** spreadsheet. Not investment advice; citations are for transparency about where numbers and assumptions come from.

Spreadsheet (view or comment): [EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)

---

## Official Eos Energy

| Resource | Role |
| --- | --- |
| [Investor relations](https://investors.eose.com/) | Earnings releases, SEC filings, presentations |
| [eose.com / technology](https://www.eose.com/technology/) | Z3 zinc hybrid cathode, duration, manufacturing claims |
| [Z3 product sheet (Jan 2024)](https://www.eose.com/wp-content/uploads/2024/02/eos_Z3_productsheet_013124_V2-2.pdf) | Module energy (~1.2 kWh) vs **Z3 Module Energy Capacity** |

### Earnings used for Actual rows (through Q2 2026)

| Period | Primary source | Figures used |
| --- | --- | --- |
| Q1 2025 | [Q1 2026 10-Q YoY](https://www.sec.gov/Archives/edgar/data/1805077/000162828026034368/eose-20260331.htm) | Revenue $10.457M, COGS $35.0M, GP −$24.5M, opex, cash $111.7M. Adj. EBITDA ≈ −$43.3M is a residual from 9M’25 − Q2 − Q3 — treat as approximate. |
| Q2 2025 | [Q2 2026 earnings](https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-reports-second-quarter-2026-financial) YoY | Revenue $15.236M, COGS $46.2M, GP −$31.0M, adj. EBITDA −$51.6M, NI −$222.9M |
| Q3 2025 | [Q3 2025 earnings](https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-delivers-highest-company-quarterly) | Revenue $30.5M, GP −$33.9M, opex $27.3M, adj. EBITDA −$52.7M, NI −$641.4M, cash $126.8M, pipeline $22.6B / ~91 GWh, backlog $644.4M / ~2.5 GWh, diluted shares 271.6M |
| Q4 / FY 2025 | [Q4 2025 earnings](https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-reports-fourth-quarter-and-full-year-2025) | Revenue $58.0M / FY $114.2M, GP −$54.4M, adj. EBITDA −$71.5M, NI −$120.5M, cash $624.6M, pipeline $23.6B / ~99 GWh, backlog $701.5M / 2.8 GWh, Q4 bookings **$240M** |
| Q1 2026 | [Q1 2026 earnings](https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-reports-first-quarter-2026-financial) / [10-Q](https://www.sec.gov/Archives/edgar/data/1805077/000162828026034368/eose-20260331.htm) | Revenue $57.0M, GP −$44.4M, adj. EBITDA −$68.0M, NI $508.9M (FV marks), cash $472.4M, pipeline $24.3B, backlog $644.6M / 2.6 GWh, basic ~339.5M / diluted ~544.8M |
| Q2 2026 | [Q2 2026 earnings](https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-reports-second-quarter-2026-financial) | Revenue $68.8M, GP −$48.8M (−71% GM), adj. EBITDA −$71.4M, NI −$275.7M, cash $364.1M, pipeline $24.6B / ~112 GWh, backlog $807M / 3.4 GWh, Line 2 commercial production (mid-June), FY2026 revenue guide **$300–350M** |

Backlog identity (company): prior + new orders − shipments. Pipeline = proposals + LOI, not lead-gen. Booked orders = PO or executed MSA.

---

## In-sheet Reference tab

| Information | Source | Notes |
| --- | --- | --- |
| Average sale price higher in 2025 Q3 than Q2 | [Yahoo Finance Q3 2025 earnings call](https://finance.yahoo.com/quote/EOSE/earnings/EOSE-Q3-2025-earnings_call-369182.html) | Search for "Average selling price" |
| Derive average selling price from PTC credits | [x.com/x_times_1](https://x.com/x_times_1/status/1950885635100717222) | |
| Tax credits are not recorded as revenue. They are recorded as negative cost of goods sold. | [x.com/x_times_1](https://x.com/x_times_1/status/2006569905122898296) | **COGS - Model** subtracts **Government credits - Model**. Revenue - Model does **not** add credits. |
| Feltonomics | [x.com/philroberts](https://x.com/philroberts/status/2006725760514453566) | Independent model; **Feltonomics** tab is kept empty for later |
| Module and cell are interchangeable words with respect to Z3 | (model note) | |

---

## Suggested refresh checklist

When updating after an earnings release:

1. Enter Actuals: revenue, COGS, GP, SG&A, R&D, opex, adj. EBITDA, GAAP NI, cash, pipeline, backlog ($ and GWh), booked orders if disclosed, lines, shares.
2. Update **As of date** (column C) so years-from-present and PV stay current.
3. Confirm 45X still treated as a COGS offset in the 10-Q.
4. Add share events on **Shares** if the diluted count jumped for a stated reason.
5. Append sheet edits to [CHANGELOG.md](CHANGELOG.md).
6. `python scripts/sync_repo_from_live_sheet.py --ticker EOSE --update-snapshot` and update `actuals.py` if you typed prints in the sheet first.
