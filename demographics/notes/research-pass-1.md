# Research Pass 1 — Framework, Toolkit & the Zeihan Audit

*Plan addendum for "The Shape of People to Come." Pass 1 of 2 (this pass = framework/theory/debate level; a later heavier pass builds the ten country portraits). Generated from a fan-out deep-research run: 5 search angles → 25 sources → 123 extracted claims → adversarial verification. The 25 formally verified claims all landed on the toolkit (RQ1); RQ2–RQ4 material below is search-triangulated from the same run's search + extraction phases and is marked accordingly.*

**Sourcing caveat that applies to the whole document.** The sandbox egress proxy 403-blocked direct fetches to un.org, ntaccounts.org, imf.org, oecd.org, science.org, dni.gov, nber.org and PMC. Every quote here was triangulated across ≥2 independent search indexes, but exact page numbers and verbatim placement should be re-checked against the primary PDF before anything goes into published prose. Citations that could not be fetched are marked *[search-verified]*.

---

## Corrections to the plan (load-bearing — read first)

Three planned instruments carry labels or formulas that don't match their canonical definitions. None is *wrong* as arithmetic; each is mis-named or mis-specified relative to the literature it invokes, which for a methodology-as-exhibit article is the thing to get right.

### C1. The "support ratio" is not the NTA support ratio — relabel it.

The article computes and calls "support ratio":
$$SR_{\text{plan}} = \frac{P_{20\text{–}64}}{P_{65+}}$$
The canonical **NTA economic support ratio** is profile-weighted — effective producers over effective consumers of *all* ages:
$$SR_{\text{NTA}} = \frac{\sum_a y_l(a)\,P(a)}{\sum_a c(a)\,P(a)}$$
where $y_l(a)$ is the labor-income age profile (embedding participation, unemployment, hours, experience) and $c(a)$ is the consumption profile, both conventionally normalized to mean labor income of ages 30–49 and reported per 100 effective consumers *[search-verified: UN DESA Population Division Technical Paper 2017/1, Mason, Lee, Abrigo & Lee; NTA Bulletin 9]*. The planned metric is not even the headcount analog of this — its denominator excludes children, so it is an **inverse old-age dependency ratio**, not a support ratio. Loichinger et al. (2014, *Demographic Research* 30:34) show the weighted and headcount versions diverge materially.

**Fix:** rename the shipped metric to **"headcount old-age support ratio"** (or "inverse OADR") in `§5`, the atlas hover, and the `sr` field's prose. Optionally ADOPT the weighted $SR_{\text{NTA}}$ as a companion instrument — see N1.

### C2. The prospective old-age threshold is an approximation, not the Sanderson–Scherbov definition.

The article uses $T = 65 + \max(0,\, e_{65} - 15)$ and labels the resulting ratio "prospective old-age dependency (POADR)." The **canonical POADR** (Sanderson & Scherbov, *Science* 329, 2010, "Remeasuring Aging") sets the old-age threshold at the age $x$ where remaining life expectancy *itself* equals 15, solved directly from the life table with **no anchor at 65**:
$$\text{find } x \text{ s.t. } e(x) = 15,\qquad POADR = \frac{P_{a > x}}{P_{20 < a \le x}}$$
The linear $e_{65}$-anchored formula diverges two ways: **(a)** because $e(x)$ declines by *less* than one year per year of age, reaching $e(x)=15$ requires *more* than $(e_{65}-15)$ years above 65 — so the true threshold is strictly **above** $65+(e_{65}-15)$, and the linear formula sits below it (counting slightly too many people as "old"); **(b)** the $\max(0,\cdot)$ clamp forbids sub-65 thresholds that the canonical definition *permits and documents* in high-mortality populations (sub-65 prospective old-age thresholds appear in parts of Central/South America). *[search-verified; verifiers confirmed both points mathematically.]*

**Fix — and this touches already-shipped code.** The site pipeline already builds a life-table $e(x)$ from WPP single-age mortality (`e_at_age()` in `build_demographics_data.py` computes $e_{65}$ the right way), so the canonical form is *feasible*: solve $e(x)=15$ by interpolation instead of the linear anchor. Recommended: implement the canonical threshold and keep the "POADR" name. If the linear form is kept for simplicity, relabel it **"$e_{65}$-anchored prospective threshold (approximation)"** with the caveat. Citation hygiene: cite S&S *Nature* 435 (2005) and *Demographic Research* 16(2) (2007) for prospective age, *Science* 329 (2010) for POADR specifically.

