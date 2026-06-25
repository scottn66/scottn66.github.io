# Whole-site audit — scottn66.github.io

**Site:** https://scottn66.github.io/ (GitHub Pages, static, ~49 HTML pages)
**Source state:** `origin/main` @ `d199647` (deployed)
**Audit date:** 2026-06-18
**Method:** hybrid — 8 dimensions (security, privacy/PII, SEO, accessibility, architecture, design, code quality, writing), each grounded in live web research (70 cited best-practice sources), audited against the real deployed files, then adversarially verified. 88 candidate findings → **86 confirmed**, 2 rejected.

> Page-level companion: the `bitcoin-power-law/` page has its own deep audit in [`bitcoin-power-law/AUDIT.md`](bitcoin-power-law/AUDIT.md). This report covers the site as a whole; bitcoin-specific items below are summarized, not repeated in full.

---

## What's already good

- **No trackers, no secrets.** Zero analytics, tag managers, tracking pixels, API keys, or tokens anywhere in the deployed files. Privacy-clean by default.
- **Resume omits high-risk PII.** A full-site scan found no phone number, home address, DOB, SSN, or financial data. The resume sticks to email + professional history — the right call.
- **The flagship "research note" pages are genuinely high-craft.** `decision-theory.html`, `cartography.html`, `mandelbrot.html`, and `bitcoin-power-law/` show real design and writing ability. The problem is consistency, not capability.

## Severity summary

| Severity | Count |
|---|---|
| 🟠 High | 3 |
| 🟡 Medium | 22 |
| ⚪ Low | 49 |
| ▪️ Nit | 12 |

| Dimension | Findings | | Dimension | Findings |
|---|---|---|---|---|
| code quality | 13 | | architecture | 12 |
| accessibility | 13 | | writing | 12 |
| design | 13 | | SEO | 9 |
| security | 8 | | privacy/PII | 6 |

The single strongest theme: this is a **collection of strong individual pages that was never unified into a site** — no shared navigation, no shared design system, no shared metadata, and two visual eras that never reconciled. Most findings are facets of that.

---

## Priority shortlist

