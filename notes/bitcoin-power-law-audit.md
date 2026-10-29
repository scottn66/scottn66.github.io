# Audit report — "Does Bitcoin Follow a Power Law?"

**Page audited:** https://scottn66.github.io/bitcoin-power-law/index.html
**Source state:** `origin/main` @ `d199647` (deployed); page `data.js` generated 2026-06-16 07:20 UTC
**Audit date:** 2026-06-17
**Method:** 9 independent dimension-finders (correctness, statistics, accessibility, performance, SEO, security, responsive, editorial, HTML standards), each followed by an adversarial verifier that re-opened the source files and re-derived every number before a finding was admitted.

---

## Executive summary

The page is strong, well-engineered work. The JavaScript is clean — every `PL.*` read resolves against `data.js`, every `getElementById` has a matching element, all external `target="_blank"` links carry `rel="noopener"`, and all five figures have alt text. The econometrics is mostly sophisticated and honestly hedged. Findings cluster in five areas: **one real statistics bug**, **accessibility**, **load performance**, **social/SEO metadata**, and a **house-style conflict**.

The audit raised 69 candidate findings; adversarial verification confirmed 61 and rejected 8. After dropping one corrected false-positive and merging four cross-lens duplicates, **56 unique findings** remain, summarised below.

| Severity | Count |
|---|---|
| 🔴 Critical | 1 |
| 🟠 High | 3 |
| 🟡 Medium | 11 |
| ⚪ Low | 31 |
| ▪️ Nit | 10 |

| Dimension | Findings |
|---|---|
| seo | 9 |
| a11y | 8 |
| stats | 7 |
| perf | 7 |
| editorial | 6 |
| responsive | 6 |
| correctness | 5 |
| security | 5 |
| standards | 3 |

### The one to fix first
**The KPSS stationarity test is interpreted backwards on-screen** (`index.html:439`). KPSS's null is *stationarity*; with `kpss_p = 0.077 > 0.05` the test *fails to reject* stationarity (leans **stable**), but the page renders "borderline, leans unstable" — the opposite. The section's overall thesis survives (it rests on ADF, Durbin–Watson, and Ljung–Box), so the honest fix actually strengthens it: ADF can't reject a unit root *while* KPSS can't reject stationarity is a textbook inconclusive / low-power result.

---

## Suggested order of attack

**Today** — the KPSS fix (a visible factual error) and the contrast-token fix (one line, fixes dozens of spots).

**This week** — switch to the `plotly-basic` bundle and stop it blocking the parser; add the Open Graph block; reconcile the 17% / 21% percentile labels; pin MathJax to an exact version.

**Polish pass** — em-dash sweep; metadata block (canonical, favicon, theme-color, JSON-LD); table scroll wrappers; lazy-loading; the remaining low/nit items.

---

## 🔴 Critical (1)

### 1. KPSS test reading is statistically backwards — p=0.077 is reported as "leans unstable" when it means the opposite

