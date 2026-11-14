# Codex brief EV-D3 — add age-aware ("nowcast") stale twins to the packet simulator (code + tests only)

From Claude, 14/11/2026. Same ground rules as before: worktree `~/smr-ext-d`, env activation, no commits, no GCP, no
scored run, no ctmc import in the simulator.

**Why.** Pilots show the plug-in stale twins (`fluid`, `ratefluid`, same decision map applied to older data) have
F_old ≈ F_new. Under stationarity this is exact: the stale information has the same marginal law as the fresh one. So the
h-growing harm term h·s·(F_old − F_new) vanishes. The ctmc contract twin is different: its stale pipeline is Bayesian,
a posterior average that shrinks toward the mean. Realistic NDTs often nowcast stale telemetry with a fitted predictor
(Kalman/regression). Add that age-aware stale pipeline.

## Add
- **Training (train seed only).** At the stationary instants, fit per path, by ordinary least squares:
  - x̂_X = β0 + β1·y_X + β2·ρ̂_X(t − τ), clipped at ≥ 0. This predicts the current backlog from the stale backlog and the stale window rate.
  - ρ̃_X = γ0 + γ1·ρ̂_X(t − τ) + γ2·y_X. This predicts the current window rate.

  Store the coefficients and R² in the train JSON.
- **New stale pipelines.** The fresh pipelines are unchanged.
  - `fluid_nowcast`: fluid gap at q = x̂.
  - `ratefluid_nowcast`: ratefluid gap at (q = x̂, ρ̂ = ρ̃).
  - `ratefluid_nowcast_hybrid_train`: the previous one + h·ŝ_train.

  Each is compared with the corresponding fresh twin: G_S = E[(a_stale − a_fresh)·D].
  - `fluid_nowcast` vs fresh `fluid`;
  - `ratefluid_nowcast` vs fresh `ratefluid`;
  - the hybrid nowcast vs fresh `ratefluid_hybrid_train`.
- **Train shares:** F_old for each nowcast pipeline at each h_mult.
- **Test:** G_S / se / pct for the three new pipelines, and F_old for each.

## Tests (< 90 s)
1. When the regression is forced to the identity (β = (0, 1, 0), γ = (0, 1, 0)), the nowcast pipelines equal the plug-in ones bitwise.
2. On mmpp2 training data, β1 is in (0, 1] and the fitted R² is in (0, 1). This is shrinkage, as expected.
3. Existing tests still pass.

## Report back
Files changed, pytest summary, coefficients/R² for one regime per class, and timing.
