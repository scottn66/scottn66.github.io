# Teaching a Robot Arm to Crawl — And Why Our Best AI Got It 60 % Wrong (Until It Didn't)

*A pedagogical journey through reinforcement learning, hyperparameter optimization, dynamic programming as ground truth, and the moment a 2002 paper closes the gap we spent eighteen minutes opening. Approximately 24 minutes of script time if read at a relaxed pace.*

---

## Act 1 · Cold open  (~45 s)

A jointed robot arm sits on a flat plane. Two motors, one elbow, one wrist. There's no torque control, no continuous angles — just *push the elbow up*, *push the elbow down*, *push the wrist up*, *push the wrist down*. Four buttons. Pushing them in the wrong order makes the arm flop. Pushing them in the *right* order — and we're going to spend the next eighteen minutes figuring out what "right" means — makes the arm *crawl forward*.

> *Visual: Tk window of `src/graphicsCrawlerDisplay.py` running the optimal policy. The arm picks up a rhythm; the body slides right.*

The arm doesn't know what "forward" means. It doesn't have a body diagram, doesn't know gravity, doesn't know what its hand is doing in the world. All it has is a reward signal: at each step, +Δx if the body moved right, 0 if it didn't, negative if it slid back.

This is a textbook reinforcement learning problem. And what we're going to discover is that *every single one* of the increasingly clever model-free RL techniques we throw at it — Q-learning, schedule annealing, Bayesian optimization, population-based training, deep Q-networks, reward shaping — converges to a policy that is **about 42 % as good** as the policy we can compute exactly with a graph algorithm from 1978. We'll plateau there for about eighteen minutes. Then we'll pivot to a different question, find a paper from 2002, and close the gap to **100 %** in fewer environment steps than vanilla Q-learning needed to start moving. The whole arc is the lesson.

---

## Act 2 · The setup  (~60 s)

The crawler from Berkeley's CS188 course has a tiny state space: the elbow can be in one of 36 discrete positions, the wrist in one of 52. That's **1,872 distinct states**. Four actions each. So the agent is choosing among 7,488 (state, action) pairs.

> *Visual: `docs/img/env_diagram.png` — labeled diagram showing arm bucket and hand bucket, with state coordinates*

That sounds small, and it is. But the reward structure is brutal: the optimal locomotion gait is a specific repeating pattern of about sixteen actions in a particular corner of state space. Most actions, from most states, do nothing useful. The space is mostly *flat* — full of states where reward is essentially zero — with a thin path through it where reward is large. Find that path and you get a fast crawl; miss it and you stagger.

> *Visual: matplotlib scatter of (arm bucket, hand bucket) colored by max Δx achievable from each state*

The classical answer is Q-learning. The agent maintains a lookup table `Q[(state, action)]` of expected long-run reward, samples actions, observes rewards, applies the Bellman update `Q ← Q + α (r + γ max_a' Q' − Q)`, and after enough samples the table converges to the optimal action-values. This works. The Berkeley course assignment proves it works. We're going to push on it until it breaks.

---

## Act 3 · First contact — Q-learning with ε-greedy  (~90 s)

Vanilla setup: α = 0.5, γ = 0.95, ε starts at 1.0 and decays linearly to 0.05 over 60 % of training. Random exploration up front, increasingly greedy as the agent learns. Standard recipe from any textbook.

> *Visual: animated Tk window or the `q_evolution_v2.gif` — Q-table coloring fills in as the agent visits new states*

After 30,000 environment steps the arm crawls. The mean velocity is around 0.23 units per step. The peak — the rolling thousand-step average — is about 0.38. That's about half of what we'd actually consider a "fast crawl" by inspection, but it works, and intuitively the agent has *learned something*.

Right away there are questions. The schedule for ε matters: too fast a decay and the agent commits before learning; too slow and it never exploits. The learning rate α matters too. The discount factor γ matters. Where in the joint space of these knobs is the best policy?

This is the question that consumes the next several hours of compute and the next several minutes of script.

---

## Act 4 · The hyperparameter hunt  (~120 s)