### C3. The momentum proxy's labeling is correct — keep it.

The plan computes $\text{built-in growth} = P_{2050}^{\text{medium}} / P_{2025}$ and explicitly disclaims that this is *not* Keyfitz momentum. That disclaimer is right and necessary. Keyfitz (1971) momentum is the instant-replacement counterfactual
$$M = \frac{b\,e_0}{r\,\mu}\cdot\frac{R_0-1}{R_0}$$
(pre-drop birth rate $b$, growth rate $r$, life expectancy $e_0$, net reproduction $R_0$; $\mu$ = post-drop mean age of childbearing) — the ultimate stationary population if fertility dropped instantly to replacement *today*. The proxy instead embeds the projected fertility/mortality/migration *paths*, so it measures something different (and more policy-relevant for this article). **Keep the proxy and its label; MENTION Keyfitz in one paragraph** — see N4 for why the sign-flip is worth a sentence.

---

## §3 Capital structure by age

**Lifecycle deficit — ADOPT unchanged.** $\mathrm{LCD}(a) = c(a) - y_l(a)$ matches the canonical NTA definition exactly (consumption minus labor income at each age; the lowercase per-capita form is the standard Lee–Mason variant, = aggregate ÷ $P(a)$). Cite the NTA methodology page, the **UN DESA NTA Manual (2013)**, and **Lee & Mason, *Population Aging and the Generational Economy* (2011)**. *[search-verified; 3-0 confirmed.]* No change needed to the shipped Figure 3 or its framing.

**The OLG "capital-cheap → capital-scarce" aside — ADOPT, but present as contested.** The formal anchor is **Abel (2003, *Econometrica* 71:551–578)**: an OLG model where a baby boom (a "high realization of a random birth rate") raises saving/investment and thus the endogenous price of capital, which then mean-reverts — a *rational-expectations* version of the asset-meltdown story where the price decline is anticipated, not a surprise crash. Notably, Abel shows PAYG Social Security changes the *quantity* dynamics of capital but **not the long-run price of capital** — a clean comparative static to note. *[search-verified.]* The article's aside should cite Abel as the rigorous benchmark and immediately flag the empirical pushback (see §9/L2): Poterba finds retirees decumulate slowly, so the "capital-scarce" leg is weaker in data than in the toy model.

---

## §4 Macro consequences

**First demographic dividend — ADOPT the identity form.** Present it as the accounting identity, not a causal estimate:
$$\frac{Y}{N} = \frac{Y}{L}\cdot\frac{L}{N}\ \Rightarrow\ g\!\left(\tfrac{Y}{N}\right) = g\!\left(\tfrac{Y}{L}\right) + \frac{d}{dt}\ln SR$$
The first dividend exists exactly when the (economic) support ratio is rising; its magnitude is $\tfrac{d}{dt}\ln SR$, one-to-one with income per effective consumer holding work effort/returns/assets constant. Cite **UN TP 2017/1** as the canonical global implementation. *[search-verified; 3-0.]* The phase is transitory but long — **Lee & Mason (2006, IMF *F&D* 43(3))** put the favorable window at "five decades or more" (Europe ~1962–2000; Asia ~1975–2033) before it turns negative — a citable timescale for the pyramid→urn arc. *[search-verified; 3-0.]*

**Second dividend is institution-conditional — this is a framing constraint, not a footnote.** The second dividend arises *"to the extent that"* anticipated aging induces capital accumulation; societies funding old age through public or familial **transfers** get a *diminished* one (Mason 2005 originally said "no"; the authors later softened to "diminished" — use the graded form). It runs through two channels: asset/capital deepening **and** higher human-capital investment per child under low fertility, which **can more than offset** slower workforce growth (Lee & Mason 2010, *EJP*, quantity-quality OLG). *[search-verified; 3-0.]* Unlike the first dividend it is *not* intrinsically transitory. **Implication for the article:** the capital-shift indicator and the OLG aside must be presented as *regime-dependent*, and this is the single strongest internal check on demographic determinism — it belongs in both §4 and §9.

