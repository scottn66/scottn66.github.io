# Research plan: a moral hazard page for the portfolio

Draft only. Nothing is to be pushed, opened as a PR, or sent to anyone until Scott approves.

The public title on the site is Data Engineer. New prose should use that title, and should not repeat the actuarial page's phrase "the original risk data-scientists."

## Research questions

1. How should moral hazard be defined, in the economic sense, so that a reader who already knows the break-even formula \(p^{\ast}=C/(L-D)\) can see what that formula assumes away? The assumption to be dropped is that \(p\) and \(L\) do not depend on coverage.
2. How is moral hazard (hidden action) distinct from adverse selection (hidden type), and why is a raw positive correlation between coverage and claims not enough to separate them? (Rothschild and Stiglitz 1976; Chiappori and Salanié 2000; Einav, Finkelstein, and Cullen 2010; Einav, Finkelstein, Ryan, Schrimpf, and Cullen 2013.)
3. What is the optimal-insurance tradeoff once both risk aversion and a behavioral response are present? In particular, when is a deductible or a coinsurance rate a solution rather than an ad hoc restriction? (Mossin 1968; Zeckhauser 1970; Raviv 1979; Baily 1978; Chetty 2006.)
4. What do the best-identified empirical designs actually measure, and what do they not measure? RAND identifies a price response by random assignment of cost sharing (Manning et al. 1987). Oregon identifies the effect of winning Medicaid coverage in a lottery (Finkelstein et al. 2012). Neither is a test of hidden-type selection.
5. Which contract devices, already named on the actuarial page, can be re-read as incentive instruments: deductibles, coinsurance and copays, experience rating and bonus-malus, and monitoring or telematics? How do they relate to the informativeness principle (Holmström 1979) and to credibility (actuarial thread 5)?
6. How far should the same logic be carried into domains beyond personal insurance, in particular unemployment insurance, deposit insurance and bailouts, disaster insurance, and risk compensation in driving (the Peltzman effect)? The write-up should stay with mechanisms and evidence, and should not become a political argument.

## Proposed page outline

Recommended form: a standalone page, `moral-hazard.html`, written in the actuarial seven-beat style, with the applied page's five-beat problems used for one or two worked examples and widgets. MathJax 3, vanilla JS, the same CSS tokens as the companions, no Plotly. This matches `actuarial-pricing.html` and `applied-decision-theory.html`. Those two pages do not use KaTeX. If Scott later wants one math stack across the whole site, that is a separate choice.

Suggested badges: "Companion to the actuarial track and the playground"; "hidden action · cost sharing · optimal insurance"; "live calculator" if a widget ships.

**Lead.** One short statement of the problem. The playground treats the break rate \(p\) as fixed, and reads a premium backwards into that probability. If coverage itself changes \(p\) or \(L\), the fair premium, the buyer's break-even, and the social value of insurance all move. The page will keep harm and insurance value in the same frame: insurance is useful because of risk aversion, and costly because of hidden action.

**Thread 1. Origins, and a definition.** Setup: Arrow (1963), Pauly (1968), Arrow's 1968 reply. Principle: moral hazard is a price or incentive response, not a moral diagnosis. Worked comparison of the two 1968 comments. Takeaway: full coverage is not generally optimal once demand responds to the insured price. In practice: name the ex ante / ex post split (Ehrlich and Becker 1972; Zweifel and Manning 2000) and keep the evidence gap visible. Ex post utilization in health is the better-documented case. Ex ante prevention is theoretically ambiguous and empirically thinner.

**Thread 2. The playground formula with a behavioral response.** Start from \(p^{\ast}=C/(L-D)\) on `applied-decision-theory.html#insurance`. Replace fixed \(p\) with \(p(D)\) or with a coinsurance rate, and show how the seller's required premium and the buyer's decision both change. This is the natural home of the first widget, an optimal deductible or coinsurance simulator. Link back to the AppleCare example: a deductible already shrinks cover to \(L-D\); the new point is that it can also shrink \(p\) or \(L\).

**Thread 3. Hidden action, and the informativeness principle.** A short principal-agent statement (Holmström 1979; Grossman and Hart 1983). The informativeness principle, written as the contract-design cousin of VPI on `decision-theory.html`. One paragraph on linear contracts and coinsurance (Holmström and Milgrom 1987), and one on multitasking (1991): strong incentives on a measured claim can dull unmeasured prevention or quality.

