# Resources

Sources and references used in the **Opendoor Model** spreadsheet (and related comments). Not investment advice; citations are for transparency about where numbers and assumptions come from.

Spreadsheet: [Opendoor Model](https://docs.google.com/spreadsheets/d/1BhauTzGc9Nyt1J9gQl3NdCnpSSKCpSLbY9H7p5Obvc4)

---

## Official Opendoor

### Earnings materials (primary actuals)

Quarterly results and supplements are the main source for “actual” rows in **Quarterly Financials** (and the weekly spreads derived from them). Comments in the sheet point to:

| Metric in model | Where cited |
| --- | --- |
| Homes Purchased | Earnings supplement — *Non-GAAP Measures & Key Metrics* |
| Homes in Inventory | Earnings supplement — *Non-GAAP Measures & Key Metrics* |
| Adjusted Operating Expenses | Earnings supplement — *Non-GAAP - Operating Expenses* |
| Average Sale Price (ASP) | Q2 2026 ASP ≈ **$377.5K** (sheet input) |
| Contribution Margin | Q2 2026 CM ≈ **5.8%**; Q3 2026 guidance **4–4.5%** |
| Stock-based compensation | Q3 2026 SBC guide ≈ **$110M** (modeled weekly as ~$8.5M) |
| Basic shares / dilution | **Shares** tab — reusable event table (`Shares!A4:I20`). **Aug 2026 deal** ([8-K Aug 19, 2026](https://www.sec.gov/Archives/edgar/data/1801169/000114036126033739/ef20080596_8k.htm), [press release](https://investor.opendoor.com/news-releases/news-release-details/opendoor-reduces-shares-outstanding-5-first-ever-share-buyback)): **−45.3M** repurchase @ **$3.49**; **$650M** 0% converts (~**138M** shares @ **$4.71** conversion); capped calls through **$6.98**; **$10.38 net-zero price** = stock price where convert dilution restores repurchased shares (net Δ shares ≈ 0). **Weekly Financials**: **Share Count Adjustment - Model** (BYROW over table + SBC); **Basic Shares Outstanding - Model** = actual if present else prior + adjustment. |
| Revenue | e.g. quarterly revenue ÷ 13 for weekly run-rate; Q3 2026 guide ≥ **+20% YoY** → ~$915M × 1.2 ≈ **$1.1B** |

Management commentary captured in sheet comments (paraphrased / quoted):

- Contribution margin bottomed around September 2025 and improved monthly thereafter (Q1 2026 report).
- Near-term CM pressure while clearing older inventory.
- Historical Q2→Q3 CM drops averaged ~500 bps (ex-2023); management argued a narrower drop this cycle (Q2 2026).
- Q4 CM guided above Q3 (Q2 2026 / Kaz).
- Positive adjusted net income expected more from **volume + cost leverage** at a **~5–7% CM** target than from structurally higher unit margins.
- Fixed opex called out for accountability; recent quarterly path cited as roughly **$37M → $35M → $33M → $35M** (Q3 2025–Q2 2026).
- Acquisition contracts “typically close about a month later.”
- Q2 2026: **>50%** of scheduled Colorado resale closes financed with Opendoor Home Loans; Texas **~20%** at ~6 weeks ([Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/1801169/000180116926000019/q22026formxex991earningsre.htm)).
- [Doma closing/escrow acquisition](https://www.opendoor.com/articles/doma-acquisition-complete) — Fannie Mae Title Acceptance refis; borrower savings cited **~$300–$1,500** / **~$1,100** per refi; modeled separately from home-sale CM.

### Ancillary products (model assumptions)

| Lever | Location | Default | Notes |
| --- | --- | --- | --- |
| Max mortgage net $/attached loan | `Transitions!B29` | **$4,000** | CM add = **Open Mortgage Percent** × B29 ÷ ASP |
| Max title net $/purchase close | `Transitions!B30` | **$2,400** | CM add = **Open Title Purchase Percent** × B30 ÷ ASP |
| ODL attach ramp | **Open Mortgage Percent** | smoothstep **0% → 80%** (Jan 2026 – Jan 2029) | Four-phase smoothstep |
| Title purchase attach | **Open Title Purchase Percent** | linear **0% → 100%** (Jan 2025 – Jun 2027) | Purchase resales only |

Sources: [Opendoor Home Loans](https://www.opendoor.com/articles/why-mortgage-rates-at-opendoor-are-so-much-lower), [Doma announcement](https://www.opendoor.com/articles/doma-announcement), MBA 2024 ~$443 net/loan (industry benchmark).


- [Buyer closing & financing (Opendoor Help)](https://help.opendoor.com/buying/financing-closing/buyer-closing) — used for offer→close timing assumptions (financed ~30–45 days / ~6 weeks; cash as fast as ~14 days / ~3 weeks).

### Accountability / public projections

- Sheet comments reference Opendoor’s accountability / projection materials for acquisition acceleration (late August–early October 2026). Prefer the latest official accountability page or earnings slides when refreshing the model.

---

## Independent trackers & analysis

| Resource | Role in model |
| --- | --- |
| [Open Tracker (aubermark)](https://aubermark.github.io/open-tracker/) | Listing/acquisition funnel notes: ~**10–20%** of contracts canceled before market in 2025; some deals complete privately and never show as public listings. Combined cancel + Opendoor walk-away is modeled as weekly **Likelihood to Close** on **Weekly Financials** (~78% in 2025 → ~67% by Q2 2026). **Private Home Sales - Model** = purchases × `(1 − Likelihood to List)` lagged on **1.0 listing timing** (`Transitions!B5:J5`); not company-disclosed. Tracker starts **22 Feb 2026**, so Sep 2025–Feb 2026 new lists are modeled (including a finite **unlisted 1.0 backlog** flush, `Transitions!B21`). |
| [Wealthmatica — cohort sell-through by listing week](https://wealthmatica.substack.com/i/204433858) | Shape of **Percent Sold by Listing Week** / sell-through curve (listed homes only); combined with Q2 2026 “~91% by ~120 days” commentary. |
| [X / mudirshin article media](https://x.com/mudirshin/article/2090092238499926511/media/2090092137169760256) | Seed / calibration values for early weeks (e.g. commented “220” listing baseline). |

Refresh these periodically; independent scrapers and posts can lag or disagree with company-reported Non-GAAP metrics.

---

## Housing market / seasonality

| Resource | Role in model |
| --- | --- |
| National monthly home-sales seasonality (chart referenced via [Google image search for national average monthly home sales](https://www.google.com/search?q=National+average+monthly+home+sales+averaged+over+all+years+with+January+through+December+on+the+ex+axis&udm=2)) | **Seasonality** tab monthly weights; weekly **Seasonality Multiplier** = month weight ÷ (1/12). |
| Broader U.S. cash-purchase share (~**31–32%**) | **Transitions → Percent Cash Purchase Sales** — Opendoor does not disclose financed vs cash mix on resales, so the model uses the national trend. |

---

## Spreadsheet locations of citations

In-sheet citations appear as:

1. **Cell comments** on **Weekly Financials**, **Quarterly Financials**, and **Transitions** (earnings quotes, metric definitions, guessed rates).
2. **Inline notes** on **Transitions** (closing timing + cash %).
3. **Seasonality!A5** (link/note to the national seasonality chart being mimicked).

There are no Drive “note” fields separate from comments in the current workbook; use Comments in Google Sheets to browse the full list.

---

## Suggested refresh checklist

When updating the model after an earnings release:

1. Pull Non-GAAP homes purchased, inventory, revenue, CM, ASP, adjusted opex, fixed opex, SBC from the supplement.
2. Reconcile weekly “actual” stubs to **Quarterly Financials** (or enter weekly values and let quarterly rows sum).
3. Update CM guidance and growth / seasonality assumptions if management changes the outlook.
4. Cross-check listing/acquisition run-rates against [Open Tracker](https://aubermark.github.io/open-tracker/) and any new accountability charts; update **Likelihood to Close** (`B8` / `AE8`) if cancel/walk-away has moved.
5. Confirm transition curves still roughly match disclosed sell-through / days-on-market stats.
6. Append the sheet edits to [CHANGELOG.md](CHANGELOG.md).
