# Comstock Inc. (LODE) — retail and social narrative map

**Compiled 2026-09-19 · reference price $2.65 (close 2026-09-18) · 75.99M shares out · market cap ≈ $201M**

## How to read this file

**This is a record of what anonymous strangers on the internet believe. It is not a source of financial facts and must never be used as a modeling input.**

Nothing in this file should flow into `levers.py`, `financials_definitions.py`, or any forecast. The only legitimate uses are:

1. **Expectations risk.** Knowing which unsupported claims are priced in tells you what unwinds on a disappointing print, even when the print matches the filings.
2. **Sanity-checking the model's own framing.** If the model quietly adopts a number that turns out to trace back to a forum post rather than a filing, that is a bug.

Every claim below is labelled with a confidence level describing **how confident I am that the claim is actually widespread**, not how true it is:

- **High** — corroborated across multiple independent venues, or measurable in aggregate sentiment data.
- **Medium** — seen in two or more places, or in one place with clear evidence of circulation.
- **Low** — a single post or article. Treat as an anecdote, not a narrative. Several entries below are explicitly Low, and I have not inflated them.

The "what the company actually said" side of every comparison comes from `guidance.md` and `sec_summary.md` in this directory, which are built from filings and transcripts.

### Platform access — what I could and could not read

| Platform | Access | Notes |
|---|---|---|
| StockTwits | **Partial** | Symbol stream partially readable via search snippets; individual post history and engagement counts not accessible. Aggregate sentiment scores read from third-party trackers (AltIndex), not from StockTwits directly. |
| InvestorsHub | **Yes** | The LODE board (board 4007, ~24,400 posts) rendered in search results and page text. |
| Seeking Alpha | **Headlines and article summaries only** | Article bullet points readable; **comment sections were not accessible**, which is where the retail argument actually happens. This is a real gap. |
| Substack / independent newsletters | **Yes** | Dominic Frisby (*The Flying Frisby*, paid) and one anonymous retail SOTP author. |
| Reddit | **No direct access** | I could not load any r/pennystocks, r/Shortsqueeze, r/stocks or r/ComstockLODE thread. A LODE-specific subreddit (**r/ComstockLODE**) is confirmed to exist only because a third-party write-up cites it. Everything attributed to Reddit below is second-hand and marked Low confidence accordingly. |
| X / Twitter | **No** | No post-level access. Only indirect references (e.g. Frisby describing the CEO's X posts). |
| Yahoo Finance conversations | **No** | Not accessible. |
| YouTube | **Indirect** | Company-controlled channel content only; no independent retail commentary surfaced. |

**Consequence:** the picture below is weighted toward InvestorsHub (structurally bearish), paid newsletters, and aggregate sentiment scores. It under-samples Reddit and X, which are the venues where the most aggressive bull claims usually live. Where I flag a bull claim as Low confidence, the honest reading is often "I could not check whether this is widespread," not "this is rare."

---

## 1. The dominant bull thesis as retail states it

The bull case is a **re-rating story, not an earnings story**: the argument is that LODE is a ~$200M market cap sitting on a first industrial-scale recycling line whose steady-state economics management has publicly quantified, plus two "free" assets (Silver Springs land, Bioleum) that are worth more than the whole company. Current revenue is dismissed as irrelevant because the plant only came online in August 2026.

That structure is real and well-corroborated. The specific numbers attached to it are where it goes wrong.

### 1.1 The silver-per-panel arithmetic — the single most load-bearing and most distorted claim

**The claim:** each panel contains about half a troy ounce of silver; roughly 33 panels make a ton; therefore a ton of panels contains ~18 oz of silver, worth roughly $1,100–$1,200 per ton at recent silver prices — before tipping fees. From there retail reaches "every ton is over $1,000 of silver alone" and "one 100,000-ton plant produces ~1.6 million oz of silver a year, comparable to a mid-sized primary silver mine."

**Confidence that this is widespread: High.** The "half an ounce per panel" phrasing originates with management and has propagated into essentially every bull write-up. The oz-per-ton and oz-per-year extensions appear in the retail SOTP write-up and in InvestorsHub posts referring to panels as an "endless silver mine."

**What the company actually said:** both halves are company statements, and *they do not reconcile with each other*.

- Silver content: **16–18 g (~0.5 oz) per panel** for the substantial majority of panels (Q1 2026 call).
- Panel weight: 3.3M panels ≈ 100,000 tons, i.e. **~33 panels per ton**. Combining these gives **~18 oz of contained silver per ton of panels**.
- But silver leaves the plant only in the metal-rich tailings stream, which is **12–15% of panel weight** and grades **30–50 oz per ton of tailings** (Q2 2025 call). That is only **~4–7 oz of silver per ton of panels** — roughly **one-third** of the contained figure.
- The revenue guide confirms the lower number. Management guides silver-bearing tailings off-take at **~$125/ton of panels at ~$25–40/oz silver**. At 18 oz/ton contained, $125 would be a 17% realization; at ~5 oz/ton it is ~58% — which matches management's own statement that they capture "**only 50% or 60% of the silver value**" because tailings are sold to a third-party refiner.

**Correction:** the contained-metal figure and the recoverable figure differ by about 3x, and **retail uses the contained figure as if it were revenue**. Management is explicit that it does not currently recover silver at all — it sells tailings and lets someone else refine them, and the CEO said on the Q2 2026 call that they are "**very unsatisfied with the recoveries that we get by just selling our tailings**." The >90% recovery target requires the metal-recovery program, which is at **1-ton-per-day pilot** stage targeted for end-2026, with a 25 t/d commercial demo in 2027 and 250 t/d "industry scale" after that. **LODE has never reported a single dollar of silver revenue.**

**Verdict: Materially overstated.**

### 1.2 The "$1,000 per ton" claim

**The claim:** LODE generates about $1,000 of revenue per ton of panels processed.

**Confidence that this is widespread: Medium.** It appears in bull write-ups and follows directly from management's own conference commentary, but I could not corroborate it as a slogan across multiple retail venues.

**What the company actually said:** this one is **closer to supported than most bulls realise, but it is conditional and stale.** Management's base unit economics are **~$500/t tipping fee + ~$250/t off-take = ~$750/t total**, against ~$150/t all-in cost. The $1,000/t figure only appears when silver is high: at ~$60/oz silver, off-take goes from ~$125/t to "**$375 a ton**," which lifts the total toward ~$1,000/t. At the spring 2026 IAccess Alpha conference, with silver "over $80, maybe pushing $90," the CEO put recoveries "closer to $500 a ton."

**The silver-price condition is currently met, which is worth stating plainly.** Silver closed at **$66.35/oz on 2026-09-18**, above the ~$60 level at which management put off-take at $375/t. So unlike most claims in this file, the $1,000/t figure is *not* stranded by the commodity. What it is stranded by is everything else.

**Three things retail drops:**

1. **$750/t and $1,000/t are revenue per ton, not profit.** Some retail framing treats them as margin. All-in cost is ~$150/t on management's own numbers.
2. **Silver is extremely volatile here and management refuses to forecast it.** It peaked near **$110**, was "below $60" at the Q2 call in July, and is ~$66 now, below its own 200-day average of ~$70. The off-take line swings by a factor of three across that range.
3. **The $375/t number assumes LODE sells tailings at prevailing silver prices *net of refining and logistics*, capturing only 50–60% of contained value** — see §1.1. It is not a recovered-silver figure.

**Verdict: Supported but conditional** — a real management statement, currently consistent with spot silver, but a gross revenue figure that has never been demonstrated at scale by actual results.

### 1.3 Revenue per facility: "$60M, now $80–85M"

**The claim:** each 100,000-ton facility produces $60M of revenue, and at higher silver prices $80–85M, on only ~$12.5M of capex.

**Confidence that this is widespread: Medium.** Circulates in bull write-ups; I found it stated directly by the CEO rather than invented by retail.

**What the company actually said:** management said exactly this at the IAccess Alpha conference — "instead of generating $60 million per facility with only $12 and a half million of capital expenditure, we're pushing this thing now to **$80–$85 million**." In earnings-call form the same math is **100,000 t × ~$750/t = $70–75M**, or **~$65M revenue and ~$55M profit at 85–90% utilization** (Q2 2025 call).

**Two corrections retail consistently misses:**

1. **The capex number is wrong and has been for a year.** "$12.5M per facility" comes from the 2025-era Noble Capital sponsored report. Facility #1 actually cost **$14.5M** (Q2 2026 10-Q), plus **$1.8–1.9M** for the Eddy glass upgrade system, against a $1.5M plan. Facility #2 is now estimated at **$13M**.
2. **These are 85–100% utilization figures.** The company has guided only to **≥25%** and has explicitly refused to guide higher: "We're not going to guide past running this 25% level… It's just still too nascent."

**Verdict: Supported as a management statement, but it is a full-utilization target with an understated capex base.**

### 1.4 The facility-count roadmap

**The claim:** five to seven facilities are coming, which multiplies the per-facility revenue figure.

**Confidence that this is widespread: Medium.**

**What the company actually said:** the Q2 2026 10-Q states Comstock Metals "expects to have **at least five industry scale facilities** operating… **over the next five years (2026 through 2030)**." So *five* is a real, in-filing statement. **Seven is not** — that figure comes from the Noble sponsored research report ("plans to build up to seven industry-scale recycling facilities"), not from the company.

**The gating condition is almost always dropped in retail retellings.** Equipment for facility #2 **will not be ordered until facility #1 is operating, ramped and profitable**, and management is emphatic that "site selection is **not** synonymous with deploying production capital." Facility #3 (Cambridge, Ohio): "**We don't have a timeline.**" Facilities #4 and #5 are site assessments only. Management is also actively reconsidering whether to build in 100,000-ton units at all, floating phased 25k → 50k → 75k deployment — "**We haven't made any decisions on any of that.**"

**Verdict: Five is Supported; seven is Never stated by the company; the "operating and profitable first" gate is routinely omitted.**

### 1.5 Bioleum licensing revenue

**The claim:** Bioleum will generate high-margin licensing and royalty revenue; Comstock's $65M preferred converts into a stake in something valued near $1B.

**Confidence that this is widespread: Low-to-Medium.** The $1B figure appears in a retail SOTP write-up, which itself sources it to "Reddit and management commentary" — a second-hand chain I could not verify at the source.

**What the company actually said:**

- **No signed customer license, LOI, MOU or JV with a disclosed dollar value or gallon capacity exists for Bioleum's technology as of Q2 2026.** No upfront license fee, no per-gallon royalty rate, no revenue-per-licensed-facility figure has ever been disclosed. The licensing pipeline claims of the earlier Comstock Fuels era are **not repeated** in the FY2025 10-K or any 2026 filing.
- The model is no longer primarily licensing. Bioleum now intends to "**directly build, own and operate**" refineries and "also license" selected technologies.
- Every licensing dollar figure in the filings runs **the wrong way** — they are amounts Comstock *pays*: AST license fees of $500,000 each plus 1.0% of gross revenue on the first three facilities; NREL at 15% of sublicensing revenue and a 3% royalty with escalating minimums; RenFuel at a 3% royalty.
- Fuels segment revenue has been **$0 in every period ever reported**. The CEO's own forward statement: "We **won't have any revenue from Bioleum generating fuels**. We'll have revenue from Bioleum generating *materials* for fuels. We'll have revenues from **Hexas**" — in **2027**, with no dollar figure.
- The $1B valuation is a third-party investor reference point, and the Marathon term sheet ($325M at ~$700M valuation) dates from **2024** and predates the founder departures. The CEO's own downside framing is recovering "**$65 million for sure**" in a wind-up — a liquidation-preference floor, not a growth valuation.

**Verdict: Never stated.** Bioleum licensing revenue expectations are not supported by any disclosure.

### 1.6 SSOF / Silver Springs land NAV

**The claim:** the Silver Springs land is a hidden data-center asset worth $400–600M, and Comstock's ~48% share of that swamps the current market cap.

**Confidence that this is widespread: Medium.** The land-as-free-option argument is present in bull write-ups; the specific $400–600M range traces to the CEO.

**What the company actually said:** the range is real but it is **the CEO's own comp, not a bid**. Management's comparable range for the powered-land thesis is "$400, $500, $600 million" (2026-08-11). Underlying facts are solid: **2,200–2,500 acres**, ~**2,000 acre-feet** of water rights, and **300 MW** of gas-equivalent power won through a Southwest Gas open-bid process — but with **pipeline delivery in November 2028**.

**What retail drops:**

- Comstock **only took actual ownership of the land a few weeks before 2026-08-11**, by exercising a 2019 purchase option. Before that it held an option, not the land.
- Comstock's stake is **47.63%**, and it is a **minority** interest in a fund — not the whole asset.
- Management's own year-end 2026 test is merely "some defined transaction with some derivable value," and the CEO said a close by then is "**probably not**."
- The carrying value is **$49.0M** at 2026-06-30, and Comstock paid **$11.64M** in 2026 to move from 16.99% to 47.63%. A counterparty transacting at the $400–600M level would be paying roughly 10x what Comstock itself paid weeks earlier.

**Verdict: The $400–600M range is Supported as a management comparable, but it is an unsold, unlisted, 47.63%-owned, minority interest in land whose power does not arrive until late 2028.**

### 1.7 Sum-of-the-parts valuations

**The claim:** SOTP of roughly **$8.50–$9.00 per share** against a market price near $3.

**Confidence that this is widespread: Low.** I found exactly one such published model (an anonymous Substack piece, November 2025). I am not going to inflate one write-up into a consensus. That said, its *structure* — mining + Bioleum + land + recycling, each haircut, summed — clearly matches how bulls talk.

**Why it is now stale regardless of its merits:** it was built on **51.26M shares**. There are now **75.99M**, ~48% more. On share count alone, an $8.70 target becomes roughly **$5.85** with no change to any asset assumption. It also credited **~$60M for the mining segment**; the mining assets were subsequently sold for **$20.0M cash at closing** plus a second tranche, 2,000,000 illiquid TSX-V shares, a contingent $10M and a 1.5% NSR — headlined at "over $45M" but with only $20M of it hard cash.

**Verdict: Never stated by the company** (Comstock has never published a per-share valuation), **and the one circulating version is arithmetically stale.**

### 1.8 Published price targets that retail cites as independent

**Confidence that these circulate: High.**

- **Noble Capital Markets / Channelchek: Outperform, $6.75 target (Nov 2025).** This is **sponsored research** — Comstock pays for it. It forecast the facility commissioning in Q1 2026 and ramping in Q2 2026 (it actually came online in August 2026), and projected **25,000 tons processed in 2026 generating $12.5M of tipping fees plus $5.0M of recoveries — $17.5M of revenue and $13.9M of gross profit**. Against company guidance of **$5M for H2 2026** and actual H1 2026 revenue of **$0.59M**, that forecast is high by roughly **3x**, and its capex figure ($12.5M) understated the actual $14.5M.
- **Water Tower Research (Dec 2025):** EBITDA of −$22.1M (2026E) swinging to **+$32.6M (2027E)** and **+$86.7M (2028E)**. No price target published. The 2027 swing requires a multi-facility ramp that the company has not committed to.
- **Actual sell-side consensus is negative**: MarketBeat shows a **"Reduce"** consensus and a **$4.00** consensus target; UBS reissued **"Reduce"** on 2026-06-22. TipRanks shows $4.50.

**Correction:** the bullish targets retail quotes are sponsored or non-rating research; the unsponsored consensus is a Reduce. Sell-side consensus has also been **persistently too high on near-term revenue** — it modelled **$1.37M** for Q2 2026 against **$0.27M** actual — because it does not model the deferred-revenue mechanic.

---

## 2. The dominant bear thesis

The bear case is far better corroborated than the bull case, largely because InvestorsHub was the one high-volume retail venue I could read directly, and it skews hostile. Weight that sampling bias when reading this section.

### 2.1 Dilution — the core grievance

**Confidence: High.** This is the single most repeated bear point across every venue I could access.

The facts support it without exaggeration:

| Date | Event | Detail |
|---|---|---|
| Aug 2025 | Equity raise | **13.3M shares at $2.25**, $30M gross / **$27.6M net**, with the stock above $3 — **~30% dilution** at a $115M market cap |
| Jan 28–30, 2026 | CMPO (Titan Partners) | **18,181,819 shares at $2.75** = $50.0M gross, **$46.1M net** |
| Mar 3, 2026 | Over-allotment | **2,727,272 shares at $2.75** = $7.5M gross, ~$6.9M net |

Share count: **23.5M (2024-12-31) → 51.9M (2025-12-31) → 74.1M (2026-03-31) → 75.99M** now. Shares outstanding are up **~150% year over year**. In 1H 2026 alone LODE raised **$60.98M** gross against **$4.61M** of issuance costs. A $50M ATM program remains available.

The most specific and most damaging bear allegation, from Dominic Frisby's paid newsletter (Jan 2026):

- The August 2025 raise was accompanied by an assurance from the CEO that "**this is the last raise**." The next raise came **five months later** and was ~41% dilutive if the over-allotment filled.
- "**Just two days previously de Gasperis was boasting on X about being funded.**"
- The stock hit **$4.70** on the Monday morning and closed at **$3.50** the same day on no news, roughly a million shares sold, before the financing was announced the following evening — at **$2.75**. Frisby asked directly: "What did somebody know?" The CEO's response was that "the offering was first confidentially marketed."
- **"De Gasperis has been CEO since 2010. He owns just 135,818 shares."** Frisby's framing: "optionality without consequence… his interests are not aligned with shareholders."

I am reporting these as **allegations from a named commentator with a large retail following**, not as findings. The share-count and pricing facts are verifiable in the filings; the inference about who knew what is not. Note the partial counterpoint: the CEO **purchased 35,000 shares on 2026-05-12** (reported on InvestorsHub, consistent with an insider buy), and insiders hold ~2.49% of the company.

### 2.2 The reverse split

**Confidence: High.**

LODE has done **three** reverse splits: **1-for-5 (Nov 2017)**, **1-for-5 (Nov 2019)**, and **1-for-10 (effective 2025-02-24)**, which took 237.7M shares down to ~23.8M. Bears correctly note that **authorized shares stayed at 245,000,000** under Nevada NRS 78.2055 — so the split reset the runway for issuance rather than constraining it. Noble made the same observation at the time. The stock fell more than 10% on the announcement and was down over 60% year to date by February 2025.

The compounding matters: 1-for-5 × 1-for-5 × 1-for-10 = **a 1-for-250 cumulative reverse split**. Frisby's version — "in his time as CEO he has taken the company from ~$400 to $3" on a split-adjusted basis — is the emotional core of the long-term-holder grievance, and it is arithmetically the right kind of statement even if the exact endpoints are approximate.

### 2.3 Timeline slippage on the recycling facility

**Confidence: High** that this is a recurring bear theme, and the record supports it.

- Noble (Nov 2025) expected commissioning in **Q1 2026** with ramp in **Q2 2026**.
- FY2025 call (Mar 2026) described a 2026 profile of "$100,000 a month to $200,000 a month to **$1 million a month to $2 million a month**." Q2 2026 actual Metals revenue was **~$78K per month**.
- Q2 2026 PR (Jul 2026): facility "up and running in **August**" at ≥25% of rated capacity.
- 2026-08-11 PR: final integration completes **mid-August**; "We anticipate reaching our first production milestone in **September**."
- As of this writing (2026-09-19), **no press release confirming the 25% production milestone has appeared.**

A StockTwits post captured the current state of play precisely: "they seem to be planning to only send a PR out when they reach the 'first production milestone'… which is likely later this month or possibly even next month. If they want a full month of continuous operation, they wouldn't likely be able to announce that until October."

### 2.4 Cash burn and going concern

**Confidence: High** on the facts; **Medium** that going-concern language is specifically cited by retail (I saw it in analyst/filing summaries more than in forum posts).

- Cash: **$52.97M (2026-03-31) → $31.41M (2026-06-30)**. That is **$21.6M** in one quarter.
- Q2 2026 operating cash burn: **$10.1M**. Investing: **$11.5M**.
- Q2 2026 net loss **$25.47M**, of which ~$16.4M is the non-cash Flux Photon write-off — so ~$9M of underlying loss.
- COGS has **exceeded revenue every quarter since Q1 2025**: Q2 2026 was **$1,168,897 of COGS on $272,824 of revenue**.
- The FY2025 10-K states the company **needs additional capital and successful cash generation from the Metals segment to continue as a going concern**, and that in a failure scenario creditors are paid before common shareholders.
- Offsetting: no conventional debt outstanding, debt-to-equity 0.08, current ratio 4.51, and $20M of Mackay cash landing in Q3 2026. DilutionWatch estimates ~20 months of runway.

### 2.5 Promotional-management accusations

**Confidence: High** that this is a dominant theme on InvestorsHub; **Low** that it is the majority view across all retail venues, since the bull-leaning venues were the ones I could not read.

Representative InvestorsHub framing (paraphrased, one user, repeated across posts): dilution; "free loading directors"; "**No known income from sale of silver that is supposed to exist in solar panels**"; only insiders have benefited from Bioleum; management "predicted a game changer with lignin being used for fuel… and yet?"; "anything positive regarding LODE should start with the preface of, 'Once upon a time…'"

The specific substantive charge worth carrying forward is the third one — **that silver is central to every promotional statement and has never produced a dollar of revenue.** That is factually correct: LODE's only disclosed revenue types are Mining and Real Estate, Recycling, Decommissioning Services and Off-take. There is no silver line, and no technology or licensing line either.

Bears also point to the pattern of **peripheral acquisitions later written off**: the $8.67M LINICO goodwill impairment (Q3 2024), $12.24M of non-cash R&D on the GenMat transaction (Q4 2024), and the **$16.4M Flux Photon write-off** (Q2 2026). Management's characterisation of the last one — the impairments "are substantially all non-cash acquisition costs" and the business impact "is **zero**" — is itself cited by bears as the problem: the assets were acquired with stock, so the cost was borne by shareholders through dilution even though no cash moved.

### 2.6 The narrative-versus-revenue gap

**Confidence: High.** This is the bear point that needs no interpretation.

Quarterly revenue for the last six quarters: **$339.5K, $54.1K, $374.4K, $313.5K, $272.8K.** Against that, the company is describing itself as transforming into a "multi-billion-dollar industrial materials enterprise." Q2 2026 missed consensus of ~$1.37M by ~$1.10M. The Seeking Alpha bear piece (2026-09-10) rates it **SELL** on exactly this: "capacity isn't the same as cash flow," no evidence of sustained throughput, realized tipping fees, or positive EBITDA per ton.

The nuance most retail on **both** sides misses is the **deferred-revenue mechanic**: recycling revenue is deferred on receipt of panels and only recognised when a certificate of destruction issues. Deferred revenue was **$3,846,507** at 2026-06-30 against H1 2026 recognised Metals revenue of $510,280. Bears read the tiny revenue as "no customers"; bulls read the backlog as "revenue already in the bag." Both are wrong — cash is genuinely being collected ahead of recognition, but recognition requires the plant to actually process the panels.

---

## 3. Sentiment trajectory and inflection dates, Sep 2025 – Sep 2026

### 3.1 What the aggregate data shows

I could not read Reddit or X directly, so the only quantitative sentiment series available is from **AltIndex**, a third-party NLP tracker that parses Reddit, StockTwits and other forums. Treat it as directional, not precise — it is a vendor score, not a measurement I can reproduce.

| | Feb 26 | Mar 26 | Apr 26 | May 26 | Jun 26 | Jul 26 | Aug 26 | Current (Sep 26) |
|---|---|---|---|---|---|---|---|---|
| AltIndex sentiment score (0–100) | 92 | 93 | 94 | 95 | 98 | 94 | — | **74** |
| StockTwits mentions/day | 165 | 106 | 60 | 99 | 116 | 118 | 86 | — |

The shape is the story: **sentiment sat in a 92–98 band from February through July 2026, then broke down to 74 by September.** Mention volume peaked in February (165/day, the post-offering argument), collapsed to 60 in April, rebuilt into the June Mackay announcement, and is now **down ~30% over three months** to 86/day. That combination — falling sentiment *and* falling attention — is the signature of a story losing its audience rather than one being actively fought over.

StockTwits' own symbol page displayed **"Bearish Sentiment"** at the time I checked, against AltIndex's 90/100 bullish StockTwits sub-score. Those two are irreconcilable and I am not going to pretend otherwise; the vendor scores disagree, which is itself a reason to weight this section lightly. **Confidence: Medium** on the trajectory, **Low** on any single reading.

### 3.2 Price as a sentiment proxy, tied to events

Monthly percentage change is a cleaner and more honest proxy than any vendor score. **Confidence: High** (this is market data, not sentiment interpretation).

| Month | Change | Event |
|---|---|---|
| Sep 2025 | **+40.7%** | Recovery from the August raise; silver running |
| Oct 2025 | −9.4% | High of $4.75, faded |
| Nov 2025 | +15.5% | Noble upgrades to Outperform, **$6.75 target** (2025-11-04). Retail SOTP write-ups appear around here |
| Dec 2025 | +11.5% | Water Tower Research initiates (2025-12-17) with +$32.6M 2027E EBITDA |
| **Jan 2026** | **−21.5%** | **The offering.** High of $4.80 early in the month; CMPO priced 2026-01-30 at **$2.75**. Trust event, not a valuation event |
| Feb 2026 | +5.1% | Mention volume peaks at 165/day — the argument about the raise |
| Mar 2026 | −1.6% | **FY2025 results (2026-03-24).** Revenue $1.4M. Monthly-revenue profile of "$1M to $2M a month" set out |
| Apr 2026 | +7.5% | Quietest month of the year (60 mentions/day) |
| May 2026 | **+26.5%** | **Q1 2026 print (2026-05-07).** Revenue $313K. CEO buys 35,000 shares 2026-05-12. Sentiment peak forming |
| Jun 2026 | +0.2% | **Mackay sale announced (2026-06-22).** 52-week high of **$4.98** intramonth, but the month closed flat — the news was sold |
| **Jul 2026** | **−33.9%** | **Q2 2026 print (2026-07-23):** revenue $272,824 vs ~$1.37M consensus, $25.5M net loss, **$16.4M impairment**. Worst month of the period |
| Aug 2026 | **+20.4%** | **Facility online (2026-08-11)** and **mining sale closed (2026-08-24)**. A genuine relief rally |
| Sep 2026 (to 18th) | **−19.9%** | **No production-milestone press release.** Steady bleed from $3.29 to $2.65 on rising volume |

### 3.3 Reading the arc

Three things stand out.

**The January 2026 offering was the structural break, not the July impairment.** Sentiment scores stayed high after January because the bull thesis was intact, but the *shareholder relationship* broke there — an equity raise at $2.75 five months after a raise that had been described as the last one, with the stock at $4.70 two days earlier. Everything written about management afterwards refers back to it.

**July 2026 was the thesis break.** A 34% monthly drawdown on a print that missed consensus by 4x and carried a $16.4M write-off. Notably, management framed the impairment as having "zero" business impact — and the market disagreed violently.

**September 2026 is the credibility test, in progress right now.** The August rally priced in the facility working. The company said it would announce the first production milestone when it reached it; three weeks into September no such release exists, and the stock has given back the entire August gain. This is the live inflection and it is unresolved as of this writing.

---

## 4. Retail-held expectations for the next two quarters

Caveat up front: **this is the weakest-sourced section in the file.** Forward retail expectations live mostly on Reddit and X, which I could not access. What follows is assembled from the StockTwits stream, the InvestorsHub board, newsletter commentary, and inference from what the company has told people to expect. Confidence is marked accordingly and is mostly Medium or Low.

### 4.1 The H2 2026 $5M revenue guide

**What is hoped for:** that LODE prints roughly **$2.5M in Q3 and $2.5M in Q4**, versus $272,824 in Q2 — a ~9x step change — validating the whole unit-economics story.

**Confidence: High** that the $5M number is the focal point; **Low** on the specific quarterly split, which I am inferring rather than observing.

**Why this is the highest-risk expectation in the file.** The guide was given as "**up and running in August**… at least 25% of rated capacity **from then through year end**." The 2026-08-11 press release then moved the first production milestone to **September**. That silently removes a month or more from the numerator:

| Framing | Months at 25% | Tons | Implied revenue/ton to hit $5M |
|---|---|---|---|
| Aug–Dec (original) | 5 | ~10,400 | ~$480/t |
| Sep–Dec (post-Aug 11) | 4 | ~8,300 | ~$600/t |
| At the stated $750/t | 4 | ~8,300 | would be $6.25M |

So $5M is achievable on a September start at somewhat below full unit economics — but it has **no slack left**. Any further slip and the arithmetic stops working. The single most likely negative surprise for the next two quarters is a **quiet restatement or abandonment of the $5M figure** at the Q3 print.

There is one structural cushion retail does not talk about and bears do not credit: **$3,846,507 of deferred revenue** sat on the balance sheet at 2026-06-30 against ~9,000 tons of stockpiled panels. Much of the H2 number is the *release* of cash already collected, recognised as certificates of destruction issue, rather than new billings. That makes the revenue guide easier to hit than the bear case assumes **and less impressive than the bull case assumes** — it is not evidence of new commercial momentum.

### 4.2 The first production milestone announcement

**What is hoped for:** a press release confirming continuous operation at 25% of rated capacity.

**Confidence: High.** This is the most concrete near-term expectation I could observe, and a StockTwits post laid out the timing logic explicitly: the company appears to be holding its PR until the milestone is real, "which is likely later this month or possibly even next month… If they want a full month of continuous operation, they wouldn't likely be able to announce that until October."

That post is notable for being *more* realistic than the company's own August framing. The more relevant risk is what happens if October arrives without it.

### 4.3 The Bioleum capital raise

**What is hoped for:** a third-party Bioleum raise at a headline valuation that marks up Comstock's $65M preferred position, ideally pointing toward an IPO.

**Confidence: Medium** that this is a live retail expectation; **Low** on any specific valuation figure being widely held.

**What the company actually said:** the raise was **paused** after the realignment, and would "**resume September, October, high confidence**," with capital raised "before the end of this year." Management also flagged that "most of these firms will take **90, 120, 150 days of due diligence**" — which, started in September, lands the money in **Q1 2027 at the earliest**, not in the next two quarters.

Two further corrections:

- Bioleum's Series A was announced in 2025 as "the first of **$50 million planned this year**." **Only the initial $20M tranche ever closed.** The prior raise plan already fell ~$30M short, which is not a detail retail appears to have absorbed.
- If Comstock has to support Bioleum, management has been explicit it "would almost certainly be a **bridge loan** type of a notion, **not more equity**," sized to carry a downsized team burning ~$600–700K/month for three to four months.

**The realistic base case for the next two quarters is therefore "no Bioleum raise closed yet," which would read as a disappointment against a hope that was never actually company-guided to this window.**

### 4.4 Other live expectations

- **$20M of Mackay cash.** **Confidence: High** — it closed 2026-08-24, so it lands in Q3 2026 results. Retail is correct here. Also removes ~$1.5M/year of mining cash drain and ~$6.7M of reclamation liability. What retail over-reads is the "over $45M" headline: only **$20.0M is cash at closing**. The second tranche is due within 18 months (up to $2M settleable in stock), the 2,000,000 Mackay Parent shares are illiquid TSX-V paper, the $10M is contingent on a construction decision within seven years, and the 1.5% NSR is repurchasable for $3.5M.
- **A silver recovery result.** **Confidence: Medium.** The CEO said "if we're going for a one ton a day system by the end of the year, hopefully we'll know about silver before the end of the year." This is a **pilot validation**, not revenue, and the commercial path behind it runs 1 t/d → 25 t/d (2027) → 250 t/d.
- **An SSOF land transaction.** **Confidence: Medium.** Management's own year-end test is merely "some defined transaction with some derivable value," and the CEO said a close by year-end is "**probably not**." Anyone expecting a headline land sale in the next two quarters is expecting something management has already talked down.
- **Facility #2 equipment order.** **Confidence: Low.** Gated on facility #1 being "operating, ramped and profitable." Cannot reasonably happen in this window.

---

## 5. Claims that are verifiably false or materially overstated

This is the section the rest of the file exists to support. Each entry states the circulating claim, the correction, the source of the correction, and how confident I am that the claim genuinely circulates.

### 5.1 "A ton of panels holds ~18 oz of silver, so every ton is ~$1,200 of silver at today's price"

**Confidence it circulates: High.** **Verdict: materially overstated, by roughly 3x.**

The arithmetic (17 g/panel × ~33 panels/ton ≈ 18 oz/ton, × $66/oz ≈ $1,190) uses **contained** metal as though it were revenue. Management's own tailings disclosure — 12–15% of panel weight, grading 30–50 oz per ton of tailings — implies only **~4–7 oz of silver per ton of panels** actually reaches the saleable stream. That lower figure, not the contained figure, is what reconciles with management's guided off-take revenue of ~$125/t at $25–40/oz silver and ~$375/t at ~$60/oz. **Source:** Q1 2026 and Q2 2025 earnings calls, as compiled in `guidance.md` §1.1 and §1.3.

### 5.2 "Each facility will produce ~1.6 million oz of silver a year, like a mid-sized silver mine"

**Confidence it circulates: Medium** (found in a retail SOTP write-up; the "solar panels are a silver mine" framing is broader). **Verdict: contradicted.**

**Comstock does not produce silver and has never reported a dollar of silver revenue.** It sells metal-rich tailings to a third-party refiner. Its only four disclosed revenue types are Mining and Real Estate, Recycling, Decommissioning Services and Off-take. In-house recovery is at **1-ton-per-day pilot** stage targeted for end-2026, scaling to 25 t/d in 2027 and 250 t/d thereafter. The CEO's own words on the Q2 2026 call: "We're **very unsatisfied with the recoveries** that we get by just selling our tailings." **Source:** Q2 2026 10-Q Note 15; Q2 2026 call.

### 5.3 "2026 revenue will be about $17.5 million"

**Confidence it circulates: Medium-High** (it is the headline forecast in the sponsored research report that retail cites most). **Verdict: materially overstated, by roughly 3x.**

The figure comes from **Noble Capital Markets' November 2025 report**, which modelled 25,000 tons processed in 2026 producing $12.5M of tipping fees plus $5.0M of recoveries and **$13.9M of gross profit**. The company's own guidance is **$5M for H2 2026**, and actual H1 2026 revenue was **$0.59M** — a full-year path of roughly **$5.6M**. Noble also assumed commissioning in Q1 2026 and ramp in Q2 2026; the facility actually came online in August. **Source:** Noble/Channelchek report 2025-11-04 vs Q2 2026 earnings release and 10-Q.

**Related correction:** Noble is **sponsored research paid for by Comstock**, not independent coverage. The unsponsored consensus is a **"Reduce" rating with a $4.00 target**, and UBS reissued "Reduce" on 2026-06-22.

### 5.4 "Each facility costs only $12.5 million"

**Confidence it circulates: Medium.** **Verdict: materially overstated (understates cost by ~30%).**

Facility #1 actually cost **$14.5M** per the Q2 2026 10-Q, plus **$1.8–1.9M** for the Eddy glass upgrade system against a $1.5M plan — roughly **$16.3M all-in**. Facility #2 is estimated at **$13M**. The $12.5M figure is a stale 2025 planning number that survives because the sponsored research used it. **Source:** Q2 2026 10-Q; Q1 2026 and Q2 2026 calls.

### 5.5 "Seven facilities are planned"

**Confidence it circulates: Low-Medium.** **Verdict: never stated by the company.**

The Q2 2026 10-Q says "at least **five** industry scale facilities… over the next five years (2026 through 2030)." The number **seven** appears in the Noble report, not in any Comstock filing or release. **Source:** Q2 2026 10-Q vs Noble report.

### 5.6 "The facility went into production in August 2026"

**Confidence it circulates: High.** **Verdict: weaker than claimed.**

The 2026-08-11 release says the system was fully **integrated, tested and operated** — and that final integration completes **mid-August**, with "We anticipate reaching our **first production milestone in September**." Being brought online is not the same as running continuously at 25% of rated capacity, and **as of 2026-09-19 no release confirming that milestone has appeared.** **Source:** Comstock PR 2026-08-11.

### 5.7 "The mining sale brought in $45 million"

**Confidence it circulates: High** (the company's own headline invites it). **Verdict: weaker than claimed.**

**$20.0M is cash at closing.** The balance of the "over $45M" comprises a second tranche due within 18 months (up to $2M of which may be settled in Mackay Parent stock), **2,000,000 shares of a small TSX-V issuer** (illiquid), a **$10M payment contingent** on a construction decision or change of control within seven years, a **1.5% NSR** that Mackay can repurchase for $3.5M, and the transfer of ~$6.7M of reclamation liability. **Source:** 8-K 2026-06-24; Q2 2026 10-Q; `asset_monetization.py`.

### 5.8 "Comstock is sitting on $400–600 million of data-center land"

**Confidence it circulates: Medium.** **Verdict: weaker than claimed.**

The range is the **CEO's own comparable**, not a bid or an appraisal. Comstock holds **47.63%** — a minority interest in a fund — carried at **$49.0M**, having paid **$11.64M** during 2026 to get there. It only took actual ownership of the land weeks before 2026-08-11 by exercising a 2019 option. The 300 MW of secured power does not physically arrive until **November 2028**. Management's year-end 2026 test is only "some defined transaction with some derivable value," and the CEO said a close by then is "**probably not**." **Source:** Q2 2026 8-K; 2026-08-11 CEO interview; `asset_monetization.py`.

### 5.9 "Bioleum licensing revenue is coming" / "Bioleum is worth $1 billion"

**Confidence it circulates: Low-Medium** (the $1B figure traces through a retail write-up citing "Reddit and management commentary," a chain I could not verify at source). **Verdict: never stated / contradicted.**

- **No signed customer license, LOI, MOU or JV with a disclosed dollar value or gallon capacity exists for Bioleum's technology as of Q2 2026.** No license fee, royalty rate, or revenue-per-facility figure has ever been disclosed.
- Every licensing dollar amount in the filings is money Comstock **pays out** (AST $500,000 per facility plus 1% of gross revenue; NREL 15% of sublicensing revenue plus 3% royalty; RenFuel 3% royalty).
- Fuels segment revenue has been **$0 in every period ever reported**, and the CEO says Bioleum will have **no fuel revenue** even in 2027 — only feedstock/materials revenue via Hexas.
- The $1B reference is a third-party investor figure; the Marathon term sheet ($325M at ~$700M) is from **2024** and predates the founder departures. The CEO's own downside number is recovering "**$65 million for sure**" in a wind-up.

**Source:** FY2025 10-K; Q2 2026 10-Q Note 15; Q2 2026 call.

### 5.10 "Bioleum raised $50 million in its Series A"

**Confidence it circulates: Low.** **Verdict: contradicted.**

The May 2025 shareholder letter described the $20M tranche as "the first of **$50 million planned this year**." **Only the $20M closed.** The follow-on was subsequently paused and is now targeted to "resume September, October." **Source:** Comstock shareholder letter (May 2025); Q2 2026 call.

### 5.11 "The plant is profitable at 21% utilization, so the company is profitable"

**Confidence it circulates: Medium.** **Verdict: weaker than claimed — two different thresholds are being conflated.**

Management's claims are distinct and both were made: **facility #1 is cash-flow positive at the line-of-business level at 20–25%**, but the **company** is not profitable until **40–50%** utilization of that facility ("Getting to 50%, we're profitable as a corporation"). Retail routinely quotes the 21% figure as though it were the corporate breakeven. **Source:** Q1 2026 and Q2 2026 calls.

### 5.12 "The $5M H2 guide proves commercial demand"

**Confidence it circulates: Medium.** **Verdict: weaker than claimed.**

A large share of the H2 2026 revenue is the **recognition of the $3,846,507 deferred revenue balance** as already-stockpiled panels are processed and certificates of destruction issue — cash collected in prior periods, not new billings. **Source:** Q2 2026 10-Q Note 13.

### 5.13 A bear claim that is also overstated: "two lawsuits alleging fraud and breach of fiduciary duty"

**Confidence it circulates: Low** (found in an automated news summary rather than in forum posts). **Verdict: overstated.**

The June 2026 case is **Magnesis Corporation v. Comstock Inc. et al, 3:26-cv-00446 (D. Nev., filed 2026-06-12)**. The docket records **Nature of Suit 190, "Contract – Other Contract," cause "28:1330 Breach of Contract."** It is a contract action on its face. The "fraud and breach of fiduciary duty" characterisation comes from a secondary aggregator, not the docket. I could not read the complaint itself, so I can confirm what the case is captioned as but not the full set of claims pleaded inside it. **Source:** PACER docket 3:26-cv-00446.

### 5.14 A common conflation worth flagging: "the reverse split diluted shareholders"

**Confidence it circulates: Low-Medium.** **Verdict: contradicted as stated, though the underlying worry is legitimate.**

The 1-for-10 split of 2025-02-24 was proportional and changed no one's ownership percentage. What actually matters — and what bears are right to point at — is that **authorized shares remained at 245,000,000** under Nevada NRS 78.2055, so the split restored issuance headroom. The dilution came from the subsequent raises, not from the split. **Source:** Comstock PR 2025-02-14; FY2025 10-K.

---

## 6. Summary table

Verdicts: **Supported** / **Weaker than claimed** / **Never stated** / **Contradicted**. Confidence is in how widespread the claim is, not how true.

| Circulating claim | What the company actually said | Verdict | Confidence | Source |
|---|---|---|---|---|
| ~0.5 oz of silver per panel | 16–18 g (~0.5 oz) per panel for the substantial majority of panels | **Supported** | High | Q1 2026 call |
| A ton of panels = ~18 oz of silver = ~$1,200 of value | Tailings are 12–15% of weight at 30–50 oz/t → **~4–7 oz per ton of panels**; off-take guided at ~$125/t ($25–40 silver), ~$375/t (~$60 silver) | **Materially overstated (~3x)** | High | Q2 2025 / Q1 2026 calls |
| Each plant yields ~1.6M oz of silver a year | Comstock produces **no silver**; sells tailings to a third-party refiner. In-house recovery at 1 t/d pilot stage, targeted end-2026 | **Contradicted** | Medium | Q2 2026 10-Q / call |
| ~$1,000 of revenue per ton | ~$750/t base ($500 tipping + ~$250 off-take); ~$1,000/t only at ~$60+/oz silver. Silver is $66.35 today, so the condition currently holds | **Supported but conditional** | Medium | FY2025 call |
| $60M, or $80–85M, of revenue per facility | CEO said exactly this — at **85–100% utilization**. Company has guided only to ≥25% and refuses to guide higher | **Supported (at full utilization)** | Medium | IAccess Alpha 2026; Q2 2025 call |
| Capex is $12.5M per facility | Facility #1 cost **$14.5M** + **$1.8–1.9M** Eddy upgrade; facility #2 est. $13M | **Materially overstated** | Medium | Q2 2026 10-Q |
| Five facilities are planned | "At least five industry scale facilities… over the next five years (2026–2030)" | **Supported** | Medium | Q2 2026 10-Q |
| Seven facilities are planned | Company has only ever said five; "seven" is from sponsored research | **Never stated** | Low-Med | Q2 2026 10-Q vs Noble |
| Facilities #2–#5 are underway | Equipment not ordered until #1 is "operating, ramped and profitable"; #3 "we don't have a timeline"; #4–#5 are site assessments | **Weaker than claimed** | Medium | Q2 2026 call |
| The facility went into production in August 2026 | Integrated and tested by 2026-08-11; final integration mid-August; **first production milestone anticipated in September**. No confirming release as of 2026-09-19 | **Weaker than claimed** | High | PR 2026-08-11 |
| The plant is profitable at 21% utilization, so the company is | Facility-level profitable at 20–25%; **company-level at 40–50%** | **Weaker than claimed** | Medium | Q1/Q2 2026 calls |
| $5M in H2 2026 proves commercial demand | Much of it is recognition of the **$3,846,507** deferred revenue balance on already-stockpiled panels | **Weaker than claimed** | Medium | Q2 2026 10-Q Note 13 |
| 2026 revenue of ~$17.5M | Guidance is $5M for H2; H1 actual $0.59M → ~$5.6M full year | **Materially overstated (~3x)** | Med-High | Noble 2025-11-04 vs Q2 2026 |
| Noble's $6.75 target is independent coverage | **Sponsored research**. Unsponsored consensus is "Reduce," $4.00; UBS "Reduce" | **Contradicted** | High | MarketBeat / UBS 2026-06-22 |
| Retail SOTP of $8.50–$9.00/share | Comstock has never published a per-share valuation. The one circulating model used **51.26M shares**; there are now **75.99M** (~$5.85 equivalent), and it credited ~$60M to mining that sold for $20M cash | **Never stated / stale** | Low | Substack SOTP, Nov 2025 |
| The mining sale brought in $45M | **$20.0M cash at closing**; rest is a second tranche, illiquid TSX-V stock, a 7-year contingent $10M and a repurchasable NSR | **Weaker than claimed** | High | 8-K 2026-06-24 |
| Comstock owns $400–600M of data-center land | CEO's own comparable, not a bid. **47.63% minority** stake carried at **$49.0M**; power delivered **Nov 2028**; CEO says a 2026 close is "probably not" | **Weaker than claimed** | Medium | 2026-08-11 interview |
| Bioleum licensing revenue is coming | **No signed license, LOI, MOU or JV with any disclosed dollar value or capacity.** Every licensing figure in the filings is money Comstock pays out. Fuels revenue $0 in every period | **Never stated** | Low-Med | FY2025 10-K; Q2 2026 10-Q |
| Bioleum is worth ~$1B | Third-party reference only; Marathon's $325M at ~$700M is from **2024**. CEO's own floor: recover "$65 million for sure" in a wind-up | **Weaker than claimed** | Low | Q1/Q2 2026 calls |
| Bioleum raised $50M in Series A | **$20M closed**; it was described as "the first of $50 million planned this year." Balance never closed; raise paused, to "resume September, October" | **Contradicted** | Low | Shareholder letter 2025; Q2 2026 call |
| Bioleum's Oklahoma refinery delivers >$30M of annual operating income | Company did say this — for a **400,000 bbl/yr facility requiring ~$160M of investment** that management says it is "not ready yet" to build (TRL 6; TRL 7 needs $200–250M) | **Supported but remote** | Low | Shareholder letter 2025; FY2025 10-K |
| Management repeatedly dilutes after saying it won't | Aug 2025: 13.3M shares at $2.25 (~30% dilution). Jan 2026: 18.18M at $2.75 + 2.73M over-allotment. Shares +150% YoY. The "last raise" assurance is a named commentator's account, not a filing | **Supported (facts) / allegation (intent)** | High | 10-K; Frisby newsletter |
| The reverse split diluted shareholders | The 1-for-10 split was proportional. But **authorized stayed at 245M**, restoring issuance headroom — that is the legitimate concern | **Contradicted as stated** | Low-Med | PR 2025-02-14 |
| Silver has never produced revenue for Comstock | Correct. No silver revenue line exists in any period | **Supported** | High | Q2 2026 10-Q Note 15 |
| Two lawsuits allege fraud and breach of fiduciary duty | The June 2026 case (Magnesis, 3:26-cv-00446 D. Nev.) is docketed as **"Contract – Other Contract," breach of contract**. I could not read the complaint | **Overstated** | Low | PACER docket |

---

## 7. Bottom line

The bull case is not built on invented numbers — it is built on **real management statements stripped of their conditions**. Almost every figure retail repeats was said by the CEO. What gets lost in transmission is the qualifier: at 85–100% utilization, at $60+ silver, contained rather than recovered, revenue rather than profit, a comparable rather than a bid, gated on the first facility being profitable, pending a raise that hasn't closed.

The one genuine arithmetic error, and the most load-bearing, is **§5.1** — treating contained silver per panel as recoverable revenue per ton, which overstates by roughly 3x and is the foundation of the "urban silver mine" framing.

The bear case is better grounded in fact, particularly on dilution, but is sampled from the most hostile venue available to me and should be discounted accordingly.

**The live question, as of 2026-09-19, is narrow and testable:** the company said it would announce a first production milestone in September. It has not. The stock has given back the entire post-facility-online rally. Whatever else is true, the next two quarters turn on whether $5M of H2 revenue appears — and the arithmetic behind that guide no longer has any slack in it.

**None of the above is a modeling input.**
