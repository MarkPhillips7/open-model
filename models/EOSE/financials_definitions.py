"""Field definitions for the EOSE Financials Definitions tab."""

from __future__ import annotations

FINANCIALS_DEFINITIONS_SHEET = "Financials Definitions"

FIELD_NOTES: dict[str, str] = {
    "Units": "Column B header. Each metric row has a unit here; time series start at column C.",
    "Year": "Calendar year of the quarter column (2025–2030).",
    "Quarter": "Fiscal quarter 1–4. Eos reports on a calendar quarter.",
    "Quarter ending": "EOMONTH of the quarter. Used for years-from-present and Stock price lookup.",
    "As of date": "Single date in C. Years from present = (quarter ending − this) / 365. Update after each earnings print.",
    "Years from present": "Discount tenor for present-value stock price. Formula from quarter ending vs As of date.",
    "Pipeline": "Commercial opportunity pipeline ($B) as disclosed. Proposals + LOI; excludes lead-gen. Actual only.",
    "Pipeline - Model": "Carries last actual forward. Edit a future cell to assume pipeline growth.",
    "Pipeline (GWh)": "Pipeline energy (GWh) when Eos discloses it.",
    "Pipeline (GWh) - Model": "Carries last actual GWh forward.",
    "Booked orders": "New orders in the quarter ($M). Disclosed when available (e.g. Q4 2025 $240M); otherwise implied as Δbacklog + revenue.",
    "Booked orders - Model": "Default: last actual booked orders carried forward. Primary demand assumption.",
    "Backlog": "Ending backlog ($M). Company identity: prior + orders − shipments.",
    "Backlog - Model": "Prior (actual if present else model) + orders (actual if present else model) − revenue (actual if present else model).",
    "Backlog (GWh)": "Ending backlog energy (GWh) as disclosed.",
    "Backlog (GWh) - Model": "Same roll as dollar backlog using GWh shipped - Model and implied GWh orders (dollar orders / ASP).",
    "Backlog conversion lag": "Quarters of beginning backlog assumed convertible this quarter. Default 4. Caps GWh shipped - Model together with factory capacity.",
    "GWh shipped": "Energy shipped / recognized in the quarter when disclosed. Often blank — revenue is the better actual.",
    "GWh shipped - Model": "MIN(factory capacity, beginning backlog GWh / conversion lag).",
    "Z3 ASP": "Average selling price ($/kWh) when derived or disclosed. Usually blank.",
    "Z3 ASP - Model": "Assumption: $250 early 2025, $256 thereafter. Revenue - Model = GWh shipped - Model × ASP.",
    "Z3 Module Energy Capacity": "kWh per Z3 module (product sheet ~1.2 kWh). Scalar in C, copied across.",
    "Z3 module cycle time": "Reported cycle time when disclosed (Line 2 ~10% faster vs Line 1 in Q2 2026).",
    "Z3 module cycle time - Model": "Starts at 18s; compounds at the quarterly reduction rate; floored at Cycle time floor (C).",
    "Quarterly module cycle time reduction rate": "Learning-curve % per quarter (default 2.9). Guess — not disclosed as a rate.",
    "Cycle time floor": "Seconds. Model cycle time will not go below this (default 10).",
    "Z3 modules per cube": "Modules per Cube (672). Scalar.",
    "Z3 manufacturing lines": "Installed lines when known (1 through Q1 2026; 2 from Q2 2026 Line 2 launch).",
    "Z3 manufacturing lines - Model": "Editable ramp (1 → 12). Capacity ceiling, not a demand forecast.",
    "Capacity utilization": "Utilization % assumption (default 85). Apply to Model lines.",
    "Z3 manufacturing lines utilized - Model": "Lines - Model × utilization.",
    "Full utilization weeks per year": "365/7.",
    "Full utilization days per week": "Default 7.",
    "Full utilization hours per day": "Default 24.",
    "Module production count per line - Model": "Seconds in a year / cycle time / 1e6.",
    "Capacity per line - Model": "kWh/module × modules per line × utilization.",
    "Annualized module energy capacity - Model": "Capacity per line × lines (nameplate, not utilized).",
    "Factory capacity - Model": "Quarterly GWh = annualized nameplate / 4.",
    "Percent of Guided Cost Cutting Achieved": (
        "Haircut on the Q2 2026 Slide 11 cost-out (73 pts of adj. GM over 12 months). "
        "Default 70% because management has repeatedly missed cost-out timelines. "
        "100% = take the CFO plan at face value; 0% = freeze Q2 2026 costs. "
        "Edit C; D:Z copy C. Waterfall lives on the COGS tab."
    ),
    "Terminal unit COGS": (
        "Floor ($/kWh, pre-45X) after the 12-month plan, blended in as Lines 3–4 ramp "
        "(Indensity / single-piece flow). Default $160 — still an explicit thesis."
    ),
    "Unit COGS - Model": (
        "From the COGS tab: Q2 2026 starting adj. GM (−62.3%) plus haircut × guided pts "
        "phased Q2 2026→Q2 2027, then blend toward Terminal unit COGS as lines go 2→4. "
        "Pre-45X; COGS - Model still subtracts government credits."
    ),
    "45x & active electrode credits": "$/kWh statutory credit assumption (default 47).",
    "45x transfer rate": "% of credit realized (default 90).",
    "Effective 45x credit - Model": "Credit × transfer rate.",
    "Government credits - Model": "Effective credit × GWh shipped - Model. Applied as a COGS offset only — not added to revenue.",
    "Unit COGS w/ 45x - Model": "Unit COGS − effective 45X.",
    "FY 2026 revenue guidance — low": "Management FY2026 revenue guide low ($300M as of Q2 2026). Scalar in C.",
    "FY 2026 revenue guidance — high": "Management FY2026 revenue guide high ($350M as of Q2 2026). Scalar in C.",
    "Revenue": "GAAP / earnings-release total revenue ($M). Hardcoded actuals through last print.",
    "Revenue - Model": "GWh shipped - Model × Z3 ASP - Model. Does not add 45X credits.",
    "COGS": "GAAP cost of goods sold ($M).",
    "COGS - Model": (
        "Unit COGS × GWh − government credits + Non-cash COGS (D&A + SBC). "
        "The first two terms are cash/adj. COGS; the add-back is Q2 2026 SBC+D&A in COGS held flat."
    ),
    "Gross profit": "Reported gross profit (loss).",
    "Gross profit - Model": "Revenue - Model − COGS - Model.",
    "Gross margin": "Gross profit / Revenue × 100 when Revenue actual is present.",
    "Gross margin - Model": "Gross profit - Model / Revenue - Model × 100 (GAAP-like; includes non-cash COGS).",
    "Adjusted gross profit": (
        "Company adj. GP = GAAP GP + SBC in COGS + D&A in COGS. Actuals from the earnings recon "
        "(Q2 2025–Q2 2026 on Slide 11 / 8-K)."
    ),
    "Adjusted gross profit - Model": "Revenue - Model × Adjusted gross margin - Model / 100.",
    "Adjusted gross margin": "Adj. GP / Revenue × 100 when both actuals are present. Q2 2026 print −62.3%.",
    "Adjusted gross margin - Model": (
        "From the COGS tab. Start −62.3% + progress × 73 pts × haircut. "
        "At 70% haircut the 12-month exit is about −11%, not the guided +10%."
    ),
    "SG&A": "Selling, general & administrative ($M).",
    "SG&A - Model": "Carries last actual SG&A forward (opex hold, OPEN-style).",
    "R&D": "Research & development ($M).",
    "R&D - Model": "Carries last actual R&D forward.",
    "OpEx": "Total operating expenses when disclosed; else SG&A + R&D.",
    "OpEx - Model": "SG&A - Model + R&D - Model.",
    "Adjusted EBITDA": "Company-defined adjusted EBITDA ($M). Actuals from earnings reconciliations.",
    "Adjusted EBITDA - Model": (
        "Adj. GP - Model − Cash OpEx run-rate. Calibrated to the company definition "
        "(Q2: −42.869 − 28.486 = −71.355). Used as the operating-cash-burn proxy "
        "(CFO: ops cash use ≈ adj. EBITDA)."
    ),
    "Operating cash flow - Model": (
        "Equals Adjusted EBITDA - Model. Explicit proxy from the Q2 2026 call / bert_gilfoyle thread. "
        "Cash - Model then subtracts capex and interest on top."
    ),
    "Adjusted EBITDA margin": "Adj. EBITDA / Revenue × 100.",
    "Adjusted EBITDA margin - Model": "Adj. EBITDA - Model / Revenue - Model × 100.",
    "Annualized EBITDA - Model": "Adj. EBITDA - Model × 4. Used only if positive in the EV formula.",
    "GAAP net income": "Net income (loss) attributable to shareholders. Dominated by warrant/derivative FV marks — do not treat as operating.",
    "GAAP net income - Model": "Adj. EBITDA - Model − net interest run-rate. Intentionally ignores FV marks.",
    "Cash": "Cash + restricted cash ($M) as disclosed.",
    "Cash - Model": (
        "Prior cash (actual if present else model) + Operating cash flow - Model − capex − interest. "
        "OCF is adj. EBITDA (CFO: ops cash ≈ adj. EBITDA); capex and interest sit on top."
    ),
    "Capex - Model": "Capex per incremental line × MAX(0, Δ lines - Model).",
    "Capex per incremental line": "Guess ($40M). 2025 investing cash outflow was ~$55M for the year.",
    "Net interest run-rate": "Quarterly net interest assumption ($12M from Q2 2026 interest expense order of magnitude).",
    "Cash OpEx run-rate": (
        "Cash operating expenses excluding COGS. Q2 2026 implied as adj. GP − adj. EBITDA "
        "($28.486M). Held flat — reported opex was sequentially unchanged despite the revenue ramp."
    ),
    "Non-cash COGS (D&A + SBC)": (
        "Q2 2026 COGS add-backs: SBC $0.516M + D&A $5.416M. Added to COGS - Model so GAAP GP "
        "is ~8 pts below adj. GM. Held flat; does not grow with lines."
    ),
    "Long term debt": (
        "10-Q/10-K line 'Long-term debt' (noncurrent), excluding related-party notes. "
        "Derived as XBRL LongTermDebtNoncurrent − LongTermNotesPayable."
    ),
    "Total debt": (
        "Carrying value of all borrowings (XBRL LongTermDebt): named long-term debt "
        "+ current portion + related-party notes. Not face/principal."
    ),
    "Total debt - Model": "Carries last actual total debt, else $1,000M placeholder.",
    "Net debt - Model": "Total debt - Model − Cash (actual if present else model).",
    "Basic shares": "Shares outstanding / basic weighted average (million).",
    "Fully diluted shares": "Diluted weighted average or fully diluted count (million) from the 10-Q.",
    "Fully diluted shares - Model": "Last actual diluted shares carried forward. Add events on the Shares tab when you want incremental dilution.",
    "Stock price": "Last daily close on or before quarter-end from Price History (GOOGLEFINANCE).",
    "Market cap": "Stock price × diluted shares / 1000 ($B).",
    "EV / EBITDA": "Multiple applied only when annualized EBITDA - Model is positive (default 30).",
    "Discount rate": "Annual discount rate for PV of implied future price (default 20%).",
    "Enterprise value - Model": "IF(annualized EBITDA > 0, annualized EBITDA × EV/EBITDA / 1000, blank) in $B.",
    "Market cap - Model": "Enterprise value − net debt / 1000.",
    "Implied future stock price - Model": "Market cap - Model / diluted shares × 1000.",
    "Present stock price discounted - Model": "-PV(discount rate, years from present, 0, implied future price).",
}