**Thread 4. Distinct from adverse selection.** Rothschild and Stiglitz (1976). The actuarial page already names an "anti-selection" loading. This thread separates that loading from a moral-hazard loading. Then the positive-correlation test (Chiappori and Salanié 2000) and why it cannot, alone, tell the two problems apart. Point to Einav-Finkelstein work for designs that go further, and be explicit that their employer microdata are not public.

**Thread 5. What the experiments show.** RAND (Manning et al. 1987; Aron-Dine, Einav, and Finkelstein 2013) and Oregon (Finkelstein et al. 2012). Quote only published figures, with citations. Do not invent cell means. If a second widget is built, it should plot published plan-level RAND results, or results the reader computes after obtaining ICPSR or NBER files under their terms.

**Thread 6. Remedies the contract can carry.** Deductibles (Mossin 1968; Raviv 1979), coinsurance and copays (Zeckhauser 1970), experience rating and bonus-malus (already named at `actuarial-pricing.html#cred`), monitoring and telematics (Holmström 1979; Edlin 1999). Frame these as self-sustaining mechanisms that keep insurance solvent by putting some of the loss, or some of the future premium, back on the party who can change it.

**Thread 7. Other domains, kept short.** Unemployment insurance and the Baily-Chetty tradeoff (Baily 1978; Chetty 2006, 2008). Deposit insurance, too-big-to-fail, and bailouts (Keeley 1990; Farhi and Tirole 2012). Disaster insurance and charity hazard (Raschky and Weck-Hannemann 2007; Browne and Hoyt 2000). The Peltzman (1975) offset as a cousin of ex ante moral hazard, not as an insurance-contract result. Each item gets a mechanism, a citation, and a limit. No policy prescription.

**Colophon.** What is Scott's exposition and what is cited. Every number either recomputed from a stated model or quoted from a named table or abstract. Link the three companion pages.

## Interactive ideas and datasets

Both ideas below are meant to be vanilla JS widgets, in the same style as `#widget-be` on the applied page, not Plotly dashboards.

### Idea 1. Optimal deductible or coinsurance simulator under a behavioral response

The user sets a loss \(L\), a loading, a risk-aversion coefficient, and an elasticity of use or of hidden effort with respect to out-of-pocket share. The widget returns the premium, expected uninsured loss, and expected utility (or a certainty equivalent) as functions of the deductible or the coinsurance rate, and marks the optimum.

This is the data-engineering-friendly version of thread 2. It does not require microdata. Default elasticity can be calibrated to the Manning et al. (1987) abstract figure of a price elasticity of about 0.2 in absolute value, with the citation on the widget and a warning that a single elasticity is a simplification of the RAND design. The risk-premium side should use a named utility (for example CARA, which matches the actuarial exponential principle) rather than an unnamed curve.

A second mode can treat hidden prevention effort explicitly, so the user sees ex ante moral hazard rather than only an ex post utilization elasticity.

No dataset gate. This is the better first widget.

### Idea 2. An empirical widget, with an honest limit on what public data can do

A true Chiappori-Salanié positive-correlation test needs contract choice and claims on the same policies, plus the observables the insurer used. The original French insurer file in Chiappori and Salanié (2000) is not public. The Einav-Finkelstein employer files are not public. The plan should not promise a replication of those papers on a public file.

Three public options exist, with different identifications:

**A. Published RAND plan-level results.** No microdata license. The widget would display expenditure or visits by cost-sharing plan, taken from tables in Manning et al. (1987) or from the Aron-Dine, Einav, and Finkelstein (2013) review, typed in by hand and cited cell by cell. This is the safest empirical widget, and the one that best matches the site's "every figure is checked" standard.

