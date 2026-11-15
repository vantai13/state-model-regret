# EV-TE: state–model regret on a real WAN topology (DRAFT design for author review)

Claude, 15/11/2026, at the author's request: "phần c hãy tự thiết kế thí nghiệm và chạy trên server gcp".
- Status: **DRAFT, not locked.** Nothing has run.
- The card, predictions and lock are written only after the author approves this design.
- Branch `ext/validity`; never merge into main.

## 1. Why
Reviewers will say the paper rests on a toy model: two paths, one aggregate, two actions. This experiment asks whether the main results still hold on a **real WAN topology** with:
- many OD demands;
- multiple paths that share links;
- more than two TE actions.

The main results to check are:
1. the first-order law $G_S(h)\approx h\,s\Delta F + B$;
2. its predictable sign;
3. the $O(1)$ effect for plug-in twins.

It also asks where a **real TE epoch** (5–60 min) falls relative to $T_{int}$.

## 2. Data (official sources; downloaded outside Git with sha256)
- **Topology** (SNDlib, now at `sndlib.put.poznan.pl`):
  - **Abilene**: 12 nodes, 15 links, capacities 9920 Mb/s and one 2480 Mb/s link, 132 OD demands.
  - **GÉANT**: 22 nodes, 36 links.
- **Traffic matrix**:
  - the SNDlib mean/peak demand matrices (Abilene: Zhang 2004; GÉANT: Uhlig 2005) set the **spatial pattern** of mean OD demand;
  - the 5-min Abilene TMs over 6 months (49 MB) feed Arm R.
- Citations to add later: SNDlib (Orlowski et al., Networks 2010) and the dataset source. DOTE (NSDI 2023, already in the library) uses Abilene/GÉANT TMs and 5-min TE epochs.

