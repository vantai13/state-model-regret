# Codex brief EV-D — independent packet-level simulator with realistic arrival processes (code + tests only)

From Claude (orchestrator) for Doan Van Tai, 14/11/2026. Implement and test. **No scored run, no GCP** in this task.

## Ground rules
- cwd: git worktree `~/smr-ext-d`, branch `ext/ev-d`. Env:
  `source /home/vantai/state-model-regret/.venv/bin/activate && source experiments/explore_ctmc/env.sh` (`rg` not installed).
- Only ADD files. All existing files are read-only.
- The simulator itself must **not** import `experiments.explore_ctmc.ctmc`; it is an independent implementation. Tests may import ctmc for comparison.
- Do not commit. Keep it compact: target ≤ 500 lines of code + tests. Use numpy vectorisation across decision instants. No new dependencies.

## Plant
- Two disjoint FIFO single-server queues A and B. Each packet has its own service time S ~ Exp(μ), μ = 10.
- Background arrivals per path come from an arrival class (below) with long-run mean λ_A or λ_B.
- The managed flow is a Poisson stream of rate u. It goes to A under Stay and to B under Switch.
- Cost: ∫ (n_A + n_B) dt (packets in system, both paths).

**Arrival classes** (`arrivals(cls, lam, params, T, rng)` returns sorted arrival times on [0, T]):
- `mmpp2`: Poisson base rate λ − a, plus ONE exponential ON/OFF source with peak 2a and mean ON = mean OFF = κ (a = 6). This is exactly the ctmc-v1 background, used for validation.
- `onoff_exp`: K sources, exponential ON/OFF. Mean ON = f·T_c, mean OFF = (1 − f)·T_c. Peak p chosen so the aggregate mean is λ − b, plus a Poisson base b. Parameters: K, f, T_c, b.
- `onoff_pareto`: same, but ON and OFF are Pareto(α) truncated at `cap` × mean (renormalise so the means are as specified). Parameters: K, f, T_c, b, α, cap.
- Start every source in its stationary state: ON with probability f, plus a stationary residual time. For truncated Pareto, the residual-time draw may use a simple, documented approximation; state it.

## Decision instants and futures (common random numbers)
- Simulate one long Stay run (background + managed on A) after a warm-up. Pick n_inst decision instants t_i with spacing ≥ max(h + τ, given gap). τ = 1.
- At each instant: fresh info x = (n_A(t_i), n_B(t_i)); stale info y = backlogs at t_i − τ, from the same run.
- From t_i, run both actions over [t_i, t_i + h] with CRN. Use the same background arrivals (the actual run's future); one managed-flow Poisson stream per instant, routed to A or B; initial backlogs with fresh Exp(μ) services (memoryless). Get each branch's cost by Lindley recursion. D_i = cost(Switch) − cost(Stay); E_stay = mean Stay cost.

## Twins (backlog-only, mean rates, no modes)
- **Fluid twin M0:** with drift d = λ̄ − μ (λ̄ = mean background + u if the flow is on that path), the cost of backlog q over h is ∫_0^h max(0, q + d t) dt (closed form). The gap is (Switch − Stay) summed over paths; Switch iff gap < 0.
  - fresh: q = x;
  - stale: q = y (plug-in, no compensation for τ).
- **Hybrid twins:** fluid gap + h·ŝ.
  - `hybrid_mm1`: ŝ from the M/M/1 formula r = ρ/(1 − ρ) at the mean loads.
  - `hybrid_train`: ŝ from the measured stationary mean backlogs of a separate training run under each action.

## Outputs per (regime, h, seed)
- G_S = E[(a_stale − a_fresh)·D] for each twin: absolute, and in % of E_stay. Standard error by batch means over instants.
- F_old, F_new: the Switch shares of the fluid twin on stale and fresh info.
- E_stay, ŝ_train (mean backlog difference Switch − Stay from long runs under each action).
- T_int estimate: the integral of the Stay-backlog autocorrelation (total backlog) up to its first zero crossing.
- CPU.

CLI:
- `train --cases F --out DIR` per regime: long runs under both actions, giving ŝ_train, T_int, the twin's F shares on the stationary instant distribution. No D, no costs.
- `test --cases F --train DIR --out DIR --workers N`: write-once JSON per (regime, h).
- h is set in units of the train T_int: h_mult ∈ {1, 3, 10}.
- Seeds: train and test use disjoint seeds (seed, seed + 10^6).

## Required tests (fast, < 90 s total)
1. **Physics vs exact (mmpp2).** For one small regime (λ = 7, κ = 1/2), the simulated stationary mean backlog and E[∫_0^h n dt | n0, mode] for 3 start states match `ctmc.chain(...).r` and `.V([h])` within 4 se.
2. **Pipeline vs exact (mmpp2).** For the same regime pair (λA = 7, λB = 15/2, u = 1, κ = 1/2, h = 3), the DES G_S of the backlog-only fluid twin matches the exact value within 4 se. The exact value comes from ctmc: decision maps that depend on the backlog only (fresh: n of x; stale: y), with the true values from `C.evaluate(..., arrays=True)` (dA/dB per x, dAo/dBo per y) and `C.pair_sum`. Write that exact helper inside the test.
3. Lindley cost integral vs a brute-force event-by-event integral on a tiny example.
4. **Pareto sanity.** Truncated Pareto means match the specification within 2%; a K-source aggregate has the right mean rate.

## Report back
Files added; pytest summary; timing of `test` for one regime of each class at h = 10·T_int with n_inst = 20000; deviations.
