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

## 2026-09-25 — Initial CSIQ workbook

- **Tab / range:** Created Welcome, Levers, Quarterly Financials, Financials Definitions, Pillars, Valuation, Shares, Price History, Reference. Removed the empty default Sheet1. No chart tab was created.
- **Insert/delete:** New sheets only. Quarterly Financials is labels in A:B and quarters 2025 Q1–2030 Q4 in C:Z.
- **Formulas:** Every `- Model` row, the As of date, years from present, stock price (`GOOGLEFINANCE` lookup), and market cap. Templates live in `quarterly_model_formulas.py`. Valuation columns pull 2026 Q3 and 2027 Q4 from Quarterly Financials. Price History is one `GOOGLEFINANCE("CSIQ","all",...)` spill.
- **Data:** Reported actuals through 2026 Q2 from the Q1 and Q2 2026 earnings releases (Q1 2025 product lines are H1 2025 minus Q2 2025). Yellow `- Plan` paths: 2026 US modules 6.7 GW and US storage 5.0 GWh, then the thesis steady state of 6 GW/year and 5 GWh/year. Lever defaults are the 2026-04-28 thesis, except US module ASP at $0.30/W from the Q2 call's mid-$0.30 bookings, and CSIQ's direct 75.1% of CS PowerTech rather than 100% of US value.
- **Side effects:** Header, section, and yellow input formatting. Number formats on quarterly value columns and on dated or decimal levers. No charts.
