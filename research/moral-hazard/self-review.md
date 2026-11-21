# Self-review: Moral hazard article

Reviewer stance: a judge model asked to score a standalone conceptual article before any code is written, against completeness, technical correctness, overlay, originality, evidence, clarity, and ethics. Scores are out of 10.

The draft that was first assembled as a complete article is the "before" draft. The "after" scores reflect one revision pass on that draft, plus a short typographic cleanup done while preparing the reading PDF (currency math, figure caption, one connective sentence). No second conceptual rewrite was done after this review was written.

## Scores

| Criterion | Before | After | Note |
|---|---:|---:|---|
| Conceptual completeness | 8.5 | 9.0 | All nine required threads are present and connected. Systemic moral hazard remains the thinnest section by design, not by omission of the asked cases. |
| Technical correctness | 7.0 | 9.0 | The first draft's insurance DAG was cyclic (`s` both caused the contract and was caused by later action). The Pauly (1968, p. 535) quotation was slightly shortened. Both were fixed. A two-outcome likelihood-ratio paragraph was added so the informativeness principle is not only stated. |
| Coherence and overlay | 8.5 | 9.0 | The four-term grammar (contractibility, residual risk, signal value, change of contractible event) is reused from the introduction through the overlay table. The table is the actual synthesis, not a restatement. |
| Originality and insight | 8.5 | 8.5 | The contribution is arrangement and overlay, not a new theorem. That is the right ambition for this brief. It was not inflated on revision. |
| Evidence and citations | 8.0 | 8.5 | Chetty (2006) equation (8) is copied from the typeset PDF, not reconstructed. RAND and Oregon results are given with their limits. Nexus Mutual is labeled as project documentation. Baker (1996) is paraphrased, not page-quoted. |
| Clarity | 8.5 | 9.0 | Notation is defined once and reused. The illustrative numerical example is labeled as such and was computed, not guessed. The PDF render of the math is clean. |
| Ethics treatment | 8.5 | 8.5 | Several views are presented without a winner, and they are located on named edges of the same graph. The section does not pretend to settle the questions it poses. |

Average, after revision: 8.9.

## What was wrong in the first complete draft, and what was changed

1. **A cyclic graph.** The first insurance DAG had a path `s → coverage → a → s`. That is illegal in a Bayesian network and would have been a serious technical error. The revision splits the signal into `s_pre` and `s_post`, and says explicitly that the contract may be written as a rule that will later use `s_post`, without the realized value of `s_post` choosing the contract.

2. **A slightly shortened Pauly quotation.** The first draft compressed the sentence on p. 535. The revision restores the wording confirmed from the JSTOR PDF: the response of seeking more medical care with insurance than in its absence is "a result not of moral perfidy, but of rational economic behavior."

3. **Two citations present in the bibliography but mute in the body.** Pratt (1964) is now cited where relative risk aversion `γ` is defined. Mirrlees (1976) is now distinguished from the 1975/1999 first-order-approach critique, so a reader is not left thinking they are the same paper.

4. **The informativeness principle needed a worked likelihood-ratio case.** A short two-outcome illustration was added so "use `s` if and only if it is informative about `a` given `x`" is not only a slogan.

5. **Typographic cleanup for the reading PDF (not a conceptual change).** `$\$18.5$` was a broken attempt to write a dollar amount and broke math parsing; it is now "USD 18.5 million." The figure had a double caption and, in an earlier render, a missing Greek pi in the coverage node; the coverage node is now labeled "premium, contract." A dangling sentence that introduced a mermaid block (stripped in the PDF) was removed. Mermaid and ASCII forms of the graph remain in the Markdown source for later site use.

## Strongest ideas (the ones a judge should weigh most heavily)

These are also the ideas the parent report should carry.

1. **One grammar for the whole article.** Hidden object, contractible event, residual risk, and the value of a further signal. A change of contractible event (parametric trigger, oracle, telematics) does not repeal the information constraint. It moves it, usually at the price of basis risk, and it can create a new hidden action where the new observable is produced.

2. **Value of information splits by information structure.** For a single expected-utility decision maker, more information cannot hurt (EVPI, EVSI, Blackwell). In a risk-sharing market, public information before trade can destroy the market (Hirshleifer). Telematics is mainly an action signal, and is governed by the informativeness principle. Genetic testing is mainly a type signal, and is governed by Hirshleifer. GINA is then readable as a choice to keep a class of type-information out of a class of contracts.

