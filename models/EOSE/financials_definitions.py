"""Field definitions for the EOSE Financials Definitions tab."""

from __future__ import annotations

FINANCIALS_DEFINITIONS_SHEET = "Financials Definitions"

FIELD_NOTES: dict[str, str] = {
    "Year": "Calendar year of the quarter column (2025–2030).",
    "Quarter": "Fiscal quarter 1–4. Eos reports on a calendar quarter.",
    "Quarter ending": "EOMONTH of the quarter. Used for years-from-present and Stock price lookup.",
    "As of date": "Single date in C. Years from present = (quarter ending − this) / 365. Update after each earnings print.",
    "Years from present": "Discount tenor for present-value stock price. Formula from quarter ending vs As of date.",
    "Pipeline": "Commercial opportunity pipeline ($B) as disclosed. Proposals + LOI; excludes lead-gen. Actual only.",
    "Pipeline - Model": (
        "Q1 2025 copies Pipeline actual, then compounds at that column's Pipeline "
        "quarterly growth rate (D:Z copy C, default 10% / q)."
    ),
    "Pipeline quarterly growth rate": "QoQ % applied to Pipeline - Model after 2025 Q1. Scalar in C. Guess.",
    "Pipeline (GWh)": "Pipeline energy (GWh) when Eos discloses it.",
    "Pipeline (GWh) - Model": (
        "1000 × Pipeline - Model ($B) / Z3 ASP - Model ($/kWh). Converts the dollar pipeline "
        "at model ASP. (A prior C-only formula divided by unit COGS after a row shift — that was a bug.)"
    ),
    "Booked orders": "New orders in the quarter ($M). Disclosed when available (e.g. Q4 2025 $240M); otherwise implied as Δbacklog + revenue. A second Booked orders row with units GWh sits below Booked orders - Model (Q4 2025 1.1).",
    "Booked orders - Model": (
        "If the $M actual is present, copy it; otherwise prior Model × 1.2. "
        "Column C uses the units cell as the prior (B14) — that is how the live sheet is typed."
    ),
    "Backlog": "Ending backlog ($M). Company identity: prior + orders − shipments.",
    "Backlog - Model": (
        "Column C copies Q1 Backlog actual ($C$ Backlog). Later columns are prior "
        "Backlog - Model × 1.03. Not the company prior + orders − shipments identity."
    ),
    "Backlog (GWh)": "Ending backlog energy (GWh) as disclosed.",
    "Backlog (GWh) - Model": "Backlog - Model ($M) / Z3 ASP - Model ($/kWh).",
    "Backlog conversion lag": (
        "Quarters of beginning backlog assumed convertible this quarter. Default 4. "
        "Scalar still lives in C; GWh shipped - Model is no longer on Quarterly Financials."
    ),
    "GWh shipped": (
        "No longer a Quarterly Financials row. Previously MWh shipped / 1000. "
        "Kept here because the Definitions tab still has the label."
    ),
    "GWh shipped - Model": (
        "No longer a Quarterly Financials row. Previously MIN(factory capacity, "
        "beginning backlog GWh / conversion lag)."
    ),
    "MWh shipped": (
        "No longer a Quarterly Financials row. Old name for a typed MWh print; "
        "energy now lives on MWh shipped - Derived from PTC."
    ),
    "MWh shipped - Derived": (
        "Removed. Was Revenue × 1000 / Z3 ASP - Model — circular with Revenue - Model "
        "and not a shipment actual. Replaced by MWh shipped - Derived from PTC."
    ),
    "MWh shipped - Derived from PTC": (
        "Energy sold (MWh) reverse-engineered from 45X: statutory PTC $M × 1000 / "
        "45X cell & module credit ($/kWh). Q2 2025: 5.069 × 1000 / 45 = 112.6 MWh. "
        "Blank when Production Tax Credits is blank. 10-Q: PTC hits COGS when "
        "inventory is sold, so this is shipped kWh, not factory output."
    ),
    "MWh shipped - Model": (
        "If MWh shipped - Derived from PTC is present, copy it; otherwise prior "
        "Model × 1.22. Column C uses the units cell as the prior (B63) — that is "
        "how the live sheet is typed. Revenue - Model, COGS - Model, and "
        "Government credits - Model (when PTC is blank) use this energy."
    ),
    "Z3 ASP - Derived": (
        "If Booked orders (GWh) is 0: Pipeline ($B) × 1000 / Pipeline (GWh); "
        "else Booked orders ($M) / Booked orders (GWh). Mixes Cube and Indensity."
    ),
    "Z3 ASP - Model": (
        "$260 in 2025 Q1, then prior × 0.96714 while column() < 9 (through 2026 Q2); "
        "held flat after. Revenue - Model uses this ASP with MWh shipped - Model."
    ),
    "Z3 Module Energy Capacity": "kWh per Z3 module (product sheet ~1.2 kWh). Scalar in C, copied across.",
    "Z3 module cycle time": "Reported cycle time when disclosed (Line 2 ~10% faster vs Line 1 in Q2 2026).",
    "Z3 module cycle time - Model": "Starts at 18s; compounds at the quarterly reduction rate; floored at Cycle time floor (C).",
    "Quarterly module cycle time reduction rate": "Learning-curve % per quarter (default 2.9). Guess — not disclosed as a rate.",
    "Cycle time floor": "Seconds. Model cycle time will not go below this (default 10).",
    "Z3 modules per cube": (
        "Modules packed in the original Cube container (672). Cube-specific — Indensity "
        "is a denser architecture of the same Z3 modules. Do not use 672 to convert Indensity shipments."
    ),
    "Z3 manufacturing lines": (
        "Installed / effective lines when known (1 through Q1 2026; 2 in Q2 2026 after "
        "Line 2 launch; Q3 2026 working 1.5 — in-quarter, not a print)."
    ),
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
        "Live C is 70 (default) because Eos has repeatedly missed cost-out timelines. "
        "100% = take the CFO plan at face value; 0% = freeze Q2 2026 costs. "
        "Edit C; D:Z copy C. Cost-out waterfall and yellow levers live on the COGS tab."
    ),
    "Cost-out plan progress - Model": (
        "0 at the COGS cost-out start quarter (Q2 2026), 1 at the complete quarter "
        "(Q2 2027), held at 1 after. Linear in between. Drives how much of the "
        "guided pts (× haircut) has been applied to adj. GM."
    ),
    "Guided adjusted gross margin - Model": (
        "Slide 11 path with no haircut: starting adj. GM + progress × 73 pts. "
        "At completion this is about +10.7%. Comparison case only — the Model "
        "P&L uses Adjusted gross margin - Model (haircut applied)."
    ),
    "Scale absorption blend - Model": (
        "0 until cost-out progress = 1, then ramps 0→1 as Z3 manufacturing lines - Model "
        "go from 2 → 4 (COGS start/complete line levers). Blends unit COGS from the "
        "haircut adj-GM level toward Terminal unit COGS."
    ),
    "Adj. EBITDA at $200M revenue - Guided": (
        "Illustration only: $200M quarterly revenue × Guided adjusted gross margin − "
        "Cash OpEx run-rate. Does not feed Cash - Model or valuation. Revenue amount "
        "is a yellow lever on the COGS tab."
    ),
    "Adj. EBITDA at $200M revenue - Model": (
        "Same $200M illustration using Adjusted gross margin - Model (haircut path). "
        "At the 70% default this stays negative vs ~$28.5M cash OpEx."
    ),
    "Unit COGS - Derived": (
        "GAAP COGS ($M) × 1000 / MWh shipped - Derived from PTC. Q2 2025 checks to ~$410/kWh "
        "(46.189 × 1000 / 112.6). Blank when PTC energy is blank."
    ),
    "Unit COGS - Model": (
        "Q2 2026 starting adj. GM (−62.3%) plus haircut × guided pts phased "
        "Q2 2026→Q2 2027 (COGS tab levers), then blend toward Terminal unit COGS "
        "(COGS tab, default $181/kWh) as lines go 2→4. Pre-45X; COGS - Model still "
        "subtracts government credits. $/kWh of energy, not per Cube or Indensity SKU."
    ),
    "45X cell & module credit": (
        "IRC 45X statutory $35/kWh cell + $10/kWh module = $45/kWh. Scalar in C, "
        "copied across. Divisor for MWh shipped - Derived from PTC. Does not include the 10% "
        "electrode active-material add-on (that lives in 45x & active electrode credits)."
    ),
    "45x & active electrode credits": (
        "$/kWh statutory credit assumption including ~$2/kWh electrode (default 47). "
        "Used for Effective 45x / Government credits - Model. PTC→MWh uses the $45 "
        "cell+module lever, not this 47."
    ),
    "45x transfer rate": "% of credit realized (default 90). GAAP PTC is recorded at this transfer value.",
    "Effective 45x credit - Model": "Credit × transfer rate (47 × 90% = $42.30/kWh at defaults).",
    "Production Tax Credits": (
        "45X credits recognized as a reduction of GAAP COGS ($M), from the 10-Q/10-K "
        "government-grant footnote (not XBRL). Transfer-value dollars — Q2 2025 $4.562M "
        "is $5.069M statutory at a 90% transfer rate."
    ),
    "Production Tax Credits (statutory) - Derived": (
        "Production Tax Credits / (45x transfer rate / 100). Gross statutory 45X $M "
        "before the transfer discount. Q2 2025: 4.562 / 0.90 = 5.069."
    ),
    "Government credits - Model": (
        "Copy Production Tax Credits actual when present; else effective credit × "
        "MWh shipped - Model / 1000. Applied as a COGS offset only — not added to revenue."
    ),
    "Unit COGS w/ 45x - Model": "Unit COGS − effective 45X.",
    "FY 2026 revenue guidance — low": "Management FY2026 revenue guide low ($300M as of Q2 2026). Scalar in C.",
    "FY 2026 revenue guidance — high": "Management FY2026 revenue guide high ($350M as of Q2 2026). Scalar in C.",
    "Revenue": "GAAP / earnings-release total revenue ($M). Hardcoded actuals through last print.",
    "Revenue - Model": (
        "MWh shipped - Model / 1000 × Z3 ASP - Model. Does not add 45X credits. "
        "Follows PTC energy when present, else the 1.22× shipment path."
    ),
    "COGS": "GAAP cost of goods sold ($M).",
    "COGS - Model": (
        "Unit COGS × MWh shipped - Model / 1000 − government credits + Non-cash COGS (D&A + SBC). "
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
        "Through 2026 Q2 (column < 9) copies Adjusted gross margin actual. After "
        "cost-out progress hits 1, prior Model + 5 pts/q capped at 30%. Otherwise starting "
        "adj. GM (−62.3%) + cost-out plan progress × 73 pts × haircut. Levers "
        "(start GM, pts, dates) are on the COGS tab."
    ),
    "SG&A": "Selling, general & administrative ($M).",
    "SG&A - Model": (
        "If SG&A actual is present, copy it; otherwise prior Model. Column C uses the "
        "units cell as the prior — that is how the live sheet is typed."
    ),
    "R&D": "Research & development ($M).",
    "R&D - Model": (
        "If R&D actual is present, copy it; otherwise prior Model. Same units-cell "
        "prior in column C as SG&A - Model."
    ),
    "OpEx": "Total operating expenses when disclosed; else SG&A + R&D.",
    "OpEx - Model": (
        "If OpEx actual is present, copy it; otherwise prior Model. Not SG&A - Model + "
        "R&D - Model."
    ),
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
        "2025 Q1 copies Cash actual. Later: prior cash (actual if present else model) "
        "+ Operating cash flow - Model − capex − interest + Δ Total debt - Model + "
        "Δ Fully diluted shares - Model × prior Stock price × 0.7 (dilution proceeds haircut)."
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
    "Total debt - Model": (
        "Copy Total debt actual when present; otherwise prior Model × 1.02 per "
        "quarter. Column C uses the units cell as the prior — that is how the live "
        "sheet is typed. Cash - Model adds the quarter's Δ debt."
    ),
    "Net debt - Model": "Total debt - Model − Cash (actual if present else model).",
    "Basic shares": "Shares outstanding / basic weighted average (million).",
    "Fully diluted shares": (
        "If-converted count (million), not GAAP diluted WAS. Basic WAS + every "
        "potential share in that quarter's 10-Q EPS footnote (converts, warrants, "
        "Series B, RSUs/options), including shares GAAP excludes as anti-dilutive "
        "in a loss quarter. Q2 2026: 339.799 + 263.131 = 602.930."
    ),
    "Fully diluted shares - Model": (
        "Copy Fully diluted shares actual when present; otherwise prior Model × "
        "1.02 per quarter. Add events on the Shares tab when you want a discrete "
        "dilution increment instead of the 2% QoQ crawl."
    ),
    "Stock price": "Last daily close on or before quarter-end from Price History (GOOGLEFINANCE).",
    "Market cap": "Stock price × diluted shares / 1000 ($B).",
    "EV / EBITDA": "Multiple applied only when annualized EBITDA - Model is positive (default 30).",
    "Discount rate": "Annual discount rate for PV of implied future price (default 20%).",
    "Enterprise value - Model": "IF(annualized EBITDA > 0, annualized EBITDA × EV/EBITDA / 1000, blank) in $B.",
    "Market cap - Model": "Enterprise value − net debt / 1000.",
    "Implied future stock price - Model": "Market cap - Model / diluted shares × 1000.",
    "Present stock price discounted - Model": "-PV(discount rate, years from present, 0, implied future price).",
}
