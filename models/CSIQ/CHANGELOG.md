# Spreadsheet changelog

The live model is the Google Sheet for **Canadian Solar** (`CSIQ`). Git does not see those edits unless they are recorded here. Repo/platform changes go in the [root CHANGELOG](../../CHANGELOG.md).

**After every agent write to the sheet, append an entry below before finishing.** One dated heading per change-set.

Entry template:

```markdown
## YYYY-MM-DD — short title

- **Tab / range:** what changed
- **Insert/delete:** dimension, start index, count
- **Formulas:** before → after (a template is enough if copied across columns)
- **Data:** cells and values, plus why
- **Side effects:** charts, notes, number formats
```

---

## 2026-09-25 — Fill 2025 quarterly actuals

- **Tab / range:** Quarterly Financials, actual rows only, columns C:H (2025 Q1–2026 Q2). Future quarters stay blank. Yellow `- Plan` rows and `- Model` formulas were not rewritten. Financials Definitions column B was rewritten so the notes match the new figures.
- **Insert/delete:** none
- **Formulas:** unchanged. Model rows already prefer a typed actual, so 2025 Q3–Q4 revenue and the shipment model rows now show the actual instead of the plan.
- **Data:** From the Q1, Q2, Q3, and Q4 2025 earnings releases (and the Q1 2026 release for March 31 cash). Segment lines that were blank — manufacturing revenue, gross profit, gross margin, and operating income, and Recurrent revenue, gross profit, and operating income — are the CSI Solar / Manufacturing and Recurrent Energy segment tables. Q3–Q4 module, storage, and other manufacturing revenue, and Q3–Q4 total revenue, are the product and consolidated lines. Gross margin is segment gross profit divided by segment revenue, to one decimal. Also filled 2025 module GW (6.9, 7.9, 5.1, 4.3), cash, restricted cash, debt ($5.7B / $6.3B / $6.4B / $6.5B), non-recourse, converts (Q2–Q4), capex, operating cash flow, shares, and the rounded 2025 Q4 placeholders (gross profit, opex, net income, operating cash flow) with the thousands from the statements. Q1 2026 cash $1,441M and restricted cash $442M were on the Q1 2026 segment note and were blank. Storage GWh for 2025 is 0.8, 2.3, 2.7, 2.0: Q1 is the shipment slide, Q3 is stated, Q4 is 2.0 because Q1 2026's 2.1 GWh was up 5%, and Q2 is the residual of the stated 7.8 GWh year. Q1 2026 converts stay blank (the release said about $0.4B; that is not a carrying value).
- **Side effects:** none on charts. Definitions text for shipments, manufacturing margin, cash, debt, converts, capex, and shares was updated.

## 2026-09-25 — Initial CSIQ workbook

- **Tab / range:** Created Welcome, Levers, Quarterly Financials, Financials Definitions, Pillars, Valuation, Shares, Price History, Reference. Removed the empty default Sheet1. No chart tab was created.
- **Insert/delete:** New sheets only. Quarterly Financials is labels in A:B and quarters 2025 Q1–2030 Q4 in C:Z.
- **Formulas:** Every `- Model` row, the As of date, years from present, stock price (`GOOGLEFINANCE` lookup), and market cap. Templates live in `quarterly_model_formulas.py`. Valuation columns pull 2026 Q3 and 2027 Q4 from Quarterly Financials. Price History is one `GOOGLEFINANCE("CSIQ","all",...)` spill.
- **Data:** Reported actuals through 2026 Q2 from the Q1 and Q2 2026 earnings releases (Q1 2025 product lines are H1 2025 minus Q2 2025). Yellow `- Plan` paths: 2026 US modules 6.7 GW and US storage 5.0 GWh, then the thesis steady state of 6 GW/year and 5 GWh/year. Lever defaults are the 2026-04-28 thesis, except US module ASP at $0.30/W from the Q2 call's mid-$0.30 bookings, and CSIQ's direct 75.1% of CS PowerTech rather than 100% of US value.
- **Side effects:** Header, section, and yellow input formatting. Number formats on quarterly value columns and on dated or decimal levers. No charts.