First idea: sweep one knob at a time, hold the others fixed. Vary ε's decay length across `{500, 2000, 5000, 15000, 30000, 60000}` steps. Five seeds each.

> *Visual: `docs/img/schedule_sweep.png` — curves showing cum_reward vs decay length*

Result: the optimum sits around decay length = 26 k steps when total training is 50 k. There's a clear inverted-U; too fast or too slow are both bad. This is satisfying. We have a number. The schedule has a structure. Let's get more rigorous.

`scripts/find_optimum.py` adds budget as a second axis. We test the same decay sweep at training budgets of 30 k, 60 k, and 120 k. The best decay scales roughly linearly with budget — `decay* ≈ k × B` with `k ≈ 0.6`.

> *Visual: `docs/img/optimum_scaling.png` — log-log plot of optimal decay vs budget*

That's a scaling law. With the slope `k`, you can compute the recommended schedule for any budget without re-running the sweep. The recipe writes itself.

We have a number. We have a law. Let's get fancier.

---

## Act 5 · Bayesian optimization  (~150 s)

Why grid-sweep when you can use a Gaussian process? `scripts/bo_optimize.py` does 2D Bayesian optimization over (α, ε-decay-length), starting with a Latin-hypercube prior and exploiting Expected Improvement as the acquisition function. After about 40 iterations the GP has carved out a smooth posterior surface, and the EI is concentrating right where the prior sweep said.

> *Visual: `docs/img/bo_evolution.gif` — GP mean + EI surface evolving as observations accumulate*

Then we get greedy. `scripts/bo_optimize_7d.py` puts seven hyperparameters into the GP: α start, α end, α decay length, γ, ε start, ε end, ε decay length. Now we're not just tuning the schedule, we're tuning *the shape of the schedule*. The BO produces an interesting result — it consistently picks α schedules that go *up* through training, not down.

That contradicts the Robbins-Monro condition that any classical RL textbook will tell you is necessary for convergence: `Σ α = ∞` but `Σ α² < ∞`. A rising α violates the second condition. Either the textbook is wrong on this domain, or BO is exploiting some quirk of the simulator, or seed noise is fooling the GP. We don't know yet. (Spoiler: it was a bit of column A and column C. With more seeds the rising-α effect mostly washes out.)

But we have a result: with BO-found hyperparameters the agent reaches max_v ≈ 0.34 — *not* better than the simple swept schedule's 0.38. Adding dimensions hurt us. Curse of dimensionality + seed noise.

A thing to notice here that will only matter in retrospect: BO is *also model-free*. The Gaussian process is a model of *the hyperparameter landscape*, not of *the environment*. We're using a model where we don't need one (HP optimization) and refusing to learn one where we should (the actual MDP). File that observation away — we'll come back to it.

---

## Act 6 · Population-based training  (~120 s)

Maybe a single agent is the wrong unit. Try sixteen agents in parallel, each with random hyperparameters, periodically having them face off in a tournament. The losers copy the winners' parameters (perturbed slightly) and keep training. PBT.

> *Visual: `docs/img/pbt_lineage.png` — 16 agent lineages over time, tournaments visualized*

`scripts/pbt_optimize.py` runs this. We discover a real problem: the standard PBT recipe copies *everything* from winner to loser — including the Q-table. But the Q-table is tuned for the *winner's body state* (positions, angles), not the loser's. So the loser inherits a policy that was correct in someone else's world, applies it in their own world, and gets junk rewards.

The fix: PBT-Pure. Copy only hyperparameters, not Q-tables. The loser keeps its own learned values but gets the winner's schedule recipe.

> *Visual: `docs/img/pbt_comparison.png` — 4-panel comparison of Baseline / Pure / Multi-Seed / Long*

PBT-Pure beats Baseline PBT by about 5×. Multi-seed PBT (each "agent" is actually 3 sub-agents averaged together to reduce seed noise) achieves the tightest outcome spread of any variant — 260 vs 279 raw — exactly what bandit theory says you'd get from variance reduction.

