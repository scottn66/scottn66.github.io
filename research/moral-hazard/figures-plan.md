# Figures and game sequences: plan

The aim is a small set of pictures that teach something the present prose, tables, and existing DAG do not. Each kept figure has to change what a careful reader can see, not merely decorate a section. All computed curves use stated, illustrative parameters, mostly the article's own toy example ($W=121$, $L=96$, $u(w)=\sqrt{w}$, $q(0)=1/2$, $q(1)=1/5$). Nothing is estimated from data. Color, type, and node shapes follow the existing Figure 1 palette (blue, gold, purple, plus Wong vermillion and orange where a third contrast is needed), with shape or line style carrying meaning and not color alone.

Target: about eleven figures, including the existing DAG, numbered in the order they appear.

## Kept

**Figure 1. Three games, and where the information set sits.** Section 2.4.
Three extensive-form panels in one visual grammar: hidden-action insurance, screening (Rothschild-Stiglitz timing), and signaling (Spence timing). What prose and the taxonomy table cannot show is the location of the dashed information set. In moral hazard the principal has already offered the contract, and the hidden object is the agent's later action. In screening, Nature draws a type and the uninformed principal offers a menu inside an information set over types. In signaling, the informed party moves first, and the dashed line sits at the uninformed party's response. A short numbered play in the text walks the hidden-action tree.

**Figure 2. Screening in state-contingent wealth, and possible nonexistence.** Section 2.4, referenced again in 4.4.
A Rothschild-Stiglitz diagram in the $(w_{\mathrm{no\ loss}}, w_{\mathrm{loss}})$ plane, computed from the same $W$, $L$, $u$ as the toy example, with types $p_L=1/5$ and $p_H=1/2$ (here these are pre-existing types, not chosen actions). Panel A: endowment, fair-odds lines, full insurance, the high-risk indifference curve that anchors a separating menu, and the cream-skimming attack on a pooling contract. Panel B: how that separating menu itself can fail to be an equilibrium when the share of high-risk types is small. The geometry is the result; the numbers are illustrative.

**Figure 3. Which signals belong in the contract.** Section 3.5, referenced in 5.4.
Two panels. Left: a discrete outcome and an extra signal, with likelihood ratios showing when $s$ is informative about $a$ given $x$, and when $x$ is already a sufficient statistic. Right: a Blackwell garbling, $s_B$ as $s_A$ passed through further noise. The informativeness principle and the Blackwell order are easy to conflate in prose; the picture keeps "does this signal change the likelihood ratio given $x$?" distinct from "is this monitor a noisy version of that one?"

**Figure 4. The illustrative contract: first best, second best, and the agency cost.** Section 3.7.
Computed entirely from the article's toy parameters. Panel A: state-contingent wealth, with the uninsured point $(121, 25)$, the first-best sure point at $101.80$, and the second-best point at about $(113.80, 53.79)$ on the high-prevention fair-odds line. Panel B: expected utility as a function of the coinsurance rate $\alpha$, under the zero-profit premium for $a=1$, with the incentive-compatibility threshold $\alpha^{\ast}\approx 0.625$, the first-best value, and the agency-cost gap marked. This is the moral-hazard trade-off as a picture.

**Figure 5. Deductible and coinsurance, once losses can vary.** Section 4.2.
Indemnity, and the insured's out-of-pocket, as functions of a variable loss $L$. The two instruments are calibrated to be the same contract at the toy example's single loss, $d=\alpha L \approx 60$ at $L=96$, and then shown to come apart for smaller and larger losses. Prose says this; the crossing at one $L$ and the divergence elsewhere is what a reader should see.

**Figure 6. Bonus-malus as a Markov chain on rating classes.** Section 4.2.
A three-class chain with a stated, illustrative transition rule: a claim moves the insured one class worse, a claim-free year one class better. The claim probability is the toy example's $q(a)$. The figure shows the transition diagram and the two stationary distributions, under $a=0$ and $a=1$. The point is not "how credibility works as statistics." It is that today's action moves the future premium, which is why experience rating is an incentive instrument.

**Figure 7. When information can hurt.** Section 5.2.
A computed contrast, labeled illustrative. Left: a single decision maker, for whom the expected value of perfect information is nonnegative. Right: the same risk-averse preferences facing a fair insurance market, with and without public revelation of the loss state before trade. Ex ante utility falls once the veil is lifted (Hirshleifer). The two panels share a vertical scale in expected utility so the sign difference is visible.

**Figure 8. An acyclic graph of the insurance relationship.** Section 6.1.
The existing DAG, renumbered. No change in content, aside from matching any typographic cleanup of the shared style.

**Figure 9. Two graphs, two tests.** Section 6.3.
Side-by-side subgraphs: adverse selection only (type as a common cause of coverage and claims) versus moral hazard (a causal path from coverage to use or to loss). The $do(\text{coverage})$ intervention is marked, and the paths that remain or vanish are the Chiappori-Salanié versus RAND contrast. Figure 8 is the full relationship; this figure is the identification claim.

**Figure 10. Parametric cover: basis risk, and the oracle's hidden action.** Section 7.3, referenced in 7.5.
Panel A: an illustrative scatter of actual loss against index payout, generated from a stated joint distribution, with the 45-degree indemnity line and the two basis-risk regions (loss without payout, payout without loss). Panel B: an extensive-form oracle game with a stake, a possible misreport, and a chance of detection and slashing, plus a short backward-induction play in the text. The two panels together are the section's rule: moving the contractible event off the individual loss buys off one hidden action with basis risk, and can create another hidden action at the reporter.

**Figure 11. A bailout as a time-inconsistency game.** Section 8.
An extensive-form tree in which a bank chooses risk and, after a failure, a regulator who cannot commit re-optimizes ex post. Illustrative payoffs are chosen so that backward induction is unique: the regulator bails out once failure is realized, the bank anticipates this and takes the risky action, and both are worse, ex ante, than under commitment to no bailout. This is the grammar of Section 7.7 in reverse, which the present prose states and does not show.

## Dropped, and why

- **A standalone EVPI decision tree.** The useful contrast is not that EVPI is an upper bound, which the text already states, but that the sign of the value of information can flip in a market. That contrast is Figure 7.
- **A continuous likelihood-ratio wage schedule from the first-order approach.** The article deliberately does not display that formula, because of the validity caveats in Section 3.4. A discrete likelihood-ratio picture is included in Figure 3 instead.
- **A second "EU versus coverage" figure, separate from the toy example.** Merged into Figure 4.
- **A multitasking cartoon of effort pulled between two tasks.** The prose already states the redirection; a new picture would not add a constraint or a number.
- **A Peltzman schematic.** The article treats the magnitude as debated and is not in a position to draw an empirical offset.
- **A new overlay graphic that redraws Section 10's table.** The table is the overlay. The new trees, the DAG comparison, and Figure 4 already carry the grammar. A poster-style summary would be decorative.
- **An ethics diagram.** The disagreement is over which edges may enter $\pi$. Drawing those edges as a moral compass would editorialize what Section 9 is careful not to settle.

## Production notes

- Static PNG and SVG in `figures/`, scripts in `figures/scripts/`, shared typography in `style.py`.
- Captions are sentence case, say what to look at, and mark computed examples as illustrative.
- Each figure is referenced by one or two sentences in the body, with a short numbered play for Figures 1, 10, and 11.
- The reading PDF and a contact sheet of all eleven figures are produced after integration. No site code, no push, no messages.