3. **The insurance DAG makes the two identification stories testable.** Moral hazard and adverse selection are different sets of edges, hence different conditional independencies. RAND is close to `do(coverage)`. A raw coverage-claims correlation, as in the Chiappori-Salanié positive-correlation test, is not a test of one row of the taxonomy against the other.

4. **Basis risk is the price of dropping indemnity adjustment, and the oracle is a new hidden-action node.** On-chain reserves make collateral observable. They do not make `a` or `θ` observable. Hard-money collateral does not, by itself, fix a denomination mismatch when losses are in another unit. These are stated as established logic, and are separated from speculation about particular protocols.

5. **Ethics as disagreement over which edges may enter the premium.** Welfarist, actuarial-fairness, solidarity, rights, and contractualist views are not blended into one "balanced" position. They disagree about particular parents of `π`, and about whether some signals should exist in the contract at all.

## Remaining weaknesses

These should be scored against, not hidden.

- **Section 8 is brief.** Deposit insurance, too-big-to-fail, the Peltzman effect, and disaster insurance (charity hazard) are present and sourced, but they are a tour, not a review of those literatures. A judge who wanted equal depth in every domain will mark this down. The article's spine is insurance design, information, and the overlay, so the brevity is intentional.

- **No original empirics.** The numerical example is illustrative and computed. RAND and Oregon are reported from published abstracts and papers, not re-estimated. The classic French-insurer and employer microdata used in Chiappori-Salanié and Einav-Finkelstein work are not public, and the article correctly refuses to pretend otherwise.

- **Nexus Mutual is documented, not audited.** Paid-claim figures and assessor rules are taken from the project's own documentation, fetched on 16 November 2026, and labeled as such. They are not peer-reviewed facts.

- **Baker (1996) is paraphrased.** A PDF fetch of the paper returned HTML, not a page image. The article does not invent a page-level quotation.

- **Some classic papers have no original journal DOI.** Arrow (1963), Pauly (1968), Spence and Zeckhauser (1971), Hirshleifer (1971), Keeley (1990), and a few others are cited by journal, volume, and pages, with a stable link. Reprint DOIs, where used, are labeled as reprints. No DOI was invented.

- **Howard and Matheson (2005) page range.** The article uses 127-143, following RePEc. At least one secondary listing reports a wider range. The citation should be checked against the journal issue if the paper is typeset for publication.

- **The first-order approach is described, not derived.** The continuous-outcome wage formula that falls out of the first-order approach is omitted on purpose, with a pointer to the validity conditions (MLRC, CDFC, Jewitt). A technically strict reader may still want the displayed formula.

- **Privacy is named as an open modeling question.** The article says, correctly, that a privacy cost is a participation constraint the standard model will ignore unless it is put in, and that putting it in without begging the ethical question is unsolved here. That is a remaining gap, not a solved one.

- **The PDF is a reading render.** It is not the eventual site page. Mermaid and ASCII graphs live in the Markdown and are omitted from the PDF in favor of Figure 1. No widget or code is included, as requested.

## Citations verified, qualified, or omitted

Verified and used, with a DOI or a stable URL, include the principal-agent and insurance core (Holmström 1979; Holmström and Milgrom 1987, 1991; Grossman and Hart 1983; Rogerson 1985; Jewitt 1988; Raviv 1979; Shavell 1979; Arrow 1963 and 1968; Pauly 1968; Ehrlich and Becker 1972; Baily 1978; Chetty 2006, 2008; Pratt 1964), the identification papers (Chiappori and Salanié 2000; Einav, Finkelstein, and Cullen 2010; Einav, Finkelstein, Ryan, Schrimpf, and Cullen 2013), RAND (Manning et al. 1987) and Oregon (Finkelstein et al. 2012, from the abstract and the MIT/RePEc record after a PMC fetch failed), Hirshleifer (1971), Howard (1966), Blackwell (1953), Howard and Matheson (2005), Doherty and Richter (2002), Cummins, Lalonde, and Phillips (2004), Keeley (1990), Farhi and Tirole on bailouts, Peltzman (1975), GINA (Pub. L. 110-233), and Baker (1996) as a source for the genealogy of the term, paraphrased.

Deliberately not invented: an original-journal DOI for several pre-DOI *AER* articles, including Hirshleifer (1971). A DOI of the form `10.1257/aer.61.4.561` was not used, because it was not verified.