We have algorithms. We have findings. We have a website (`docs/index.html`) full of plots. The max velocity any of these methods has ever achieved is still around **0.38**.

Another thing to file away: PBT-Pure copies *hyperparameters*. It never copies *what the agent learned about the world* — because we never asked the agent to *learn anything about the world*, only to map states to actions. The whole optimization layer is treating the agent as a black box. It's a model-free optimizer wrapped around a model-free learner. We'll keep going for now.

---

## Act 7 · The schedule cliff  (~120 s)

By now we suspect that the optimum has a particular shape. `scripts/gradient_sweep.py` samples 50 agents along a dense ε-decay-length gradient at fixed α and γ.

> *Visual: `docs/img/gradient_sweep.png` — 50 colored points, viridis-gradient, showing the dead zone and the cliff*

The result is striking. Below decay = 22,000 the robot is **completely stuck** — mean velocity ≈ 0.002, never reaches any meaningful x position. Above decay = 22,000 it *crawls* — mean velocity ≈ 0.08. The transition is a sharp **cliff**, not a smooth curve.

That cliff is the difference between "the agent ran out of exploration before learning the policy" and "the agent had enough exploration runway." If you don't give ε at least ~22 k steps to decay from 1.0 down toward 0, you don't learn this task. Period.

Hold this thought too. The cliff is at 22 k random walks. That's not a property of *the task* — that's a property of *random walks on this task*. A directed exploration strategy that knew where to look wouldn't need 22 k steps of coin-flipping to stumble onto the cycle. We'll see one in Act 13.

The evolutionary loop in `scripts/evolve_loop.py` iterates a tighter and tighter band around the survivors, converging in five generations to a soft plateau around decay ≈ 30 k.

> *Visual: `docs/img/gradient_sweep_trajectory.png` — band contraction over 5 generations*

The convergence is clean. The optimum is at decay ≈ training budget. We are now state-of-the-art on this problem — by our own measure.

---

## Act 8 · Scaling laws  (~120 s)

Does the optimum decay length stay invariant if we vary the training budget itself? `scripts/scaling_sweep.py` runs the gradient sweep at five different budgets ranging from 10 k to 250 k steps.

> *Visual: `docs/img/scaling_result.png` — log-log fit of optimal decay vs budget*

The relationship is *sub-linear*: best fit is `decay* ≈ 645 × B^0.39`. So:

- Tiny budget (B = 10 k): optimal decay is *longer* than budget itself. The agent never finishes annealing.
- Medium budget (B = 50 k): optimal decay ≈ 0.85 × budget. Some greedy time at the end.
- Large budget (B = 250 k): optimal decay ≈ 0.34 × budget. Most of training is greedy refinement.

This is *saturation*: optimal decay grows, but with diminishing returns. We fit a saturation model and extract `T_∞ ≈ 42,000`. That's the asymptote — the most exploration the task will benefit from, regardless of how long you train.

We have a scaling law. We even have a number, T_∞. Let's go test what affects it.

---

## Act 9 · The recipe twist  (~120 s)

`scripts/axis_sweep.py` varies one hyperparameter axis at a time, holding everything else at the optimal recipe. First α:

> *Visual: `docs/img/axis_sweep_alpha.png` — optimal decay shifts dramatically with α*

| α | optimal decay |
| --- | --- |
| 0.05 | 232,000 |
| 0.15 | 112,000 |
| 0.30 | 77,000 |
| 0.50 | 31,000 |
| 0.80 | 31,000 |

T_∞ scales as roughly 1/α. With α = 0.05 the agent needs **7.5× more exploration** than at α = 0.5. Lower α = slower per-step learning = more visits needed = bigger T_∞. Sample-complexity theory, made concrete.

Now γ:

> *Visual: `docs/img/axis_sweep_gamma.png` — sharp phase transition between γ=0.85 and 0.95*

Below γ = 0.95 the agent essentially *can't learn this task* — the credit-assignment horizon is too short for reward to propagate back to the actions that caused it. Above γ = 0.95 the agent learns. γ = 0.99 actually beats γ = 0.95: max velocity 0.412 vs 0.377, the best result in the whole study.