**Savings/current-account channel — ADOPT as the empirical anchor for the capital-shift logic.** **Higgins (1998, *International Economic Review* 39:343–369; NY Fed Staff Report 34)** is the seminal quantified result: age structure moves savings and investment *differently*, so demography is a determinant of the current account, with an estimated demographic effect on the CA balance **exceeding 6% of GDP** over three decades for a number of countries. The "center of gravity" for investment demand (youth share, via labor-force growth) sits earlier than for savings supply (mature-adult share, via retirement saving) — so a country's transition stage predicts capital-importer (young) vs. capital-exporter (mature) status. This directly underwrites the article's capital-shift indicator $[P_{35\text{–}64}/P_{65+}]_{2040} - [\cdot]_{2025}$. Higgins enters the full age distribution via a cubic-polynomial restriction on age-share coefficients — **replicable from WPP age shares + World Bank CA/savings data.** *[search-verified.]*

**IMF External Balance Assessment (EBA) — MENTION as the institutional current-account-demography model (new material, N2).** The EBA CA regression's "demographic block" uses three static regressors, all as deviations from world average — population growth (proxy for youth share), old-age dependency, and prime-aged-saver share of the working-age population — plus a dynamic longevity term (a current prime-aged saver's life expectancy interacted with OAD 20 years ahead, capturing the nonlinearity between longevity and the CA). **All computable from WPP outputs**, and the demographic block *survived* the 2022 robustness-based methodology pruning — i.e. the IMF treats demographic determinants of external balances as statistically robust. Cite the 2022/2023 EBA methodology paper. *[search-verified.]*

---

## §5 Instrument panel — verdicts

| Instrument | Verdict | Action |
|---|---|---|
| Lifecycle deficit $c(a)-y_l(a)$ | **ADOPT** | keep as-is (§3) |
| Headcount old-age support ratio $P_{20\text{–}64}/P_{65+}$ | **ADOPT + RELABEL** | rename (C1); it's an inverse OADR |
| Weighted NTA support ratio $\frac{\sum y_l(a)P(a)}{\sum c(a)P(a)}$ | **ADOPT (companion)** | borrowed profiles, disclose (N1) |
| First dividend $= \tfrac{d}{dt}\ln SR$ | **ADOPT** | present as identity, cite TP 2017/1 |
| Prospective OADR | **REFORMULATE or RELABEL** | solve $e(x)=15$ (C2) |
| Workforce replacement $P_{20\text{–}24}/P_{60\text{–}64}$ | **ADOPT** | keep (plan is fine) |
| Built-in growth $P_{2050}/P_{2025}$ | **ADOPT** | keep label; MENTION Keyfitz (C3, N4) |
| Capital-shift $\Delta[P_{35\text{–}64}/P_{65+}]$ | **ADOPT** | anchor to Higgins 1998 (§4) |
| Keyfitz momentum (true) | **MENTION / optional ADOPT** | see N4 |
| Lee–Carter mortality forecasting | **SKIP** | WPP already supplies projected mortality; re-forecasting is redundant and out-of-scope |
| Generational accounting / fiscal gap (Auerbach–Kotlikoff) | **SKIP for the index, MENTION in §4** | needs age-profiles of taxes & benefits per country = microdata/fiscal data beyond WPP+WB; cite as the tool that prices the fiscal stakes, don't compute |
| Cohort-component projection + probabilistic (UN) | **MENTION** | the article *consumes* WPP's medium variant; note the UN's own probabilistic bands exist and that end-of-century figures are unstable (§9/L3) |

**Feasibility ruling on the weighted ESR (N1).** It *is* computable within the WPP-only constraint but **only with borrowed/stylized age profiles** — full NTA replication needs survey microdata the pipeline can't derive. Precedent: **Mason (2005)** computed the support ratio and first dividend for *every* country with WPP age-sex data using a single fixed weight profile (Taiwan 1998). The UN's 2017 global run needed *measured* NTA profiles for 60 countries + model-imputed for 106 more (166 total; second-dividend estimates for only 111) — proof the profiles are imported products, not WPP derivations. **Action:** if adopting, use one global (or a few regional) stylized profiles, disclose the borrowed-profile assumption prominently, and date-stamp the 60/106/166/111 counts as 2017-era (Mason et al. 2022, *PDR*, expands to 186 economies). Log the sensitivity of cross-country rankings to profile choice as an open question.

---

## §6 Composite score

