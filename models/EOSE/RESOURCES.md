# Resources

Sources and references used in the **EOSE Model** spreadsheet. Not investment advice; citations are for transparency about where numbers and assumptions come from.

Spreadsheet (view or comment): [EOSE Model](https://docs.google.com/spreadsheets/d/1mkceZ4pgKhCAsWszlUVzk0RoHGeRRORfWIX9lB7Ejek/edit?usp=sharing)

Canonical links and XBRL tag map: [`sources.py`](sources.py). Reported Actuals: [`actuals.py`](actuals.py).

---

## Official Eos Energy

| Resource | Role |
| --- | --- |
| [Investor relations](https://investors.eose.com/) | Earnings releases, SEC filings, presentations |
| [eose.com / technology](https://www.eose.com/technology/) | Z3 zinc hybrid cathode, duration, manufacturing claims |
| [Z3 product sheet (Jan 2024)](https://www.eose.com/wp-content/uploads/2024/02/eos_Z3_productsheet_013124_V2-2.pdf) | Module energy (~1.2 kWh) vs **Z3 Module Energy Capacity** |
| SEC companyfacts `CIK0001805077` | Repeatable GAAP pull (`scripts/fetch_sec_gaap.py`) |

### Where each Actual row comes from

| Sheet row | Source | Repeat next quarter |
| --- | --- | --- |
| Revenue, COGS, GP, SG&A, R&D, GAAP NI | 10-Q / 10-K income statement (XBRL) | `fetch_sec_gaap.py` |
| OpEx | Total operating expenses = SG&A + R&D + PP&E write-down | same |
| Cash | Cash + restricted cash (earnings “total cash”; XBRL cash+restricted) | same |
| Long term debt | 10-Q line “Long-term debt” (ex related-party notes) | XBRL LTD noncurrent − related-party notes |
| Total debt | All borrowings carrying value (XBRL `LongTermDebt`) | same |
| Basic / Fully diluted shares | Weighted-average shares in the quarter column | XBRL; **Q4 WAS is in the 8-K three-month column**, not the 10-K FY average |
| Adjusted EBITDA | Earnings 8-K Ex. 99.1 reconciliation | **not in XBRL** |
| Pipeline $ / GWh, backlog $ / GWh | Earnings highlights + slides; GWh often only on the call | IR release / transcript |
| Booked orders | Disclosed in release or slides; else implied Δbacklog + revenue (adjustments can break the identity — Q4 2025 disclosed $240M vs ~$115M implied) | same |
| Z3 manufacturing lines | Capacity commentary (Line 2 commercial production Q2 2026) | earnings ops section |
| GWh shipped / Z3 ASP | Usually **not disclosed** — leave blank; use revenue | — |

Fully diluted WAS equals basic in a **loss** quarter (anti-dilutive). Q1 2025 and Q1 2026 were GAAP-profit quarters (FV marks), so diluted WAS is the if-converted count. Q2 2026 Fully diluted Actual is left blank so **Fully diluted shares - Model** keeps Q1 2026’s 544.8M if-converted print.

### Earnings used for Actual rows (through Q2 2026)

| Period | 10-Q / 10-K | Earnings 8-K / IR | Figures used |
| --- | --- | --- | --- |
| Q1 2025 | [10-Q](https://www.sec.gov/Archives/edgar/data/1805077/000180507725000051/eose-20250331.htm) | [release](https://investors.eose.com/node/11541/pdf) / [slides](https://investors.eose.com/static-files/37bf65c1-0b9f-409a-8a14-4e02c51038cb) | Rev $10.457M, GP −$24.539M, adj. EBITDA **−$43.238M** (recon, not a residual), NI +$15.136M, cash $111.694M, pipeline $15.6B / 60 GWh, backlog $680.9M / 2.6 GWh, bookings **$9.2M**, diluted WAS 436.4M |
| Q2 2025 | [10-Q](https://www.sec.gov/Archives/edgar/data/1805077/000180507725000154/eose-20250630.htm) | [8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/1805077/000180507725000152/eoseq22025earningsreleas.htm) / [slides](https://investors.eose.com/static-files/9f77f7a1-7547-4d12-a596-3ccd63341ec4) | Rev $15.236M, GP −$30.953M, adj. EBITDA −$51.626M, NI −$222.937M, cash $183.175M, pipeline $18.8B / 77 GWh, backlog $672.5M / 2.6 GWh, bookings **$6.9M** |
| Q3 2025 | [10-Q](https://www.sec.gov/Archives/edgar/data/1805077/000162828025049588/eose-20250930.htm) | [8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/1805077/000162828025049552/eoseq32025earningsreleas.htm) | Rev $30.512M, SG&A $19.786M, opex $27.296M, adj. EBITDA −$52.690M, NI −$641.393M, cash $126.799M, pipeline $22.6B / 91 GWh, backlog $644.4M / 2.5 GWh |
| Q4 / FY 2025 | [10-K](https://www.sec.gov/Archives/edgar/data/1805077/000162828026011961/eose-20251231.htm) | [8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/1805077/000162828026011958/eoseq4fy25earningsreleas.htm) / [call](https://earningscalls.dev/transcripts/eos-energy-enterprises-inc_eose_earnings_call_transcript_2026-02-26) | Rev $57.998M / FY $114.203M, SG&A $18.841M, R&D $7.579M, adj. EBITDA −$71.536M, NI −$120.453M, cash $624.566M, pipeline $23.6B / **99 GWh**, backlog $701.5M / 2.8 GWh, Q4 bookings **$240M** |
| Q1 2026 | [10-Q](https://www.sec.gov/Archives/edgar/data/1805077/000162828026034368/eose-20260331.htm) | [IR](https://investors.eose.com/news-releases/news-release-details/eos-energy-enterprises-reports-first-quarter-2026-financial) / [call](https://www.theglobeandmail.com/investing/markets/stocks/EOSE/pressreleases/1912895/eos-energy-eose-q1-2026-earnings-transcript/) | Rev $56.963M, adj. EBITDA −$68.019M, NI $508.883M (FV marks), cash $472.368M, pipeline $24.3B / **107 GWh**, backlog $644.6M / 2.6 GWh, basic WAS 339.602M / diluted 544.829M |
| Q2 2026 | [10-Q](https://www.sec.gov/Archives/edgar/data/1805077/000162828026052906/eose-20260630.htm) | [8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/1805077/000162828026052903/eoseq2fy26earningsreleas.htm) / [call](https://www.roic.ai/quote/EOSEW/transcripts/2026-year/2-quarter) | Rev $68.775M, adj. EBITDA **−$71.355M**, NI −$275.710M, cash $364.070M, pipeline $24.6B / ~112 GWh, backlog $807M / 3.4 GWh, Line 2, FY2026 guide **$300–350M** |

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

When updating after an earnings release (same steps every quarter):

1. `python models/EOSE/scripts/fetch_sec_gaap.py --year YYYY --quarter N` — GAAP vs `actuals.py`.
2. Open the 8-K Ex. 99.1 from [`sources.py`](sources.py) (or IR). Copy adj. EBITDA recon, pipeline, backlog, booked orders, lines.
3. If pipeline GWh is missing from the release, use the earnings-call transcript / slides.
4. Patch [`actuals.py`](actuals.py) (sheet units: $M, pipeline $B, shares million). Leave GWh shipped / ASP blank unless disclosed.
5. `python models/EOSE/scripts/load_quarterly_actuals.py`
6. Update **As of date** (column C) so years-from-present and PV stay current.
7. Confirm 45X still treated as a COGS offset in the 10-Q.
8. Add share events on **Shares** if the diluted count jumped for a stated reason.
9. Append sheet edits to [CHANGELOG.md](CHANGELOG.md).
10. `python scripts/sync_repo_from_live_sheet.py --ticker EOSE --update-snapshot` if you typed prints in the sheet first.
