# Codex brief EV-D2 — add a rate-aware fluid twin to the packet simulator (code + tests only)

From Claude, 14/11/2026. Same ground rules as `EV-D_brief.md`: worktree `~/smr-ext-d`, env activation, no commits, no GCP,
no scored run, no ctmc import in the simulator.

**Context.** `experiments/ext_validity/packet.py` is your EV-D code, with two review edits by Claude: `h_mult` may now
include 30, and the optional `spacing_mult` (instant spacing in units of the train T_int, overlapping futures allowed).
A pilot showed something important. With the backlog-only, mean-rate fluid twin, stale and fresh decisions are almost
identical (F_old ≈ F_new), and fresh state never harms. In ctmc-v1, harm needs the fresh information to carry the
current burst state, which the horizon-blind twin then over-weights. So add the burst-aware analogue of the contract
twin.

## Add
- **Rate estimate.** ρ̂_X = (number of background arrivals of path X in [t_info − W, t_info]) / W, with t_info = t_i (fresh) or t_i − τ (stale), and W = `params['rate_window']` (default T_r).
- **Relaxation time.** T_r = T_c·f·(1 − f): the correlation time of an exponential ON/OFF source. For mmpp2, T_c = 2κ and f = ½, so T_r = κ/2, exactly the ctmc mode time. For Pareto the same formula is a deliberate twin mis-specification; document it.
- **Rate-aware fluid twin `ratefluid`.** The background rate is assumed to relax as λ(t) = λ̄ + (ρ̂ − λ̄)·e^{−t/T_r}. Cumulative net input C(t) = (λ̄ + u_X − μ)·t + (ρ̂ − λ̄)·T_r·(1 − e^{−t/T_r}), where u_X = u if the managed flow is on that path. Cost = ∫_0^h max(0, q + C(t)) dt, vectorised.
  - q + C(t) can rise and then fall (when ρ̂ + u_X > μ at t = 0). The drift is monotone decreasing in t, so find the emptying time by bisection after the peak, as a mean rollout does.
  - Gap = Σ_paths (Switch − Stay); Switch iff gap < 0; ties → Stay.
  - Fresh uses (x, ρ̂ at t_i); stale uses (y, ρ̂ at t_i − τ).
- **`ratefluid_hybrid_train`:** ratefluid gap + h·ŝ_train.
- **Train additions:** F_old / F_new of ratefluid at each h_mult, from the stationary instants. No D, no costs.
- **Test additions:** the same G_S / se / pct fields for `ratefluid` and `ratefluid_hybrid_train`, plus `F_old_rate` and `F_new_rate`.

## Tests (keep the file < 90 s)
1. With ρ̂ = λ̄, ratefluid cost equals the existing fluid cost (≤ 1e−9).
2. The ratefluid cost matches a fine trapezoid integral of max(0, q + C(t)) for a rising-then-falling case and a draining case (≤ 1e−6 relative).
3. Window rate estimator: mean over many windows ≈ λ̄ within 3 se for mmpp2.
4. Existing tests still pass.

## Report back
Files changed, pytest summary, and one train+test timing at h = 10·T_int (n_inst = 10000, spacing_mult = 3) per class.