### 🔴 Now (minutes each, high impact)
1. **Delete the `polyfill.io` script** — `robot-arm-sim/narrative.html:12`. It loads attacker-controlled JS from a domain compromised in the June 2024 supply-chain attack (CVE-2024-38526). MathJax 3 (line 13) needs no polyfill. Just remove the line.
2. **Fix the homepage `yourdomain.com` placeholders** — `index.html:15,16,26`. Your most-shared URL currently previews blank and mis-attributes your identity. Replace with `https://scottn66.github.io` and point `og:image` at a real 1200×630 image (the referenced `assets/images/og-image.png` doesn't exist).
3. **Fix the solar host-institution contradiction** — the homepage card says the Solar project was "Built for DATA 201 at California State University, San Jose," but every page inside `solar/` says "Cal Poly Humboldt." One is factually false; correct it.
4. **Delete dead scaffolding** — the `pages/` directory (4 lorem-ipsum template pages), `about-us/contact.md`, and `sun/test.html` are deployed publicly. Remove them (or finish them).

### 🟠 This week
5. **Migrate the 10 StackPath pages** off `stackpath.bootstrapcdn.com` (StackPath shut its CDN down) to pinned `jsdelivr` Bootstrap, or vendor it locally. Pin the floating tags too: `plotly-latest`, `font-awesome 6.0.0-beta3`, `mathjax@3`.
6. **Add Subresource Integrity** (`integrity` + `crossorigin`) to versioned CDN includes — currently only 2 of ~38 pages have any.
7. **Add a shared header/footer** with a "back to home" link to the ~12 dead-end pages.
8. **Fix or retire the `sun/` ROI calculator** — its "Calculate" button calls an undefined function and throws; the chart never renders.
9. **Add OG + `meta description`** to the flagship research pages (only 3 of 49 have OG; only 7 have a description), and add `sitemap.xml` + `robots.txt`.

### 🟢 This month (structural)
10. **Extract one shared design system** (a single `site.css` with locked color/type/spacing tokens) and converge on the research-note look. Unify Bootstrap 4 → 5; drop unused jQuery.
11. **Accessibility pass** — fix the light-mode footer (#333 on #333), lighten dim/muted text below 4.5:1, add `role="img"`+`aria-label` to charts/canvases, add skip links and `prefers-reduced-motion`.
12. **Add a `<meta>` CSP** and consider an email alias / contact form instead of the plain `mailto`.

---

## Findings by theme

### 1. Security & supply chain
- 🟠 **`polyfill.io` (CVE-2024-38526)** at `robot-arm-sim/narrative.html:12` — the domain was acquired by Funnull (Feb 2024) and served malware/scam redirects (Sansec disclosure, June 2024; Namecheap suspended it June 27). The page is reachable (linked from `Q.html` and `robot-arm-sim/index.html`). The domain is currently dormant (suspended), but the right fix is removal, not a mirror. *(Cloudflare, Sansec)*
- 🟡 **No SRI on ~95% of third-party loads** — only `solar/heatmap/heatmap_ca.html` and `heatmap_norcal.html` use `integrity`. jsdelivr, code.jquery.com, cdnjs, and cdn.plot.ly all send CORS headers, so SRI works everywhere. *(MDN SRI)*
- 🟡 **Floating/beta tags can't be SRI-protected** — `font-awesome 6.0.0-beta3`, `plotly-latest`, `mathjax@3` resolve to moving targets. Pin exact versions first, then add SRI.
- ⚪ **Dead StackPath Bootstrap CDN** on 10 pages; **jQuery 3.3.1** (known CVEs) loaded on 10 pages, usually unused; **no CSP** anywhere (a `<meta http-equiv>` CSP is possible on Pages); six distinct CDN origins form an unmonitored trust surface.

### 2. Discoverability & social (SEO)
- 🟠 **Homepage OG is placeholder text** (`index.html:15-16`, JSON-LD `:26`) — `og:image`/`og:url` point to `yourdomain.com`; the image doesn't exist; only `twitter:card` is present with no `twitter:image/title/description`. Independently flagged by the SEO, writing, architecture, and design lenses. *(ogp.me, Google Search Central)*
- 🟡 **OG/Twitter on only 3 of 49 pages; `meta description` on only 7 of 49** — the flagship research notes have neither. Template per-page tags (and per-city descriptions for the 20 solar reports).
- ⚪ **No `sitemap.xml`, no `robots.txt`, no canonical anywhere**; structured data is thin and partly broken (one `Person` schema with the placeholder URL).

### 3. Information architecture & organization
- 🟡 **No shared global navigation** — most pages are dead-ends with no way back to the site. Add one shared nav/header (brand → home, Projects link) included on every page.
- 🟡 **Chrome is copy-pasted into ~50 standalone files** (not DRY). Introduce a small `include.js` for nav/footer, or a templating step in the CI you already run for the manifest.
- 🟡 **`yourdomain.com` undermines URL identity** across canonical/OG/schema.
- 🟡 **Orphaned `sun/` app** — in `published-corpus.json` but linked from nowhere (and broken). Wire it in or retire it.
- ⚪ Dead/duplicate scaffolding: `pages/` (4 superseded pages), `about-us/contact.md`, `financial_fun/compoundingInterest.html` (orphan, also invisible to the manifest), `cartography`/`mandelbrot` landing-vs-app duplicates; the manifest's discovery rules miss nested/non-index pages; **missing `.nojekyll`**; inconsistent file/folder naming.

### 4. Design & visual coherence
- 🟡 **5+ visual eras, no shared design language** — bespoke dark research notes vs. default Bootstrap templates. Extract one shared stylesheet (locked tokens, type scale, spacing scale) and pick the research-note direction. *(NN/g, designsystems.com)*
- 🟡 **Bootstrap 4.3.1 and 5.3.0 mixed**, jQuery still loaded on legacy pages. Standardize on Bootstrap 5.3.x (update `ml-/mr-` → `ms-/me-`), drop jQuery.
- 🟡 **No shared/persistent nav** (design lens, same root as IA). 
- ⚪ No locked type scale (px/rem mixed); no 8-pt spacing scale; unbounded line length; unfinished dark-mode artifacts on the homepage; Font Awesome beta; header text fails AA over the coral gradient end.

### 5. Accessibility
- 🟡 **Homepage footer is invisible in light mode** — `#333` text on a `#333` footer (`index.html:174-181`, `:54`, `:51`). Give the footer an explicit light `color`.
- 🟡 **`sun/` submit button**: white on green at 2.78:1 (and the result heading) fail contrast.
- 🟡 **Interactive visuals have no text alternative** — Plotly charts (`bitcoin-power-law` `#hero/#osc/#lppls/#roll`) and the `cartography.html` `<canvas>` have no `role`/`aria-label`. Add `role="img"` + descriptive `aria-label`, wrap in `<figure>`. *(WebAIM, W3C WAI)*
- 🟡 **Dim text below 4.5:1** on the dark research pages (`--dim #6b7787`) — lighten to ~`#8a97a8`. (Also in the bitcoin page audit.)
- ⚪ No skip links; no `prefers-reduced-motion`; headings used for styling (HMM h2→h5); `<th>` without `scope`; navbar `href="#"` no-ops; cartography removes focus outlines.

### 6. Privacy & PII
- **Good baseline** (see top): no trackers, no high-risk PII, resume is appropriately minimal.
- ⚪ **Personal Gmail in plain `mailto`** across 4 locations (`resume.html:122`, `index.html:543,558`, `Q.html:502`) — harvestable, non-disposable, and a single reusable identifier linking homepage/resume/projects (OSINT surface). Consider an alias, a contact form, or light obfuscation, and a privacy note on any form. *(EFF SSD)*
- ▪️ The non-functional contact-form stub has a placeholder LinkedIn URL; the `feross@feross.org` address in vendored MAB files is the library author's, not yours (not a leak).

### 7. Writing & content accuracy
- 🟡 **`yourdomain.com` placeholder shipped** to production metadata (writing lens).
- 🟡 **Four lorem-ipsum scaffolding pages** (`pages/*`) are publicly deployed with placeholder bios and `your_photo.jpg`/`yourlinkedin` strings.
- 🟡 **Weak homepage value proposition** — an animated loop of role nouns instead of a one-line tagline stating specialty + outcome.
- ⚪ **Solar host-institution contradiction** (false claim, see Now #3); typos on the MAB page; self-undermining filler on HMM/MAB that clashes with the confident voice elsewhere; resume verb-tense + a rendering bug; stale/inconsistent copyright years; README is a single bare line; uneven project blurbs.
- ▪️ **Em-dash house style violated site-wide** — including the crawler pages a prior "strip em-dashes" commit was meant to fix, and the newer pages. (Leave en-dashes in compound names alone.)

### 8. Code quality & broken features
- ⚪ **`sun/` ROI calculator is broken** — `onsubmit` calls `calculateROI()`, which is defined nowhere (`script.js` only defines `updateEquation`/`validateInput`/`updateCurrentDate`); clicking throws a `ReferenceError` and the chart canvas is never drawn.
- ⚪ **`sun/test.html`** scratch/test file shipped to prod; **duplicated** jQuery+Bootstrap includes in `sun/index.html`; **broken link** `href="sunlighthours.com"` (missing scheme → 404s to a local path).
- ⚪ **jQuery 3.3.1 is a dead include** on 9 pages (loaded, never called); Font Awesome beta in prod; a JS-style `//` comment inside a CSS block; homepage links to HMM/MAB via hardcoded absolute URLs.

---

## Complete findings appendix

All 86 confirmed findings, grouped by dimension and severity. Fixes are abbreviated; full detail (evidence, verifier notes, cited best-practice source) is in the audit data.

### Security & supply chain (8)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟠 | Compromised polyfill.io supply-chain dependency served to visitors | `robot-arm-sim/narrative.html:12` | Delete line 12 entirely. Cloudflare explicitly recommends REMOVING polyfill.io rather than swapping to a mirror, because modern browsers do not need it and Math |
| 🟡 | Subresource Integrity absent on ~95% of third-party script/style loads | `site-wide (38 HTML files load cross-origin scripts; only 2 use integrity=)` | Add integrity="sha384-..." + crossorigin="anonymous" to every versioned third-party <script>/<link rel=stylesheet>. Generate hashes at srihash.org. cdn.jsdelivr |
| 🟡 | Floating/beta CDN tags can't be SRI-protected — pin Font Awesome beta, plotly-latest, MathJax@3 | `index.html:41; Q.html:21; dashboard.html:9 (font-awesome 6.0.0-beta3); HMM.html:188 and MA` | Pin each to a specific released version, then add SRI: Font Awesome → a stable release such as `6.5.2` (or self-host the icon CSS+fonts); plotly-latest → a fixe |
| ⚪ | Bootstrap CSS/JS loaded from dead StackPath CDN on 10 pages | `HMM.html:6,190; MAB.html:6,177; arxiv_scraper.html:6,316; sep_scraper.html:6,273; wikipedi` | Replace every stackpath.bootstrapcdn.com URL with the current official Bootstrap CDN on jsDelivr, pinned to a specific patch: `https://cdn.jsdelivr.net/npm/boot |
| ⚪ | Outdated jQuery 3.3.1 with known CVEs loaded on 10 pages | `HMM.html:189; MAB.html:176; arxiv_scraper.html:315; sep_scraper.html:272; wikipedia_scrape` | Upgrade to the latest jQuery 3.7.x from a pinned, SRI-protected URL (e.g. `https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.slim.min.js` with integrity= +  |
| ⚪ | No Content-Security-Policy anywhere on the site | `site-wide (0 of ~50 HTML files contain a Content-Security-Policy)` | Add a `<meta http-equiv="Content-Security-Policy">` tag whose script-src/style-src allowlist only the origins each page actually uses (cdn.jsdelivr.net, cdn.plo |
| ⚪ | 20 solar report pages load versioned Plotly without SRI | `solar/reports/*.html (20 files, each loading https://cdn.plot.ly/plotly-2.35.0.min.js)` | Add `integrity="sha384-..." crossorigin="anonymous"` to the plotly-2.35.0 tag in all 20 report files (one hash from srihash.org applies to all, since the URL is |
| ⚪ | Six distinct third-party CDN origins form an unmonitored trust surface | `site-wide (executable origins: polyfill.io, stackpath.bootstrapcdn.com, cdn.plot.ly, cdn.j` | After removing polyfill.io and migrating off stackpath, self-host the small static assets where practical (typed.js, Font Awesome icon CSS+webfonts, jQuery), an |

### Privacy & PII (6)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| ⚪ | Primary personal Gmail exposed as plain-text mailto: across 4 locations (harvestable, non-disposable) | `index.html:543 and index.html:558; resume.html:122; Q.html:502 (robot-arm narrative footer` | Replace all four raw mailto: occurrences with a non-literal contact channel: (a) a JavaScript-assembled mailto link so the address never appears in HTML source; |
| ⚪ | No disposable alias or working form-based contact path — primary inbox is the only channel and can't be retired | `site-wide (contact surfaces: index.html#contact lines 537-548, resume.html:120-124, Q.html` | Introduce a single dedicated disposable forwarding alias (e.g. a SimpleLogin/addy.io alias or jobs@yourdomain) and use it everywhere a contact link appears, OR  |
| ⚪ | One real-name primary Gmail reused as a single linkable identifier across homepage, resume, and project pages (doxxing/OSINT surface) | `site-wide (index.html:543/558, resume.html:122, Q.html:502) plus reused LinkedIn handle sc` | Decouple the public contact identifier from the primary account by publishing a purpose-specific alias (see above). Periodically self-audit by 'dorking' your ow |
| ▪️ | Non-functional contact-form stub with no privacy note and a placeholder LinkedIn URL | `pages/contact.html:37-54` | Either (a) delete pages/contact.html since the real contact path lives at index.html#contact, or (b) wire the form to a real backend (Formspree/Netlify Forms) w |
| ▪️ | Third-party library author's email leaks via vendored bundle in MAB plot files (incidental, NOT owner PII) | `assets/images/projects/MAB/cum_reg_cmsi_432_ass3_sims.html, ...sims2.html, ...sims4.html (` | Low priority. If these generated plot HTML files are regenerated, strip or minify out bundled author/license comment headers, or host the figures as static imag |
| ▪️ | CONFIRM-GOOD: Resume correctly omits high-risk PII (no DOB, SSN, phone, or home street address) | `resume.html (whole file)` | Maintain this discipline: keep DOB/SSN/driver's-license/full-street-address/phone off the public resume, keep location at city/region granularity, and withhold  |

### SEO & metadata (9)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟠 | Homepage Open Graph tags are unfilled placeholders (yourdomain.com) — social previews broken for the front door | `index.html:15-16 (and JSON-LD url at line 26)` | Replace all three placeholders with real absolute HTTPS URLs: og:url and JSON-LD url → https://scottn66.github.io/ ; og:image → a real 1200x630 PNG that actuall |
| 🟡 | Open Graph / Twitter Card metadata present on only 3 of 49 pages — flagship research notes have none | `site-wide; only index.html, decision-theory.html, Q.html carry og: tags` | Add a complete OG + Twitter block to every indexable page: og:title, og:type (article for research notes, website for index/dashboards), og:url (absolute), og:i |
| 🟡 | Meta description present on only 7 of 49 pages | `site-wide; description present only on index, bitcoin-power-law, cartography, cartography_` | Add a unique, accurate, page-specific `<meta name="description">` (roughly one sentence, no boilerplate, no keyword stuffing) to every indexable page. For the 2 |
| ⚪ | No sitemap.xml at repo root — search engines have no crawl map | `site-wide (missing /sitemap.xml at repo root)` | Create sitemap.xml at the repo root listing only canonical, indexable, 200-status pages with absolute https://scottn66.github.io/ URLs. EXCLUDE the duplicate la |
| ⚪ | No robots.txt at repo root — no crawl directives, no sitemap reference | `site-wide (missing /robots.txt at repo root)` | Add robots.txt at the repo root with `User-agent: *` / `Allow: /` and a `Sitemap: https://scottn66.github.io/sitemap.xml` line. Optionally Disallow the legacy s |
| ⚪ | No page declares a canonical URL — duplicate landing pairs left ambiguous | `site-wide; acute on cartography.html / cartography_landing.html and mandelbrot.html / mand` | On every indexable page add a self-referencing absolute canonical, e.g. `<link rel="canonical" href="https://scottn66.github.io/cartography.html">`. For each du |
| ⚪ | Heatmap chart pages have no <title> element | `solar/heatmap/heatmap_ca.html, solar/heatmap/heatmap_norcal.html` | If these are standalone pages, add a descriptive `<title>` (e.g. "California Solar Viability Heatmap"). If they are iframe fragments only, exclude them from sit |
| ⚪ | Legacy scaffolding page is an unfilled template ("Project Title", "Brief description of the project") | `pages/project_details.html:8,32,34 (and sibling pages/about.html, pages/contact.html, page` | Either delete the pages/ scaffolding directory, or if kept for reference, exclude it via robots.txt Disallow: /pages/ and add `<meta name="robots" content="noin |
| ⚪ | Structured data is thin and partly broken — only one Person schema (with placeholder URL), no WebSite or Article schema | `index.html:20-32 (only JSON-LD on the site); absent on resume.html and all research notes` | Fix the Person url to https://scottn66.github.io/ (covered by the homepage placeholder fix). Add a WebSite schema site-wide, a fuller Person schema on resume.ht |

### Accessibility (13)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟡 | Homepage footer text and icons are invisible in default (light) mode — #333 on #333 | `index.html lines 174-181 (footer{color:var(--text-color)}), resolved against --footer-bg:#` | Give the footer an explicit light text color independent of --text-color, e.g. footer{color:#f4f4f4} and footer a{color:#f4f4f4}, or set --footer-bg to a dark v |
| 🟡 | Sun ROI app: green primary button has white text below 3:1 (2.78:1) and result heading fails | `sun/styles.css lines 53-65 (input[type=submit]) and lines 29-34 (h2); rendered in sun/inde` | Darken the green to meet contrast: use #2e7d32 (white-on-green ~5.0:1) for the submit button background, and use a darker green (e.g. #2e7d32 or #1b5e20) for th |
| 🟡 | Plotly charts on bitcoin-power-law have no short text alternative and are keyboard/SR-inaccessible | `bitcoin-power-law/index.html — empty target divs at lines 129 (#hero), 219 (#osc), 242 (#l` | For each plot div add role="img" and an aria-label naming the chart type and subject (e.g. aria-label="Log-log scatter of Bitcoin price vs. time with fitted pow |
| 🟡 | Cartography map canvas has no accessible name or text alternative | `cartography.html line 120 (<canvas id="map"></canvas>); <html lang> present (line 2), but ` | Add role="img" and an aria-label to the canvas (e.g. 'Live-rendered road network and elevation map for the searched city') and an aria-live status region announ |
| 🟡 | Bitcoin-power-law muted text (--dim #6b7787) is below 4.5:1 on figcaptions, footer, byline and table headers | `bitcoin-power-law/index.html — :root --dim:#6b7787 (line 19); applied to figcaption (line ` | Lighten --dim to about #8a96a6 or brighter (≈4.6:1 on #0a0d12, ≈4.5:1 on #121821) so all figcaption/footer/byline/th text clears 4.5:1. Verify specifically agai |
| ⚪ | No 'Skip to main content' link on any page (site-wide) | `site-wide — confirmed absent in index.html, decision-theory.html, cartography.html, HMM.ht` | Add as the first child of <body>: <a class="skip-link" href="#main">Skip to main content</a> with CSS that visually hides it until focused (position:absolute;le |
| ⚪ | Sun app: heading order is broken and page lacks lang and landmarks | `sun/index.html line 2 (<html> no lang), line 18 (<h2 id=current_date>), line 26 (<h1>), li` | Set <html lang="en">. Make the ROI Calculator the <h1> and demote the date/result headings (or make the result an aria-live region rather than a heading). Wrap  |
| ⚪ | HMM page: heading levels used for styling, breaking the outline (h2 → h5, h2 → h4) | `HMM.html line 89 (<h5>Primer for Encyclopedic Knowledge</h5> directly under the line-88 <h` | Use heading levels for structure only: make line 89 a styled <p>/<p class="subtitle"> (or a real <h3> if it is a genuine subsection), and change the line-169 <h |
| ⚪ | Data tables use <th> header cells without scope attributes (bitcoin-power-law) | `bitcoin-power-law/index.html — table headers at line 183 (static model table) and the JS-b` | Add scope="col" to each column header (<th scope="col">), and where the first cell of each row is a label (e.g. 'Model', 'Halving', 'Cycle run-up'), mark it <th |
| ⚪ | Sun app: inline '?' tooltips are not keyboard- or screen-reader-accessible | `sun/index.html lines 29, 34, 38, 42, 51, 55, 59 — <span data-toggle="tooltip" title="…">?<` | Make the help affordance a real focusable control: <button type="button" class="btn-help" aria-label="System size help" title="…">?</button>, or render the guid |
| ⚪ | No prefers-reduced-motion support anywhere; homepage typed.js and card hover-lift animate unconditionally | `site-wide (grep for prefers-reduced-motion → none); homepage index.html typed.js loop (lin` | Add a site-wide @media (prefers-reduced-motion: reduce){ *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transiti |
| ⚪ | Homepage navbar brand and 'View Project' links use href="#", creating no-op/placeholder targets | `index.html line 214 (<a class="navbar-brand" href="#">) and the modal-trigger cards at lin` | Point the brand at href="index.html" (or '#top' to a real landmark). For the modal openers use <button type="button" class="btn btn-primary w-100" data-bs-toggl |
| ▪️ | Cartography removes focus outline on text inputs and selects with no replacement | `cartography.html line 57: input[type=text]:focus, select:focus { outline: none; border-col` | Keep a visible indicator: replace with a box-shadow ring, e.g. input[type=text]:focus, select:focus { outline:none; border-color:var(--accent-2); box-shadow:0 0 |

### Architecture & organization (12)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟡 | Orphaned 'sun' solar-calculator app: in the manifest, linked from nowhere on the site | `sun/index.html (+ sun/test.html); listed in published-corpus.json lines 93-99 as unit "sun` | Decide the page's fate. Either (a) retire sun/ — delete the directory and let manifest CI drop the 'sun' unit — or (b) keep it and wire it in: add a project car |
| 🟡 | Two coexisting design systems with no shared, persistent global navigation | `site-wide — Bootstrap-era pages (index.html, dashboard.html, MAB.html, HMM.html, *_scraper` | Define one global nav/header (logo → home, plus a Projects index link) and include it on EVERY page via a small shared HTML/JS include rather than per-page copy |
| 🟡 | Shared layout/chrome is copy-pasted into every page (not DRY) | `site-wide — nav block index.html lines 211-233 vs dashboard.html lines 113-122; footer ind` | Introduce one lightweight reuse mechanism: a small nav.html/footer.html fetched-and-injected by a shared include.js, or add a static-site generator/templating s |
| 🟡 | Placeholder 'yourdomain.com' in canonical/OG/schema URLs undermines the site's URL identity | `index.html lines 15-16 (og:image, og:url), line 26 (schema.org url)` | Replace every 'yourdomain.com' with 'https://scottn66.github.io' (og:url, og:image, schema url) and provide a real og-image asset at the referenced path. Standa |
| ⚪ | Stale scaffolding directory pages/ — four orphaned, superseded pages still deployed | `pages/about.html, pages/contact.html, pages/landing.html, pages/project_details.html` | Delete the pages/ directory. Its content is fully superseded by the sections in index.html. build_manifest.py already excludes pages/ (EXCLUDE_DIRS), confirming |
| ⚪ | Orphaned financial_fun/compoundingInterest.html — unreachable AND missing from the manifest | `financial_fun/compoundingInterest.html` | Pick one: (a) retire it (delete financial_fun/), or (b) promote it — rename to financial_fun/index.html so the manifest scanner picks it up as a project unit, a |
| ⚪ | Duplicate cartography/mandelbrot landing-vs-app pages create two URLs for one project each | `cartography.html + cartography_landing.html; mandelbrot.html + mandelbrot_landing.html (pu` | Either consolidate each pair into one page (intro + launch button + canvas in a single document, like robot-arm-sim/index.html) OR keep the split but (a) add a  |
| ⚪ | Manifest is the declared source of truth but its discovery rules miss nested and non-index pages | `scripts/build_manifest.py lines 62-87; published-corpus.json (15 units)` | Tighten the manifest: (1) recurse one more level for directory entry points, or standardize every project's entry file to index.html (rename compoundingInterest |
| ⚪ | Missing .nojekyll at the publishing root | `repository root (extraction shows .github, .gitignore, README.md but no .nojekyll)` | Add an empty file named exactly '.nojekyll' (all lowercase, leading dot, no extension) at the repo root to bypass Jekyll entirely and future-proof any underscor |
| ⚪ | Inconsistent folder/file naming (mixed case, two scraper styles, scattered top-level files) | `site-wide — HMM.html, MAB.html, Q.html (uppercase) vs cartography.html, decision-theory.ht` | Adopt one convention: lowercase-hyphenated filenames and a directory-per-section layout. Group the three scrapers under a scrapers/ section and consider groupin |
| ▪️ | Orphaned legacy contact stub about-us/contact.md | `about-us/contact.md` | Delete about-us/ — the contact information is canonical in index.html's #contact section and the footer. |
| ▪️ | robot-arm-sim ships both narrative.html (rendered) and NARRATIVE.md (source); several dirs publish README.md dev docs | `robot-arm-sim/narrative.html + robot-arm-sim/NARRATIVE.md; also bitcoin-power-law/README.m` | Keep .md files in the repo for development but exclude them from the deployed surface, or accept them as source docs and ensure none are mistaken for pages. The |

### Design & aesthetics (13)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟡 | Site fragments into 5+ unrelated visual eras with no shared design language | `site-wide (index.html, dashboard.html, resume.html, bitcoin-power-law/index.html, decision` | Extract one shared stylesheet (e.g. /assets/site.css) defining locked color tokens, a type scale, and a spacing scale, and include it on every page. Pick ONE di |
| 🟡 | Bootstrap 4.3.1 and 5.3.0 are mixed across the site, with jQuery still loaded on legacy pages | `Bootstrap 4.3.1: arxiv_scraper.html:6, sep_scraper.html, wikipedia_scraper.html, MAB.html:` | Standardize on a single Bootstrap major (5.3.x) across every page that uses it, update the markup utilities (ml-/mr- to ms-/me-), drop jQuery from the migrated  |
| 🟡 | No shared/persistent navigation — most pages are navigational dead-ends with no way back | `resume.html (no nav), cartography.html, mandelbrot.html, mandelbrot_landing.html, cartogra` | Add one shared header/nav component (same markup, same links, same styling) to every page, including resume, the landing pages, and the scraper pages. Standardi |
| 🟡 | Dark research page: faint borders (1.29:1) and dim caption text (4.28:1) miss WCAG AA | `bitcoin-power-law/index.html:19 (--dim #6b7787, --line #1f2731), used at :50 (.byline), :7` | Lighten --dim to ~#8a97a8 (>=4.5:1 on #0a0d12) for any text that uses it, and lift --line to ~#313c4a (>=3:1) so borders are perceivable. Per dark-mode guidance |
| ⚪ | Animations ignore prefers-reduced-motion (typed.js loop, hover transforms, smooth-scroll) | `index.html:690-697 (Typed loop) & :77 (scroll-behavior:smooth) & :158-160 (.card hover tra` | Wrap non-essential motion in @media (prefers-reduced-motion: no-preference){...}, or add a global @media (prefers-reduced-motion: reduce){ *{animation:none!impo |
| ⚪ | Live placeholder/lorem content on the legacy pages/* scaffolding | `pages/about.html:44-55 and pages/landing.html:84-99 (also pages/contact.html, pages/projec` | Delete the entire pages/ scaffolding directory (about/contact/landing/project_details) since real equivalents exist (index.html sections, resume.html). If any c |
| ⚪ | No locked type scale: font sizes mix px and rem with an open-ended set of one-off values | `bitcoin-power-law/index.html:42-91, decision-theory.html:57-116, index.html:97-205, resume` | Define one modular type scale as CSS custom properties (e.g. --fs-xs .75rem / --fs-sm .875rem / --fs-base 1rem / --fs-lg 1.125rem / --fs-h3 1.25rem / --fs-h2 1. |
| ⚪ | Inconsistent / unbounded prose line length across pages | `resume.html:30-36, index.html:269 vs :390/:456, bitcoin-power-law/index.html:49 (.lede 760` | Constrain body prose containers to ~60-72ch (roughly 640-720px) site-wide via a shared .prose/.measure utility, while letting full-bleed elements (plots, tables |
| ⚪ | No shared 8-point spacing scale; arbitrary odd values throughout | `index.html:92, :110, :134; bitcoin-power-law/index.html:50, :54, :66, :89; resume.html:34` | Adopt an 8-point spacing scale as tokens (4/8/16/24/32/48/64px; 4px half-step only inside components) and replace ad-hoc paddings/margins/gaps. Round odd values |
| ⚪ | Homepage About and Projects sections share the same gray fill; unfinished dark-mode artifacts | `index.html:247 (#about .section-bg), :263 (#projects .section-bg), :538 (#contact .section` | Establish a deliberate alternation (e.g. white / subtle-tint / white) applied consistently, giving Projects clear separation from About. Remove the invalid '//' |
| ⚪ | Stale placeholder metadata: og:image/og:url point to yourdomain.com and JSON-LD url is a placeholder | `index.html:15-16, :26` | Replace yourdomain.com with https://scottn66.github.io throughout, point og:image at a real committed share image (the project pages already ship cards like ass |
| ▪️ | Homepage header text fails WCAG AA contrast over the coral end of the gradient | `index.html:107-114 (.header) and :102-105 (.nav-link:hover)` | Darken the coral accent used as a text background (or strengthen the text) so nav-hover and any normal text over coral reaches 4.5:1. Replace the faint .text-mu |
| ▪️ | Font Awesome pinned to a pre-release beta (6.0.0-beta3) years after stable | `index.html:41, dashboard.html:9, Q.html` | Pin to a current stable Font Awesome 6.x release (e.g. 6.5.x) on the same CDN, and load it from the single shared stylesheet include rather than re-declaring it |

### Code quality (13)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟠 | polyfill.io script loaded from the attacker-controlled supply-chain domain (CVE-2024-38526) | `robot-arm-sim/narrative.html:12` | Delete line 12 entirely. MathJax 3 (loaded on line 13) requires no polyfill on modern browsers. If a polyfill is ever truly needed, use a vetted Cloudflare/Fast |
| 🟡 | No Subresource Integrity (SRI) on any hand-authored third-party CDN include, site-wide | `site-wide (e.g. index.html:35 & 686 Bootstrap, index.html:689 typed.js, Q.html:17/25/507, ` | Add `integrity="sha384-…" crossorigin="anonymous"` to every CDN <script> and <link>. Generate hashes via `openssl dgst -sha384 -binary <file> \| openssl base64  |
| 🟡 | Dead/abandoned CDNs: Bootstrap 4 stackpath + plotly-latest, with no fallback if they stop serving | `stackpath.bootstrapcdn.com (HMM.html:6/190, MAB.html:6/177, arxiv_scraper.html:6/316, sep_` | Migrate the stackpath pages to a maintained CDN (jsdelivr `bootstrap@5.3.x` or `@4.6.2`) or vendor Bootstrap locally; for the legacy pages that only use Bootstr |
| ⚪ | sun/test.html: a scratch/test file with placeholder code shipped to the public origin | `sun/test.html (whole file)` | Delete sun/test.html from the deployed branch. Keep scratch/experiment files out of the published origin (a separate branch, a /dev gitignored dir, or local onl |
| ⚪ | sun/ ROI calculator is broken: 'Calculate' calls an undefined function and the chart canvas is never drawn | `sun/index.html:27 and sun/index.html:70 (vs sun/script.js)` | Either remove the broken submit `calculateROI()` call (the input listeners already drive `updateEquation`) or implement `calculateROI`; and either wire up Chart |
| ⚪ | Placeholder 'yourdomain.com' shipped in production Open Graph and Schema.org metadata | `index.html:15-16 and index.html:26` | Replace all three `yourdomain.com` references with `https://scottn66.github.io` and supply a real OG image (or remove the og:image line until one exists). Grep  |
| ⚪ | Orphaned legacy scaffolding (pages/, sun/) with placeholder bios, missing assets, and a dead contact form | `pages/about.html, pages/contact.html, pages/landing.html, pages/project_details.html; sun/` | Delete the pages/ directory and (if unintended) the sun/ directory from the deployed branch, or finish and link them. Confirm every deployed page is intentional |
| ⚪ | jQuery 3.3.1 is a dead include on 9 pages (loaded, never called) | `arxiv_scraper.html:315, sep_scraper.html:272, wikipedia_scraper.html:248, HMM.html:189, MA` | Remove the jQuery <script> from all 9 pages — nothing breaks. For sun/, replace the one jQuery tooltip call with Bootstrap's native tooltip API or vanilla JS, t |
| ⚪ | Duplicated jQuery + Bootstrap CSS/JS includes in sun/index.html (each loaded twice) | `sun/index.html:6-11` | Delete the duplicate lines 9-11 (keep one copy of each). Better, since sun/ only needs jQuery for one tooltip call, drop jQuery and use Bootstrap's native toolt |
| ⚪ | Broken relative link to 'sunlighthours.com' (missing scheme, resolves to a local path) | `sun/index.html:44` | Either remove the dead 'here' link or point it at a real, scheme-qualified URL. When linking external sites always include `https://` and `target="_blank" rel=" |
| ⚪ | Font Awesome 6.0.0-beta3 (a pre-release build) used in production on 3 pages | `index.html:41, Q.html:21, dashboard.html:9` | Bump to a current stable Font Awesome 6 release (e.g. 6.5.2 / 6.7.x) and add SRI. Verify the icon names still resolve after the bump. |
| ▪️ | Invalid '//' (JS-style) comment inside a CSS block | `index.html:63` | Change to a proper CSS comment `/* --primary-color: #0093E9; */` or delete the dead line. Run the CSS through a linter (stylelint) to catch this class of issue  |
| ▪️ | Homepage links to HMM/MAB via hardcoded absolute https://scottn66.github.io URLs | `index.html (project links to https://scottn66.github.io/HMM.html and https://scottn66.gith` | Change to relative links `HMM.html` and `MAB.html` to match the rest of the homepage and stay origin-agnostic. |

### Writing & content (12)

| Sev | Finding | Location | Fix |
|---|---|---|---|
| 🟡 | Placeholder "yourdomain.com" leaks into shipped homepage social/SEO metadata | `index.html lines 15, 16, 26` | Replace all three occurrences of https://yourdomain.com with https://scottn66.github.io. Point og:image at a real asset that exists in the repo (verify the path |
| 🟡 | Four fully-templated lorem-ipsum-equivalent scaffolding pages are publicly deployed | `pages/about.html (lines 41, 45, 49), pages/project_details.html (lines 27, 30, 32, 34, 36)` | Delete the entire pages/ directory (it is dead, superseded by the real index.html sections and standalone project pages). If any route must be preserved, replac |
| 🟡 | Homepage value proposition is a looping list of role nouns, not a descriptive tagline | `index.html lines 6, 236-239, 691-696` | Replace (or supplement) the animated span with a static one-line tagline that states specialty + outcome + audience, e.g. "Data scientist building ML systems fo |
| ⚪ | Solar project's host institution contradicts itself across pages (one claim is false) | `index.html line 272 vs solar/index.html lines 172 & 177, solar/heatmap/index.html lines 34` | Determine the correct course host and make it identical everywhere. Fix the single outlier — index.html line 272 — to match the solar pages (or correct the sola |
| ⚪ | Typos in published MAB project page body copy | `MAB.html line 96 ("guarentee") and line 137 ("hvae")` | Fix "guarentee" -> "guarantee" (line 96) and "hvae" -> "have" (line 137). Run a spell-check pass over the full MAB.html and HMM.html prose, which were clearly d |
| ⚪ | Self-undermining and filler copy on the HMM and MAB pages contradicts the confident voice elsewhere | `HMM.html lines 117, 118, 176; MAB.html line 90` | Delete the self-deprecating line at HMM.html:176 (or replace it with a concrete, neutral note about model limitations and what you'd use instead). Remove the or |
| ⚪ | Resume verb-tense inconsistency and a rendering bug in the experience/education copy | `resume.html lines 134-140 (Meta bullets), 171 ("&amp Pipeline"), 137 ("pre—deployment")` | Normalize all Meta bullets to past tense ("Stress-tested", "Compiled", "Developed"). Fix line 171 to "Data Engineering & Pipeline Development" (proper & entity) |
| ⚪ | Inconsistent and stale copyright year stamps across the site | `index.html line 554 (© 2023), resume.html line 228 (© 2023), mandelbrot_landing.html line ` | Standardize footer copyright to a single current year (or a range like 2023-2026) site-wide, and update the homepage and resume footers to 2026. Make the MAB fo |
| ⚪ | README is a single bare line with no project description | `README.md (entire file)` | Expand the README to a short paragraph stating what the site is (Scott Nelson's portfolio), a link to https://scottn66.github.io, and a brief bulleted index of  |
| ⚪ | Homepage project blurbs are uneven: some lead with outcome, the legacy ML cards still lead with technology | `index.html lines 326 (MAB card), 356 (HMM card) vs lines 341 (Crawler card), 515 (Bitcoin ` | Rewrite the MAB and HMM cards to lead with a concrete result or insight, matching the Crawler/Bitcoin cards — e.g. for MAB, name the finding (which ASR won, by  |
| ▪️ | Em-dash house style is violated site-wide, including newer pages and the crawler pages a prior commit was meant to fix | `site-wide (literal — in 32 files incl. index.html, decision-theory.html, bitcoin-power-law` | Decide the rule once and enforce it. If em-dashes are banned, run a find-replace converting both — and &mdash; to the chosen substitute (comma, colon, or spaced |
| ▪️ | Inconsistent percent-sign spacing within the robot-arm narrative | `robot-arm-sim/narrative.html (title line 6, lines 87/99 use "100%"/"0%"; lines 805-840, 89` | Pick one convention (tight "97%" is conventional in US English and matches the homepage) and apply it across both robot-arm pages and the title. |

---

## What the verifiers rejected

Two candidate findings were refuted on re-check (a sign the verification pass is honest):

- **[a11y] Sun app: dynamic ROI chart canvas has no text alternative** — The finding's core premise is fabricated. It claims "The ROI projection is drawn to a bare <canvas id='roiChart'>" via "the calculateROI flow in sun/script.js" — but verification of the deployed files refutes this: 1. The canvas is never drawn to. grep across sun/ shows `roiChart` appears ONLY in in
- **[a11y] Homepage muted project subtitles sit just under 4.5:1 on the gray section background** — Refuted on its central factual claim. The finding assumes .text-muted equals #6c757d, which is the Bootstrap 4 / 5.0-5.1 muted color. This page loads bootstrap@5.3.0 via cdn.jsdelivr.net, where .text-muted was reworked to color var(--bs-secondary-color) with !important, and --bs-secondary-color in l

---

## Sources consulted

70 best-practice citations were gathered during the research phase. Deduplicated by URL:

- **allaccessible.org** — [link](https://www.allaccessible.org/blog/color-contrast-accessibility-wcag-guide-2025)
- **auditbuffet.com** — [link](https://auditbuffet.com/patterns/ab-000490)
- **blog.cloudflare.com** — [link](https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/)
- **blog.uxfol.io** — [link](https://blog.uxfol.io/digital-portfolio/)
- **consumer.georgia.gov** — [link](https://consumer.georgia.gov/consumer-topics/identity-theft-information-job-seekers)
- **content-security-policy.com** — [link](https://content-security-policy.com/examples/meta/)
- **crystallize.com** — [link](https://crystallize.com/blog/frontend-performance-checklist)
- **designsystems.com** — [link](https://www.designsystems.com/space-grids-and-layouts/)
- **dev.to** — [link](https://dev.to/wrypa/2025-developer-portfolio-tips-how-to-keep-yours-modern-professional-3l87)
- **developer.mozilla.org** — [link](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/SRI) · [link](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity) · [link](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) · [link](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity) · [link](https://developer.mozilla.org/en-US/docs/Glossary/Graceful_degradation) · [link](https://developer.mozilla.org/en-US/docs/Glossary/Progressive_enhancement)
- **developer.twitter.com** — [link](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/summary-card-with-large-image)
- **developers.google.com** — [link](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) · [link](https://developers.google.com/search/docs/appearance/snippet) · [link](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data) · [link](https://developers.google.com/search/docs/crawling-indexing/canonicalization) · [link](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- **docs.github.com** — [link](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- **dol.gov** — [link](https://www.dol.gov/general/ppii)
- **ecenica.com** — [link](https://www.ecenica.com/blog/best-practices-for-email-obfuscation-to-stop-email-scraping/)
- **eff.org** — [link](https://www.eff.org/deeplinks/2020/12/doxxing-tips-protect-yourself-online-how-minimize-harm)
- **freecodecamp.org** — [link](https://www.freecodecamp.org/news/reusable-html-components-how-to-reuse-a-header-and-footer-on-a-website/)
- **fyld.pt** — [link](https://www.fyld.pt/blog/javascript-patterns-improve-code-quality-at-scale/)
- **github.blog** — [link](https://github.blog/news-insights/bypassing-jekyll-on-github-pages/)
- **github.com** — [link](https://github.com/jsdelivr/bootstrapcdn)
- **iubenda.com** — [link](https://www.iubenda.com/en/help/22475-how-to-create-a-gdpr-contact-form)
- **krumzi.com** — [link](https://www.krumzi.com/blog/open-graph-image-sizes-for-social-media-the-complete-2025-guide)
- **monster.com** — [link](https://www.monster.com/career-advice/article/personal-info-on-your-resume)
- **nngroup.com** — [link](https://www.nngroup.com/articles/ia-vs-navigation/) · [link](https://www.nngroup.com/articles/homepage-design-principles/) · [link](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/) · [link](https://www.nngroup.com/articles/plain-language-experts/) · [link](https://www.nngroup.com/topic/tone-voice/)
- **ogp.me** — [link](https://ogp.me/)
- **postaffiliatepro.com** — [link](https://www.postaffiliatepro.com/faq/xml-sitemap-pages-include/)
- **sansec.io** — [link](https://sansec.io/research/polyfill-supply-chain-attack)
- **semrush.com** — [link](https://www.semrush.com/blog/website-structure/)
- **sessions.edu** — [link](https://www.sessions.edu/notes-on-design/visual-hierarchy-key-ux-principles-that-drive-results/)
- **sitepoint.com** — [link](https://www.sitepoint.com/stop-spam-harvesting-email-obfuscation/)
- **sonatype.com** — [link](https://www.sonatype.com/blog/polyfill.io-supply-chain-attack-hits-100000-websites-all-you-need-to-know)
- **ssd.eff.org** — [link](https://ssd.eff.org/module/how-to-manage-your-digital-footprint)
- **straightnorth.com** — [link](https://www.straightnorth.com/blog/xml-sitemaps-and-robots-txt-how-to-guide-search-engines-effectively/)
- **topinterviewtips.com** — [link](https://www.topinterviewtips.com/developer-portfolio-guide-projects-that-get-you-hired-in-2025)
- **uxpin.com** — [link](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/)
- **vfunction.com** — [link](https://vfunction.com/blog/dead-code/)
- **w3.org** — [link](https://www.w3.org/TR/WCAG22/) · [link](https://www.w3.org/WAI/tutorials/images/complex/) · [link](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) · [link](https://www.w3.org/WAI/WCAG22/Techniques/css/C39)
- **webaim.org** — [link](https://webaim.org/articles/contrast/) · [link](https://webaim.org/techniques/keyboard/) · [link](https://webaim.org/techniques/semanticstructure/) · [link](https://webaim.org/techniques/skipnav/) · [link](https://webaim.org/standards/wcag/checklist)
- **webportfolios.dev** — [link](https://www.webportfolios.dev/blog/web-developer-portfolio-guide)
- **youmightnotneedjquery.com** — [link](https://youmightnotneedjquery.com/)

---

*Generated from a verified multi-agent audit (104 agents, 8 dimensions × research → audit → adversarial verification).*