**Prospective measures reorder the map — include at least one.** Prospective (remaining-years-based) measures show a systematically *slower* pace of aging than fixed-chronological-age measures across essentially all countries in UN-projection-based forecasts — **but conditional on rising life expectancy.** Where LE stagnates or falls (the standing example is Russia in the 1990s–2000s), prospective aging is *not* slower. *[search-verified; 2-1 vote — present as conditional, not universal.]* For a composite index built on fixed age-65 cutoffs this is the central caveat: two instruments that look redundant (conventional OADR and headcount support ratio) both hard-code 65, so the index inherits a single ageing convention. Keeping a genuine prospective instrument (C2's canonical POADR) in the panel is the cheapest hedge. OECD calibration point: OECD-average $e_{65}$ in 2024 is ~21.6y (women) / ~18.5y (men) — already 3.5–6.6y above the 15-year prospective threshold, and projected to rise a further ~4y by 2065 *[search-verified: OECD Pensions at a Glance 2025]*, so the fixed-65 vs. prospective gap is large and widening in exactly the rich aging countries the article foregrounds.

**No new normalization change recommended.** The winsorized-z / clamp-±3 / weighted-simplex design is standard and defensible; the substantive risk is *component definition* (C1/C2), not aggregation.

---

## §9 Limitations — the steelman against the article

This is the section the research most enriches. Five citable counterweights, strongest first:

**L1. Aging has not lowered growth in the cross-section — the automation offset.** **Acemoglu & Restrepo (2017, AER P&P 107(5):174–79; full mechanism in NBER WP 24421 / *ReStud* 2022)**: across countries, *"there is no such negative relationship in the data — if anything, countries experiencing more rapid aging have grown more"* (1990–2015), attributed to faster automation adoption where middle-aged labor is scarcer. Demographic factors alone explain *close to half* of cross-country variation in robot adoption. This is the strongest published counter-evidence to any mechanical aging→decline chain, and it targets *exactly* the two channels the article's OLG aside and capital-shift indicator formalize (older-worker productivity; excess savings / secular stagnation). Their aging regressor — $\Delta[P_{50+}/P_{20\text{–}49}]$ — is WPP-computable and could even be displayed; the robot-adoption data (IFR, 49 countries) is out-of-constraint, so cite-but-don't-recompute the offset. *[search-verified.]*

**L2. The asset-meltdown premise is weak in data.** **Poterba (2001, *REStat*; 2004, NBER WP 10851)**: no robust relationship between age structure and real returns on bills, bonds, or stocks in US/Canada/UK time series; age-wealth profiles *"decline much more gradually"* in retirement than they rise in the 30s–40s (retirees don't dump assets); and projected asset demand *does not fall* 2020–2050. Verdict in the literature: *"modest support at best"* for meltdown. Pair with Abel (2003) from §3 — the theory permits a mean-reverting price dip, the data barely find it. Directly qualifies the article's capital-shift and "capital scarcity" framing. *[search-verified.]*

**L3. The UN's own track record: totals reliable, age-structure less so.** Historical UN world-population projections were highly accurate — most vintages within 1–2%, none off by >5% at 30–40-year horizons (Keilman's evaluations, via Our World in Data). **But** global accuracy masks offsetting errors: in Europe the UN *systematically overestimated future children and underestimated the elderly* — i.e., the age-structure components a demographic-strategic index depends on have historically been *less* reliable than headline totals. And long horizons are unstable: the 2019 revision projected 10.9bn by 2100; the 2022 revision, 10.4bn peaking mid-2080s — a ~0.5bn shift in three years. *[search-verified.]* The article already uses the medium variant honestly; this sharpens the §9 language: trust the 2050 working-age counts (already born), discount the 2080+ tails, and flag that *age-structure* error > *total* error.

**L4. Institutions price the stakes as chronic strain, not collapse.** The **NIC's Global Trends 2040** treats demographics as one of four structural forces and prices the stakes as *fiscal/governance pressure, migration-control pressure, localized instability, a rising Asia* — explicitly **not** deglobalization, capital scarcity, or trade collapse. **OECD Pensions at a Glance 2025**: public pension spending rises from 8.8% → 10.0% of GDP (2023/24 → 2050), ~1.2pp over 26 years — real but far from catastrophic — while retirement ages are *already* being legislated upward (OECD-average normal retirement age rising to 66.4/65.9 for 2024 entrants; 70+ legislated in Denmark, Estonia, Italy, Netherlands, Sweden; Czechia and Slovenia 65→67). This is the endogenous-adaptation rebuttal to passive-doom framings, with named documents. *[search-verified.]*

**L5. Published critiques of Zeihan specifically.** Two serious, usable reviews:
- **Noah Smith, "Book Review: The End of the World Is Just the Beginning" (Noahpinion, 2022):** the demographic half is *"by far the most solid ground"* in the book, but demographics are *"fairly marginal"* to Zeihan's doom forecasts — the dominant driver is an *assumed* American-led security collapse destroying world trade. Smith's method critique: Zeihan systematically assumes *zero adaptive capacity* (naval power "can change very quickly"; metal processing is "unsophisticated technology" others would scale); a specific factual error (Zeihan ranks Japan above China post-collapse on naval grounds, but China's navy already outmatches Japan's); and a historical upper bound — *even the Depression + WWII didn't revert humanity to pre-1870 living standards.* Verdict: *"directionally correct"* — exaggerated but with seeds of truth; *"better phrased as a warning than as a forecast."*
- **Money & Macro (Joeri Schasfoort), "Economist Fact-Checks Zeihan's China Collapse Story" (2023):** China's demographic decline is a genuine expert-acknowledged problem but does *not* imply collapse; Zeihan's method is *"too sloppy and too committed to his established narrative."*

*[Both search-verified; fetch blocked.]* These give the §9 steelman its named sources without the article having to originate the critique.

---

## §2 addendum — Zeihan's causal chain, graded

Reconstructed and graded link by link. **(a)** = textbook, **(b)** = mainstream-but-contested, **(c)** = distinctive to Zeihan.

1. **Bretton Woods → US security guarantee globalized trade.** (a) The postwar open-trade order is real and US-underwritten. (b) That the *US Navy specifically* is the *sole load-bearing pillar* — contested. **SUPPORTED as history, CONTESTED as mono-causal.**
2. **Globalized industrialization → urbanization → fertility collapse.** (a) Pure demographic-transition textbook; urbanization flips children from farm asset to urban liability. **SUPPORTED.** (The article's §2 rests here — solid ground.)
3. **Staggered start dates → staggered aging cliffs.** (a) Timing is real and WPP-visible. **SUPPORTED.**
4. **US withdrawal → deglobalization → trade collapse.** (c) The load-bearing distinctive step. Noah Smith: assumes zero naval/industrial adaptation; China's navy can already suppress the piracy Zeihan predicts. **CONTESTED → likely WRONG on severity.** *The article must treat this as the contested link and stand on demographic math instead — which the plan already does.*
5. **Shrinking young cohort → consumption collapse.** (c) Money & Macro: *"most consumption is actually done by those over 35"* because income peaks later, so a smaller young cohort *"will not decimate consumption immediately."* **WRONG as stated** — and note this *reinforces* the article's own NTA $c(a)$ profile, which correctly peaks in mid-life, not the 20s–30s. Good place to show the article's math out-performing the popularization.
6. **China collapse by ~2050 / "the 2020s are the decade."** (c) Uses the most extreme available projection; the Lancet (Vollset et al. 2020) and UN put China's *halving* near **2100, not 2050**. Zeihan has predicted China's collapse "within the next decade" since ~2010; it hasn't happened. **CONTESTED → WRONG on timeline.**
7. **China overcounts population by 100M+.** (c) Amplification of **Yi Fuxian** (Project Syndicate 2021: true 2020 population ~1.28bn, ~130M below the 1.41bn census; local governments inflate counts for fiscal transfers; a ~20M cohort discrepancy in school/hukou registries). It is a *real demographer's* argument but a **contested minority estimate** — UN population chief Patrick Gerland rejects taking either China's raw stats *or* Yi's 100–130M overcount at face value, and WPP 2024 already applies cohort-reconciliation adjustments. **CONTESTED; attribute to Yi, not Zeihan, and note WPP already adjusts.**
8. **Capital scarcity / rising capital cost.** (c) Rests on the asset-meltdown mechanism — see L2: weak empirical support. **CONTESTED.**

---

## New material not in the plan

- **N1. Weighted NTA economic support ratio** as an optional §5 companion instrument (borrowed profiles; Mason 2005 precedent). Adds a "textbook-correct" support ratio alongside the relabeled headcount one.
- **N2. IMF EBA demographic block** as the institutional current-account-demography specification — a named, WPP-computable regression the article can cite (or, ambitiously, approximate) in §4.
- **N3. The "consumption peaks after 35" correction** (Zeihan link 5) is a rhetorical gift: the article's own NTA $c(a)$ curve already gets this right, so it's a clean example of the article's math beating the popular version.
- **N4. Keyfitz momentum sign-flip** as a one-paragraph §5 aside: $M \approx 1.6$ for 1971-era high-fertility countries (Keyfitz's Brazil illustration) but $M < 1$ today — Blue & Espenshade (2011) find 12 countries (11 European + Japan) would shrink >10% *even at instant-replacement fertility*. The sign flip itself is article material and motivates why the plan's forward-projection proxy is the more honest instrument. $b, r, R_0, e_0, \mu$ are all WPP-derivable, so true Keyfitz momentum is *optionally* in-constraint if the added stable-population machinery is judged worth it (open question).
- **N5. Generational accounting / fiscal-gap (Auerbach–Kotlikoff)** as the named tool that *prices the fiscal stakes* — MENTION in §4 as what a treasury would compute, explicitly out-of-constraint for the index (needs country tax/benefit age-profiles).

---

## Deferred to country pass

- **China census reliability** — full adjudication of Yi Fuxian vs. UN/Gerland vs. NBS, with the school-enrollment/hukou cohort-discrepancy evidence and the counter-explanations (enrollment lags, migrant undercount). Belongs in the China portrait, not the framework.
- **Country-specific measured NTA profiles** (60 countries as of 2017; 186 economies in Mason et al. 2022) — for portraits, swap the borrowed global profile for the country's own where measured.
- **Robot-density leaders** (US 9.1 vs Japan 14.2 vs Germany 17.0 robots/1,000 mfg workers, 2014, Acemoglu–Restrepo) — Japan/Germany portraits (automation-as-response-to-aging).
- **Country peak-population years** vs. GT2040's "most developed and many emerging economies peak and shrink by 2040" — per-country falsification against WPP 2024.
- **Russia as the prospective-aging exception** — the LE-stagnation case where prospective measures do *not* show slower aging; a portrait-level nuance.
- **Lancet/IHME (Vollset et al. 2020) vs UN medium variant** divergence per country — for portrait uncertainty framing (esp. China 2050 vs 2100).
- **Mercer/CFA Global Pension Index and Swiss Re sigma** — the insurer/actuary pension-gap quantifications were named but not retrieved this pass; chase in the country/finance pass for hard shortfall numbers.

---

## Ranked source shortlist to keep open for the country pass (≤15)

1. **UN DESA WPP 2024** — the data spine (already the pipeline source).
2. **Mason, Lee, Abrigo & Lee (2017), UN Technical Paper 2017/1, "Support Ratios and Demographic Dividends: Estimates for the World"** — canonical global ESR/dividend implementation; the template for doing this within a WPP-only constraint.
3. **Lee & Mason (2011), *Population Aging and the Generational Economy*** (Edward Elgar) — NTA book of record.
4. **Sanderson & Scherbov (2010), "Remeasuring Aging," *Science* 329:1287–1288** — canonical POADR; the C2 fix.
5. **Higgins (1998), *International Economic Review* 39:343–369** — demography → savings/current account, the §4 empirical anchor.
6. **Acemoglu & Restrepo (2022), "Demographics and Automation," *ReStud* 89(1)** (+ 2017 AER P&P) — the automation offset, strongest §9 counterweight.
7. **Poterba (2004), NBER WP 10851, "The Impact of Population Aging on Financial Markets"** — asset-meltdown verdict.
8. **Abel (2003), *Econometrica* 71:551–578** — OLG asset-price formalization for the §3 aside.
9. **IMF External Balance Assessment methodology (2022/2023 update)** — current-account-demography model with a WPP-computable demographic block.
10. **NIC, Global Trends 2040 (2021), demographics chapter** — the authoritative "milder-than-Zeihan" institutional framing.
11. **OECD Pensions at a Glance 2025** — pension-cost and retirement-age-adaptation numbers; the endogenous-adaptation rebuttal.
12. **Goodhart & Pradhan (2020), *The Great Demographic Reversal*** — the pro-severity book (inflation/capital-scarcity thesis); *not retrieved this pass — read directly in the country/finance pass to steelman the Zeihan-aligned side.*
13. **Noah Smith, Noahpinion review of *The End of the World Is Just the Beginning* (2022)** — the flagship serious Zeihan critique.
14. **Yi Fuxian, Project Syndicate (2021)** + UN/Gerland pushback (Newsweek 2024) — the China-data dispute, both sides, for the China portrait.
15. **Our World in Data / Keilman — accuracy of past UN projections** — the §9 track-record evidence.

---

*Verification ledger: 25/25 formally verified claims confirmed (0 refuted), all on RQ1; RQ2–RQ4 claims above are search-triangulated extractions from the same run, individually cited and marked. Full run journal: workflow `wf_cfffbeb0-aed`.*