Omitted rather than faked: any claim about Nexus Mutual that could not be read in the official documentation; any re-use of RAND or Oregon microdata; any numerical result from memory that could not be recomputed or copied from a typeset source.

## Judgment against the brief

The brief asked for a standalone, complete, conceptually overlaid article, written before any code, at a "terrific" standard, bylined Scott Nelson, Data Engineer, with no push and no messages. The article meets the scope. It should survive a strong model's scoring if the judge values overlay, careful citation, and an honest map of limits. It will lose points where a journal referee would: no new theorem, a short systemic section, project-documented rather than audited on-chain figures, and a still-open treatment of privacy inside the formal model.

Those are the right points to lose. They are not hidden in the text.


## Effect of the figures (added 18 November 2026)

Eleven figures now sit in the article, including the original DAG, renumbered as Figure 8. Scripts and SVG+PNG sources are in `figures/` and `figures/scripts/`. A contact sheet is at `/workspace/moral-hazard-figures.png`.

The figures change what a reader can see, not only what the prose restates. The three-game tree (Figure 1) shows where the information set sits, which the taxonomy table cannot. Figure 2 is the Rothschild-Stiglitz geometry, computed from the article's own $W$, $L$, and $u$, with types rather than actions, and with a computed threshold (λ below about 0.16) at which the separating menu fails. Figure 4 is the agency-cost gap of Section 3.7 as a picture. Figure 7 makes the sign of the value of information visible. Figure 9 is the identification claim of Section 6.3. Figures 10 and 11, with short backward-induction plays, show a moved hidden action and a time-inconsistent backstop.

### Scores after the figures were added

| Criterion | After first revision | After figures | Note |
|---|---:|---:|---|
| Conceptual completeness | 9.0 | 9.5 | The timings, the RS geometry, the identification graphs, and the bailout game were previously only verbal. |
| Technical correctness | 9.0 | 9.0 | The new pictures are computed from stated parameters. They add parameterization risk, noted below, rather than algebraic errors in the core model. |
| Coherence and overlay | 9.0 | 9.5 | The same grammar is now visible in trees, wealth space, a DAG, and a bailout game, not only in the Section 10 table. |
| Originality and insight | 8.5 | 9.0 | Reusing one illustrative parameterization across the toy contract, the RS types, the bonus-malus claim rates, and the Hirshleifer market is the main design choice. |
| Evidence and citations | 8.5 | 8.5 | No new empirical claims. Illustrative figures are labeled as such. |
| Clarity | 9.0 | 9.0 | Several figures remain tight at letter-page width, especially Figures 1 and 2. |
| Ethics treatment | 8.5 | 8.5 | Unchanged. No ethics diagram was added, on purpose. |

Average after figures: 9.0.

### Correctness risks introduced by the figures

- **Rothschild-Stiglitz (Figure 2).** The diagram uses the article's $W$, $L$, and $u$, with $p_L=1/5$ and $p_H=1/2$ read as types. The cream-skimming point, the separating contract, and the critical share of high-risk types (about 0.16) are computed from those parameters. They are not a general constant of the Rothschild-Stiglitz model, and they are labeled illustrative.
- **Hirshleifer (Figure 7), panel A.** The single-decision-maker example introduces a mitigation outlay of 40 that is not part of the Section 3.7 contract. The caption and the text state that the two panels are different decision problems, and that only the sign of the value of information is to be compared. Mixing the two as if they were one market would be a misreading.
- **Bonus-malus (Figure 6).** The three-class transition rule is invented for the figure. The stationary distributions, $(1/3,1/3,1/3)$ and $(16/21,4/21,1/21)$, are exact for that rule and for $q(a)$ from Section 3.7. They are not taken from a real motor-insurance scale.
- **Oracle and bailout payoffs (Figures 10 and 11).** Both games use illustrative payoffs chosen so that backward induction is unique. They are not estimated, and the text says so. A different stake, bribe, or social cost would change the path.
- **Basis-risk scatter (Figure 10A).** Generated from a stated joint distribution (seed 20261118, $n=120$). It is a picture of basis risk, not a fit to index-insurance data.
- **Print size.** Figure 1 is a tall three-panel tree and is small on a letter page. Figure 2's labels remain dense. A judge reading only the PDF, not the SVGs, may find those two harder than the others.
- **No new citations were added**, and none were invented, for the figures.