But it costs more exploration (decay shifts from 31 k to 77 k). Higher γ = longer credit chains = more samples needed = bigger T_∞ again.

**T_∞ is recipe-bound, not task-bound.** The "42,000" we extracted earlier was specific to (α = 0.5, γ = 0.95, Linear schedule). Change the recipe, the scaling law changes. The number we thought was telling us something about the *task* was actually telling us something about *our specific algorithm parameterization*.

This is a humbling result. It's also where this whole exercise really *should* have started giving us pause.

---

## Act 10 · The function approximation experiment  (~120 s)

What about DQN? `scripts/compare_tabular_vs_dqn.py` implements a NumPy DQN — MLP, experience replay, target network, Adam — and runs it head-to-head with tabular Q-learning under the same recipe.

> *Visual: `docs/img/compare_tabular_vs_dqn.png` — 4-panel learning curves*

Result: tabular wins. By a lot. Tabular Q-learning hits max_v ≈ 0.41 every seed. DQN hits 0.41 *occasionally*, 0.07 most of the time. Function approximation introduces noise that the optimization can't escape; tabular has no such issues because its updates are exact on each cell.

This is exactly what theory predicts. Tabular Q-learning is *provably optimal* in finite deterministic MDPs. DQN's only advantage — generalization across states — is wasted on a problem where every state needs its own answer.

We tried reward shaping (`docs/img/compare_reward_shaping.png`). We tried sweeping the smoothing window (`docs/img/smoothing_window_sweep.png`). Smoothing the reward over 50 steps slightly helps tabular and slightly hurts DQN at the median, but the picture is the same: every variant peaks around 0.4.

Every algorithm. Every schedule. Every reward shape. Every depth of search. We're stuck.

---

## Act 11 · The reckoning  (~150 s)

Here's the punchline. The crawler is a *finite deterministic MDP*. It has 1,872 states, 4 actions, and (s, a) → (s', r) is a function — same input, same output, every time. We verified this empirically: across 500,000 random steps, every (state, action) pair we observed transitioned to *exactly* the same next state every time, with identical reward. Determinism = 1.000.

A deterministic MDP this small doesn't need reinforcement learning. It needs **dynamic programming**.

`scripts/find_optimal_policy.py`:

