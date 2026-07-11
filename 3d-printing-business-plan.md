# Peninsula Additive — Business Plan

**A 3D printing / additive manufacturing venture in Redwood City, California**
**Founder:** Scott Nelson · **Prepared:** July 2026
**Capitalization:** $10,000 founder capital + milestone-gated external capital

> **How this document was built.** Every material number below was researched and adversarially verified in July 2026 (multi-source verification; claims that failed verification were discarded and are listed in Appendix B). Confidence flags: ✅ verified against primary or multiple concordant sources · ⚠️ verified range / directional · ❓ could not be verified — confirm before relying on it. This is a planning document, not tax or legal advice; engage a CPA before the first return and confirm zoning with Redwood City Planning, (650) 780-7234.

---

## 1. Executive Summary

**The thesis, corrected.** The founding intuition — *a machine is an asset best utilized by a wide variety of adaptable solutions* — is half right. In 2026 the machine is the cheapest, least scarce, fastest-depreciating component of an additive manufacturing business. The verified industry data says value has moved decisively to **services and software**: of the $24.2B global AM market (2025), printing **services are 48% of revenue and growing 15.5%/yr, while machine sales are 26% and growing only 3.6%** ✅ (Wohlers Report 2026). The scarce assets are (a) demand relationships, (b) speed of response, and (c) the software/automation layer — and the founder's actual skills (Python, ML, full-stack, pipeline automation) map to exactly those scarce assets, not to the hardware.

**The business.** Peninsula Additive is a **software-leveraged rapid-response prototyping cell** serving the mid-Peninsula's hardware, biotech, and product-design cluster, started home-based in Redwood City with 3–4 printers and ~$10,000, and scaled only through milestone gates backed by demonstrated demand. It sells three things, in ascending margin order:

