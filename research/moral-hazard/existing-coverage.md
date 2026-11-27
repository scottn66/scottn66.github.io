# Existing coverage of moral hazard on the portfolio

Fetched 16 November 2026 (America/Los_Angeles) from the live pages and from `main` on `scottn66/scottn66.github.io`. Nothing below is a change to the site.

Sources:

- https://scottn66.github.io/actuarial-pricing.html
- https://scottn66.github.io/applied-decision-theory.html
- https://scottn66.github.io/decision-theory.html
- Raw copies: https://raw.githubusercontent.com/scottn66/scottn66.github.io/main/actuarial-pricing.html (and the two companion files)
- Homepage: https://scottn66.github.io/index.html
- Roadmap: https://scottn66.github.io/dashboard.html

## Shared stack and style

The three pages are a tightly cross-linked set, not three unrelated essays.

**Stack.** All three load MathJax 3 (`tex-svg`) from jsDelivr, with `$...$` and `$$...$$` delimiters. None of them uses KaTeX. None of them uses Plotly. The actuarial page has no interactive widget. The applied page has one vanilla JS break-even calculator with an inline SVG chart (`#widget-be`). The decision-theory page has three vanilla JS widgets (Bayes-net inference, VPI, counterfactual stepper). CSS is a large inline `<style>` block, not an external stylesheet, with the same token set: `--bg #FAFAFA`, `--accent #1F4E9E`, `--good`, `--warn`, `--gold`, `--see/--do/--imagine`. Body type is the system sans stack (`-apple-system`, `"Segoe UI"`, Roboto, Helvetica, Arial). Layout is a sticky dark topbar, a left table of contents, and a main column (`.page` is a two-column grid, about 760px of text). Shared components include `.badge`, `.act-tag` (the gold `.act-econ` tag marks insurance and pricing material), `.callout` (with `.gold`, `.good`, `.warn`, `.landmark`), `.aside-box`, numbered `.steps` / `.step` blocks, and a `.colophon`.

**Schema.** The applied page is "a problem set, not an essay." Each entry uses five beats: Setup, Principle, Work, Answer, Takeaway. The actuarial page is "a problem track, not an essay." Each thread uses those five beats plus two more: Givens and assumptions, and From first principles, then Worked numbers, Answer, In practice, and Takeaway. The decision-theory page is a curriculum ("the ladder") rather than a problem set. It is organized as acts, with definitions, worked examples, and widgets.

**Voice.** First-principles derivations, hand-checked arithmetic, a boxed answer, and a transferable takeaway. The actuarial colophon says every figure is "a small, first-principles example recomputed by hand." The applied colophon says the same of its figures and of the calculator. Cross-links are heavy: the applied topbar has "Actuarial track", the actuarial topbar and TOC have "the playground" and "the ladder," and both point back to `decision-theory.html`.

**Where they sit on the site.** As of this fetch, the homepage project grid lists `decision-theory.html` under AI and Machine Learning ("The Value of Knowing You"). It does not list `applied-decision-theory.html` or `actuarial-pricing.html`. The dashboard card "Decision theory series" also links only to `decision-theory.html`. The two companion pages are reachable from those pages' topbars, not from the homepage cards.

**A wording note for later drafts.** The actuarial lead calls actuaries "the original risk data-scientists." Scott's public title on the homepage is Data Engineer. A new page should not repeat that phrase.

## What each page already says

### Applied decision theory (`applied-decision-theory.html`)

The insurance thread (`#insurance`) and the shared break-even equation are the closest existing material.

The shared engine is

\[
p^{\ast} = \frac{C}{L - D}.
\]

Self-insuring costs \(p L\) in expectation. Insuring costs \(C + p D\). The buyer is indifferent at \(p^{\ast}\). Buy coverage if the true break rate exceeds \(p^{\ast}\). In the symbol table, \(D\) is "the residual cost you still pay even when covered," and the applied examples given for \(D\) are "a deductible, a service fee, a copay." The worked example is AppleCare+ on the iPhone 17 Pro Max: premium \(C = \$139.99\), screen repair \(L = \$379\), deductible \(D = \$29\), so \(p^{\ast} \approx 40\%\). The live calculator exposes \(C\), \(L\), \(D\), and the user's \(p\), and compares self-insure (\(p L\)) with insure (\(C + p D\)).

The page treats \(p\) as fixed. Nothing in the insurance thread, or in the calculator, lets coverage change the break rate or the loss size. Deductibles and copays appear only as a shrinkage of the transferred loss, from \(L\) to \(L - D\). They are not treated as incentive devices. The word "coinsurance" does not appear. "Moral hazard," "adverse selection," "principal-agent," and "hidden action" do not appear.