**B. RAND microdata, ICPSR 6439.** [Study page](https://www.icpsr.umich.edu/web/NACDA/studies/6439), DOI [10.3886/ICPSR06439.v1](https://doi.org/10.3886/ICPSR06439.v1). The ICPSR study page, fetched 16 November 2026, says the public-use files are available to the general public and do not require affiliation with a member institution. A free ICPSR account is still typically required. RAND's older instructions page still mentions possible fees for non-members, so access terms should be confirmed at download time. Redistribution of the microdata on the GitHub site is probably not allowed. A reproducible script that the reader runs after obtaining the files is the right pattern. Random assignment of plans identifies moral hazard, not adverse selection.

**C. Oregon public-use files, NBER.** [Oregon data page](https://www.nber.org/research/data/oregon-health-insurance-experiment-data). Replication code is posted for Finkelstein et al. (2012) and later Oregon papers. The download requires agreement to terms: no identification of subjects, no commercial use, and citation of the data. Same constraint: do not host the microdata in the public repo. The lottery identifies the effect of Medicaid coverage, not a deductible elasticity inside a private contract.

**A related, weaker public file, not a positive-correlation test.** CASdatasets `freMTPL2freq` ([documentation](https://dutangc.github.io/CASdatasets/reference/freMTPL.html)) has 677,991 French motor third-party liability policies, roughly 2011-2013, with `BonusMalus`, `ClaimNb`, and `Exposure`. The source is stated as an unknown private insurer. This file is public and easy to obtain through the CASdatasets R package. It can support a descriptive plot of claim frequency against bonus-malus. It cannot support a Chiappori-Salanié test of optional coverage, because it has no coverage-choice variable, and it is not the 2000 sample. If this file is used, the widget title should say "experience rating and claims," not "a test of asymmetric information."

Recommendation: ship idea 1 first, plus idea 2A (published RAND cells). Treat 2B and 2C as optional later work if Scott is willing to obtain the files under their terms. Use `freMTPL2` only with the caveat above, perhaps as a small companion to the actuarial credibility thread rather than as a test of moral hazard.

## Cross-links

| Destination | Role on the new page |
| --- | --- |
| `applied-decision-theory.html#insurance` and `#widget-be` | Opening hook. The formula the new page generalizes. |
| `decision-theory.html#utility` | Expected utility and risk aversion, buyer's objective. |
| `decision-theory.html#vpi` | Cousin of the informativeness principle. |
| `actuarial-pricing.html#loading` | Anti-selection margin, exponential premium, seller risk aversion. |
| `actuarial-pricing.html#cred` | Experience rating and bonus-malus, already named. |
| Homepage `index.html` and `dashboard.html` | Only if Scott wants the page findable from the project grid. The two companions are not on those cards today. |

The new page should also be added to the topbars of the two companions, in the same way those two already point at each other. That change would be part of a later draft, not of this research folder.

## Open questions for Scott

1. Should this be a standalone page, `moral-hazard.html`, or a new thread on the actuarial track, or a new problem on the applied playground? The outline above assumes a standalone page in the actuarial seven-beat style, with one playground-style widget.
2. How wide should domain coverage be in the first public draft? Health and auto plus the Baily-Chetty formula would be a tight first version. Deposit insurance, bailouts, disaster insurance, and the Peltzman effect can stay in the map and wait, or they can appear as a short final thread. The wider the domain list, the more care is needed to keep the tone to mechanisms and evidence.
3. Which interactive should be built first: the deductible and coinsurance simulator (no microdata), a widget of published RAND plan-level figures, or a script that the reader runs on ICPSR 6439 or the NBER Oregon files after obtaining them under their terms?
4. May published numerical results from Manning et al. (1987) and from the Oregon first-year paper be retyped into a widget, with citations, or should the page describe those findings in words and leave the tables in the papers?
5. After this map, what is the next step you want: a full page draft in this folder for your review, a review branch that is still not a PR, or literature and data-prep jobs written as Grok Build prompts and held until you say to queue them?

## Optional Grok Build work, not queued

If Scott wants later jobs in the grok-run queue, three that fit the existing conventions (mechanical pass/fail, owner Webby, inputs in `./in/`, outputs in `./out/`, named allowed domains) would be:

1. A typeset-formula extraction job: pull the exact Baily-Chetty expressions from Chetty (2006) and the RAND plan-level figures from Manning et al. (1987) or Aron-Dine, Einav, and Finkelstein (2013), and write a cited `figures.json`. Fail honestly if a PDF cannot be fetched.
2. A simulator-check job: given a small reference implementation of the deductible widget, recompute a grid of certainty equivalents and confirm the optimum moves with elasticity and loading in the predicted direction.
3. A data-access job: attempt to reach the ICPSR, NBER, and CASdatasets documentation pages, and write `access.json` describing what is actually downloadable without a paid affiliation. Do not download restricted microdata in the job.

None of these has been queued.