## 3. Model (generalizes Section II)
- **Network.** A fluid queue on each directed link: $\dot Q_e = \lambda_e(t) - C_e$ when $Q_e>0$. The offered load $\lambda_e$ is the sum of the rates of the ODs routed over $e$, using the offered-load approximation common in TE.
- **Cost.** $\int_0^h \sum_e Q_e\,dt$ (total backlog-time, i.e. queueing delay by Little's law), plus $c$ per switched aggregate. The primary analysis uses $c=0$.
- **Background traffic.** All non-managed ODs stay on their shortest path and are exogenous.
- **TE action.** Choose a path for each of $m$ managed aggregates (large ODs):
  - Stay = shortest path; Switch = second shortest path (Yen $k=2$);
  - $m=1$ gives 2 actions; $m=2$ gives 4 actions;
  - the action is held for $h$.
- **Arm S traffic.** Each OD is modulated by its own two-state Markov chain, with rate = mean·$(1\pm\beta)$ and time constant $T_b$. It is stationary and mixing. Half of the ODs may have a **slow component** ($10\,T_b$), to test the "slowest component" condition.
- **Observation (key point).** Stale = the **full state** $(Q,\text{modes})$ at age $\tau$; fresh = the same content at age 0.
  - The two pipelines differ **only in age**. This removes the age-plus-modes confound that the paper lists as a limitation.
  - Because the observation is the full Markov state, the posterior $X\mid Y$ can be sampled exactly by simulating forward for $\tau$.

## 4. Twins (same classes as the paper)
| Pipeline | Stale | Fresh |
|---|---|---|
| **M0** mean-value fluid twin (future rates = conditional mean, exponential relaxation) | averages its predicted cost over the posterior $X\mid Y$, then takes argmin | argmin using $X$ |
| **Plug-in** | uses $Y$ as if it were current (same rule) | as M0 |
| **CE/nowcast** | applies M0 to $\mathbb E[X\mid Y]$ | as M0 |
| **M1** true model (Monte Carlo) | argmin of $\mathbb E[V_a(h,X)\mid Y]$ | argmin of $V_a(h,X)$, using separate rollouts to avoid winner's curse |

**Evaluation.**
- True costs come from rollouts with common random numbers: the same rollouts serve every action and every $h$, recorded at each checkpoint.
- $C_{ref}=L_{11}$, the cost of M1 with fresh state.
- We compute $G_S$ for each twin, plus $G_M$ and $\Gamma$ for M0, giving the full 2×2.

## 5. Predictor (multi-action Proposition 1; written and committed before any truth run)
$G_S(h)\approx h\sum_a r_a\,[F_{old}(a)-F_{new}(a)] + B$.
- $r_a$: the long-run cost rate of action $a$, from long training runs (seed A).
- $F(a)$: the twin's action shares on a training sample of $(Y,X)$ (seed A).
- The prediction uses **twin decisions and stationary rates only**. Nothing is fitted to the test costs.
- With two actions it reduces to $h\,s\Delta F$ exactly.

## 6. Design grid
- **Arm S (main, pre-registered).** The grid is:
  - 2 topologies;
  - 4 managed sets: OD1, OD2, OD3, {OD1, OD2}. These are the largest ODs whose Stay path crosses a bottleneck link;
  - 2 loads: peak mean link utilization 0.80 and 0.90 under Stay;
  - 2 values of $\beta$: 0.3 and 0.6;
  - 2 slow-component settings: no and yes.

  This gives **64 regimes**.
  - $\tau/T_{int}\in\{0.1,0.3,1,3\}$, so **256 cells**.
  - $h/T_{int}\in\{1,2,4,7,15,30\}$.
  - $T_{int}$ is measured on the training seed. N = 500 decision instances per regime.
- **Arm R (realism, descriptive).** Replay the 6-month Abilene 5-min TMs, with loads scaled the same way and random start times.
  - TE epoch $h\in\{1,2,3,6,12\}$ epochs (5–60 min); $\tau\in\{1,2\}$ epochs.
  - Only the plug-in twin and a regression nowcast twin, since no true model exists. Results are normalized by $E_{stay}$.
  - It measures $T_{int}$ on real OD dynamics and reports **$h/T_{int}$ at real TE epochs**.

## 7. Pre-registered tests (Arm S; unit = cell, counts are denominators, not independent trials)
| ID | Claim | Eligible cells | Pass if |
|---|---|---|---|
| H1 | Level sign: sign of $z_{M0}(30T_{int})$ = sign of the predicted slope | $\lvert z\rvert\ge0.25\%$ and $\lvert\text{pred}\rvert\ge0.25\%$ | ≥ 90% |
| H2 | Sign of the increment $G_S(30)-G_S(7)$ for M0 = predicted sign | $\lvert\Delta_{pred}\rvert\ge0.25$ pp and $\lvert\Delta_{meas}\rvert\ge2$ se | ≥ 90% |
| H3 | Magnitude of the M0 increment: $\lvert\Delta_{meas}-\Delta_{pred}\rvert\le\max(0.25\text{ pp},\,0.25\lvert\Delta_{pred}\rvert,\,2\text{ se})$ | as H2 | ≥ 80% |
| H4 | Plug-in $O(1)$: $\lvert\Delta^{P}_{meas}(7\to30)\rvert\le\max(0.25\text{ pp},2\text{ se})$ | all cells | ≥ 90% |

**Descriptive (no verdict):**
- the share of cells with harm ($z<-0.1\%$);
- $z$ against $\tau$ (does harm grow with age, as the "averaging behaves like the stationary rule" mechanism suggests?);
- $G_M$, $\Gamma$ and the CE twin;
- the effect of the slow component;
- the Arm R map from real epochs to $h/T_{int}$.

## 8. Protocol
1. Codex implements the code and tests.
   - Unit tests cover: the fluid queue against a closed form; the exact posterior sampler; CRN; the reduction to the two-path, two-action case; the predictor equal to $hs\Delta F$ when $|A|=2$.
   - Claude reviews.
2. Timing pilot, used to fix N and the number of rollouts within budget.
3. Training on seed A: $r_a$, $T_{int}$, $F$, predictions.
4. Claude writes CARD.md with H1–H4 and the predictions, then a lock (sha256 of code, data and predictions).
5. **Commit and push before any truth run.**
6. Truth run on GCP, seed B, overnight. The pipeline powers the VM off automatically.
7. Scoring with the locked code, then an independent rescore by Codex. Raw data is committed before scoring.
8. Report, DL-149 and an AGENTS line.
9. After that, Codex adds a short subsection V-B and a parameter-table row to the paper.

## 9. Compute
- Rough estimate before the pilot: Abilene about 3–4 CPU-s per instance, GÉANT about 15. Arm S is about 3×10⁵ CPU-s, roughly 3 h on 32 vCPU. Arm R is small.
- Scale up to n2-standard-32 for the night, then **return to n2-custom-12-49152** (memory rule).
- Cap: 10 h wall. If the pilot shows the run exceeds that, cut N or the GÉANT topology **before locking**, never after.

## 10. Limitations (written down in advance)
- The fluid model with the offered-load approximation does not model packets or downstream shaping.
- Arm S traffic dynamics are synthetic Markov; only the topology and the mean matrix are real.
- Arm R has 5-min granularity, with nothing below 5 min. The fluid backlog at 5 min represents carried-over overload, not router buffers.
- The age-only contrast differs from the paper's main contrast (fresh full state vs stale backlog). This is a deliberate choice to isolate freshness.
- The cells come from the design and do not estimate real-world frequencies.