- **Dimension:** stats · **Confidence:** high
- **Location:** index.html — stationarity table builder, line 439 (#statab KPSS row)
- **Issue:** KPSS has a NULL of stationarity (trend/level stationary). The data has kpss_p=0.0767, which is > 0.05, so the test FAILS to reject stationarity — i.e. it leans toward stable/stationary. The JS encodes the rule `c.kpss_p<0.05?'rejects stability':'borderline, leans unstable'`, so with p=0.077 it renders the reading "borderline, leans unstable." That is the wrong direction: failing to reject the stationary null leans STABLE, not unstable. This is shown to readers in the table and is a factually incorrect interpretation of a named statistical test. (It also undercuts the section's whole "non-stationary" thesis, but the fix is to state the result correctly: KPSS here is borderline and actually does not reject stationarity, in mild tension with ADF — which is itself the honest finding.)
- **Evidence:** data.js cointegration.kpss_p=0.07668683489628747; index.html line 439: "(c.kpss_p<0.05?'rejects stability':'borderline, leans unstable')"
- **Fix:** Flip the non-rejection branch to reflect KPSS's null, e.g. `c.kpss_p<0.05?'rejects stationarity (leans non-stationary)':'fails to reject stationarity (borderline, leans stable)'`. Then reconcile the surrounding prose: ADF can't reject a unit root while KPSS can't reject stationarity is a genuine "inconclusive/low-power" outcome, which is worth stating honestly rather than mislabeling KPSS as evidence of instability.
- **Verified / corrected:** index.html line 439: KPSS with kpss_p=0.0767 (>0.05) fails to reject its stationarity null, which leans STABLE/stationary; the code labels it "borderline, leans unstable," which is the wrong direction. The result is genuinely borderline and, combined with ADF's inability to reject a unit root, indicates an inconclusive (low-power) outcome rather than evidence of instability.


## 🟠 High (3)

### 1. Body copy in --dim (#6b7787) fails WCAG AA contrast (4.5:1) at small sizes

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html CSS: figcaption (line 71, 12.5px), th (line 80, 11px), .chip .k (line 55, 11px), .byline (line 50, 13.5px), footer (line 90, 13px), inline notes lines 166 & 258 (12.5px), footer note line 311; color token --dim:#6b7787 defined line 19
- **Issue:** --dim #6b7787 yields a contrast ratio of only 4.28:1 on --bg #0a0d12, 3.92:1 on --card #121821, and 4.06:1 on --card2 #0f141c (computed via WCAG relative-luminance formula). WCAG 2.1 AA requires 4.5:1 for normal-size text. Every use of --dim is normal-weight text well below the 18.66px (or 14px-bold) large-text threshold: figcaptions (12.5px) under all 5 figures and the Plotly charts, table header cells th (11px) in every table, the chip key labels (.chip .k, 11px), the hero byline (13.5px), the whole footer (13px), and the two explanatory notes plus the credits line. This is the single most pervasive a11y defect on the page: substantial explanatory content (figure captions, table headers, method/credits) is below AA. On --card backgrounds (figcaptions inside .card, th inside tables, footer over the page) it drops to ~3.9-4.1:1, failing even more clearly.
- **Evidence:** --dim:#6b7787 ... ratios computed: #6b7787 on #0a0d12 = 4.28, on #121821 = 3.92, on #0f141c = 4.06 (all < 4.5 AA threshold)
- **Fix:** Lighten --dim to at least ~#7e8b9c (≈4.6:1 on --card) or preferably ~#8a97a8 to clear 4.5:1 on the darkest --card surfaces with margin. Re-verify each surface, since figcaption/th render on --card not --bg. Alternatively bump the smallest text (11px th and chip keys) up in size and weight, but raising the token color is the clean fix.
- **Verified / corrected:** Accurate as stated. Minor precision note: the byline (L114) and footer render over --bg/--bg2 (~4.10–4.28:1), while figcaptions, th, and the two inline notes render over --card/--card2 (~3.9–4.06:1); all fail 4.5:1 AA either way.


### 2. Plotly full bundle (~3.5MB min) loaded render-blocking in <head> with no async/defer

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html line 10: <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
- **Issue:** The full Plotly build is referenced with a plain synchronous <script> in <head>. A plain script in <head> is parser-blocking: the browser must download (plotly-2.35.2.min.js is ~3.5MB uncompressed, ~1MB+ gzipped) and execute it before it continues parsing the body, so first paint is gated on the single largest asset on the page. This page only uses scatter/line traces plus shapes/annotations and band fills — none of the 3D, geo, mapbox, finance, or gl features — so the much smaller plotly-basic bundle (~1MB uncompressed) would render identically. Loading the full bundle render-blocking is the single biggest contributor to a slow First Contentful Paint here, on the order of hundreds of ms to multiple seconds on slow connections.
- **Evidence:** <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
- **Fix:** Switch to the plotly-basic distribution (https://cdn.plot.ly/plotly-basic-2.35.2.min.js) which covers scatter/line/shapes/annotations, and add the defer attribute (or move the tag to the end of <body>) so it no longer blocks the parser. The inline init script already runs at end of <body>, so a deferred Plotly will still be available by the time newPlot is called; if moving to body, ensure Plotly loads before the inline init script.
- **Verified / corrected:** The full Plotly bundle is actually ~4.3MB uncompressed (4,558,696 bytes), not ~3.5MB; plotly-basic-2.35.2 is ~1.0MB (1,071,091 bytes), a ~3.5MB saving. Note a correctness caveat in the fix: the sole Plotly consumer is a plain (non-deferred) inline script at the end of <body> (line 314), which executes during parsing — adding `defer` to the line 10 tag alone would make Plotly load AFTER that inline script runs Plotly.newPlot, throwing a ReferenceError. The safe fix is to move the (basic) Plotly tag to just before the inline init script at end of <body> (still render-unblocking), or wrap the init in a DOMContentLoaded/load handler. The finding flags this caveat but its primary 'add defer' suggestion would break rendering if applied naively.


### 3. No Open Graph tags: shared link previews as a bare URL with no image, title, or description

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head, lines 3-15)
- **Issue:** The <head> contains only <title> and <meta name="description">. There are zero Open Graph tags (og:title, og:description, og:image, og:url, og:type). When this 'research note' is pasted into Slack, iMessage, LinkedIn, Discord, Reddit, or Facebook, the unfurl falls back to a bare link with no card, no preview image, and often a truncated/raw title. This directly undercuts the page's purpose: it is explicitly framed as a shareable note ('every chart is interactive; every test is reproducible'). Sibling pages already follow the house OG pattern, e.g. Q.html lines 10-14 set og:title/og:description/og:image/og:url plus twitter:card='summary_large_image', so this page is the exception, not the rule.
- **Evidence:** index.html lines 6-7 are the only metadata: '<title>Does Bitcoin Follow a Power Law? — An Econometric Autopsy</title>' and '<meta name="description" content="An interactive, multi-lens econometric scrutiny..."/>'. grep for 'og:title|og:image|twitter:card' across the page returns nothing. Compare Q.html line 12: '<meta property="og:image" content="https://scottn66.github.io/robot-arm-sim/img/end_card_resolution.png">'.
- **Fix:** Add the standard OG block to <head>: og:type='article', og:url='https://scottn66.github.io/bitcoin-power-law/', og:title (em-dash-free, see separate finding), og:description (reuse the meta description), and og:image pointing to an absolute https URL of a representative 1200x630 card. The 5 existing seaborn PNGs in assets/ (e.g. fig_aic.png) are not ideal social cards (wrong aspect ratio, tiny, no title), so generate a dedicated og-image; until then, an absolute URL to assets/fig_aic.png is better than nothing.
- **Verified / corrected:** The meta description is on line 7 (not lines 6-7); otherwise the finding is accurate. index.html has zero OG/Twitter tags while Q.html and the repo root index.html both follow the OG house pattern.


## 🟡 Medium (11)

### 1. Interactive Plotly chart containers have no text alternative, role, or aria-label for screen readers

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html: #hero (line 129), #osc (line 219), #lppls (line 242), #roll (line 254); Plotly.newPlot calls in the inline script (lines 415, 483, 536, 565)
- **Issue:** The four interactive charts are built into empty <div id="..." class="plot"> elements via Plotly.newPlot. Plotly renders the chart as inline SVG with no accessible name, no role="img", and no descriptive text alternative. A screen-reader user reaching #hero, #osc, #lppls, or #roll hears nothing meaningful — the entire visual argument of four of the eight lenses is inaccessible. The data underlying each chart (fit line, price series, sigma bands, z-score, LPPLS fit, rolling exponent) exists in window.PL but is never exposed as text. The adjacent <figcaption> describes how to interact ("hover, drag to zoom") but is not programmatically associated with the chart div and does not convey the chart's content/conclusion.
- **Evidence:** <div id="hero" class="plot" style="min-height:540px"></div> ... Plotly.newPlot('hero',tr,lay,CFG); — no aria/role attributes anywhere on the four .plot divs
- **Fix:** Wrap each chart in <figure role="figure" aria-label="..."> or add role="img" plus aria-label to the chart div summarizing what it shows and the takeaway (e.g. aria-label="Bitcoin log-log price vs power-law fit; price tracks a straight trend line from $0.05 in 2010 to six figures in 2026 within a plus/minus 2 sigma corridor"). Associate the existing figcaption via aria-describedby. Provide a visually-hidden data table or text summary as a fallback for the numeric content.


### 2. No skip-to-content link; horizontally scrolling nav must be traversed before reaching main

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html: <nav> lines 97-108, <main> line 118 (no skip link before nav)
- **Issue:** There is no skip-link as the first focusable element. The sticky <nav> contains a brand span plus 9 in-page anchor links that a keyboard or screen-reader user must tab through on every visit before reaching the main content. WCAG 2.4.1 (Bypass Blocks) expects a mechanism to skip repeated navigation. The nav also uses overflow-x:auto with hidden scrollbars (line 38-39), so on narrow viewports later nav links are off-screen and only reachable by tab-then-auto-scroll, compounding the problem.
- **Evidence:** <body>\n\n<nav><div class="wrap">  — first element after body is the nav, no skip link; nav .wrap{...overflow-x:auto;scrollbar-width:none}
- **Fix:** Add <a href="#claim" class="skip-link"> (or to a #main target) as the first child of <body>, visually hidden until focused (e.g. position:absolute;left:-9999px; then :focus reveals it). Add id="main" to <main> as the target.


### 3. No visible keyboard focus indicator (:focus-visible) on nav links, in-page links, or chart controls

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html CSS: a{} rules lines 31-32 and nav a rules lines 42-43; no :focus or :focus-visible rule anywhere in the <style> block (lines 16-93)
- **Issue:** The stylesheet defines a:hover (text-decoration:underline) and nav a:hover (background + color change) but never defines :focus or :focus-visible. On a dark theme the browser default focus ring is often low-contrast or, combined with custom backgrounds, can be visually lost. Keyboard users tabbing through the 9 nav links, the inline reference links (Wikipedia, Lens cross-links), and the Plotly mode-bar/button controls have no reliable visible indication of focus position, failing WCAG 2.4.7 (Focus Visible).
- **Evidence:** a:hover{text-decoration:underline} / nav a:hover{background:var(--card);color:var(--ink)...} — hover states exist but there is no :focus or :focus-visible selector in the CSS
- **Fix:** Add an explicit high-contrast focus style, e.g. a:focus-visible, nav a:focus-visible, button:focus-visible { outline:2px solid var(--orange); outline-offset:2px; border-radius:4px; }. Do not remove the default outline without replacing it.
- **Verified / corrected:** No custom :focus-visible style exists; the page relies on the browser default focus ring (outline is never explicitly removed). On the dark theme and custom-styled nav pills this default ring can be low-contrast or visually lost, degrading (not eliminating) keyboard focus visibility across the 16 focusable anchors. There are no <button> elements in the file; Plotly mode-bar controls are runtime-generated and outside this static file.


### 4. Two different "corridor percentile" values shown to the reader for the same concept (17% vs 21%)

- **Dimension:** correctness · **Confidence:** high
- **Location:** index.html line 338 (chips, reads cur.corridor_percentile) and line 506 (mrcard, reads m.current_percentile); plus inline prose at line 343/data.js mean_reversion.interpretation
- **Issue:** The header chip labeled "Corridor" renders Math.round(cur.corridor_percentile) = Math.round(17.424…) = 17%, sourced from PL.current.corridor_percentile = 17.42. The Lens-4 "Where Bitcoin stands today" card renders Math.round(m.current_percentile) = Math.round(20.734…) = 21%, sourced from PL.mean_reversion.current_percentile = 20.73. Both describe the same thing — where today's price sits in the historical deviation corridor — yet the page shows 17% in the hero chip and 21% in the card (and the data.js interpretation string also says "21th percentile"). A reader comparing the two cannot reconcile them; it reads as an internal contradiction.
- **Evidence:** current.corridor_percentile = 17.424242424242426 (chip shows 17%); mean_reversion.current_percentile = 20.734045466995344 (mrcard shows 21%)
- **Fix:** Pick one canonical percentile and bind both the chip and the card to it (e.g. make the chip read PL.mean_reversion.current_percentile too, or recompute current.corridor_percentile from the same residual/sigma used for current_percentile). At minimum reconcile the two values in data.js so they round to the same integer.
- **Verified / corrected:** The page shows 17% (hero "Corridor" chip, from the full-sample power-law fit, σ=0.276 dex) and 21% (Lens-4 "Corridor percentile" card and interpretation string, from the stationary OU residual, σ=0.230 dex) under near-identical labels with no disambiguation. Both are internally correct for their own model; the defect is the shared/ambiguous labeling, not an arithmetic inconsistency, so the fix is to relabel/disambiguate (or pick one canonical percentile) rather than to force the two data.js values to round equal.


### 5. Disclaimer is single, footer-only, and far from the page's buy-signal language

- **Dimension:** editorial · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html line 311 (footer disclaimer) vs lines 220 and 227 (valuation language)
- **Issue:** The page makes actionable-sounding valuation statements well above the fold of the disclaimer: line 220 'below the midline = historically cheap, above = expensive'; line 227 (Lens 4 verdict) 'Today Bitcoin sits below fair value, historically a favorable zone.' The chips even surface 'Price ÷ model' and 'Corridor' percentile prominently. The only 'Educational analysis — not investment advice' disclaimer sits once at line 311 in the footer, after eight long sections. A reader who stops at the Lens 4 verdict (a natural exit point that reads like a buy signal) never sees it.
- **Evidence:** line 227: 'Today Bitcoin sits below fair value, historically a favorable zone.'  line 220: 'below the midline = historically cheap'  line 311: 'Educational analysis — not investment advice.'
- **Fix:** Either soften the valuation verdicts (e.g. 'historically a below-average corridor position' rather than 'a favorable zone' / 'cheap'), or add a short inline disclaimer near the first valuation claim (Lens 4 verdict, line 227) so the 'not investment advice' caveat travels with the price-context language instead of living only in the footer.
- **Verified / corrected:** The page contains exactly one disclaimer ("Educational analysis — not investment advice.") at index.html line 311 in the footer, after all 8 lenses. Actionable valuation language appears far earlier and above the fold: the hero chips at line 115 (built lines 332-342) surface "Price ÷ model" (0.57×) and "Corridor" (17%), the Lens 4 oscillator figcaption at line 220 calls below-midline "historically cheap," and the Lens 4 verdict at line 227 states Bitcoin "sits below fair value, historically a favorable zone." These valuation statements are data-accurate per data.js (ratio_to_model 0.574, corridor_percentile 17.4) and are contextually hedged elsewhere, so the issue is disclaimer placement/proximity, not a false claim.


### 6. data.js (108KB) loaded synchronously in <head>, blocking the parser before any content paints

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html line 15: <script src="assets/data.js"></script>  (file assets/data.js is 108,572 bytes)
- **Issue:** assets/data.js (verified 108,572 bytes / ~106KB) is a plain synchronous script in <head>. It is parser-blocking: the browser stops, fetches and executes it before continuing. None of the page's chrome (nav, hero text, section copy) needs window.PL to render — only the inline init script at the bottom of <body> consumes it. Pairing a 106KB blocking data file with the already-blocking Plotly tag stacks two serial round trips ahead of first paint.
- **Evidence:** <script src="assets/data.js"></script>
- **Fix:** Add defer to the data.js tag (<script defer src="assets/data.js"></script>) or move it to just before the inline init <script> at the bottom of <body>. defer preserves execution order and guarantees it runs before the deferred inline code while no longer blocking the parser. This alone removes ~106KB from the critical render path.
- **Verified / corrected:** assets/data.js (108,572 bytes uncompressed, ~38KB gzipped as GitHub Pages serves it) is a plain synchronous <script> at index.html line 15 in <head>, with no defer/async. It is parser-blocking. Its only consumer is the inline init script at the bottom of <body> (lines 314-598; reads window.PL at line 316). No static body markup (lines 16-313) references PL, so nothing visible needs it before that init script runs. Adding defer to line 15 (or relocating the tag to just before line 314) is safe and order-preserving, removing data.js from the parser-blocking path. Note: the wire cost removed is ~38KB gzipped, not 106KB; and data.js downloads in parallel with the Plotly CDN script (different origin) — they are serial in execution, not in download.


### 7. All 5 figures are below the fold but none use loading="lazy"

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html lines 141, 168, 197, 223, 269 (all <img> tags inside <figure>)
- **Issue:** The five PNG figures (combined ~300KB: fig_lag 99,587 + fig_qq 76,711 + fig_residual_dist 52,446 + fig_aic 40,510 + fig_cycles 30,649 bytes) all live in Lens 1 and beyond, well below the hero fold. None has loading="lazy", so the browser eagerly fetches all of them on initial load, competing for bandwidth with the already-heavy render-blocking Plotly and data.js. On a first visit the user pays for ~300KB of images they may never scroll to.
- **Evidence:** <img src="assets/fig_qq.png" alt="Q–Q plot of residuals"/>
- **Fix:** Add loading="lazy" to all five figure <img> tags so off-screen figures defer until the user scrolls near them, freeing initial-load bandwidth for the critical Plotly bundle and first chart. The first figure (fig_lag) is the only borderline case; the other four are deep in the page and clearly safe to lazy-load.


### 8. Four Plotly.newPlot calls all fire eagerly on load with no lazy/on-scroll init

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html inline script: hero Plotly.newPlot at line 415, osc at line 483, lppls at line 536, roll at line 565
- **Issue:** The bottom inline script builds and renders four separate Plotly charts (hero, osc, lppls, roll) immediately and synchronously when it runs. Each Plotly.newPlot is a non-trivial main-thread layout/draw operation, and only the hero chart is above the fold; osc, lppls, and roll are deep in the page. Rendering all four up front blocks the main thread during the most load-sensitive moment, delaying interactivity (Total Blocking Time / time-to-interactive) for charts the user has not scrolled to yet.
- **Evidence:** Plotly.newPlot('hero',tr,lay,CFG); ... Plotly.newPlot('osc',tr,lay,CFG); ... Plotly.newPlot('lppls',tr,lay,CFG); ... Plotly.newPlot('roll',tr,lay,CFG);
- **Fix:** Render only the hero chart eagerly; defer osc, lppls, and roll behind an IntersectionObserver that calls Plotly.newPlot when each container scrolls into view. This spreads the main-thread cost across the session instead of front-loading it, and pairs naturally with deferring/lazy-loading Plotly itself.
- **Verified / corrected:** Real finding: all four Plotly charts (hero/osc/lppls/roll at lines 415/483/536/565) render eagerly and synchronously with no lazy/on-scroll init (no IntersectionObserver/rAF/idle callback exists in the file). Deferring the three off-screen charts is a valid TBT/TTI win, but a smaller one than removing the render-blocking Plotly <script> in head (line 10, no defer/async), which is the larger contributor to load-time blocking.


### 9. Wide data tables have no horizontal-scroll wrapper and overflow on narrow phones

- **Dimension:** responsive · **Confidence:** medium
- **Location:** index.html — .card rule line 67 (no overflow-x); affected tables: #lpplstab (line 240, rendered 7 columns at lines 539-542), #statab (line 165, 4 cols of prose), #fittab (line 151), #mtab_full/#mtab_recent (lines 194-195), #chowtab (line 257)
- **Issue:** Every table is placed inside a plain `.card` (`.card{...padding:18px...}` at line 67) which has NO `overflow-x`. Only `.eq` (line 83) carries `overflow-x:auto`. On a 360px viewport the usable width is ~316px (`.wrap{padding:0 22px}` line 34) minus 36px of card padding ≈ 280px. The LPPLS table built at lines 539-542 has 7 columns — 'Cycle run-up', 'fitted t_c', 'actual peak', 'm', 'ω', 'R²', 'bubble verdict' — with non-wrapping content like two `YYYY-MM-DD` date cells (e.g. `2025-10-07`, `2025-10-06`) and a pill reading 'ω at floor — fails'. That content cannot fit in 280px, so `table{width:100%}` (line 78) is overridden by intrinsic minimum width and the table overflows the card, causing the whole page to scroll horizontally (or the card to spill) on phones. The `#statab` table (lines 444-446) is also at risk: it has a 'What it asks' column with long sentences ('Do deviations eventually die out?') plus a 'Reading' column ('no — can’t reject a wandering unit root'), four columns total in a half-width grid cell that only goes full-width below 820px but is still ~316px wide.
- **Evidence:** .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}  (line 67 — no overflow-x); LPPLS row: '<th>Cycle run-up</th><th class="num">fitted t_c</th><th class="num">actual peak</th><th class="num">m</th><th class="num">ω</th><th class="num">R²</th><th>bubble verdict</th>' (line 539)
- **Fix:** Wrap each table in a scroll container, e.g. add a CSS rule `.card{overflow-x:auto}` is too broad (it would clip the hero shapes—do not apply to plot cards); instead introduce `.tablewrap{overflow-x:auto;-webkit-overflow-scrolling:touch}` and wrap the `<table>` elements, or target the table cards specifically: `.card>table{display:block;overflow-x:auto;white-space:nowrap}`. Simplest robust fix: give the table-bearing cards a class (e.g. `card tbl`) and add `.tbl{overflow-x:auto}`. Also set `td/th{white-space:nowrap}` on the LPPLS/numeric tables so columns scroll as a unit rather than wrapping into unreadable stacks.
- **Verified / corrected:** Wide tables (notably the 7-column LPPLS table #lpplstab at index.html line 240, plus the 4-column #statab) are not wrapped in any horizontal-scroll container — `.card` (line 67) lacks `overflow-x` and no `.tablewrap` exists. On a ~360px phone (~280px usable inside a card) these tables become cramped: most cells wrap (no `white-space:nowrap` anywhere on table cells), while the monospace YYYY-MM-DD date columns create a localized overflow risk. The result is degraded readability rather than guaranteed full-page horizontal scrolling. Fix by wrapping table-bearing cards in a `.tbl{overflow-x:auto;-webkit-overflow-scrolling:touch}` container and optionally adding `white-space:nowrap` to the LPPLS/numeric cells so they scroll as a unit.


### 10. Hero chart permanently reserves 14.5% of width for the Gaussian marginal, crushing the main panel on phones

- **Dimension:** responsive · **Confidence:** high
- **Location:** index.html — hero Plotly layout: xaxis domain [0,0.84] (line 401), xaxis2 domain [0.855,1.0] (line 403), margin.l:62 (line 400)
- **Issue:** The hero sets `xaxis.domain:[0,0.84]` and the right-edge Gaussian marginal `xaxis2.domain:[0.855,1.0]`, so 16% of the plot width is permanently handed to the bell curve plus a 1.5% gutter, regardless of screen size. On a 360px phone the plot element is ~316px wide; after `margin.l:62` and `margin.r:16` (left axis labels '$1M','$100k' etc. at lines 405/356) only ~238px remains for both panels, and the main log–log chart collapses to ~200px while the decorative marginal still claims ~34px. With ten y-tick labels (line 356) and a year axis title 'year — log scale (days since genesis)' (line 402), the panel becomes cramped to the point the curve is barely legible. The marginal adds analytic value on desktop but is near-useless at this width.
- **Evidence:** xaxis:{domain:[0,0.84],...} (line 401); xaxis2:{domain:[0.855,1.0],anchor:'y',...} (line 403); margin:{l:62,r:16,t:18,b:50} (line 400)
- **Fix:** Hide or de-prioritize the marginal on narrow viewports: detect width in the IIFE (e.g. `const narrow = window.innerWidth < 640`) and when narrow set `xaxis.domain:[0,1]`, drop the xaxis2 traces/shapes/annotations, and skip the Gaussian trace. Alternatively shorten the y-axis title and reduce `margin.l` on small screens. Plotly is already `responsive:true` (line 329) so a resize listener can re-layout.
- **Verified / corrected:** The finding is accurate except for one minor detail: line 356 defines yTick=[0.1,1,10,100,1e3,1e4,1e5,1e6,1e7], which is 9 y-tick labels, not the "ten" stated in the description. Also, margin.r is 16 (the finding states this correctly in evidence; the title's '14.5%' refers to the marginal alone while the body's '16%' includes the 1.5% gutter — both are defensible).


### 11. MathJax loaded from a MOVING major-version tag (mathjax@3) — non-reproducible and SRI-incompatible

- **Dimension:** security · **Confidence:** high
- **Location:** index.html line 14: <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" id="MathJax-script" async></script>
- **Issue:** The MathJax script is pinned only to the major tag `mathjax@3`. jsDelivr resolves `@3` to whatever the latest 3.x release is at request time (currently 3.2.2), so the exact bytes served can change under you without any change to this repo. This breaks reproducibility and, more importantly, it is impossible to add Subresource Integrity to a moving tag (an `integrity` hash would break the moment npm publishes a new 3.x). The page therefore executes third-party JavaScript with full access to the DOM and to `window.PL` with zero integrity guarantee and a content surface that can silently change. Contrast with Plotly on line 10, which is correctly pinned to an exact version (2.35.2). Note SRI genuinely cannot be applied while the tag stays moving — the fix is to pin first, then add SRI.
- **Evidence:** src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"
- **Fix:** Pin MathJax to an exact patch version and add SRI, e.g. `<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js" integrity="sha384-..." crossorigin="anonymous"></script>`. Generate the hash with `curl -s https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js | openssl dgst -sha384 -binary | openssl base64 -A`. (jsDelivr also exposes per-file SRI hashes in its UI.) If you prefer maximum control, self-host the tex-svg bundle under assets/ and drop the CDN entirely.
- **Verified / corrected:** MathJax is loaded from a moving major tag (mathjax@3, line 14), which is non-reproducible and SRI-incompatible. This is real but is one symptom of a page-wide absence of SRI (Plotly on line 10 and Google Fonts on line 9 also lack integrity hashes). On a static no-backend page with only public chart data, the risk is standard CDN supply-chain drift, warranting medium rather than high severity.


## ⚪ Low (31)

### 1. scroll-behavior:smooth not gated by prefers-reduced-motion

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html CSS: html{scroll-behavior:smooth} line 24
- **Issue:** Global smooth scrolling is applied unconditionally. Users who set prefers-reduced-motion (vestibular sensitivity) still get animated scroll-jumps when activating the in-page nav anchors (#claim, #fit, etc.). WCAG 2.3.3 (AAA) and general motion best practice call for honoring the reduced-motion preference.
- **Evidence:** html{scroll-behavior:smooth} — applied at the root with no prefers-reduced-motion guard
- **Fix:** Wrap it in a query: @media (prefers-reduced-motion: no-preference){ html{scroll-behavior:smooth} } so reduced-motion users get instant jumps.
- **Verified / corrected:** html{scroll-behavior:smooth} at index.html line 24 is the only motion-related CSS in the file and is not gated by prefers-reduced-motion; it animates in-page anchor navigation for vestibular-sensitive users (WCAG 2.3.3, AAA).


### 2. Tables built via innerHTML lack <caption> and th scope attributes

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html: empty <table id=...> at lines 151 (#fittab), 165 (#statab), 240 (#lpplstab), 257 (#chowtab), 194/195 (#mtab_full/#mtab_recent), plus static table lines 182-190; thead/th strings generated in script at lines 430, 445, 458, 539, 568
- **Issue:** All data tables (fit inference, stationarity tests, model tournament, LPPLS cycles, Chow tests) are populated by innerHTML that emits <th> cells without scope="col" and with no <caption>. The static model-claims table (lines 182-190) also omits scope and caption. Without scope, screen readers cannot reliably associate header cells with data cells in multi-column tables (e.g. the 7-column LPPLS table, the 4-column stationarity table where each row's 'Reading' depends on its 'Test' header). Without a caption the table has no accessible name describing its purpose. WCAG 1.3.1 (Info and Relationships).
- **Evidence:** '<thead><tr><th>Test</th><th>What it asks</th><th class="num">p / stat</th><th>Reading</th></tr></thead>...' — th elements emitted with no scope attribute; no <caption> element on any table
- **Fix:** Emit <th scope="col"> in every generated thead (and scope="row" on the first cell of each row where it is a row header, e.g. the Test name / Model name / Cycle label). Add a <caption> (can be visually hidden) to each table summarizing it, e.g. 'Stationarity test results'.
- **Verified / corrected:** All data tables with column headers omit `scope` and `<caption>` (confirmed: zero occurrences of either in the file). The accessibility impact is real but minor for these simple single-header-row tables — modern screen readers infer column association without `scope="col"` — so this is low/polish, not medium. The most material gap is `scope="row"` on the first cell of each row in the wider multi-column tables (#lpplstab 7-col, #statab/#chowtab/#mtab 4-col), where row+column association genuinely aids comprehension.


### 3. Section topic labels ("Lens N") are styled <div class="lenstag">, not headings, breaking the document outline

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html: .lenstag divs at lines 121,136,157,175,203,231,249,264,279 (e.g. 'Lens 1 — Fit & honest inference'); .lenstag CSS lines 59-60
- **Issue:** Each section is introduced by a non-heading <div class="lenstag"> carrying the lens number and title ("Lens 1 — Fit & honest inference"), followed by an <h2>. The lens label is the primary wayfinding label for the section but is invisible to a screen reader's heading navigation, and the numbered structure (0-7 plus the scorecard) is conveyed only visually via the .lensnum badge. The heading order h1 -> h2 -> h3 is otherwise correct, but the meaningful section-numbering metadata is not exposed semantically.
- **Evidence:** <div class="lenstag"><span class="lensnum">1</span> Lens 1 — Fit & inference</div> followed by <h2>The exponent is real...</h2> — the lens identifier is in a div, not a heading
- **Fix:** Either fold the lens label into the h2 (e.g. <h2>Lens 1 - Fit & honest inference</h2> with the descriptive line as a sub-element), or mark the numeric badge as decorative (aria-hidden) while ensuring the section's accessible name still conveys which lens it is. At minimum keep the visual order so the badge is announced near the heading.
- **Verified / corrected:** The lens/section labels are presented in non-heading `<div class="lenstag">` elements (lines 121, 136, 157, 175, 203, 231, 249, 264, 279), so the "Lens N" number and short lens title are conveyed only visually and are absent from the accessible heading text. The document outline itself is NOT broken: each section still has a well-formed, descriptive `<h2>` (h1->h2->h3 hierarchy is correct and navigable). This is a minor a11y enhancement gap (decorative wayfinding metadata not exposed semantically), not a broken outline. The finding also misquotes the label: the file reads "Lens 1 — Fit & honest inference", not "Lens 1 — Fit & inference".


### 4. Hero x-axis title stays "log scale (days since genesis)" after toggling to calendar-time/linear view

- **Dimension:** correctness · **Confidence:** high
- **Location:** index.html lines 401-402 (xaxis.title) and 409-413 (updatemenus buttons)
- **Issue:** The hero chart's x-axis title is hard-coded to 'year — log scale (days since genesis)'. The second button ("calendar time · log price") relayouts only 'xaxis.type':'linear' and does not update the axis title, so after the user switches to the calendar-time/linear view the axis still claims "log scale". The figcaption and prose specifically tell the reader this button switches between log and linear, so the stale "log scale" label directly contradicts the active view.
- **Evidence:** xaxis:{...title:{text:'year — log scale (days since genesis)',font:{size:12}}} (line 401-402); button args:[{'xaxis.type':'linear'}] (line 412) — no title relayout
- **Fix:** Include the title in each button's relayout args, e.g. the log button sets 'xaxis.title.text':'year — log scale (days since genesis)' and the linear button sets 'xaxis.title.text':'year — linear (calendar time)'. Or use a neutral title like 'year' that is correct in both modes.
- **Verified / corrected:** After clicking the "calendar time · log price" button, the hero x-axis switches to linear scale but its title still reads "year — log scale (days since genesis)" (index.html line 402), contradicting both the active view and the prose (lines 126, 130) that describe this toggle. Cosmetic label-only issue affecting only the non-default view; low severity.


### 5. Many text bindings silently coerce missing data to 0/'undefined-free' placeholders, hiding generation failures

- **Dimension:** correctness · **Confidence:** high
- **Location:** index.html line 506 Math.round(m.current_percentile) and line 582/594 Math.round(rk.max_drawdown_pct) (no ||0 guard), vs the ||0-guarded reads elsewhere (e.g. lines 337-339, 493-500)
- **Issue:** The script is inconsistent about defensive defaults. Most numeric reads use (x||0).toFixed(...), but a few call Math.round() directly on possibly-undefined fields: Math.round(m.current_percentile) (line 506) and Math.round(rk.max_drawdown_pct) (lines 582, 594). If data.js ever omits current_percentile or max_drawdown_pct (a partial/failed regeneration), Math.round(undefined) yields NaN and the page prints 'NaN%' to the reader rather than failing safe like the guarded fields. The values exist today, so this is latent, but it is an avoidable correctness/robustness gap and the inconsistency is a smell.
- **Evidence:** Line 506: <td class="num">${Math.round(m.current_percentile)}%</td>; line 582: ${Math.round(rk.max_drawdown_pct)}%; line 594: dd.textContent=Math.round(rk.max_drawdown_pct)+'%'. Compare line 337: (f.n||0).toFixed(2).
- **Fix:** Apply the same ||0 (or Number.isFinite checks) used elsewhere: Math.round(m.current_percentile||0), Math.round(rk.max_drawdown_pct||0), so a missing field degrades to 0 (or a dash) instead of 'NaN'.
- **Verified / corrected:** Two unguarded `Math.round` reads (current_percentile at line 506; max_drawdown_pct at lines 582 and 594) would render 'NaN%' if their field is missing, unlike the guarded `Math.round(cur.corridor_percentile||0)` on line 338. Both fields are present in the current data.js (20.73 and -83.80), so the bug is latent, not active.


### 6. Pervasive em-dash usage contradicts the documented no-em-dash house style

- **Dimension:** editorial · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (88 instances) + README.md (11 instances); representative: line 6 (title), line 113 (lede), line 153 (Lens 1 verdict), line 303 (bottom line)
- **Issue:** The site owner deliberately avoids em-dashes (prior commit 'Strip em-dashes across crawler pages'), yet this page is saturated with them: 88 em-dashes in index.html and 11 more in README.md (99 total). They appear in the most prominent places, starting with the <title>: 'Does Bitcoin Follow a Power Law? — An Econometric Autopsy' (line 6), the lede 'tracked a straight line on log–log axes for over a decade — a power law in time' (line 113), and nearly every verdict box and paragraph. This is a consistent, systematic violation of the established voice, not a one-off. (Note: the ~36 EN-dashes in 'log–log', 'Newey–West', 'Durbin–Watson', etc. are typographically correct and should be left alone — only the em-dash '—' is the house-style problem.)
- **Evidence:** <title>Does Bitcoin Follow a Power Law? — An Econometric Autopsy</title>  (line 6); 88 '—' in index.html, 11 in README.md
- **Fix:** Mechanical fix: replace em-dashes with the owner's preferred construction (sentence split, colon, comma, or parenthetical). Do a global pass over index.html (88) and README.md (11), being careful NOT to touch the en-dash '–' used in compound names/ranges (log–log, Newey–West, Ornstein–Uhlenbeck, ±2σ corridor, year ranges). Start with the title and the five .verdict boxes since those are highest-visibility.
- **Verified / corrected:** 99 em-dashes total (88 in index.html on 88 lines, 11 in README.md) violate the site's documented no-em-dash house style; the 36 en-dashes in compound names/ranges are typographically correct and should be left untouched. This is a stylistic/editorial issue (low severity), not a correctness, UX, SEO, or security gap.


### 7. Ordinal typo '21th percentile' shown to readers

- **Dimension:** editorial · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/assets/data.js (PL.mean_reversion.interpretation), rendered at index.html line 509 (#mrcard, ${m.interpretation})
- **Issue:** The mean_reversion.interpretation string ends 'Bitcoin sits 0.91σ below fair value (21th percentile).' The ordinal is wrong: 21 takes 'st', not 'th'. This text is injected verbatim into the 'Where Bitcoin stands today' card via index.html line 509, so the typo is visible on the live page. (Confirmed Math.round(20.73)=21, so the figure itself is fine; only the suffix is wrong.)
- **Evidence:** data.js: "...0.91σ below fair value (21th percentile)."  rendered by: <p ...>${m.interpretation||''}</p>  (index.html line 509)
- **Fix:** Edit the interpretation string in data.js to '21st percentile'. Better, since this string is generated by scripts/pl_econometrics.py, fix the ordinal logic at the source so it never emits 'Nth' for 1/2/3-ending numbers (21st, 22nd, 23rd, etc.), then regenerate data.js.
- **Verified / corrected:** The interpretation string in PL.mean_reversion ends "...0.91σ below fair value (21th percentile)." and is rendered verbatim at index.html line 509 inside #mrcard. The ordinal should be "21st". The number 21 is correctly derived (Math.round(20.734)=21); only the suffix is wrong.


### 8. 'dex' unit used in reader-facing tables but never defined

- **Dimension:** editorial · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html lines 498, 499, 507, 510 (Lens 4 OU card and volatility spans)
- **Issue:** The OU card prints 'Equilibrium θ ... dex' (498), 'Shock vol σ ... dex/yr' (499), 'Stationary 1σ dispersion ±... dex' (507), and the inline volatility range '...dex/yr' (510). 'dex' (a decade / log10 unit, ~factor-of-10) is genuinely obscure to the stated general-but-curious audience and is defined only in a JS code comment ('// dex (log10 units)', line 352) that readers never see. The prose around it explains θ, λ, σ in plain language but leaves the unit itself unexplained.
- **Evidence:** line 352 comment: 'sigma=(PL.fit_full||{}).resid_sigma||0.276;     // dex (log10 units)'; line 507: '±${(m.resid_sigma||0).toFixed(2)} dex (≈...%)'
- **Fix:** Define 'dex' once on first user-visible use, e.g. add a parenthetical in the Lens 4 lede or OU card: 'dex = orders of magnitude in log10 price (1 dex = a 10× move).' The line 507 row already shows the %-equivalent in parentheses, so leaning on that translation everywhere (or adding a tooltip) would also work.
- **Verified / corrected:** The finding's locations are correct, but it undercounts the reader-facing occurrences: 'dex' also surfaces via the mean_reversion.interpretation string printed at index.html line 509 (m.interpretation), so the undefined unit appears in five places across two cards plus the inline Lens 4 prose, not the four the finding lists.


### 9. Three different headline exponents shown for 'the' power-law slope

- **Dimension:** editorial · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html line 337 (chip), line 424 (#fittab), line 153 (Lens 1 verdict), line 296 (scorecard)
- **Issue:** A reader scanning for 'the exponent' sees three inconsistent numbers without explanation. The hero chip 'Exponent n' uses PL.fit_full.n = 5.54 (line 337). The Lens 1 inference table uses PL.fit_coinbase.n = 5.426 ≈ 5.43 (line 424). The Lens 1 verdict prose says 'it's 5.4' (line 153). And the scorecard 'Does not survive' bullet frames the contrast as '≈[4.3, 6.2], not 5.8 ± 0.01' (line 296), introducing yet a fourth figure (5.8, the literature value) as if it were the page's own point estimate. The full-history vs Coinbase-window distinction is real, but it is never flagged at the chip, so the 5.54 vs 5.43 gap looks like an error.
- **Evidence:** chip: ['Exponent n', (f.n||0).toFixed(2)...] with f=PL.fit_full → '5.54'; fittab: ['Exponent n (point estimate)', (fc.n||0).toFixed(3)] with fc=PL.fit_coinbase → '5.426'; line 153: '5.4 with a 95% bootstrap interval'; line 296: '≈[4.3, 6.2], not 5.8 ± 0.01'
- **Fix:** Pick one headline exponent for the chip (the Coinbase-window 5.43 that the formal tests and CI actually use, to match Lens 1), or label the chip 'Exponent n (full history)' so the 5.54 vs 5.43 difference is intentional and legible. In the scorecard bullet (line 296), keep '5.8' clearly attributed to the literature ('not the literature's 5.8 ± 0.01') so it isn't read as the page's own estimate.
- **Verified / corrected:** The page shows two distinct page-derived exponents, not three: an unlabeled hero chip "Exponent n = 5.54" (PL.fit_full.n, full history) versus the Coinbase-window 5.43 used by the fittab (labeled "Coinbase window 2016–2026"), the Lens 1 prose, and the scorecard CI. The fittab's 5.426 and the prose's 5.4 are the same number rounded, not separate figures. The 5.8 is the literature value and is attributed as such on line 153, though the line-296 scorecard bullet omits inline attribution. The real defect is that the hero chip never flags its full-history basis, and line 557 mislabels the Coinbase value (fc.n=5.43) as "full-sample n".


### 10. Data cadence described inconsistently: 'weekly' in the chart vs 'daily closes (~3,650 obs)' in the method/footer

- **Dimension:** editorial · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html line 130 (hero figcaption 'weekly') vs lines 139, 150 (Lens 1 'daily') and line 310 (footer 'daily closes (≈3,650 obs)')
- **Issue:** The hero figcaption says 'Blue = BTC (Coinbase, weekly)' (line 130), which matches the plotted PL.series (523 points at 7-day spacing — verified). But Lens 1 prose and the footer method describe the same dataset as daily: 'So ~3,650 daily prices are not 3,650 independent observations' (line 139), 'keep every day but tell the math how correlated it is' (line 150), and 'real Coinbase BTC-USD daily closes (≈3,650 obs) for all formal tests' (line 310). A careful reader cannot tell whether the analysis is on 523 weekly points or ~3,650 daily ones. (The formal tests may legitimately run on daily data while the chart is downsampled to weekly, but nothing on the page says so.)
- **Evidence:** line 130: 'Blue = BTC (Coinbase, weekly)'; line 310: '2016–2026 real Coinbase BTC-USD daily closes (≈3,650 obs) for all formal tests'; PL.series length = 523 with 7-day gaps
- **Fix:** Add one clarifying clause so the two cadences are reconciled, e.g. footnote the hero caption: 'chart downsampled to weekly for clarity; all formal tests use daily closes.' If the tests are in fact on the weekly series, correct the '≈3,650 daily' language in lines 139, 150, and 310 to match.
- **Verified / corrected:** The page describes its data cadence inconsistently: the hero figcaption (line 130) says the plotted BTC series is "weekly" (matching PL.series: 523 points at exactly 7-day spacing), while Lens 1 prose (lines 139, 150) and the footer method (line 310) describe the dataset as "daily closes (≈3,650 obs)". Nothing on the page reconciles the two, and the #datanote span that could clarify is set to empty (line 345). The underlying data is in fact downsampled in several ways (weekly series, 5-day residuals, monthly full-history fit), none of it daily as shipped. This is an editorial consistency gap, not a false claim, since the formal tests may legitimately run on daily data the chart downsamples.


### 11. Missing preconnect to fonts.gstatic.com (the actual font-file origin)

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html line 8 (only preconnect present) and line 9 (Google Fonts stylesheet)
- **Issue:** There is a preconnect to https://fonts.googleapis.com (the CSS origin) but none to https://fonts.gstatic.com, which is where the actual .woff2 font files are served from. The googleapis.com stylesheet only returns @font-face rules pointing at gstatic.com, so the connection setup (DNS + TCP + TLS) to gstatic.com is not started until the CSS arrives and is parsed — adding a full round trip before Inter and JetBrains Mono can download. Because body text uses Inter (line 29) and many elements use JetBrains Mono, this delays the visible swap from the system fallback to the intended fonts.
- **Evidence:** <link rel="preconnect" href="https://fonts.googleapis.com"/>
- **Fix:** Add <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> immediately after the existing googleapis preconnect on line 8. The crossorigin attribute is required for font fetches; without it the preconnect is ignored.
- **Verified / corrected:** index.html has a preconnect to fonts.googleapis.com (line 8) but none to fonts.gstatic.com, the origin that serves the actual Inter/JetBrains Mono .woff2 files. Adding <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> saves about one connection-setup round trip on the font fetch. Because the stylesheet loads from the already-preconnected googleapis origin and uses display=swap, the effect is a modest reduction in font-swap latency, not a render-blocking fix.


### 12. All 5 PNG figures lack width/height attributes, causing layout shift (CLS) as each loads

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html lines 141 (fig_lag), 168 (fig_qq), 197 (fig_aic), 223 (fig_residual_dist), 269 (fig_cycles); CSS rule figure img at line 70
- **Issue:** Every <img> for the seaborn figures is rendered with width:100% and no width/height attributes and no CSS aspect-ratio. Until each PNG downloads, the browser does not know its height, so the figure collapses to near-zero height and then jumps to full height when the image arrives, shifting all content below it. The intrinsic sizes differ per figure (fig_aic 952x546, fig_cycles 784x532, fig_lag 784x616, fig_qq 784x588, fig_residual_dist 924x546), so each reserves a different height. This is a textbook Cumulative Layout Shift source affecting five separate scroll positions.
- **Evidence:** <figure><img src="assets/fig_lag.png" alt="Today's deviation versus yesterday's"/>
- **Fix:** Add the intrinsic width and height attributes to each img (e.g. fig_aic: width="952" height="546"; fig_lag: width="784" height="616"; etc.). Combined with the existing width:100% CSS, modern browsers compute the correct aspect-ratio box and reserve space before download, eliminating the shift. Alternatively add aspect-ratio to the figure img rule per image.
- **Verified / corrected:** All five seaborn figure <img> elements lack width/height attributes and the figure img CSS rule (line 70) has no aspect-ratio, so each PNG triggers a small layout shift on load. Real but low severity given small same-origin assets and below-the-fold placement.


### 13. No preconnect/dns-prefetch for the two render-critical third-party origins (plot.ly and jsdelivr)

- **Dimension:** perf · **Confidence:** high
- **Location:** index.html head: preconnect block at line 8; Plotly at line 10; MathJax at line 14
- **Issue:** The page pulls render-affecting resources from cdn.plot.ly (the largest asset, blocking) and cdn.jsdelivr.net (MathJax), but only preconnects to fonts.googleapis.com. For the Plotly origin in particular, the connection handshake (DNS + TCP + TLS) is not started until the parser reaches the script tag, adding a full round trip before the 3.5MB download can even begin.
- **Evidence:** <link rel="preconnect" href="https://fonts.googleapis.com"/>
- **Fix:** Add <link rel="preconnect" href="https://cdn.plot.ly" crossorigin> and <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin> in <head>, ideally before the script tags, so the handshakes overlap with HTML parsing. Lower impact than fixing the blocking script itself, but cheap and complementary.
- **Verified / corrected:** No preconnect/dns-prefetch exists for cdn.plot.ly (render-blocking script, line 10) or cdn.jsdelivr.net (async MathJax, line 14); the only resource hint is a preconnect to fonts.googleapis.com (line 8). Adding preconnect hints is a cheap, low-impact polish; the '3.5MB' size of the Plotly asset is asserted/unverified from the static files and is not central to the finding.


### 14. Hero chart fixed at min-height:540px wastes vertical space and is too tall-but-narrow on phones

- **Dimension:** responsive · **Confidence:** high
- **Location:** index.html — line 129 (id="hero" style="min-height:540px"); also #osc/#lppls/#roll at 360px (lines 219,242,254)
- **Issue:** The hero plot has a hard `min-height:540px` inline (line 129) with no media query to reduce it. On a ~316px-wide phone the chart becomes an awkward 316×540 portrait box for what is fundamentally a wide log–log time series, exaggerating the squeeze from the marginal (related finding) and the 62px left margin. There is exactly one media query in the stylesheet (line 92, grid collapse at 820px) and it does not touch plot heights, so nothing adapts the chart aspect ratio for mobile.
- **Evidence:** '<div id="hero" class="plot" style="min-height:540px"></div>' (line 129); only media query is '@media(max-width:820px){.grid2,.scorecard{grid-template-columns:1fr}}' (line 92)
- **Fix:** Add a mobile rule, e.g. `@media(max-width:560px){#hero{min-height:380px}}`, and consider lowering the other plots' 360px min-heights similarly. Pair with the marginal-hiding fix so the reduced width is spent on the actual series.
- **Verified / corrected:** Accurate as written. Minor refinement: with `.wrap` padding of 22px per side, the effective mobile chart width is ~272px (not 316px) on a 316px viewport, making the tall-narrow box marginally worse than the finding states, not better.


### 15. Nav links are below the 44px minimum tap target in the horizontally scrolling bar

- **Dimension:** responsive · **Confidence:** high
- **Location:** index.html — nav a rule line 42 (font-size:13px;padding:6px 10px) within nav .wrap height:52px overflow-x:auto (line 38)
- **Issue:** The sticky nav is a horizontally scrolling row of nine links (lines 99-107). Each link is `font-size:13px;padding:6px 10px` (line 42): computed height ≈ 13px line box + 12px vertical padding ≈ 25-30px, well under the 44×44px touch target recommended by WCAG 2.5.5 / Apple HIG. They sit inside a 52px-tall bar that itself scrolls horizontally (`overflow-x:auto` line 38) with hidden scrollbars (lines 38-39), so on a phone a user must accurately tap a ~28px-tall target while also being able to scroll the strip — easy to mis-tap or accidentally scroll. Adjacent links ('Spurious?', 'Model tournament', etc.) are only `gap:6px` (line 38) apart, compounding mistaps.
- **Evidence:** nav a{color:var(--mute);font-size:13px;padding:6px 10px;border-radius:7px;white-space:nowrap;font-weight:500} (line 42); nav .wrap{...height:52px;overflow-x:auto;scrollbar-width:none} (line 38)
- **Fix:** Increase vertical padding so each link is ≥44px tall (e.g. `nav a{padding:11px 12px}` and raise `nav .wrap{height:auto;min-height:48px}` or use `min-height:44px` on the links), and/or increase `gap` on touch widths. Since the bar already scrolls, taller targets won't break the layout.
- **Verified / corrected:** Each nav link computes to roughly 33px tall (font-size 13px × inherited line-height 1.65 ≈ 21.45px line box + 6px top/bottom padding ≈ 33.5px), not 25-30px as stated. Still under the 44px touch-target recommendation, so the conclusion holds; only the height figure was slightly understated.


### 16. No Subresource Integrity on the pinned Plotly script

- **Dimension:** security · **Confidence:** high
- **Location:** index.html line 10: <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
- **Issue:** Plotly is correctly version-pinned to 2.35.2 (good — it is reproducible), but it has no `integrity`/`crossorigin` attributes. If cdn.plot.ly is compromised or DNS/CDN-hijacked, an attacker can swap in arbitrary JavaScript that runs with full page privileges. Because this is the largest dependency and the only one that is already pinned (so SRI is fully applicable), it is the single highest-value place to add SRI. Note: cdn.plot.ly is Plotly's own origin (Fastly-backed), not a generic multi-tenant CDN, but the threat model for a static page that quotes financial figures still warrants integrity pinning.
- **Evidence:** <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>  (no integrity= on line 10; grep for 'integrity' across index.html returns nothing)
- **Fix:** Add SRI + crossorigin: `<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" integrity="sha384-..." crossorigin="anonymous" charset="utf-8"></script>`. Compute with `curl -s https://cdn.plot.ly/plotly-2.35.2.min.js | openssl dgst -sha384 -binary | openssl base64 -A`. Alternatively, serve plotly from jsDelivr (`https://cdn.jsdelivr.net/npm/plotly.js@2.35.2/dist/plotly.min.js`) whose UI provides ready-made SRI hashes, or self-host it under assets/.
- **Verified / corrected:** index.html line 10 loads version-pinned Plotly 2.35.2 from cdn.plot.ly with no integrity/crossorigin attributes (confirmed; no "integrity" anywhere in the file). Adding SRI is valid defense-in-depth, but on a static, no-auth, no-data informational page the impact is page defacement / arbitrary JS in a benign origin, not exposure of any sensitive data — low, not high. Note the unpinned MathJax moving tag on line 14 is a larger and SRI-incompatible supply-chain exposure than the pinned Plotly script.


### 17. No Content-Security-Policy (no meta CSP) to constrain script/style/connect origins

- **Dimension:** security · **Confidence:** high
- **Location:** index.html <head> (lines 3-15) — no <meta http-equiv="Content-Security-Policy"> present; grep for 'http-equiv'/'content-security' returns nothing
- **Issue:** GitHub Pages cannot set HTTP response headers, so a `<meta http-equiv="Content-Security-Policy">` is the only available CSP mechanism for this site — and it is absent. Without a CSP, if any third-party script (Plotly/MathJax, neither of which has SRI) is tampered with, or if any injection vector ever appears, there is no second line of defense restricting which origins scripts may load from or exfiltrate to. A CSP would also formally document the trusted origins (cdn.plot.ly, cdn.jsdelivr.net, fonts.googleapis.com, fonts.gstatic.com).
- **Evidence:** grep -ni 'http-equiv|content-security' index.html -> (no matches)
- **Fix:** Add a meta CSP in <head>, e.g. `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' https://cdn.plot.ly https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; base-uri 'none'">`. The inline <script>/<style> and Plotly's runtime styling force `'unsafe-inline'` here (a known meta-CSP limitation), but the directive still pins external origins and blocks unexpected connect/img/font destinations. Test in the browser console for violations after adding, since MathJax may need script-src to include jsdelivr (it does, above).
- **Verified / corrected:** No meta CSP is present (confirmed), but because the recommended policy requires script-src 'unsafe-inline' for the page's inline script/style/MathJax/Plotly, the CSP would not defend against the tampered-third-party-script scenario the finding emphasizes; its real benefit is limited to pinning external origins and constraining connect/img/base-uri on a static, same-origin, no-auth page — defense-in-depth hardening, hence low rather than medium.


### 18. Google Fonts stylesheet has no SRI and leaks visitor IP/User-Agent to Google at runtime

- **Dimension:** security · **Confidence:** high
- **Location:** index.html lines 8-9: <link rel="preconnect" href="https://fonts.googleapis.com"/> and <link href="https://fonts.googleapis.com/css2?family=Inter...&family=JetBrains+Mono...&display=swap" rel="stylesheet"/>
- **Issue:** Two privacy/supply-chain notes. (1) Every page load fetches the stylesheet from fonts.googleapis.com and then the font binaries from fonts.gstatic.com, sending each visitor's IP address and User-Agent to Google — a third-party data leak some jurisdictions (e.g. a 2022 German court ruling) treat as a GDPR issue, and which is inconsistent with a privacy-conscious personal site. (2) SRI is not meaningfully applicable to the Google Fonts css2 endpoint because Google serves UA-tailored CSS (different @font-face URLs per browser), so an integrity hash would break across clients — do NOT claim SRI is the fix here. The honest remediation is self-hosting.
- **Evidence:** <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
- **Fix:** Self-host the two fonts: download the Inter and JetBrains Mono woff2 files (e.g. via google-webfonts-helper), place them under assets/fonts/, and replace the <link> with local @font-face rules in the existing <style>. This removes the runtime third-party request entirely (better privacy AND supply-chain posture) and lets you drop the fonts.googleapis preconnect on line 8. If you keep the CDN, at minimum add `crossorigin` to the preconnect.
- **Verified / corrected:** Lines 8-9 do load Google Fonts at runtime, leaking visitor IP/User-Agent to Google; self-hosting (not SRI) is the correct fix, and the finding says so. But the same IP/UA already leak to cdn.plot.ly (line 10) and cdn.jsdelivr.net (line 14), so this is one of several CDN dependencies rather than a uniquely fonts-driven leak. Appropriate severity is low/nit, not a security vulnerability.


### 19. No Twitter Card meta: X/Twitter previews degrade to a plain link

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head)
- **Issue:** There is no <meta name="twitter:card"> (nor twitter:title/description/image). Without it, X renders a bare-link card. Every other shared page on the site sets it; Q.html line 14 uses summary_large_image. Quant/finance content like this is frequently shared on X, so the omission is consequential.
- **Evidence:** No 'twitter:' string exists anywhere in index.html. Q.html line 14: '<meta name="twitter:card" content="summary_large_image">'.
- **Fix:** Add '<meta name="twitter:card" content="summary_large_image">' and (optionally) twitter:title/twitter:description/twitter:image. Twitter will fall back to the OG tags for title/description/image, so at minimum the twitter:card declaration plus the OG block from the previous finding is enough.
- **Verified / corrected:** index.html for bitcoin-power-law has no twitter:card (nor og:* tags), so X renders a plain text card from the standard <title>/description. This is real but minor: only 2 of 14 root pages on the site set twitter:card, so it is not a broken site-wide convention, and the page still yields a title+description preview. Fix by adding <meta name="twitter:card" content="summary_large_image"> plus an Open Graph block (og:title/og:description/og:image/og:url) so the card actually shows an image.


### 20. No canonical link: the page is reachable at two URLs with no canonical signal

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head)
- **Issue:** There is no <link rel="canonical">. GitHub Pages serves this index at both https://scottn66.github.io/bitcoin-power-law/ and https://scottn66.github.io/bitcoin-power-law/index.html, and trailing-slash variants. Without a canonical, search engines may treat these as duplicates and split ranking signals, and OG/Twitter scrapers have no authoritative URL to attribute shares to.
- **Evidence:** No 'rel="canonical"' present in index.html. The page is one HTML file served from a directory, so both /bitcoin-power-law/ and /bitcoin-power-law/index.html resolve.
- **Fix:** Add '<link rel="canonical" href="https://scottn66.github.io/bitcoin-power-law/"/>' to <head> (same URL used for og:url).
- **Verified / corrected:** No <link rel="canonical"> is present (confirmed). Note the page also has no Open Graph or Twitter Card tags whatsoever, so the OG/Twitter-attribution argument is part of a larger social-metadata gap rather than a canonical-only issue. Fix: add <link rel="canonical" href="https://scottn66.github.io/bitcoin-power-law/"/> to the head.


### 21. No favicon / apple-touch-icon: blank tab icon, inconsistent with house style

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head); also no icon files in assets/
- **Issue:** There is no <link rel="icon"> and no favicon asset in the folder, so browsers show a blank/default tab icon and bookmarks/home-screen saves have no icon. The site has an established pattern: decision-theory.html line 12-13 and robot-arm-sim/index.html line 11 both use an inline SVG-emoji data-URI favicon. The page even has a natural glyph for it — the bitcoin '₿' used in the nav brand (index.html line 98).
- **Evidence:** No 'rel="icon"' in index.html; 'find' for *favicon*/*.ico/apple-touch* in the page folder returns nothing. House pattern, decision-theory.html: '<link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns=...><text y=13 font-size=13>🪜</text></svg>" />'.
- **Fix:** Add an inline SVG-emoji favicon matching the house pattern, e.g. a '₿' glyph: '<link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='13' font-size='13'>₿</text></svg>"/>'. Optionally add an apple-touch-icon.
- **Verified / corrected:** The page has no favicon/apple-touch-icon, so tabs and bookmarks show a default icon. This is a minor branding/polish inconsistency (not a real SEO issue), and the house data-URI-favicon pattern is present on only 2 of 53 site pages rather than being a site-wide standard. Fix by adding an inline SVG ₿ favicon to the head, matching the pattern in decision-theory.html line 12.


### 22. No theme-color meta despite a fully dark UI

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head; background defined at line 18 --bg:#0a0d12)
- **Issue:** The page is a deeply dark theme (--bg:#0a0d12, sticky translucent nav) but declares no <meta name="theme-color">. On mobile Chrome/Android and some PWA contexts the browser chrome will not match the page, producing a jarring light bar above the dark content.
- **Evidence:** index.html line 18 sets '--bg:#0a0d12'; no 'theme-color' meta exists in the file.
- **Fix:** Add '<meta name="theme-color" content="#0a0d12">' to <head> to match the page background.
- **Verified / corrected:** No <meta name="theme-color"> exists in index.html; adding one matching --bg (#0a0d12) would align mobile browser chrome with the dark UI. This is a UX/polish nit rather than a true SEO issue.


### 23. No JSON-LD structured data despite the page being a textbook ScholarlyArticle

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head)
- **Issue:** The page is a long-form research note with a clear author, method/reproducibility section, references (Santostasi, Burger, Sornette), and a generated date — an ideal candidate for schema.org Article or ScholarlyArticle markup, which can enable richer search results and author attribution. The site already uses JSON-LD elsewhere (root index.html has a Person block), so the pattern exists. Currently there is none here.
- **Evidence:** No 'application/ld+json' script in index.html. Root index.html lines 19-32 contain a '@type":"Person"' JSON-LD block, establishing the house uses structured data. The page has the raw fields: footer 'Generated <span id="genfoot">' (data.js generated_at='2026-06-16 07:20 UTC'), author byline material, and a reference list.
- **Fix:** Add a JSON-LD '@type":"ScholarlyArticle"' (or 'Article') block with headline, description, author (Person: Scott Nelson), datePublished/dateModified (from data.js generated_at), and an image (the og-image). Keep it server-static rather than relying on the runtime data.js.
- **Verified / corrected:** No JSON-LD structured data exists in bitcoin-power-law/index.html. Adding a static `@type:"ScholarlyArticle"` (or "Article") block with headline, description, author (Person: Scott Nelson), datePublished/dateModified, and references is a reasonable low-severity SEO enhancement. Note: the page also has no Open Graph/Twitter tags and no og-image asset, so the "image" field cannot reference an existing og-image; it would need a new asset or could point to one of the existing seaborn figure PNGs.


### 24. Em-dash in <title> violates house style and risks awkward SERP/social truncation

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html line 6
- **Issue:** The title 'Does Bitcoin Follow a Power Law? — An Econometric Autopsy' contains a literal em-dash (—). The site owner deliberately strips em-dashes from crawler/published pages (prior commit 'Strip em-dashes across crawler pages'), so this is an explicit house-style violation in the single most SEO-load-bearing string. The whole page body is also riddled with em-dashes, but the title is the one that shows in the browser tab, search results, and as the default OG/Twitter title. At ~52 characters it is borderline for SERP width, and the em-dash plus the trailing ' — An Econometric Autopsy' is exactly the kind of suffix Google truncates.
- **Evidence:** index.html line 6: '<title>Does Bitcoin Follow a Power Law? — An Econometric Autopsy</title>' — the '—' is a U+2014 em-dash. Author's own published-corpus titles that pre-date the strip still show — (e.g. line 12 'City Cartography — Roads...'), confirming em-dash is the thing being removed.
- **Fix:** Replace the em-dash with a colon or middot to match house style, e.g. '<title>Does Bitcoin Follow a Power Law? An Econometric Autopsy</title>' or '... Power Law? · An Econometric Autopsy'. Apply the same to og:title/twitter:title when added. (A full body em-dash sweep is out of scope for SEO but consistent with the owner's stated preference.)
- **Verified / corrected:** index.html line 6 title contains a U+2014 em-dash (verified via hexdump e2 80 94), violating the owner's documented house style (commit 946ac63 "Strip em-dashes across crawler pages"; published-corpus.json normalizes em-dashes to —). The title is 57 characters (not ~52). There are no og:title/twitter:title tags, so <title> is the sole tab and default social title. The defect is style inconsistency; em-dashes are valid in titles and the truncation risk is mild. Severity low is correct.


### 25. Four <figcaption> elements are not inside a <figure> (W3C validator error)

- **Dimension:** standards · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html lines 130, 220, 243, 255
- **Issue:** Per the HTML spec, a <figcaption> element must be a child of a <figure> element. Four captions are instead direct children of <div class="card">. Line 128-131: <div class="card"> ... <figcaption>Interactive: hover for fair value...</figcaption></div>. Same pattern at line 218-221 (oscillator), 241-244 (LPPLS), and 253-256 (rolling exponent). The W3C Nu validator reports each as a hard error: 'Element figcaption not allowed as child of element div in this context' / 'The figcaption element must be the first or last child of a figure element.' These four caption divs wrap a Plotly <div> (#hero, #osc, #lppls, #roll) rather than an <img>, so the author used a bare <figcaption> without the surrounding <figure>. Note the genuinely correct usage elsewhere (e.g. lines 141-142, 168-169, 197-198) where <figcaption> IS nested in <figure> with an <img> — so this is an inconsistency, not a global pattern.
- **Evidence:** line 128 `<div class="card">`, line 129 `<div id="hero" class="plot" ...></div>`, line 130 `<figcaption>Interactive: hover for fair value vs. actual...`
- **Fix:** Change the four wrapping `<div class="card">` to `<figure class="card">` (figure may contain flow content including the Plotly div plus a trailing figcaption), or replace the bare `<figcaption>` with a plain `<p class="figcaption">` / `<div class="cap">` styled the same. The simplest fix that preserves styling: add a `figure.card{...}` rule (or reuse `.card`) and swap `<div class="card">`→`<figure class="card">` (with matching `</figure>`) at lines 128/131, 218/221, 241/244, 253/256.
- **Verified / corrected:** Four bare `<figcaption>` elements (index.html lines 130, 220, 243, 255) are direct children of `<div class="card">` instead of a `<figure>`, a W3C/HTML-spec conformance error. Real but cosmetic/standards-only — appropriately low severity, not high, since it does not affect rendering, function, security, or meaningfully affect SEO.


### 26. Model-tournament verdict calls a ΔAIC of 372 an "edge" — contradicting the page's own ">10 = decisively worse" rule

- **Dimension:** stats · **Confidence:** high
- **Location:** index.html — Lens 3, fig_aic figcaption (line 198) and v-warn verdict (line 199); also README.md line 19
- **Issue:** The recent-window model table (PL.model_comparison) has logistic ΔAIC=0 and power law ΔAIC=+372.5 (verified: power delta_aic=372.55, stretched +374.7, exp +1146). One paragraph earlier the page itself defines the rule of thumb "<2 ≈ a tie, >10 = decisively worse" (line 179). Yet the caption says "over the last decade a saturating logistic edges it" and the verdict says "a logistic S-curve fits better" / scorecard says "A logistic fits the recent decade better; the data can't separate them" (line 298). A gap of 372 AIC points is not an "edge" and is not "data can't separate them" — by the page's stated criterion the power law is decisively beaten in that window. The hedge language directly contradicts the rendered number and the page's own rule.
- **Evidence:** data.js model_comparison: power delta_aic=372.5478934052735; index.html line 198 "a saturating logistic edges it"; line 179 ">10 = decisively worse"; line 298 "the data can't separate them"
- **Fix:** Either reword to reflect the magnitude (e.g. "on the recent window the logistic decisively outfits the power law, ΔAIC≈373") OR, if the intended message is genuine indistinguishability, explain why a 372-point AIC gap should be discounted (effective-sample-size deflation) with an actual corrected number — do not call 372 an "edge" or claim the data "can't separate them" while showing 372.
- **Verified / corrected:** The page does NOT leave a 372-point gap unexplained or simply call it an "edge"/"can't separate them" in contradiction of its own rule. Line 199 explicitly discounts the nominal gap via effective-sample-size deflation (ρ≈0.998 ⇒ tiny effective N ⇒ inflated AIC gaps), which is the very justification the finding demanded. The only real defect is the loose word "edges" in the figcaption (index.html:198) and README:18, where the effective-N caveat is not restated alongside the number — a low-severity wording polish, not a critical false claim.


### 27. Rolling-exponent chart's dashed "full-sample n" line and label use 5.43 (Coinbase), not the 5.54 full-history value the chips advertise

- **Dimension:** stats · **Confidence:** high
- **Location:** index.html — #roll chart, lines 555 and 557 (shapes/annotation use fc.n); figcaption line 255
- **Issue:** The Lens 6 rolling chart draws a dashed reference line and annotates it "full-sample n=5.43" using fit_coinbase.n (PL.fit_coinbase.n=5.4258). But the page's headline chip "Exponent n" shows 5.54 from fit_full (PL.fit_full.n=5.5413), and the hero/Lens-0 framing treats 5.54 as the canonical full-history exponent. So the page presents two different numbers both called the "full-sample"/headline exponent (5.54 vs 5.43) with no signposting of which sample each refers to. The caption "dashed orange = the full-sample n" is misleading because that dashed line is the 2016–2026 Coinbase fit, not the full-history fit the chip touts.
- **Evidence:** data.js fit_full.n=5.541342452426244 (chip), fit_coinbase.n=5.425751166749155 (rolling ref); index.html line 557 annotation text 'full-sample n='+(fc.n||0).toFixed(2); caption line 255 'dashed orange = the full-sample $n$'
- **Fix:** Label the dashed line precisely (e.g. "Coinbase-window n=5.43") and/or note that the headline chip 5.54 is the full-history monthly fit while 5.43 is the daily Coinbase fit, so readers don't read the two as inconsistent estimates of the same quantity.
- **Verified / corrected:** The dashed line label "full-sample n=5.43" is not strictly misleading in isolation (it is the full-sample fit of the rolling chart's own Coinbase daily series, and matches the Lens-1 inference table's 5.426); the real issue is the absence of signposting distinguishing it from the hero chip's full-history monthly exponent of 5.54. This is a low-severity clarity gap, not a high-severity correctness error.


### 28. Hero verdict says the line spans "$0.05 (2010) to six figures (2026)" but today's price is five figures ($74k)

- **Dimension:** stats · **Confidence:** high
- **Location:** index.html — Lens 0 v-real verdict, line 132 ("from $0.05 (2010) to six figures (2026)")
- **Issue:** current.price = $74,243 — five figures, not six. The model fair-value line at the right edge (current.model_price ≈ $129,291) is six figures, but the verdict sentence is about where the actual data/line lands ("a single straight line spans ... and independent early-era prices land on it"). A reader sees the live price chip implicitly (today $74k via the chart) and the verdict claiming "six figures (2026)," which overstates the current actual price by ~74%. BTC was briefly six figures earlier in the cycle (cycle-4 peak $124,720 in data.js) but the sentence pins "six figures" to 2026, the year of a $74k current print.
- **Evidence:** data.js current.price=74243.14 (5 figures) for date 2026-05-27; current.model_price=129291 (6 figures); index.html line 132 'to six figures (2026)'
- **Fix:** Either say "to the high five figures (2026)" / "to ~$74k today (with the fitted line near six figures)" or attribute the six-figure mark to the 2025 cycle peak ($124.7k), not to the 2026 current price. Avoid implying today's price is six figures.
- **Verified / corrected:** The line 132 verdict's "to six figures (2026)" is literally accurate for the fitted line (model_price $129,291 at the 2026 edge), but ambiguous because the actual BTC price in 2026 is five figures ($74,243). The risk is a reader misreading it as a claim about today's actual price; it is a clarity nit, not a false statement.


### 29. Footer says HAC errors use a 365-lag Newey–West window, but the displayed lag-1 autocorrelation is ~0.998 — and the table reports HAC SE ±0.54 with no lag disclosed

- **Dimension:** stats · **Confidence:** high
- **Location:** index.html — footer method note line 309 ("Newey–West (HAC, 365-lag)"); Lens 1 fit table line 424 (n_se_hac)
- **Issue:** With ρ≈0.998 on weekly data, a 365-lag Newey–West window would extend roughly 7 years (365 weeks), which is implausibly long for a ~523-point weekly series and would consume most of the sample; conversely if the data were truly daily, 365 lags is one year, which is defensible. The 365-lag claim only makes sense for daily data, but the series shipped is weekly — so the method note is internally inconsistent with the data file (compounding the daily-vs-weekly issue above). The fit table reports HAC SE ±0.54 (n_se_hac=0.539) without stating the lag, so a reader can't reconcile it with the footer.
- **Evidence:** index.html line 309 'Newey–West (HAC, 365-lag)'; data.js fit_coinbase.n_se_hac=0.5391722812825759; series is weekly (523 pts)
- **Fix:** State the HAC lag in the units of the actual data and choose a value consistent with the sampling frequency (e.g. a data-driven Bartlett bandwidth). Reconcile the footer's 365-lag claim with whatever frequency series actually uses.
- **Verified / corrected:** The method note (index.html line 309) specifies a 365-lag Newey–West window, which is consistent with the footer's own claim of daily data (line 310, ≈3,650 daily obs) but mismatched against the actually-shipped PL.series, which is weekly (523 points, 7-day spacing). This is essentially the daily-vs-weekly data discrepancy, not a self-contained footer contradiction. Separately, the fit table (line 424) shows the HAC SE as "± 0.54" without restating the lag — a minor disclosure point — and the table's "≈ 0.998" lag-1 autocorrelation (line 426) is a hardcoded value; the real residual lag-1 autocorrelation is ~0.987.


### 30. Cointegration story is internally inconsistent: Lens 2 table reports "no cointegration" while the scorecard says cointegration is "undefined vs a deterministic clock"

- **Dimension:** stats · **Confidence:** high
- **Location:** index.html — Lens 2 #statab Engle–Granger row (line 440, renders "no cointegration") vs scorecard line 299 ("cointegration is undefined vs. a deterministic clock")
- **Issue:** The page makes a correct and sophisticated point in the scorecard and README: cointegration is undefined when one regressor (log age) is a deterministic clock rather than a stochastic I(1) process, so the "spurious regression" label is misapplied. But the Lens 2 table still runs an Engle–Granger test (eg_p=0.428) and prints the reading "no cointegration" as if the concept applied — directly contradicting the scorecard's own caveat that the test is undefined here. Reporting an EG p-value and a "no cointegration" verdict for a regression on a deterministic trend is methodologically wrong by the page's own later admission.
- **Evidence:** data.js cointegration.eg_p=0.42777635425250127; index.html line 440 Engle–Granger reading 'no cointegration'; line 299 'cointegration is undefined vs. a deterministic clock'
- **Fix:** In the Lens 2 table, mark the Engle–Granger row as "not applicable — regressor is a deterministic clock, cointegration undefined" (consistent with the scorecard), instead of reporting a p-value and a "no cointegration" reading that the page elsewhere says is meaningless.
- **Verified / corrected:** The Lens 2 #statab Engle–Granger row (index.html line 440) prints the reading "no cointegration" without carrying the "cointegration is undefined vs. a deterministic clock" caveat that the scorecard (line 299), prose (line 162), and README (lines 15-16) make central — a genuine internal inconsistency. It is not, however, a factually false statement (it is the test's literal output and is directionally consistent with the page's "descriptive trend, not a proven law" verdict), so the impact is low rather than medium.


### 31. Latent contradiction in data.js: lppls.interpretation claims ω=4 is in the bubble bounds and valid_omega=true, opposite to the page's stated ω∈[6,13] filter

- **Dimension:** stats · **Confidence:** high
- **Location:** assets/data.js — lppls.interpretation and lppls.valid_omega/valid_omega flags; cf. index.html Lens 5 prose line 238 and lppls_cycles 2021 row
- **Issue:** Not currently rendered (the JS lppls block does not print lp.interpretation), so it's not shown to readers — hence low severity. But it is an internal data inconsistency that would surface if the template ever displayed it: lppls.interpretation states "m=0.81, ω=4.0 fall in the literature's bubble-regime bounds — log-periodic acceleration is detectable" and lppls.valid_omega=true, whereas the page's Lens 5 text explicitly sets the acceptance band at ω∈[6,13] with ω≈4 being the search FLOOR that fails, and lppls_cycles' 2021 row correctly has passes_strict_filter=false for the same ω=4. The acceptance logic in the data generator disagrees with itself (valid_omega=true for ω=4) and with the page's prose.
- **Evidence:** data.js lppls.omega=4, lppls.valid_omega=true, interpretation '...ω=4.0 fall in the literature's bubble-regime bounds...'; lppls_cycles 2021 omega=4 passes_strict_filter=false; index.html line 238 'accept ... only if $\omega\in[6,13]$'
- **Fix:** Fix the data generator so valid_omega reflects the stated [6,13] acceptance band (ω=4 should be false), and correct the interpretation string to say ω=4 sits at the search floor and fails the bubble filter — so the cached interpretation can't later be surfaced as a contradiction.
- **Verified / corrected:** In assets/data.js, lppls.valid_omega=true and lppls.interpretation both treat ω=4 as a valid bubble-regime frequency, contradicting (a) index.html line 238's stated acceptance band ω∈[6,13], (b) line 245's verdict that ω=4 "collapses to the search floor" and fails, and (c) lppls.passes_strict_filter=false (and lppls_cycles' 2021 row) for the same ω=4. The contradiction is purely latent: lppls.interpretation is never rendered (the LPPLS IIFE at index.html lines 516-543 never reads it; line 509's interpretation belongs to the mean_reversion block), so no reader sees it. Hence low severity — a data-hygiene bug, not a reader-facing falsehood.


## ▪️ Nit (10)

### 1. ₿ brand glyph and decorative icon characters have no text alternative

- **Dimension:** a11y · **Confidence:** high
- **Location:** index.html: nav brand <b>₿</b> line 98; '⛏ halving' annotations generated at script line 559; '★' scorecard lenstag line 279; '▸' win marker line 455; pill text '✓ Holds up'/'✗ Does not survive' lines 283/293
- **Issue:** The Bitcoin glyph ₿ is used as the logo in the nav brand. Standalone it may be read as 'B with stroke', an unfamiliar symbol name, or skipped depending on the screen reader, so the brand is announced ambiguously. Similarly the ⛏ (pick) halving markers, ★, ▸, ✓ and ✗ are decorative/semantic Unicode characters with no aria handling. The ✓/✗ in the scorecard headings ('✓ Holds up' / '✗ Does not survive') carry real meaning (pass vs fail) conveyed by symbol+color; a screen reader may announce them inconsistently.
- **Evidence:** <span class="brand"><b>₿</b> Power Law</span> — the ₿ glyph is the visual logo with no aria-label on the brand element
- **Fix:** Give the brand an accessible name: e.g. <span class="brand" aria-label="Bitcoin Power Law"><b aria-hidden="true">₿</b> Power Law</span>. Mark purely decorative glyphs (★, ▸, ⛏) aria-hidden. For the scorecard, ensure the heading text 'Holds up' / 'Does not survive' is read independent of the check/cross glyph (it currently is, since the words follow the glyph — keep that, and aria-hidden the symbol).
- **Verified / corrected:** The accessibility gap is real (no aria handling anywhere in the file), but it is nit-level, not a meaningful UX gap: the brand reads as "bitcoin sign Power Law" on modern AT, the ⛏ marker lives in a Plotly chart that AT largely ignores anyway, and the scorecard pass/fail meaning is carried by the words "Holds up"/"Does not survive" (read independently of the ✓/✗ glyph), so no information is lost. Minor location slip: the ▸ win marker is generated at index.html line 453, not 455.


### 2. Worst drawdown rendered as a double-negative "-84%" after the prose says "reached"

- **Dimension:** correctness · **Confidence:** high
- **Location:** index.html line 267 (#ddpct span) bound at line 594; risk card "Worst drawdown on record" at line 582
- **Issue:** max_drawdown_pct in data.js is stored as a signed value -83.80. Both bindings do Math.round(rk.max_drawdown_pct)+'%', producing the literal string "-84%". In the body text the sentence reads "its worst drawdown reached -84%", and the risk-card row "Worst drawdown on record" shows "-84%". A drawdown is already a loss, so "reached -84%" / "Worst drawdown … -84%" is a double negative; the intended magnitude is 84% (or "-84%" only if you drop the word 'drawdown'). Readers may also misread -84% as a smaller loss than 84%.
- **Evidence:** max_drawdown_pct = -83.8015349610509 -> Math.round = -84; ddpct text = "-84%"; riskcard worst drawdown = "-84%"
- **Fix:** Render the absolute value: Math.round(Math.abs(rk.max_drawdown_pct))+'%' so it shows "84%", matching the noun "drawdown". Apply at both line 594 (#ddpct) and line 582 (riskcard).
- **Verified / corrected:** Both bindings (index.html line 582 riskcard and line 594 #ddpct) render "-84%" from PL.risk.max_drawdown_pct = -83.80. This is a stylistic redundancy ("worst drawdown ... -84%"), not a factual error — negative-signed drawdowns are a standard finance convention. Optional polish: render Math.abs to show "84%".


### 3. PL.projections is loaded but never read; PL.model_line.q05/q25/q75/q95 are shipped but unused

- **Dimension:** correctness · **Confidence:** high
- **Location:** data.js keys 'projections' and 'model_line.q05/q25/q75/q95'; consumed nowhere in the index.html inline script
- **Issue:** The data bundle contains a top-level 'projections' object and four pre-computed corridor-quantile arrays inside model_line (q05/q25/q75/q95, 200 points each). The inline script never references PL.projections, and the hero chart computes its ±1σ/±2σ bands from ml.mid and fit_full.resid_sigma rather than from the shipped quantiles. This is dead payload (the q-arrays alone are a large share of the 108KB data.js) and, more importantly, the displayed bands use a parametric ±σ corridor while the data ships an empirical-quantile corridor that disagrees with it (e.g. at the last index mid/10^(1.645σ) = 2.86e7 vs shipped q05 = 3.74e7), so any future code reading the quantiles would render a different corridor than the chart.
- **Evidence:** Object.keys(window.PL) includes 'projections'; model_line keys = ['dates','mid','q05','q25','q75','q95'] but script only reads ml.dates and ml.mid (lines 349-355). Script bands: up=(m,k)=>m*Math.pow(10,k*sigma) with sigma=fit_full.resid_sigma (line 353).
- **Fix:** Either drop the unused 'projections' object and the q05/q25/q75/q95 arrays from data.js to shrink the payload, or switch the hero bands to plot the shipped empirical quantiles so the chart and the data agree. Decide which corridor definition is authoritative and use it consistently.
- **Verified / corrected:** PL.projections and model_line.q05/q25/q75/q95 are loaded in data.js but never referenced by index.html or README (dead payload ≈14.2% of the file: q-arrays 13.7%, projections 0.5%). The hero chart draws only ±1σ and ±2σ bands computed parametrically from ml.mid and fit_full.resid_sigma, which disagree with the shipped (asymmetric) empirical quantiles — e.g. at the last index shipped q05=3.74e7 vs a parametric 5th-percentile of 2.86e7. The chart never renders a 1.645σ band, so that specific comparison is illustrative of the corridor-definition mismatch rather than a band shown to readers.


### 4. Long em-dashed display equations rely solely on .eq overflow; verify they actually scroll rather than clip inside padded card

- **Dimension:** responsive · **Confidence:** high
- **Location:** index.html — LPPLS formula in .card.eq (lines 235-237); OU equation in .card.eq (lines 207-210); .eq rule line 83
- **Issue:** The wide MathJax display equations ARE wrapped in `.card.eq` (lines 124, 207, 235), so they inherit `overflow-x:auto` (line 83) and should scroll — this is correct and is the right pattern. The residual risk is that `.card.eq` also inherits `.card{padding:18px}` (line 67), and the LPPLS SVG `$$ \ln p(t) = A + B\,(t_c-t)^m + C\,(t_c-t)^m\cos(...) $$` (line 236) at `font-size:15px` (line 235) is the widest single element on the page (~520px+ on desktop). On a 316px card it will overflow its content box; `overflow-x:auto` makes it scrollable, but MathJax centers display math, so the start of the long formula can be scrolled off-left and there is no scroll affordance hint. This is a minor UX wrinkle, not breakage, but worth confirming on a real device that the formula is reachable and not visually clipped by the rounded card corners.
- **Evidence:** .eq{overflow-x:auto;padding:6px 2px;color:#dbe4ee} (line 83); '<div class="card eq" style="font-size:15px">' then '$$ \ln p(t) = A + B\,(t_c-t)^m + C\,(t_c-t)^m\cos\!\bigl(\omega\ln(t_c-t)-\phi\bigr) $$' (lines 235-236)
- **Fix:** Confirm on a 360px device. If the centered overflow hides the formula's left edge, set the inner equation to left-align on small screens (`@media(max-width:560px){.eq{text-align:left}}`) and/or reduce display-math font-size on mobile. Optionally add `padding-bottom` so the horizontal scrollbar doesn't overlap the formula.
- **Verified / corrected:** The wide display equations (LPPLS lines 235-237, OU lines 207-210) correctly scroll inside their `.card.eq` boxes via `overflow-x:auto` (line 83) and are NOT clipped by the card's rounded corners (no `overflow:hidden` on `.card`), and the full formula IS reachable by horizontal scroll. The only real issue is cosmetic: centered display math may rest mid-formula on narrow screens with no scroll affordance — a nit-level polish item, not a rendering or reachability bug.


### 5. Gradient-clipped hero heading has no solid-color fallback if background-clip:text is unsupported

- **Dimension:** responsive · **Confidence:** high
- **Location:** index.html — h1 .g rule line 48
- **Issue:** The word 'power law' in the H1 uses `-webkit-text-fill-color:transparent` together with `-webkit-background-clip:text;background-clip:text` and an orange gradient (line 48). Modern Safari/Chrome/Firefox support this, so it renders correctly in current browsers. However, `-webkit-text-fill-color:transparent` is applied unconditionally: in any engine that supports `-webkit-text-fill-color` but NOT `background-clip:text` (older or niche browsers, some in-app webviews), the text becomes fully transparent and the headline word disappears entirely — the title reads 'Does Bitcoin follow a ?'. There is no `color` fallback declared before the transparent fill.
- **Evidence:** h1 .g{background:linear-gradient(95deg,var(--orange),#ffb454);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent} (line 48)
- **Fix:** Add a supports guard or fallback color: set `color:var(--orange)` on `.g` first, then wrap the clip/transparent declarations in `@supports ((background-clip:text) or (-webkit-background-clip:text)){ h1 .g{ -webkit-text-fill-color:transparent; ... } }`. This guarantees a visible orange word if clip-to-text isn't honored.
- **Verified / corrected:** The `.g` gradient-text rule (index.html line 48) lacks a solid-color fallback, so a browser that supports `-webkit-text-fill-color` but not `background-clip:text` would render the word "power law" (line 112) transparent. Real but a cosmetic edge case: both prefixed and unprefixed `background-clip:text` are present and supported by all current major engines, the affected text is one decorative hero word, and the full question still appears in the title/meta/body — nit-level, not low.


### 6. innerHTML built from data.js strings — currently safe (author-controlled), but an unescaped sink worth hardening

- **Dimension:** security · **Confidence:** high
- **Location:** index.html inline <script>, innerHTML assignments at lines 341, 429, 444, 458, 490, 502, 538, 567, 578, 586 (free-text fields: mean_reversion.interpretation, risk.interpretation, risk.prediction.interpretation, lppls_cycles[].label, model_comparison.models[].model, stability.chow_tests[].halving, anchors[].note)
- **Issue:** Ten innerHTML sinks interpolate values from window.PL directly into markup without escaping, including free-text fields such as `m.interpretation`, `rk.interpretation`, `pred.interpretation`, `c.label`, and `m.model`. Today this is NOT an exploitable XSS hole: data.js is generated at build time by the author's own Python scripts (pl_data.py), there is no user input or query-string/localStorage data on the page, and I confirmed every current string value is plain prose/dates with no HTML or script (e.g. mean_reversion.interpretation = "Deviations mean-revert with half-life ~278 days..."). The risk is purely latent: if the data pipeline ever ingests an externally-sourced string (an exchange label, a news snippet, a future API field) and forwards it into one of these strings, it would execute as HTML. Flagging as defense-in-depth, not a live vulnerability.
- **Evidence:** document.getElementById('mrcard').innerHTML= ... `<p ...>${m.interpretation||''}</p>` (line 509); confirmed values contain only prose, e.g. mean_reversion.interpretation = "Deviations mean-revert with half-life ~278 days (~9.1 months)..."
- **Fix:** For the free-text fields specifically, prefer textContent over innerHTML where the value is plain text (e.g. set the interpretation paragraphs via a dedicated element + textContent), or run a small escapeHtml() helper over interpolated string values before concatenation. Leave the numeric/.toFixed() interpolations as-is (they cannot contain markup). This is a cheap guardrail that future-proofs the page if the data source ever stops being 100% author-controlled.
- **Verified / corrected:** Nine of the ten cited innerHTML sinks interpolate window.PL strings without escaping; this is a latent (non-exploitable) hardening concern, not a live XSS vulnerability, because the page has no untrusted-input path and all data is author-generated at build time. (anchors[].note is rendered via Plotly customdata, not innerHTML, so it is not one of the unescaped innerHTML sinks.)


### 7. No author meta and no robots meta

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html (head)
- **Issue:** There is no <meta name="author"> identifying the author (the visible byline only credits tools — 'Built with Python · statsmodels · Plotly · seaborn', line 114 — not a person), and no <meta name="robots">. The author meta aids attribution and some discovery surfaces; an explicit robots='index,follow' is harmless reassurance for a page you want crawled (and the slot is the place you'd later add 'noindex' if you ever wanted to hide it).
- **Evidence:** No 'name="author"' or 'name="robots"' in index.html. The byline at line 114 names only libraries, not a person.
- **Fix:** Add '<meta name="author" content="Scott Nelson">' and '<meta name="robots" content="index,follow">' to <head>. Consider also adding a visible author name to the byline for human readers.
- **Verified / corrected:** The head (index.html lines 3-15) lacks <meta name="author"> and <meta name="robots">, and the byline (line 114) credits only tools. This is real but cosmetic: a robots="index,follow" tag is a no-op since indexing is the default, and the author tag has negligible SEO impact — hence nit, not low.


### 8. Meta description front-loads a long jargon list and risks SERP truncation

- **Dimension:** seo · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html line 7
- **Issue:** The description is ~210 characters and ends in an eight-item comma list ('...mean reversion, LPPLS bubbles, structural stability, and risk.'). Google typically renders ~155-160 chars, so the tail list will be cut off and the snippet reads as a keyword dump rather than a hook. It is serviceable but not optimized for click-through.
- **Evidence:** index.html line 7: content='An interactive, multi-lens econometric scrutiny of the Bitcoin power law: fit, inference, stationarity, model selection, mean reversion, LPPLS bubbles, structural stability, and risk.' (about 210 chars).
- **Fix:** Tighten to ~150-155 chars leading with the payoff, e.g. 'An interactive, eight-lens econometric test of whether Bitcoin really follows a power law: honest error bars, model tournament, mean reversion, and more.' Reuse the same string for og:description.
- **Verified / corrected:** The meta description (index.html line 7) is 183 characters (not ~210) and ends in an eight-item comma list, modestly exceeding Google's ~155-160 char display so the final clause may be truncated. Separately, the page has no Open Graph tags at all, so there is no og:description to align it with.


### 9. Obsolete charset attribute on the Plotly <script> (validator warning)

- **Dimension:** standards · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html line 10
- **Issue:** The <script> tag loading Plotly carries charset="utf-8". The charset content attribute on the script element was removed from HTML5; the W3C Nu validator emits the warning 'The charset attribute on the script element is obsolete.' It has no effect for an external script served by a modern CDN (the response's own Content-Type/charset governs decoding), so it is dead markup, not a functional bug. The document already declares UTF-8 via <meta charset="utf-8"> at line 4.
- **Evidence:** line 10 `<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>`
- **Fix:** Remove the `charset="utf-8"` attribute from the Plotly <script> tag so the document validates warning-free: `<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>`. (The MathJax and data.js scripts on lines 14-15 do not carry charset and are fine.)
- **Verified / corrected:** Real W3C validator warning ("The charset attribute on the script element is obsolete") on line 10 of index.html; no functional effect. Best classified as a nit/low polish item, not a bug.


### 10. font-weight:750 / 650 are not in the loaded Inter weight set, so they will not render as intended

- **Dimension:** standards · **Confidence:** high
- **Location:** /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html lines 63 (h2) and 64 (h3); font request line 9
- **Issue:** The Google Fonts link (line 9) requests Inter as a discrete weight list: `Inter:wght@400;500;600;700;800` — NOT a variable range (which would be written `wght@400..800`). With a discrete-instance request, only the named weights 400/500/600/700/800 are delivered. The CSS then asks for `font-weight:750` (h2, line 63) and `font-weight:650` (h3, line 64). Those exact weights are not among the loaded faces, so the browser maps them to the nearest available face — 700 for both — meaning the 750/650 values silently render identically to 700 and the intended slightly-heavier headings never appear. Note: `font-weight:750`/`650` is VALID CSS syntax (CSS Fonts Level 4 allows any 1–1000 value), so this is not a validator error; it is a functional 'the value has no visible effect' issue. system-ui/-apple-system fallback fonts also generally only expose 100-step weights, so the fallback rounds too.
- **Evidence:** line 9 `...css2?family=Inter:wght@400;500;600;700;800&...`; line 63 `h2{...font-weight:750;...}`; line 64 `h3{...font-weight:650;...}`
- **Fix:** Either (a) load Inter as a variable axis so intermediate weights resolve: change the request to `Inter:wght@400..800`, or (b) snap the CSS to weights you actually load — `font-weight:700` for h2 (line 63) and `font-weight:600` for h3 (line 64). Option (b) is the minimal change and makes the rendered weight match what is shipped.
- **Verified / corrected:** h2 (font-weight:750) and h3 (font-weight:650) request weights not in the discretely-loaded Inter set (400/500/600/700/800), so they snap to the nearest loaded face per the CSS font-matching algorithm. Because that algorithm searches upward first for weights above 500, 750 renders as 800 (heavier than intended) and 650 renders as 700 — they do NOT both collapse to 700 as the finding claims. The visible difference is minor; this is cosmetic polish, not a medium-severity issue. Fix by loading a variable axis (Inter:wght@400..800) or snapping the CSS to a loaded weight chosen for the desired look.


---

## Verification — what the adversarial pass rejected

These candidate findings were checked and dismissed, which is itself a useful signal of what holds up:

- **Data described as "~3,650 daily obs" / "3,650 daily prices" but the analyzed series is weekly (523 points)** — The finding's core claim is provably FALSE. It asserts that fit_coinbase and model_comparison were computed on the 523-point weekly PL.series, not on ~3,650 daily points, making the footer/Lens-1 "daily / ≈3,650 obs" narrative inconsistent with what was fit. Re-deriving from data
- **Hero corridor caption asserts a Gaussian 68/95 rule while Lens 2 shows the residuals have fat tails (its own QQ plot)** — The finding's two quoted strings are accurate (index.html line 130 hero caption "≈68% ... ±1σ and ≈95% within ±2σ" with a symmetric Gaussian bell drawn at lines 386-388; line 169 QQ caption "fatter than a bell curve predicts") and the corridor asymmetry is real (data.js corridor 
- **Lens 1 prose treats ρ≈0.998 as residual autocorrelation, but the figcaption defines it as the level (not residual) lag-plot correlation, and the table labels it "residual lag-1"** — The finding's central claim — a semantic mismatch between the figcaption and the table — is wrong. The figcaption (index.html line 142) reads "Today's deviation from trend vs. yesterday's (ρ = 0.998)." "Deviation from trend" IS the residual, so this is a residual-on-lagged-residu
- **MathJax tex-svg output has limited screen-reader accessibility as configured** — Refuted. The finding's core premise is factually wrong for the component actually loaded. index.html line 14 loads the MathJax 3 COMBINED component cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js. I inspected that bundle directly: it contains the line `r.Loader.preLoad("loader","st
- **--mute (#93a1b2) used for small italic/secondary text passes AA only narrowly; verify on --card surfaces** — Self-refuting finding. I re-derived the WCAG contrast ratios for --mute (#93a1b2) using the standard sRGB-linear/relative-luminance formula and confirmed the finding's exact numbers: 6.77:1 on --card (#121821) and 7.40:1 on --bg (#0a0d12). It also clears 4.5:1 AA on every other s
- **All external target=_blank links correctly carry rel="noopener" (no reverse-tabnabbing exposure)** — Confirmed the factual claims but this is a positive "no vulnerability" confirmation, not an actionable defect. Verified in /Users/scottnelson/Library/Mobile Documents/com~apple~CloudDocs/Desktop/website-related/scottn66.github.io/.audit-bitcoin/bitcoin-power-law/index.html: there
- **Inline MathJax in the model-claims table cannot wrap and forces table overflow on mobile** — Refuted by direct measurement of the rendered page at both 375px and the finding's own stated 360px viewport. The "What each curve actually claims" table (index.html lines 182-190, inside the .card at line 180) does NOT overflow and does NOT push the page horizontally.

Re-derive
- **OU / risk / fitted-process cards render fixed-width inner tables that can overflow inside collapsed grid cells** — The finding's core claim is contradicted by the actual CSS. The #oucard and #mrcard tables are NOT "fixed-width": index.html line 78 sets `table{width:100%;border-collapse:collapse}`, so they fluidly fill their container. There is no `min-width`, no `table-layout:fixed`, and no `

---

## Corrected after the audit

- **"Page is orphaned / not in `published-corpus.json`" — withdrawn (false positive).** The finder read the stale local branch (27 commits behind). On deployed `origin/main` the page **is** linked from the homepage ("View Project" button, `index.html:518`) and **is** indexed in `published-corpus.json` (the `bitcoin-power-law` unit). No action needed.
- **Open Graph finding confirmed and strengthened.** `index.html` and `Q.html` each carry 5 `og:`/`twitter:` tags; `bitcoin-power-law/index.html` has zero — it is the lone exception to the established house pattern. (Note: the em-dash in the title also propagates into `published-corpus.json`.)

