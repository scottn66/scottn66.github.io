# Deep-Research Pass 3 — Adversarial Verification Record
### Archival log for the 110-agent deep-research run of 2026-06-19 (session `af26b554`, task `wsud11lsv`)

> **Why this file exists:** `conscious-agents.html` cited a "(1–2) adversarial refutation" of the MDP/Markov-reward-process bridge that appeared in **no repo log** — the event happened in a live session workflow whose output was never archived. The review pass of 2026-06-26 (see `conscious-agents-review-findings.md`, finding F1/CM-2) flagged the citation as unauditable. This file reconstructs the verification record **from the session transcript** so the citation chain is complete. Reconstructed, not raw output — the original temp file was garbage-collected.
>
> **Vote convention in this pass:** 3 verifiers per claim; **2/3 refutes kill the claim**. A "1-2" result = 1 uphold / 2 refutes = **killed**. ⚠️ This differs from Pass 2's reporting, where "1-2" on the free-particle claim was described as *contested* — do not equate the two conventions across passes.

## Run parameters

- 6 search angles → 27 sources fetched → 117 claims extracted → 25 verified → **21 confirmed, 4 killed** → 5 synthesized findings
- 110 agent calls, ~3.68M subagent tokens

## The four killed claims (verbatim)

1. **[0-3]** "The trace order forms a non-Boolean logic, which maps homomorphically to a 'Lebesgue logic' of probabilistic beliefs — providing a **published** basis for the research question's trace-logic / non-Boolean claims." *(source: sciety.org abstract listing)*
   — Killed as **stated-from-abstract-only**: at verification time the preprint body was unreachable (HTTP 403), so "published basis" could not be sustained. **Later resolved:** the full-PDF read (log 3) confirmed the theorems in-text. The kill was about evidentiary status, not the mathematics.

2. **[1-2]** "The trace order induces a logic on Markov kernels (trace logic) that is globally non-Boolean — having no greatest kernel and many incomparable elements — yet maps homomorphically to a 'Lebesgue' logic of probabilistic beliefs; the trace-order relation is P ≤t Q iff P is a trace of Q." *(source: ResearchGate record)*
   — Same evidentiary problem as #1; also later resolved by the full-PDF read.

3. **[1-2]** "A Markovian policy in an MDP induces a Markov process on the state space, and the joint state-reward process (X_t, r_t(X_t,Y_t)) is itself a Markov process termed a 'Markov reward process.' **This is the precise formal mechanism by which Hoffman's 'policy' (action selection over observer windows) yields a derived/induced transition structure that is again Markov.**" *(source: ASU STP425 MDP lecture notes)*
   — ⚠️ **This is the kill that `conscious-agents.html` cites.** Note the claim is compound: the first sentence is textbook-true (Puterman); what the refuters rejected is the bolded **bridge** — that this mechanism is *Hoffman's*, formalizing policy-over-windows. No primary source uses MDP/reward/policy language. The correct citation is therefore: *"the textbook induced-chain fact stands; the Hoffman-formalization bridge was killed 1-2 in the Pass-3 verification (this log) — and independently has no primary-source support (Pass 1 §2.3, Pass 2 Thread 4)."*

4. **[0-3]** "The structure-preserving compression over the selected subset I is provably a legitimate Markov process … This supports the formal claim that a 'trace' (sub-window) of a Markov chain is itself a well-defined Markov chain, not merely a heuristic restriction." *(source: arXiv:2506.22918, Fornace & Lindsey)*
   — Killed for over-generalization: the compression result has its own hypotheses; it does not license the unconditional claim. (Consistent with the later review finding F2: under partial leakage the trace is only **sub**-Markovian.)

## The five synthesized findings (confirmed side, condensed)

1. **[high, 3-0]** *Traces of Consciousness* (Hoffman, Prakash, Chattopadhyay; Preprints.org `10.20944/preprints202410.1305.v1`; 17 Oct 2024; non-peer-reviewed) is the canonical trace-order source; abstract verbatim confirmed via Sciety/ResearchGate.
2. **[high, 3-0]** The established-math trace is the censored/watched Markov chain: Schur-complement form, restricted stationary distribution, transitive censoring (Zhao arXiv:2101.11657; Fornace-Lindsey arXiv:2506.22918 for the row-stochastic induced chain — with hypotheses).
3. **[high, 3-0]** The foundation is standard textbook math (SLP3; Levin-Peres-Wilmer; ASU STP425); the paper frames HMMs as a restricted trace chain.
4. **[medium]** Trace logic as partial order / locally-Boolean / Lebesgue-homomorphic: refuted from abstract-only (see kills 1-2), **confirmed by the full-PDF read** (log 3: Thm 4.2, Thm 4.12, Cor 4.4). The Dirichlet-form distance thread is rigorous mathematics outside Hoffman but **absent from his corpus**.
5. **[medium]** The speculative payload (time dilation, SR, mass/spin/momentum, amplituhedron bridge) is the authors' sketch; policy/meta-policy recursion and the monad framing are not formalized anywhere found.

## Chain of custody

- Pass 1 (breadth): `HMM-hoffman-research.md` — 2026-06-18
- Pass 2 (threads): `HMM-hoffman-research-2-trace-logic.md` — 25 claims, 21 confirmed / 4 killed (0-3 convention for kills; the lone 1-2 there = *contested*)
- Pass 3 (this record): 110-agent deep-research, 2026-06-19 — 25 claims, 21 confirmed / 4 killed (2/3-to-kill convention)
- Pass 3.5 (full-PDF ground truth): `HMM-hoffman-research-3-traces-paper.md` — resolves the evidentiary kills #1-2 above
- Pass 4 (recursion bridges): `HMM-hoffman-research-4-recursion-bridges.md`
- Review R1 (page audit): `conscious-agents-review-findings.md` — 2026-06-26, 39 confirmed findings; F1/CM-2 triggered this archive
