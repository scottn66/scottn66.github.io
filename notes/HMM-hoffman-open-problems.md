# Hoffman–Prakash Conscious-Agent / Trace-Logic Program — Open-Problems Brief
### A citable starting point for work with a professor

> Built only from adversarially-verified items (3-vote, ≥2 to kill). Citations checked against primary sources; page corrections noted inline. Status tags: **thesis** / **conjecture** / **open problem** / **proven special case** / **contested** / **outside extrapolation**.

---

## 0. Is there a canonical "nine"? — No.

There is **no enumerated list of exactly nine** conjectures or theses anywhere in the corpus. The honest landscape:

- **The only branded, explicitly-numbered enumeration is "The Eight Conjectures" (of physics)** — items 01/08–08/08 on the Trace Institute research page (`traceinstitute.org/research`), cross-referenced as "the eight conjectures of physics" in the Recursive Trace Logic step and the 2026 Whitepaper. It is **eight, not nine.**
- The recurring **"eight or nine"** phrasing is a loose paraphrase of Hoffman's *spoken* remark about "eight or nine technical hurdles." It is conversational, not a printed list — don't cite it as a structured nine.
- Other numbered lists have **different counts**: the noetic.org 2023 full proposal phrases things as a handful of "precise hypotheses"; the 2024 *Traces of Consciousness* physics-projection dictionary is a set of conjectural rows (mass/spin/speed/distance/momentum-energy), not a curated nine.

**So:** treat **"The Eight Conjectures"** as the canonical *physics* target list, and the items in §2 as the citable *mathematical* open problems.

---

## 1. The Eight Conjectures (of physics) — the canonical numbered list

Source: **Trace Institute, "Research → The Eight Conjectures: A framework for deriving the foundations of physics," items 01/08–08/08, `traceinstitute.org/research`** (accessed June 2026); same eight referenced in the RTL step (04/04) and the 2026 Whitepaper. All are the authors' **conjectures** (a research program, not theorems).

| # | Name | Claim |
|---|------|-------|
| 01/08 | **Special Relativity** | Minkowski space emerges as the limiting behavior of Markov chains representing n-cycles as n→∞ under certain conditions. |
| 02/08 | **General Relativity** | Curved spacetime emerges as the limiting behavior of special classes of *non-cyclic* Markov chains under certain conditions. |
| 03/08 | **Cosmology** | Cosmology and cosmic evolution arise as properties of long samples of certain classes of Markov trace chains. |
| 04/08 | **Planck-Scale Failure of Spacetime** | The breakdown of spacetime at the Planck scale is a consequence of the increase of energy with the number of states in a trace. |
| 05/08 | **Quantum Wavefunction & Born Rule** | Free-particle wavefunctions, and the Born rule, can be recovered from the asymptotic behavior of enhanced Markov chains. |
| 06/08 | **Elementary Particles** | Each elementary particle in the Standard Model can be identified with a particular class of Markov chains. |
| 07/08 | **Scattering Amplitudes** | Scattering amplitudes arise from properties of relevant Markov chains, with ABHY associahedra appearing as subpolytopes of the Markov polytope. |
| 08/08 | **Entanglement** | Disjoint traces of an ergodic Markov chain create spacelike-separated observers with hidden interactions, giving rise to quantum entanglement. |

> These eight are **aspirational derivation targets**, gated (every one) on the unresolved problems in §2–§3. Note 02/08 (GR) is, in the published papers, entirely unrealized — only special-relativistic geometry is sketched (see §3.7).

---

## 2. The mathematical open problems — the authors' own (legitimate, citable targets)

### 2.1 The Combination Conjecture (Conjecture 3) — *best-posed math starting point*
- **Statement:** Given any pseudograph of conscious agents (any mix of directed/undirected edges), any subset can be combined into a single new conscious agent. The two-agent cases are **proven**: Theorem 1 (undirected join), Theorem 2 (directed join), both by construction.
- **Citation:** Hoffman & Prakash, "Objects of Consciousness," *Frontiers in Psychology* 5:577 (2014), Conjecture 3; Theorems 1–2.
- **Status:** proven special case (n=2); general n is conjectured.
- **Tractable sub-question:** Prove the **three-agent case** (chain and triangle topologies), *or* characterize which pseudograph topologies admit an **associative / order-independent** combination. Self-contained, finite, no physics.