Risk aversion is mentioned once, in the insurance answer: a risk-averse buyer's threshold sits slightly below \(p^{\ast}\), "by a risk premium \(\approx \tfrac12 A(W)\,\mathrm{Var}(\text{loss})\)" that is "negligible when the loss is tiny against your wealth." The formula is the Arrow-Pratt approximation. The page does not name Arrow or Pratt. Expected utility is the stated engine of the whole playground (and of the law thread). Self-insurance is the alternative to buying the plan, not a comment on hidden effort.

### Actuarial pricing (`actuarial-pricing.html`)

This page prices a given loss distribution. It does not model how coverage changes that distribution.

The three tools announced in the lead are the time value of money (\(v = 1/(1+i)\)), the whole loss distribution (frequency times severity, and mortality), and the price of risk (loadings, and pricing under \(\mathbb{Q}\) rather than \(\mathbb{P}\)). The five threads are the equivalence principle, net-to-gross loadings, ruin and capital, real-world versus risk-neutral measures, and Bühlmann credibility.

The only phrase that touches selection is in thread 2's "In practice" note on loadings. A working actuary is said to split a 20% loading into named pieces: "acquisition commission, per-policy maintenance, the cost of capital held against adverse deviation, plus margins for anti-selection and lapse risk." "Anti-selection" is named, not modeled. "Moral hazard" does not appear. There is no deductible, coinsurance, copay, principal-agent, or hidden-action discussion.

Experience rating and bonus-malus do appear, but as applications of credibility, not as incentive remedies. Thread 5 (`#cred`) works a trucking-fleet example, \(Z = n/(n+k)\), and then says: "This same machinery drives experience rating, bonus-malus / no-claims-discount schemes in motor insurance, and workers' compensation." The takeaway is Bayesian shrinkage as an actuarial value of information, "the seller's cousin of the medicine problem's VPI."

Risk aversion appears on the seller side. The exponential premium principle uses the insurer's risk-aversion coefficient \(a\), \(H[S] = \frac{1}{a}\ln E[e^{aS}]\). Thread 4 treats the gap between \(\mathbb{P}\) and \(\mathbb{Q}\) as "risk aversion to the tail." "Self-insuring" on this page is the insurer holding capital against its own ruin, not the insured retaining a deductible.

### Decision theory (`decision-theory.html`)

The ladder page builds expected utility, maximum expected utility, and the value of perfect information, then climbs to `do` and counterfactuals. Utility theory is introduced through von Neumann-Morgenstern. VPI is "the crown jewel" of Act II. There is no insurance example, no deductible, no moral hazard, and no adverse selection. The one hit on "asymmetric" is a spam-filter illustration: "asymmetric utilities (a lost real email hurts more than a leaked spam)." Hits on "Arrow" are graph arrows, not Kenneth Arrow. The applied playground is advertised from this page as the place where the same engine is pointed at insurance, markets, medicine, and law.

The informativeness principle in contract theory (Holmström 1979) is a cousin of VPI, but that link is not drawn here.

## What is missing, and where a moral hazard piece would link in

None of the three pages defines moral hazard, distinguishes it from adverse selection, or lets the loss probability or loss size respond to coverage. The applied insurance widget is the natural place to show that gap. It already has \(C\), \(L\), \(D\), and a fixed \(p\). A moral hazard extension would make \(p\) or \(L\) a function of \(D\) (and of coinsurance, if that is added), then recompute both the buyer's break-even and the premium the seller must charge.

Suggested hooks, if a new page or a new thread is written:

| Existing anchor | Why it is the hook |
| --- | --- |
| `applied-decision-theory.html#insurance` and `#widget-be` | Deductible \(D\) is already in the break-even formula, but \(p\) is fixed. This is the cleanest "what the playground skipped" opening. |
| `applied-decision-theory.html` symbol table, row \(D\) | Already lists deductible and copay as residual cost. Coinsurance can be added as another form of \(D\), now with an incentive reading. |
| `actuarial-pricing.html#loading` | The loading already includes a named "anti-selection" margin. A moral hazard page can separate that margin from a moral-hazard loading, and can show why a deductible can substitute for a larger loading. |
| `actuarial-pricing.html#cred` | Experience rating and bonus-malus are already named. They can be re-read as incentive and selection devices, not only as shrinkage toward a book rate. |
| `decision-theory.html#utility` | Expected utility and risk aversion are the buyer's side of the optimal-insurance tradeoff. The applied page already uses the Arrow-Pratt approximation without naming it. |
| `decision-theory.html#vpi` | VPI is the value of information before a decision. The informativeness principle is the value of a signal inside a hidden-action contract. |

A standalone page that uses the actuarial seven-beat schema, with one or two vanilla JS widgets and MathJax 3, would match this set better than a Plotly essay. It should be linked from both companion topbars and, if Scott wants it findable from the homepage, from the decision-theory series card as well.