1. **Same-day/next-day printed parts** for local B2B customers — the one service ship-in networks (JLC3DP from $0.30/part, Xometry, Craftcloud) structurally cannot offer and the free library makerspaces cannot match in materials, capacity, or reliability ✅;
2. **Design-adjacent engineering labor** (design-for-printing, iteration management, small-batch production runs) billed at $60–95/hr, inside the verified market band of $40–125/hr ⚠️;
3. **The software layer** — automated quoting, order-to-print orchestration, and fleet analytics — built first as internal tooling (the founder's core skill, near-zero marginal cost), monetized externally only if traction appears.

**Why Redwood City works — and what it forbids.** Within ~10 miles: Guardant Health and Revolution Medicines (Redwood City), the 1M+ SF Redwood LIFE campus, San Carlos's 2.5M SF biotech cluster, Zoox (Foster City, ~7 mi), Skydio (San Mateo, ~8 mi), StudioRed and the Palo Alto design firms, and an AIA chapter of architecture firms ✅ — a dense pool of buyers for fast prototype iterations. Meanwhile **no dedicated 3D printing service physically operates in Redwood City / San Carlos / Menlo Park** ⚠️ (the nearest full-service bureau, ProtoCafe, is across the bridge in Newark; Fathom retrenched its Bay Area operation; Fictiv was acquired and is a broker, not a shop). What the location forbids is equally clear: at ~$2.05–2.48/SF/mo NNN with ~800 SF minimum units (≈$1,650–2,000/mo before NNN loads) ✅, **leased industrial space is unaffordable at this capitalization**, and Redwood City's home-occupation rules (business incidental to residence, <25% of floor area, no exterior evidence, no non-resident employees, storage restrictions ⚠️) cap the home-based fleet at roughly a spare room of quiet printers — which is exactly the right size for phase one anyway.

**The honest headline numbers.** Verified operator-reported economics put undifferentiated print capacity at **$75–400/printer/month gross**, reaching ~$1,200/month only with proven products at near-24/7 utilization ✅. This plan's base case therefore builds to **~$2,100/month revenue by month 12** (printing + design labor), turns a modest accounting profit, and **does not cover the founder's opportunity cost in year one** — stated plainly in §8 rather than hidden. The venture is justified in year one as a capital-light option: it costs ~$10k and ~10 disciplined hours/week to discover whether a durable niche exists, while building reusable software IP and a B2B client list. Gates at months 4, 9, and 15 (§9) decide scale-up, pivot, or shutdown — with shutdown recovering an estimated $4–6k.

**Capital plan in one line:** $10k founder cash funds phase one; an SBA microloan ($15–25k at 8–13% ✅) funds phase two *only after* three consecutive months of ≥$2,000 revenue at ≥40% contribution margin; investor capital (SAFE) is raised *only* for the software product or a contracted-demand expansion — **never for speculative print capacity**.

---

## 2. Founder Fit — an Honest Assessment

| Asset | Evidence | Business relevance |
|---|---|---|
| Advanced Python / ML / LLM engineering | Meta Llama 2/3 fine-tuning, red-teaming, eval work | Quoting automation, failure-detection analytics, demand-side tooling — the layer where AM value is accruing |
| Full-stack + automation | Firebase/Supabase/Flask/Vercel portal builds; n8n pipelines; solo-engineer consulting | Customer portal, order-to-print orchestration, marketing automation — replaces ~$5–40/printer/mo of SaaS ✅ and hours of labor |
| Data discipline | ETL, eval metrics, statistical analysis | The owner's scorecard (§9) run as an actual instrumented pipeline, not a spreadsheet aspiration |
| Solo-operator experience | Sole technical owner of a $480K-portfolio debt-collection business | Has already run a one-person P&L with a non-technical counterparty |

**Gaps, stated plainly:**

- **No mechanical engineering / CAD background.** Design IP is one of the two scarce assets, and the founder does not yet have it. Mitigation: (a) sell *process* (speed, reliability, iteration management) rather than *design* in phase one; (b) build CAD fluency deliberately (OpenSCAD/Fusion 360 — OpenSCAD is code, which plays to strength); (c) partner for genuinely engineered parts rather than faking competence — the wind-turbine class of load-bearing product is explicitly out of scope (§10).
- **High opportunity cost.** A Bay Area data scientist's time markets at roughly $70–100+/hr; mechanical-engineering consulting benchmarks at $68–89/hr average ⚠️. Every hour on plate-swapping is an hour below the founder's wage. This forces the design decision that defines the company: **automate operations until the business consumes ≤10 hr/week**, and treat any task that can't be automated or priced above the founder's rate as a candidate for elimination.
- **Concurrent MS program (SJSU, Applied Data Intelligence).** A constraint and an asset: it caps founder hours (enforcing the automation discipline) and keeps a career fallback warm. The plan assumes **no reliance on business income for living costs in year one**.

**Fit verdict:** the founder is *mis-fit to a labor-intensive print farm* and *well-fit to a software-leveraged service cell*. The plan is shaped accordingly.

---

## 3. Market Analysis (verified July 2026)

### 3.1 Industry: where value accrues

- Global AM market **$24.2B in 2025, +10.9% YoY** — growth well below the historical 20%+, i.e., a maturing market ✅ (Wohlers Report 2026, via Wohlers/ASTM press releases).
- Segment mix: **services $11.7B (48%, +15.5%)** · systems $6.2B (26%, +3.6%) · materials $4.9B (20%) · software $1.4B (6%) ✅.
- Interpretation (flagged as inference): customers increasingly *buy outcomes, not machines* — consistent with entry-level printer shipments hitting ~1M units in Q1 2025 alone ⚠️ (supply-side flooding of the hardware layer).

### 3.2 Local competition map

| Competitor class | Who / where | Implication |
|---|---|---|
| Full-service bureau | **ProtoCafe**, Newark (founded 2003, ex-Redwood City; SLA/FDM/SLS/PolyJet, CAD, casting, finishing) ✅ | Owns the "full value chain, established relationships" position. Do not fight it head-on; win on same-day turnaround and software-native customer experience for small jobs it deprioritizes. |
| Free public capacity | **Redwood City Library Makerspace** (6 FDM printers, laser, free materials) ✅; all San Mateo County libraries now have 3D printers ✅ | Consumer/hobbyist PLA printing is **free** locally. Do not sell commodity PLA prints to consumers. The paid gap is B2B: speed, engineering materials, capacity, reliability, invoiceability. |
| Ship-in networks | JLC3DP (parts *from $0.30*, China) ✅; Xometry, Craftcloud, Hubs, Makelab (2-day ship to Palo Alto) ⚠️ | Set the price ceiling on non-urgent work. The defensible local premium is **speed (same-day) + bundled design labor** — verified as the only premium that survives ⚠️. |
| Local shops | Jinxbot (Mountain View, ~24h); small Yelp-tier operators ⚠️; **no dedicated print service found physically in Redwood City / San Carlos / Menlo Park** ⚠️ | A real, if narrow, geographic gap on the mid-Peninsula. |
| Market signals | Fathom consolidated its Bay Area operation into a smaller Fremont center ⚠️; Fictiv acquired by MISUMI ($350M, closed June 2025), HQ now Oakland ✅; Shapeways' 2024 Chapter 7 (prior knowledge ❓) | Even scaled players found Bay Area physical operations hard — capacity is not where the money is. Reinforces the services/software weighting. |

### 3.3 Demand pools within ~15 miles

Biotech: Guardant Health (RWC, oncology volumes +34% YoY ⚠️), Revolution Medicines (RWC), Redwood LIFE campus (1M+ SF) ✅, San Carlos cluster (2.5M SF, Alexandria Center 556K SF) ⚠️. Hardware/robotics: Zoox (Foster City), Skydio (San Mateo) ✅, plus a long tail of startups (directional counts only ❓). Product design: StudioRed (Palo Alto, 4,000+ projects) ⚠️, IDEO, Nonobject. Architecture: AIA San Mateo County chapter and member firms ✅ (count ❓). Dental: local labs exist (FR Dental Laboratory, RWC ⚠️) — but see §5.4 for why dental is a *partner* channel, not a lead product. Stanford's Product Realization Lab is students-only ⚠️ — a talent/deal-flow pool, not a competitor.

**Target customer, precisely:** the engineer or lab manager within 20 minutes of Redwood City who needs 1–20 parts *this week*, in real materials (PETG/ASA/PA-CF/TPU), invoiced to a company card, with zero procurement friction — the job that is too small for ProtoCafe's quote cycle, too urgent for JLC3DP's boat-or-air timeline, and beyond the library's free PLA queue.

---

## 4. Strategy — Three Layers, One Flywheel

**Positioning:** *the fastest prototyping loop on the mid-Peninsula, run by software.*

| Layer | What it is | Why we win | Revenue character |
|---|---|---|---|
| **L1 — Rapid-response parts** | Same-day/next-day FDM (later resin) service, instant web quoting, pickup or courier | Geography + speed + zero-friction ordering; competitors are either far, slow, or free-but-capped | Taxable fabrication sales (9.875% ✅), $75–400/printer/mo base ✅ |
| **L2 — Engineering-adjacent labor** | DFM advice, print-optimization, iteration management, small-batch production management, automation consulting for other shops | Founder's hourly value is in judgment + automation, not plate-swapping; verified rate band $40–125/hr ⚠️ | Service labor, higher margin; mostly *not* taxable when no TPP transfers, but bundled design-and-production contracts are fully taxable ✅ (Reg. 1501.1) |
| **L3 — Software/data layer** | Internal first: instant quoting, order→print orchestration, camera/failure analytics, CRM automation. External only on proven traction | Founder's core skill; fleet-SaaS market has real documented pain (Bambu lock-in ✅, weak failure detection ✅) but **low willingness-to-pay — segment leader ≈ $350k ARR bootstrapped** ✅. So: build for self, sell only if pulled | $0 in the base case; option value (§8) |

**The flywheel:** L1 generates demand data and cash → L3 automation cuts L1's labor cost and improves turnaround → faster turnaround wins more L1/L2 work → the L3 tooling becomes demonstrably valuable → optionality on productizing L3 or licensing it.

**What we explicitly do NOT do** (each backed by a verified finding): consumer PLA trinkets on marketplaces (free local alternative ✅ + clone-driven price wars); load-bearing/outdoor functional products (liability, materials engineering, no insurance in place); dental as a cold entrant ($1–5/arch commodity economics ✅); venture-scale fleet-SaaS fantasies ($350k-ARR leader ✅); leased industrial space before Gate B (~$20–24k/yr minimum ✅ would consume 2× the entire capitalization).

---

## 5. Operations Plan

### 5.1 Phase-one footprint (home-based, months 0–9)

- **Fleet:** 3× Bambu P1S-class FDM (~$550 street ✅, ~$800 all-in each with AMS share/spares/plates) + 1 filament-drying station + enclosure ventilation. One printer is the redundancy/overflow unit. Optional month-4 addition: 1 resin printer (~$400–600) only if a specific customer demand appears.
- **Zoning compliance ⚠️ (verify §2.50 text with Planning before launch):** business confined to <25% of dwelling floor area; no exterior evidence (noise, odor, signage); no non-resident employees; no walk-in customer traffic (courier/pickup at door only); watch the storage-of-materials condition — keep filament inventory lean (4–6 weeks, ~$300–500) partly *because the ordinance may require it*. A 3–4 printer spare-room cell plausibly complies; a 10–30 printer farm plausibly does not — which is one of the two reasons Gate B (§9) triggers a space decision.
- **Electricity:** ~0.12 kWh/printer-hr × **$0.38–0.40/kWh blended (E-TOU-C + Peninsula Clean Energy)** ✅⚠️ ≈ $0.046–0.048/printer-hr. Even at PG&E's nation-leading rates, power is ~2% of job cost — measure it (smart plugs, also the audit-proof tax deduction) but don't optimize it.
- **Software stack (founder-built):** instant-quote web portal (upload STL → price in seconds — Supabase/Vercel, founder's stack); job queue + printer orchestration (Bambu ecosystem now, with the documented lock-in risk ✅ noted in §10; open-source Klipper/Moonraker path ⚠️ kept as the exit ramp); camera monitoring + failure alerting; automated invoicing with sales-tax line.

### 5.2 Capacity and utilization (anchored to verified benchmarks)

Theoretical: 3 printers × 720 hr/mo = 2,160 machine-hours. Realistic well-run band: 50–70% with lights-out discipline; manual-only ~25–30% ⚠️. **Plan at 30–40%** for a part-time solo operator: ~650–850 good machine-hours/month by month 6. First-pass-yield target ≥95%; every job >8 print-hours gets segmented or first-layer-checked (failure hazard compounds ~0.5%/hr ⚠️ — a 50-hour print fails ~22% of the time).

### 5.3 Service workflow (the actual product)

Quote (instant, automated) → accept + card-on-file → auto-queue → print (lights-out where trusted) → QC photo sent to customer → same-day pickup window or courier. Target: **quote-to-part under 8 business hours** for jobs ≤200g in stocked materials. That number *is* the marketing.

### 5.4 Deliberate non-operations

Dental models only as white-label overflow for an existing lab that brings the relationships (outsource benchmark $5/arch, in-house $1–3 ✅ — no margin for a cold entrant). No employee before ~$8k/mo revenue: Redwood City minimum wage $18.65/hr ✅ + ~3.5% payroll taxes on the first $7k + workers' comp makes the first hire a real threshold, and the automation layer exists precisely to defer it.

---

## 6. The Accounting Engine

*(The discipline that separates an owner from a hobbyist with revenue.)*

### 6.1 Machine-hour costing (Redwood City inputs)

| Cost element | $/yr per printer | $/machine-hr @ 3,000 hr/yr | Basis |
|---|---|---|---|
| Depreciation (economic) | $267 | $0.089 | $800 all-in ÷ 3-yr life ✅ (obsolescence-driven; ~2.5–3 yr product cycles) |
| Maintenance & consumables | $230 | $0.077 | Nozzles, plates, belts, repair reserve ⚠️ |
| Electricity | $137 | $0.046 | 0.12 kWh/hr × $0.38/kWh ✅⚠️ (vs ~$0.016 at national-average rates — the CA penalty is real but small) |
| Insurance share (BOP + product liability) | $300 | $0.100 | ~$900/yr policy ÷ 3 printers ❓ (quote before launch) |
| Software/hosting share | $80 | $0.027 | Self-built on ~$20/mo hosting |
| **Fully absorbed machine cost** | **~$1,014** | **≈ $0.34/hr** | Excludes labor and materials |

Variable-only floor (electricity + wear): **≈ $0.12/hr** — the accept/reject threshold for filler work. Quote against the absorbed rate **at practical capacity**, never against current low volume (the death-spiral rule).

### 6.2 Job standard cost (reference: 140g PETG functional part, 5.5 print-hr, B2B)

| Line | Calc | $ |
|---|---|---|
| Material | 140g × 1.08 waste × $0.025/g (PETG, resale-cert purchased ✅) | 3.78 |
| Machine | 5.5 hr × $0.34 | 1.87 |
| Direct labor | 22 min honest touch time (setup amortized, removal, QC, pack) × $0.50/min ($30/hr loaded) | 11.00 |
| Spoilage allowance | 4% standard on material+machine | 0.24 |
| **Standard cost** | | **16.89** |
| B2B price (same-day premium) | | **$39–49 + 9.875% sales tax** |

Labor is ~65% of cost — **the entire margin battle is labor minutes, which is why the software layer is the business**. Every automation that cuts touch time 5 min/job adds ~$2.50/job of margin at zero marginal cost.

### 6.3 Contribution margin per machine-hour — the master metric

Rank every job and product line by CM/machine-hour; the weekly floor is **$3.00/hr for external work** (below that, the queue slot goes to internal tooling, R&D, or stays idle at the $0.12 variable floor). Verified community norms of $1–5/machine-hr ✅ make $3+ an above-median but defensible target *given the same-day positioning*.

### 6.4 Two P&Ls, from day one

1. **Tax P&L:** federal — 100% bonus depreciation (permanent, OBBBA ✅) or de minimis expensing (<$2,500/item ✅) writes the fleet off immediately; **California adds it back** (no bonus conformity ✅), with CA §179 capped at $25k and usable only against business income ✅ — in a startup-loss year the CA deduction defers (≈$2,144 first-year MACRS on $15k vs $15k federal ✅).
2. **Management P&L:** printers depreciated over **30 months of economic life**, a funded replacement reserve (~3%/mo of fleet value), and the founder's imputed wage as a real cost line. This is the P&L that decides the gates in §9. The tax P&L will look ~20–30 points more profitable than reality after year one — pricing or distributing against it is the classic self-deception this section exists to prevent.

### 6.5 California/Redwood City compliance stack (all ✅ unless noted)

| Item | Amount / rule | Timing |
|---|---|---|
| CA LLC minimum franchise tax | **$800/yr, no first-year waiver** (expired for post-2023 LLCs) | FTB 3522, 15th day of 4th month |
| LLC gross-receipts fee | $0 below $250k CA income ($900 at $250k+) | FTB 3536 if applicable |
| Seller's permit + sales tax | **All fabrication revenue taxable at 9.875%** (Pub 108; itemized or bundled; even on customer-supplied material). Design-and-production contracts fully taxable incl. design line (Reg. 1501.1) | Register before first sale; CDTFA filings |
| Filament purchases | Tax-free with resale certificate | At vendor setup |
| Equipment purchases | Manufacturing partial exemption (RTC 6377.1, through 6/30/2030): state portion cut 3.9375% → ~5.9375% effective on qualifying printers (CDTFA-230-M) — ⚠️ "primarily engaged in manufacturing" test is fact-specific | At purchase |
| Redwood City business license | Measure BB: $90 base + per-employee tier; full rates from 7/1/2026; solo ≈ $90–150/yr (exact category rate ❓) | Before operating |
| Home occupation permit | Required; §2.50 conditions ⚠️ | Before operating |
| SMC business personal property | ~1.1–1.25%/yr on assessed equipment; possible exemption ≤$5,000 assessed ⚠️ | 571-L only if asked / ≥$100k |
| CA income tax on profit | 8–9.3% marginal at plan scale; **no QBI deduction in CA** | Quarterly estimates |
| Entity | Single-member LLC, disregarded; S-corp not until ~$90–110k sustained profit ⚠️ | Formation, month 0 |

---

## 7. Financial Projections

*(Three scenarios; all revenue anchors from verified operator data — $75–400/printer/mo base, ~$1,200 top-decile ✅; design labor $40–125/hr ⚠️. Sales tax excluded from revenue below — it's collected in trust, never counted as income: the first discipline of a California fabricator.)*

### 7.1 Startup budget — the $10,000

| Use | $ |
|---|---|
| 3× FDM printer, all-in (incl. AMS share, spares, plates; partial mfg exemption applied) | 2,400 |
| Dryer, ventilation, racking, smart plugs, camera | 500 |
| Filament starting inventory (lean, per zoning) | 400 |
| LLC formation + agent + permits + business license | 350 |
| Year-1 franchise tax reserve ($800) | 800 |
| Insurance (BOP + product liability, year 1) ❓ quote | 900 |
| Hosting, domain, tooling subscriptions (yr 1) | 300 |
| Marketing: direct outreach materials, sample kits for 30 target firms, courier trials | 650 |
| Working capital + contingency | 3,700 |
| **Total** | **10,000** |

Note what is *absent*: rent (home-based), software licenses (founder-built), employees. ~37% of capital is buffer — the working-capital starvation pattern kills more micro-fabricators than any cost line ⚠️.

### 7.2 Year-1 monthly trajectory — base case

| Month | Printing rev | Labor rev (hrs × $75) | Total rev | COGS+var | Fixed | Op. profit |
|---|---|---|---|---|---|---|
| 1–2 (build) | 0 | 0 | 0 | 0 | 290 | (290) |
| 3 | 250 | 300 (4) | 550 | 190 | 290 | 70 |
| 4 — **Gate A** | 450 | 450 (6) | 900 | 300 | 290 | 310 |
| 6 | 800 | 600 (8) | 1,400 | 450 | 290 | 660 |
| 9 — **Gate B** | 1,100 | 750 (10) | 1,850 | 590 | 290 | 970 |
| 12 | 1,300 | 800 (11) | 2,100 | 660 | 290 | 1,150 |

Year-1 totals (base): **revenue ≈ $14,500; operating profit ≈ $6,200** before founder comp; ending fleet 4 printers (one added from cash flow ~month 7). Printing revenue at month 12 = $325/printer/mo across 4 printers — the *middle* of the verified $75–400 band, not the top.

### 7.3 Scenarios (year-1 revenue / op. profit / month-12 run-rate)

| | Downside | Base | Upside |
|---|---|---|---|
| Per-printer gross (mo. 12) | $120 | $325 | $700 |
| Design-labor hrs/mo (mo. 12) | 3 | 11 | 20 |
| Year-1 revenue | $5,200 | $14,500 | $31,000 |
| Year-1 op. profit | ($900) | $6,200 | $16,800 |
| Month-12 run-rate | $660/mo | $2,100/mo | $5,000/mo |
| Gate outcome | **Exit/pivot at Gate A or B** (recover ~$4–6k: printer resale ~40–50% ⚠️ + unspent buffer) | Gate B: microloan decision | Gate B early; space decision |

### 7.4 Year 2–3 (base case, gates passed)

Month 15: SBA microloan **$18,000 at ~11%/5yr ≈ $391/mo** ✅ funds 6 more printers + a space decision (Maker Nexus-style membership $75–160/mo ✅ or shared sublet ❓ — full industrial lease still unjustified below ~$8k/mo revenue). Year-2 revenue $38–55k; year-3 $60–90k with either (a) a B2B anchor account, or (b) first external software revenue. DSCR on the microloan at month-15 run-rate ≈ 2.5–3× *after* a $2,000/mo founder draw — sized so the loan is never the risk. Beyond this, projections are scenario planning, not forecasts, and are re-derived at each gate from actuals.

---

## 8. Thinking Like an Owner — the Value-Creation Frame

### 8.1 Economic profit, not accounting profit

Base-case month-12: $1,150/mo operating profit on ~40 founder-hours/month of residual ops+sales ≈ **$29/hr earned** — real, but below the founder's $70–100/hr market rate. Add a 10% capital charge on $10k (~$83/mo) and year-one **economic profit is negative — by design and stated honestly**. What the owner actually buys in year one, for ~$10k and capped hours:

1. **Information** (the most valuable output): verified answers about which niche, which customers, and which price points survive contact with the Peninsula market — bought for less than one quarter of a data-science salary differential;
2. **Reusable IP**: the quoting/orchestration/analytics stack, portfolio-grade and career-adjacent (AI + manufacturing operations) even if the venture folds;
3. **A B2B relationship set** in the exact cluster (hardware, biotech, robotics) the founder's career serves;
4. **Optionality with a capped downside**: worst case ≈ $4–6k net cost; upside paths in §8.3.

The wealth event, if it comes, is **not year-one print margin** — it is what compounding the flywheel makes ownable: a niche service business earning real economic profit at ~10 printers with ≤10 founder-hours/week, a software product with external users, or both.

### 8.2 ROI arithmetic the founder should hold himself to

- **Return on capital:** base case year-1 cash-on-cash ≈ 62% on $10k before founder comp — meaningless alone (it's mostly the founder's unpaid wage recycled); which is why the binding metric is:
- **Implied founder wage** = (op. profit − 10% capital charge) ÷ founder hours. Track monthly. Gate D (§9) fires when it crosses $70/hr sustained — that is the moment this stops being a project and becomes a business.
- **CM/machine-hour ≥ $3.00** external floor; **first-pass yield ≥ 95%**; **revenue per founder-hour** trending up every quarter (the automation dividend, measured).

### 8.3 Wealth & exit paths (in descending probability)

1. **Cash-flowing niche cell** (most likely good outcome): 8–12 printers, 2–3 anchor B2B accounts, $8–15k/mo, mostly automated — a durable ~$50–100k/yr economic-profit asset, sellable at 2–3× SDE to a strategic local buyer (a ProtoCafe-class bureau or a lab-services firm) ❓ (multiple is market lore, not verified).
2. **Software spin-out**: if the internal stack solves the documented Bambu-era orchestration pain better than the $350k-ARR incumbent class ✅, license it to other small farms — priced as boring B2B SaaS, not venture-scale (the verified willingness-to-pay is $4–40/printer/mo ✅).
3. **Acqui-outcome / career capital**: the AI-manufacturing operator profile is rare; the venture is a standing audition for AM-software roles (Backflip $30M seed, Tripo ~$397M raised ✅ — the *hiring* market in AI×3D is better funded than the *selling* market).
4. **Wind-down** (planned-for, not feared): capital recovery ~$4–6k, IP and relationships retained.

### 8.4 What "innovation" means here, concretely

Not inventing a printer. The innovation surface with real, verified pull: **failure-detection analytics** (documented dissatisfaction with built-in spaghetti detection ✅; consumer WTP low, but as an *internal* yield weapon it converts directly to margin — each failure-point ≈ 1.5–2 points of lost good hours ⚠️); **instant-quote UX** for the small-batch B2B buyer (the friction ProtoCafe-class incumbents leave on the table); **demand analytics** — using the order stream to find which product/customer niches clear the CM/hr floor, i.e., the founder's data-science instinct applied to his own P&L.

---

## 9. Milestone Gates & Capitalization Plan

**The rule that governs everything: demand evidence precedes capital deployment — every tranche, every time.**

| Gate | When | Test (management P&L) | Pass → | Fail → |
|---|---|---|---|---|
| **A — signal** | Month 4 | ≥10 paying B2B jobs; ≥3 repeat customers; CM/machine-hr ≥ $3 | Continue; add printer 4 from cash flow | Pivot to L2/L3-only (design+software services, near-zero COGS) or wind down with ~$5–6k recovered |
| **B — scale** | Months 9–12 | 3 consecutive months ≥$2,000 revenue at ≥40% CM; backlog ≥5 days; yield ≥95% | **SBA microloan $15–25k** ✅ (8–13%, nonprofit intermediaries; avg loan ~$13–16k — squarely our size); 6+ printers; space decision (membership/sublet first) | Stay at 4 printers; the business is a stable side asset — that is a legitimate steady state, not a failure |
| **C — software** | Opportunistic | ≥3 external operators actively using the tooling unpaid, asking to pay | Productize; consider **SAFE $50–150k** at a modest cap for 12 months of focused build ❓ (terms market-dependent) | Keep internal; it's still earning its keep as margin |
| **D — commitment** | Any time | Implied founder wage ≥ $70/hr for 2 consecutive quarters | Full-time decision, with the MS as the credential backstop | Keep the portfolio posture |

**What investor capital is FOR / NOT FOR (the owner's covenant with himself):**
- **Never** for speculative print capacity — printers are ~$600 modular increments a healthy business buys from cash flow; equity is the most expensive money that exists and buying depreciating commodity hardware with it is value destruction ✅ (collateral/resale value ~40–50% in 2 years ⚠️).
- **Debt (microloan)** for capacity *only* against Gate-B demonstrated demand — DSCR ≥1.5 after a market founder wage, stress-tested at the low end of the verified CM band.
- **Equity (SAFE)** only for L3 software with external traction (Gate C) or a contracted-demand expansion that outruns self-funding — the two cases where speed genuinely buys something.
- Founder skin stays senior: the $10k is spent before any external dollar; household runway stays independent of the business throughout year one.

---

## 10. Risk Register

| Risk | Verified basis | Mitigation |
|---|---|---|
| **Demand shortfall** (the #1 killer) | Utilization/queue-starvation is the binding constraint industry-wide ✅; even a 70-printer operator publicly framed his farm as needing rescue in 2026 ⚠️ | Gates; capacity trails demand; 37% of capital held as buffer; outreach starts before the printers arrive |
| Bambu ecosystem lock-in / vendor risk | Authorization-control firmware broke third-party tooling (Jan 2025) ✅; Farm Manager EULA reserves commercial fees ✅; Stratasys v. Bambu US litigation active ⚠️ | Keep Klipper/Moonraker open-source exit ramp scoped ⚠️; no lifetime software licenses purchased; fleet standardized but portable |
| Price ceiling from ship-in networks | JLC3DP from $0.30/part ✅; bureau band $8–40 per 100g part ⚠️ | Never compete on non-urgent commodity work; the product is *hours-to-part*, not $/gram |
| Zoning / home-occupation limits | §2.50 conditions ⚠️ (storage, exterior evidence, <25% floor) | Verify ordinance text pre-launch; lean inventory; quiet enclosed FDM only; Gate-B space decision before the fleet outgrows the room |
| CA tax drag compresses net margin | $800 floor ✅ + 9.875% on all fabrication ✅ + no QBI ✅ + no bonus conformity ✅ | Priced into every quote (§6); quarterly estimates; CPA from year one |
| Founder time / MS collision | Self-evident | ≤10 hr/wk ops budget enforced by automation; the constraint is a feature |
| Product liability | Tiles-as-interior-finish flame-spread issues, functional outdoor parts ⚠️ | Prototype/fixture/enclosure work only; no load-bearing, no outdoor-functional, no medical-device output; product liability cover before first functional part ❓ quote |
| Insurance on home-based operation | Homeowner's/renter's policies typically exclude business equipment/liability ❓ | BOP quote in month 0 — unresolved insurance is a launch blocker, not a TODO |
| Key-person fragility | One operator = one point of failure | Automation + documented runbooks; capped scale until Gate D |
| Obsolescence | ~2.5–3-yr printer product cycles ✅ | 30-month economic depreciation + funded replacement reserve (§6.4); loan term ≤ asset life |

---

## 11. Viability Verdict

**Is small-scale additive manufacturing viable as a business in 2026?** As a *hardware-utilization* business — buying printers and selling their hours — **no**: capacity is in structural oversupply (≈1M entry-level printers shipped in Q1 2025 alone ⚠️), free public capacity exists in every San Mateo County library ✅, China-based bureaus price commodity parts near zero ✅, and verified operator economics ($75–400/printer/mo ✅) cannot carry Bay Area costs, let alone a Bay Area founder's opportunity cost.

As a **services-and-software business that happens to own printers** — **yes, conditionally**: the market's value is verifiably migrating to exactly that layer (48% services, +15.5% ✅), a real geographic/speed gap exists on the mid-Peninsula ⚠️, the local demand cluster is dense and cash-rich ✅, and this founder's specific, unusual skill set (ML + full-stack + automation + data discipline) attacks the two costs that actually matter — labor minutes and demand acquisition — rather than the machine costs that don't.

**For this founder, the conditions of success are:** (1) the automation discipline that keeps founder-hours ≤10/week; (2) the accounting discipline of §6 — two P&Ls, CM/machine-hour floor, sales tax in trust, replacement reserve; (3) the capital discipline of §9 — demand before dollars, debt before equity, equity only for software; and (4) the honesty of §8 — measuring economic profit against a $70–100/hr alternative wage and letting the gates, not sunk cost or enthusiasm, decide what happens at months 4, 9, and 15. Run that way, the venture risks ~$4–6k net worst-case against a realistic path to a durable, mostly-automated $50–100k/yr economic-profit asset with genuine software-upside optionality — an asymmetry an accountant can sign.

---

## Appendix A — Key Verified Numbers (July 2026)

| Figure | Value | Source class |
|---|---|---|
| Global AM market 2025 / growth | $24.2B / +10.9% | Wohlers Report 2026 (primary PR) ✅ |
| Services share / growth | 48% ($11.7B) / +15.5% vs systems +3.6% | Wohlers ✅ |
| Peninsula industrial rent | ~$1.98–2.48/SF/mo NNN; min units ~800 SF | Kidder Mathews + aggregators ⚠️✅ |
| Maker memberships | Maker Nexus $75–160/mo; Hacker Dojo ~$112.50/mo | Primary org pages ✅⚠️ |
| PG&E B-1 commercial | ~$0.41–0.42/kWh; residential TOU blended ~$0.38–0.40; PCE −10% on generation | Tariff sheets / CCA comparisons ✅⚠️ |
| Operator revenue per printer | $75–400/mo base; ~$1,200 top-decile (≥$2 profit/print-hr target) | Operator interviews/forums ✅ |
| Bureau price, ~100g FDM part | $8–40; JLC3DP "from $0.30" | Marketplace-observed ⚠️✅ |
| Design/eng labor rates | CAD $16–77/hr; mech-eng consult $68–89/hr avg; Fiverr band $40–125/hr | Marketplace ⚠️ |
| Fleet-SaaS market | Leader ~$350k ARR bootstrapped; pricing $4–40/printer/mo; Bambu Farm Manager free | Company profile + vendor pricing ✅ |
| SBA microloan | Up to $50k; avg ~$13–16k; 8–13% | SBA primary ✅ |
| CA LLC tax / CA §179 / bonus / QBI | $800 (no waiver) / $25k cap / no conformity / none | FTB primary ✅ |
| Redwood City sales tax / min wage / license | 9.875% / $18.65 / $90 base (Measure BB, full 7/1/2026) | CDTFA-concordant + city ✅⚠️ |
| Mfg partial sales-tax exemption | 3.9375% off state portion, through 6/30/2030 (CDTFA-230-M) | CDTFA primary ✅ |
| Federal 2026: bonus / §179 / de minimis | 100% permanent / $2.56M / $2,500-per-item | Rev. Proc. 2025-32, OBBBA ✅ |

## Appendix B — Claims That Failed Adversarial Verification (do not use)

- "$10k/month from 4–6 well-utilized printers" (vendor-derived) — **refuted**; top-decile at best.
- "B2B prototyping bills $100+/design-hour as a standard rate" — **refuted** as a general anchor; verified band $40–125/hr with medians far lower.
- "Queue software saves 10–20 hrs/week and doubles capacity" (vendor survey) — **refuted** as an independent fact.
- "Bay Area turnaround bar is under one day, which entrants must beat" — **refuted**; same-day is a differentiator, not table stakes.
- "Fleet standardization is a precondition for automation ROI" — **failed verification** as stated.

## Appendix C — Pre-Launch Checklist (month 0)

1. Call Redwood City Planning (650-780-7234): confirm home-occupation §2.50 text, storage and noise conditions; obtain permit.
2. Form single-member LLC; calendar FTB 3522 ($800) and quarterly estimates; engage CPA.
3. CDTFA seller's permit; resale certificate to filament vendors; CDTFA-230-M partial-exemption certificate for printer purchases.
4. Redwood City business license (Measure BB schedule — confirm category rate).
5. Insurance quotes: BOP + product liability for a home-based fabrication business — **launch blocker until bound**.
6. Build the quote portal and instrumentation *before* buying printer #2 and #3 — software first is the whole thesis.
7. Assemble the 30-firm outreach list (Redwood LIFE tenants, San Carlos biotech, Skydio/Zoox-adjacent suppliers, StudioRed-class design firms, AIA-SMC members) and book meetings for delivery week.