1. **Build the empirical model**: explore randomly for 500 k steps. Record every (s, a) → (s', r). Build a transition table.
2. **Value iteration**: `V*(s) ← max_a [r(s, a) + γ V*(s')]`. Iterate to convergence. Takes 833 iterations and 0.87 seconds.
3. **Extract the greedy policy**: `π*(s) = argmax_a [r(s, a) + γ V*(s')]`.
4. **Cross-check with Karp's max-mean-cycle algorithm**: independent computation of the true asymptotic ceiling on velocity, free of discount factor. From 1978. Runs in O(V·E) — under a second.

Total wall clock: about three seconds.

> *Visual: `docs/img/optimal_policy.png` — V* heatmap, optimal-action field, 16-step limit cycle traced on the state grid, comparison bars*

The result:

| approach | max_velocity | percent of optimum |
| --- | --- | --- |
| **π\* via VI (γ=0.99, simulated)** | **0.901** | **100 %** |
| Karp's max-mean-cycle (theoretical) | 0.894 | 99 % |
| best tabular Q-learning (any of 7 seeds) | 0.379 | 42 % |
| best DQN (any of 7 seeds) | 0.340 | 38 % |

The optimal policy *crawls 2.4× faster* than anything we've ever produced with RL. The optimal policy reaches x = 500 in **559 steps**. Tabular Q-learning, after extensive hyperparameter optimization, takes about 22,000 steps to cover the same distance — a **40× speedup** by switching to DP.

And it's worse than that. The whole sprawling stack of techniques we built — the schedules, the BO, the PBT, the scaling laws, the axis sweeps — was optimizing within a basin of attraction at 42 % of optimal. Every improvement we celebrated was an improvement within the basin. None of it touched the actual optimum.

We were *locally* state-of-the-art. *Globally*, we were not even close.

And now the question becomes: **can we get RL to do what DP just did?** Not "tune ε better" — that's the wrong question. The right question is "can RL learn the transition table from experience, and then use it the way DP uses it?"

---

## Act 12 · Closing the gap, or trying to  (~120 s)

Why didn't Q-learning find this? It's not because Q-learning is wrong — it's because *ε-greedy is sample-inefficient*. Random exploration is unbiased: it bounces around the middle of state space because the expected drift from uniformly-random actions is zero. The optimal 16-step limit cycle lives in *one corner* of state space. Random exploration almost never finds it before Q-values commit you to a suboptimal but locally consistent policy.

So we tried smarter exploration.

`scripts/compare_exploration.py` puts six conditions head-to-head:

> *Visual: `docs/img/compare_exploration.png` — bar chart with DP ceiling line at 0.893*

| condition | max_v | % of optimal |
| --- | --- | --- |
| ε-greedy @ 100 k | 0.411 | 46 % |
| ε-greedy @ **1,000,000** (10× more time) | 0.418 | 47 % |
| count-based β = 0.5 @ 100 k | 0.475 | 53 % |
| count-based β = 0.5 @ 500 k | 0.486 | 54 % |
| UCB1 c = 1.0 @ 100 k | 0.050 | 6 % |
| UCB1 c = 1.0 @ 500 k | 0.050 | 6 % |

**Just more time doesn't help.** Ten times the budget gets ε-greedy from 46 % to 47 %. The basin is *locked*.

**Count-based exploration helps.** Adding `β/√N(s, a)` to the reward signal is "optimism under uncertainty" — undersampled (s, a) pairs look more attractive than they really are. This pulls the agent into corners ε-greedy avoids. Result: 46 % → 54 %. A real improvement.

**But the gap remains.** Even with 5× the budget *and* better exploration, we're still at 54 % — *nowhere near* 100 %.

**UCB1 fails entirely.** The +∞ bonus on never-visited actions never lets the agent commit; with 7,488 (s, a) pairs and a `√(ln T / N)` term that shrinks too slowly, the agent keeps re-trying every action everywhere. Bad parameterization for this MDP structure.

The deeper truth: **count-based exploration is local**. It biases you toward undersampled (s, a) pairs, but if the Q-policy has no path *to* that pair, you never visit it. The optimum is in a corner; you have to walk through suboptimal states *just to find it*; and during the walk, you're updating Q-values for those suboptimal states, building a self-consistent local policy that doesn't include the corner.

This is the **deep exploration problem**. The known fixes — bootstrapped DQN, posterior sampling, R-MAX with explicit bonus propagation through the Bellman equation — are real engineering. None are five-line patches. But one of them is sitting in a 2002 paper, and it turns out to be exactly the right size for this problem.

---

## Act 13 · The model-based pivot  (~150 s)

Step back. Look at everything we tried for the last twelve acts. ε-greedy, scheduled ε, BO over schedules, PBT, evolutionary loops, scaling sweeps, axis sweeps, DQN, reward shaping, count-based bonuses, UCB1. *Every single one of these is model-free RL.* The agent never builds a representation of the environment's dynamics. It samples (state, action) → (reward, next state) tuples from the world and feeds them through a value-update rule. The world's transition function is *implicit* in the agent's Q-table — never explicit.

That's the assumption we've been working under without ever questioning it. And the RL literature has been telling us, since the 1990s, that we shouldn't.

> *Visual: title card — "Sutton 1990 · Brafman & Tennenholtz 2002 · S&B Ch. 8"*

Sutton's 1990 *Dyna* architecture says: while you're doing real Q-updates, *also* maintain an empirical model `T[(s, a)] = (s', r)` of what happens when you take action `a` in state `s`. Then, between real environment steps, sample (s, a) pairs from your "seen" pool, retrieve `T(s, a)`, and do *imagined* Q-updates with the model's predictions. Every real step is now worth `n + 1` Q-updates instead of just one.

Brafman & Tennenholtz's 2002 paper, *R-MAX*, takes this much further. Maintain the empirical model. Treat unknown (s, a) pairs as if they paid a fixed maximum reward forever — `V_opt = R_max / (1 − γ)`. Run value iteration on this *optimistic* model. Act greedy. Once the agent visits an unknown (s, a) and updates the model, the optimism evaporates for that pair and the policy adjusts. Repeat.

That's the entire algorithm. There's no ε. There's no exploration schedule. There's no UCB constant. The optimism *is* the exploration: any (s, a) the agent hasn't visited is mathematically more attractive than any explored one. And the moment the model covers enough of the world to plan an optimal path, R-MAX *acts* on that plan.

The theoretical claim — proven in the original paper, polished in dozens of follow-ups — is that R-MAX is **PAC-MDP optimal**: with high probability, it reaches an ε-near-optimal policy in a number of environment steps polynomial in `|S|`, `|A|`, and `1/(1−γ)`. On our deterministic MDP with `|S| × |A| = 7,488`, "polynomial" means *fewer than ten thousand* real steps. Half of what vanilla Q-learning needed just to start moving.

We have to try this.

---

## Act 14 · The full arc  (~180 s)

We implement three model-based agents in [`src/modelBasedAgents.py`](../src/modelBasedAgents.py): **Dyna-Q** (the bare Sutton 1990 recipe), **Dyna-Q+** (with the staleness bonus κ·√τ from S&B §8.3), and **R-MAX** (Brafman-Tennenholtz 2002 with `m = 1` because the MDP is deterministic, `K = 20` VI sweeps after each new (s, a) is discovered, warm-started from the previous V). [`scripts/compare_full_arc.py`](../scripts/compare_full_arc.py) runs everything from ε-greedy through R-MAX in a single shot, 3 seeds each, with the DP ceiling drawn as a dashed reference line.

> *Visual: `docs/img/full_arc.png` — the 4-panel headline figure*

Here is what closing the gap looks like:

| condition | budget (real steps) | max_v | % of DP optimum | t to reach 85 % of DP |
| --- | ---: | ---: | ---: | --- |
| ε-greedy | 100 k | 0.411 | **46 %** | never |
| count-based β = 0.5 | 100 k | 0.475 | **53 %** | never |
| UCB1 c = 1.0 | 100 k | 0.050 | 6 % | never |
| **Dyna-Q n = 50** | **30 k** | **0.865** | **97 %** | **23 460** |
| **Dyna-Q+ n = 50, κ = 1e-3** | **30 k** | **0.868** | **97 %** | **23 323** |
| **R-MAX m = 1, K = 20** | **10 k** | **0.901** | **101 %** | **7 595** |
| DP optimum (Karp) | — | 0.893 | 100 % | 559 |

Three things to notice.

**One: Dyna-Q alone — bare model + planning, no exploration trick — closes 84 % of the gap.** Just *learning the transition table* and *replaying it 50 times per real step* takes us from 0.41 to 0.87. The staleness bonus in Dyna-Q+ adds another half a percentage point. The architecture is doing all the work.

**Two: R-MAX matches DP exactly. All three seeds reach max_v = 0.901, identical to value iteration on the offline-computed transition table.** We validated this: dumping R-MAX's learned `T` after 10 k steps and comparing to the offline DP oracle's `T` on shared (s, a) pairs, the number of mismatches is **zero**. R-MAX learned the same world model the DP solver was handed for free. Then it ran value iteration on it. Then it acted. The agent *is* the DP solver, just with the model-learning step folded into the same training loop.

**Three: sample efficiency is the headline.** R-MAX reaches 85 % of the DP optimum in a median of **7,595 environment steps**. Vanilla Q-learning at 1,000,000 steps — 130× more environment interaction — never gets there.

> *Visual: full_arc.png panel C — log-y bar chart showing R-MAX's t85 next to ε-greedy / count / UCB at "never"*

The thing the audience should walk away seeing: the bar chart for max_v looks like a ladder. ε-greedy at 46 %. Count-based at 53 %. (UCB at 6 % — a parameterization warning.) Then a 30-percentage-point cliff up to Dyna-Q at 97 %. Dyna-Q+ at 97 %. R-MAX at 101 %. The DP ceiling at 100 %, dashed across the top. Each rung is a different paper, a different idea, a different mechanism — and each one is one unmistakable step closer to optimal.

The gap is closed. We did it with one new agent file and one comparison script. The crucial technique is from 2002.

---

## Act 15 · Synthesis  (~150 s)

What did we actually learn?

**1. The right axis of RL design is *model-free vs model-based*, not "tune ε vs use a neural net."** Every "improvement" we made for twelve acts was within the model-free regime: schedule shape, optimizer, function approximator, exploration trick, reward shaping. None of those touched the bottleneck. The moment we changed *what the agent knows about the world* — from "Q-values, full stop" to "Q-values plus an empirical transition table" — performance jumped from 46 % to 97 % in one move.

**2. Optimism under uncertainty is the principled exploration strategy.** R-MAX doesn't need an ε-schedule because the math says undiscovered (s, a) pairs are worth more than discovered ones. It's not a heuristic — it's the consequence of treating "I don't know" as "I should find out." Brafman & Tennenholtz proved this gives polynomial sample complexity. ε-greedy doesn't have that guarantee; UCB1 has a related one only under specific parameterizations (cf. Jin et al. 2018 for the Q-learning + tuned UCB analysis).

**3. Hyperparameter optimization within the wrong algorithm class is wasted work.** All the BO, PBT, evolutionary refinement, scaling laws — they were optimizing *within model-free RL's basin of attraction*. Polishing the boundary of a local maximum is not the same as finding the global one. **If you're consistently far from a known ceiling, the right move isn't more tuning; it's changing the algorithm.**

**4. When you can learn the model, learn the model.** RL's value proposition is bridging environments you can't write down — Atari, robotics with noisy contact dynamics, language games. The crawler isn't that. It's a 1,872-state deterministic MDP that DP can solve in three seconds. And here's the surprise: even on a problem DP could solve, *RL can match DP* — but only if you let RL learn the model. R-MAX is "online value iteration with directed exploration"; on a small finite MDP it converges to π* itself.

**5. Reproducibility comes from the right inductive bias, not from luck.** Earlier acts asked whether we could find the optimum reproducibly. The answer turns out to be yes — *with the right algorithm*. All three R-MAX seeds reach 0.901. All three Dyna-Q+ seeds reach 0.87. The bistability we saw in DQN and the local-minimum behavior we saw in vanilla Q-learning are not laws of nature; they're symptoms of a model-free agent on a problem that wanted a model-based one.

**6. The 1990s and 2000s RL papers are not vintage curiosities.** Sutton's Dyna (1990), Brafman-Tennenholtz's R-MAX (2002), Moore & Atkeson's prioritized sweeping (1993): these are the references that *resolved* a problem we spent twelve acts not resolving. The modern deep-RL literature is partially a response to the fact that these techniques don't scale to huge state spaces. On problems where they *do* scale, they're often the right answer.

---

## Closing  (~45 s)

The robot arm crawls. It crawls fast — 0.901 distance units per step, the physical maximum we can prove with a 1957 algorithm and an algorithm from 1978. We didn't get there by tuning more carefully. We got there by asking a different question: *should the agent be building a map?*

The answer for this problem is yes. The answer for Atari is no — the map is too big to store. The answer for most engineering problems is somewhere in between, and figuring out where on that spectrum your problem lives is more important than choosing between Adam and SGD.

If your problem is a small, finite, deterministic MDP: use dynamic programming, or use R-MAX, or use Dyna-Q. The "RL vs DP" question is a false dichotomy — R-MAX *is* RL doing DP. If your problem is a large continuous one: use deep RL, but know what you're paying for in instability and sample efficiency. If your problem is somewhere in between: do the work to figure out which side of the line it's on, *before* you spend three weeks tuning hyperparameters.

That's the lesson. Eighteen minutes to find it, two minutes to fix it, one line on the figure. Choose your algorithm class first; everything else is downstream.

> *Visual: end card. Top line: "RL (ε-greedy): 0.41". Bottom line: "RL (R-MAX, 2002): 0.90". Tagline: "The right tool was always there."*

---

## Appendix: the figure catalog

For anyone wanting to follow the actual experimental path, every plot referenced above is in `docs/img/`:

| script | figure | what it shows |
| --- | --- | --- |
| `sweep_schedules.py` | `schedule_sweep.png` | 1-D ε-decay sweep, first scaling result |
| `find_optimum.py` | `optimum_scaling.png` | optimal decay vs budget, classical fit |
| `bo_optimize.py` | `bo_evolution.gif` | 2D Bayesian-optimization trajectory |
| `bo_optimize_7d.py` | (varies) | 7D BO over schedule shape |
| `pbt_optimize.py` + `pbt_compare.py` | `pbt_comparison.png` | 4 PBT variants |
| `gradient_sweep.py` | `gradient_sweep.png` | dense gradient over ε-decay |
| `evolve_loop.py` | `gradient_sweep_trajectory.png` | 5-gen GD-like band contraction |
| `scaling_sweep.py` | `scaling_result.png` | optimal decay vs budget (denser version of `find_optimum.py`) |
| `axis_sweep.py` | `axis_sweep_alpha.png`, `axis_sweep_gamma.png` | T_∞ vs α, T_∞ vs γ |
| `compare_tabular_vs_dqn.py` | `compare_tabular_vs_dqn.png` | DQN vs tabular learning curves |
| `compare_reward_shaping.py` | `compare_reward_shaping.png` | raw Δx vs rolling-mean reward |
| `sweep_smoothing_window.py` | `smoothing_window_sweep.png` | best smoothing window per agent |
| `find_optimal_policy.py` | `optimal_policy.png` | V*, π*, limit cycle, ground-truth bars |
| `compare_exploration.py` | `compare_exploration.png` | the gap to optimal, by exploration method |
| `compare_full_arc.py` (uses `src/modelBasedAgents.py`) | **`full_arc.png`** | **the climactic figure — model-free → model-based → DP ceiling** |

## Appendix: the key papers

The acts above implicitly cite these. If you want to read further:

| reference | what it gives you |
| --- | --- |
| Bellman 1957, *Dynamic Programming* | The original VI / policy iteration formulation. |
| Watkins & Dayan 1992, *Q-learning* | Tabular Q-learning convergence proof. |
| Karp 1978, *A characterization of the minimum cycle mean in a digraph* | The O(V·E) algorithm for the asymptotic-velocity ceiling. |
| Sutton 1990, *Integrated Architectures for Learning, Planning, and Reacting…* | The Dyna architecture. |
| Moore & Atkeson 1993, *Prioritized Sweeping* | Smarter ordering of imagined backups (the next refinement past Dyna-Q+). |
| Kearns & Singh 1998, *Near-Optimal RL in Polynomial Time* (E³) | The PAC-MDP framework R-MAX builds on. |
| Brafman & Tennenholtz 2002, *R-MAX* | The 2002 paper that closes our gap. |
| Strehl & Littman 2008, *An Analysis of Model-Based Interval Estimation…* | The MBIE-EB generalization of R-MAX. |
| Osband et al. 2013, *(More) Efficient Reinforcement Learning via Posterior Sampling* | PSRL — the Bayesian sibling of R-MAX. |
| Mnih et al. 2015, *Human-level control through deep reinforcement learning* | The original DQN paper. |
| Sutton & Barto 2018, *Reinforcement Learning: An Introduction* (2nd ed.), Ch. 8 | Canonical exposition of Dyna-Q, Dyna-Q+, and planning-vs-learning. |
| Jin et al. 2018, *Is Q-Learning Provably Efficient?* | The proof that Q-learning + properly-tuned UCB is sample-efficient. Explains why our naïve UCB1 failed. |