### 2.2 The General Join in the Trace Logic (Remark 4.10)
- **Statement:** Joins/meets in the trace logic exist only between "compatible" kernels; no general form is known. Verbatim: *"We seek a solution for the 9 unknown matrices … to the 9 equations (A56)–(A58). … It is an open question whether solutions always exist and, if so, are unique."*
- **Citation:** Hoffman, Prakash & Chattopadhyay, "Traces of Consciousness," Preprints.org doi:10.20944/preprints202410.1305.v1 (17 Oct 2024), **Remark 4.10, Appendix A.4** (printed page "43 of 46"), eqs. A53–A58.
- **Status:** open problem (the authors' own).
- **Tractable sub-question:** Solve the A56–A58 system for **2- and 3-state kernels sharing 2 states**, and give an explicit **compatibility criterion** — characterize exactly which kernel pairs admit a join.

### 2.3 The Commute-Time / Periodicity ("Speed") Conjecture — *best "could become a theorem"*
- **Statement:** *"An ergodic Markov chain on n states has a minimal total expected commute time between states if and only if it is periodic with period n."* (Verified by the authors only for n=2, Figure 9.)
- **Citation:** "Traces of Consciousness" (2024), p.26 (Fig. 9; proposal p.25).
- **Status:** conjecture (proven n=2).
- **Tractable sub-question:** Prove the **iff** — total expected commute time over ergodic n-state chains is minimized exactly by the period-n (cyclic) kernels. A clean optimization over the Markov polytope Mₙ, with established **effective-resistance tools** (commute time = 2m·R_eff). Strong candidate for a genuine result.

### 2.4 The Conscious-Agent Thesis
- **Statement:** *"Every property of consciousness can be represented by some property of a dynamical system of conscious agents"* (2014, "Hypothesis 2"). Operationalized as Church–Turing-analogous: a conscious process *not* representable by any Markov kernel would falsify it.
- **Citation:** Hoffman & Prakash 2014, p.10; operational reframing in Fields, Hoffman, Prakash & Singh, "Conscious agent networks," *Cognitive Systems Research* 47 (2018) 186–213, **p.190** (eScholarship qt2d34n6zf).
- **Status:** thesis (empirical/falsifiable, not a theorem).
- **Tractable sub-question:** Pin down the **representability class** — which cognitive operations are Markov-kernel-representable, at what state-space cardinality.

### 2.5 Agent–Particle Correspondence + the Markov→Decorated-Permutation completion
- **Statement:** *"We conjecture an agent-particle correspondence: a particle … is an aspect of a physical projection of the dynamics of a communicating class of conscious agents to a face of an amplituhedron."* The supporting map (Definition 2, "Markov Decorated Permutations") is a **one-way construction**, not a proven bijection.
- **Citation:** Hoffman, Prakash & Prentner, "Fusions of Consciousness," *Entropy* 25(1):129 (2023), §7 and Definition 2 (open access PMC9858210).
- **Status:** conjecture.
- **Tractable sub-question (math half):** Upgrade Definition 2 toward a **characterized (ideally bijective)** correspondence between Markov communicating classes and decorated permutations / positroid cells. Postnikov–Williams already give the proven decorated-permutation ↔ positroid-cell bijection; **the Markov side is the missing half.** (The physical half — a gluon-scattering decorated permutation inside a real CA's dynamics — is a hard research program, not a student starter.)

---

## 3. The physics-projection dictionary (the authors' conjectural identifications)

All conjectural; cited to "Traces of Consciousness" (2024). The recurring obstacle for **every** one is the **undetermined dimensional bridge constant** — the projected quantity is dimensionless, the physical one is not.

- **3.1 Mass = entropy rate of the RCC.** `h(Q) = −Σᵢ πᵢ Σⱼ Qᵢⱼ log Qᵢⱼ`; periodic/zero-entropy ⇒ massless. **eq. 47** (the cleanest entry). *Note the symbol clash:* this `h(Q)` is entropy rate, **not** Planck's `h` in 3.5.
- **3.2 Spin = determinant of Q ("C-spin").** Geometric-algebra construction collapsing det(Q) to S ∈ {0, ½, 1}. **eq. 50.** ⚠️ *Verify eq. 50 directly in the PDF before relying on it — a thinner sketch than the others.*
- **3.3 Speed = total commute time of the RCC.** Periodic ⇒ minimal commute ⇒ maximal speed c. **eqs. 51–57** (tied to §2.3).
- **3.4 Distance = commute time, `T_ab = ‖a−b‖²`.** A resistance/Dirichlet-energy quantity. **p.24.** Commute time = effective resistance = squared-Euclidean embedding is **established outside Hoffman** (Doyle–Steiner arXiv:1107.2612; Chandra et al. C = 2m·R_eff); the leap is calling it *physical* distance.
- **3.5 Momentum/energy ~ 1/(asymptotic-state count d):** `p = h/d`, `E = hc/d` (h = Planck's constant). **eq. 44.** *Sub-question:* derive *why* the inverse-count law holds (de Broglie form, but d↔wavelength is asserted, not derived).

### 3.6 Harmonic functions = free-particle wavefunction — **CONTESTED**
- The authors assert (eqs. 36–39, and flatly in 2014) that the enhanced chain's harmonic functions are *"identical in form"* to a free-particle wavefunction. **The crux is the real-vs-complex gap**: harmonic functions are a real-valued discrete cis-sum over asymptotic events; the wavefunction is a continuum complex plane wave. *Attribution note:* the authors state this flatly; the "identical vs. merely analogous" split is a downstream verification caveat, not the authors' own hedge. **Don't cite as a settled result until resolved.**

### 3.7 Special Relativity sketch + the missing SR→GR passage
- Tracing a period-n kernel onto m<n states yields a Lorentz-like factor **β ~ n/m** (m≪n ⇒ v→c). Explicitly a **sketch** ("we expect to explore further"); "time dilation" never appears. The corpus reaches only **special-relativistic** conformal/twistor geometry (G(2,4) ≅ Minkowski algebra, rotor group SU(2,2)). **There is no worked passage to general relativity / Einstein's equations** (despite Conjecture 02/08). Citation: p.29.
- **Tractable sub-question (SR only):** upgrade β ~ n/m from a *ratio* to a derived **full Lorentz transformation** (boosts compose, the (1−β²)^(−½) structure appears, Lorentz covariance of the trace dynamics). **Do not** attempt the GR step.

---

## 4. NOT the authors' own — outside extrapolations (do not miscredit Hoffman)

- **Partial Boolean Algebra / Kochen–Specker lattice identity.** The idea that the global trace logic *is* a partial Boolean algebra is an **outside extrapolation**. The papers only say the logic is *not* an orthomodular lattice and stop there. Verify before attributing.
- **Meta-policy recursion / "Recursive Trace Logic."** Policies-of-policies / chains whose states are observer-windows. **Pre-publication** (Trace Institute Whitepaper 2026, the "Multiscale Logic" talk) — not a printed theorem.
- **Dirichlet-form / diffusion metric on observers.** The machinery to turn §3.4's commute-time embedding into a rigorous Riemannian metric is **absent from the corpus** (rigorous outside Hoffman, unbuilt inside). A clean extrapolation target, but *your* problem to pose, not the authors' stated conjecture.

---

## 5. How to pick (for a student + professor)

- **Most tractable, best-posed (proven-adjacent, no physics):** §2.1 (three-agent / topology characterization of the Combination Conjecture) and §2.2 (which kernel pairs admit a join). Both extend *already-proven* special cases; purely finite/combinatorial.
- **Best "could become a real theorem":** §2.3 / §3.3 (the commute-time periodicity *iff*) — a clean optimization over Mₙ with established effective-resistance tools, already proven for n=2.
- **Use as motivation, not a thesis target:** the physics dictionary (§3), the SR→GR step (§3.7), and especially the contested wavefunction identity (§3.6) — open-ended derivation programs gated on undetermined bridge constants and (for §3.6) the real-vs-complex gap. High risk of no clean closed result on a student timeline.

---

## 6. Verification caveats (be honest with your professor)

- **Citation page corrections applied:** the CA-networks Church–Turing passage is **p.190** (not p.189); the general-join Remark 4.10 is on printed page **"43 of 46."**
- **An "entropy-rate monotonicity" conjecture** ("if P ≤ₜ Q then entropy rate of P < entropy rate of Q") appears in my direct read of the 2024 PDF, but the adversarial pass could **not** independently pin its exact wording/location — **verify it in the paper before citing.** (It would, if confirmed, be another tractable target, parallel to §2.3.)
- **Source status:** the trace-logic results rest on a **non-peer-reviewed preprint**; "The Eight Conjectures" live on the Trace Institute site / 2026 Whitepaper, which is **pre-publication**. The peer-reviewed anchors are the 2014 *Objects of Consciousness*, 2018 *Conscious Agent Networks*, 2020 *Fitness-Beats-Truth*, and 2023 *Fusions of Consciousness*.

---
*Compiled via a 70-agent adversarial verification pass (17 items confirmed, 5 killed). Companion to `HMM-hoffman-research*.md`.*
