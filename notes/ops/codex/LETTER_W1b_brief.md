# Codex brief LETTER-W1b: E3 (age-only exact comparison) and E2 (hybrid with ŝ levels), CTMC

From Claude for Doan Van Tai, 16/11/2026. Read `results/letter/CARD_W1.md` first; its predictions P7–P12 are fixed. Branch `letter` (already checked out).
- cwd: `/home/vantai/state-model-regret`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh.**
- **Do not modify any existing file.** `experiments/explore_ctmc/ctmc.py` stays byte-identical: import it.
- New code goes in `experiments/letter/e3_agediff.py` and `experiments/letter/shat.py`; outputs in `results/letter/w1b/`.
- Another Codex job (W1a) works in parallel in `experiments/letter/` on other files (`ties_topology.py`, `lemma_check.py`, `ctmc_saved_tables.py`); do not touch them. Create `experiments/letter/__init__.py` only if it is absent.

## Model change for E3 (the advisor's point 2.5)
In `ctmc.evaluate` the stale observation is the old backlog only. Its posterior (`posterior_mean`) averages the old mode, so fresh and stale differ in information as well as in age.

**E3 makes stale = the full old state $(n,m)$ at age τ.** Under stationary Stay operation, the decision-time state and the old state both follow $\pi_0$. Given the old state $x'$, the current state has law row $x'$ of $e^{Q_0\tau}$. Paths are independent and gaps add across paths, so the per-path posterior mean of any state function $f$ given $x'$ is `expm_multiply(stay.Q*tau, f)` indexed by the full state. The weights are then the full stationary law (`stay.pi`), not the backlog marginal `pA`.

Implement `evaluate_agediff(lamA, lamB, u, kappa, hs, tau, c=0, a=...)`:
- it mirrors `evaluate` (same chains, gaps, `pair_sum`, `c11`/`c10`/`c01`/`c00`, `G_S`, regret table, hybrid twins);
- only the stale side changes, as above;
- fresh = full current state (unchanged).

**Unit tests:**
- (a) at τ → 0, the stale decision equals the fresh decision, so G_S = 0 for every pipeline;
- (b) at very large τ, the stale posterior is π0 for every old state;
- (c) a regime from `cases/asym.json` at τ = 1 s runs and returns finite values;
- (d) the age-only G_S is computed with the same `pair_sum` conventions (ties → Stay).

## ŝ estimators (`experiments/letter/shat.py`)
Levels for each regime:
- **(i) true s.**
- **(ii) MMPP/M/1 with estimated parameters.** Simulate the two-state mode process of each path for a telemetry record of length W = 100·T_int, sampled every Δ = T_int/10, with a fixed seed per regime (seed 20261116 + regime index). Estimate from the sampled arrival rate:
  - λ̂ = mean;
  - α̂ = standard deviation;
  - κ̂ = −2Δ/ln ρ̂₁, from the lag-1 autocorrelation (clip ρ̂₁ to (0, 1)).

  Then compute $\hat r_a$ = stationary mean backlog of `ctmc.chain(load, κ̂, N, â).r` per path and action, and ŝ = r̂_Switch − r̂_Stay. If â exceeds the model domain (λ̂ < â) or a chain is not valid, record INVALID and fall back to level (iii) for that regime, flagged.
- **(iii) M/M/1:** `s_mm1` as in `ctmc.evaluate`.
- **(iv) true s × (1 + ε),** ε ∈ {−0.5, −0.25, −0.1, 0.1, 0.25, 0.5}.
- **(v) −s** (sign flipped, worst case).

For each level, the hybrid twin adds h·ŝ to the M0 gap on both fresh and stale sides. Report regret (% of C_ref) for hybrid_new and hybrid_old, G_S_hybrid, and the switch shares.

## Runs
- **Regimes:** `results/explore_ctmc/cases/asym.json`, `zf_a3_asym.json`, `zf_a7p5_asym.json` (99 regimes; use each case's own `a` and `hs`).
- **Ages:** τ ∈ {1 s} ∪ {0.1, 0.3, 1, 3}·T_int.
- **Pilot first** (3 regimes) and estimate CPU. If the projection exceeds 3 h on 8 local workers, run `asym.json` only and stop; Claude moves the rest to GCP.
- Write raw per-regime JSON to `results/letter/w1b/raw/` (write-once), then a summary CSV.

## Analysis (`results/letter/w1b/README.md`)
- **P7 and P8:** compare with the saved confounded runs `results/explore_ctmc/runs/asym/*.json` and `runs_l72/zf_*_asym/*.json` at matching (regime, h).
- **P9–P12:** per h/T_int bin.
- Mark each prediction held / not held mechanically.
- Tables only, plus one plain paragraph.
- Then run `python3 -m pytest -q tests/test_letter_w1b.py --basetemp=/tmp/lw1b_pt -o cache_dir=/tmp/lw1b_cache`.

## Final message (Vietnamese)
P7–P12 outcomes, the main tables, CPU time, any INVALID ŝ, anything ambiguous.
