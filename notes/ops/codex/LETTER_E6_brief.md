# Codex brief LETTER-E6: exact end-to-end regret with record-based rate estimates (GÉANT)

From Claude for Doan Van Tai, 17/11/2026. **Read `results/letter/e6/CARD_E6.md` first (committed).**
- cwd `/home/vantai/state-model-regret`, branch `letter`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh. Do not modify existing files.** New code goes in `experiments/letter/e6_endtoend.py` (+ tests in `tests/test_letter_e6.py`); outputs in `results/letter/e6/`.
- Another Codex job is editing `/home/vantai/state-model-regret-papers/letter_smr` in parallel; do not touch that folder.

## What to compute
**Reuse the E4 code** (`experiments/letter/e4_geant.py`, which you wrote) to regenerate, for each of the 17 regimes and each of the 10 chunks of **both** test seeds (E4: 3000001, outputs in `results/letter/e4/raw`; E4b: 5000001, in `results/letter/e4b/raw`):
- the exact instances (fresh states and the age-τ stale states) with the same seed derivation as `compute_chunk`;
- the fluid-twin predicted costs V̂_a(h, x) for the fresh state;
- the stale posterior average of V̂_a(h, ·) for each τ, exactly as the Hybrid pipelines do in `compute_chunk`.

Do **not** recompute the true costs V or the M1_new decisions; read them from the saved npz (`V[instance, action, h]`, `decisions[..., pipeline='M1_new', side='fresh', ...]`).

**Hybrid decision for an arbitrary rate vector r̂:** argmin_a V̂_a(h, ·) + h·r̂_a, for fresh and for each stale τ, with the same tie convention as `compute_chunk`.

## Validation (stop and report if it fails)
1. With r̂ = the training rates (level i), the recomputed decisions must equal the saved `Hybrid-i` decisions for every instance, τ, h and side.
2. The same for the saved `Hybrid-reversed` and the four noise variants.
3. Report the number of mismatches (it must be 0) and the CPU used.

## Record-based estimates (E5)
- Source: `results/letter/e5/raw/<regime>.npz`, array `means[rep, L, action]` with `L_Tint = (1, 3, 10, 30, 100, 300)`, 200 records per regime. Use L ∈ {30, 100, 300} (indices 3, 4, 5).
- For each record rep and each L:
  - **Hybrid:** decisions with r̂ = `means[rep, L, :]`, then costs from the saved V. Per seed, regime, τ and h, compute L_fresh and L_stale as means over the 500 instances, and regret = 100·(L − C_ref)/C_ref, with C_ref the saved M1_new cost (as in `cells.csv`).
  - **Stationary rule from the same record:** a* = argmin r̂ (same action in every state). Cost = mean over instances of V[:, a*, h]; one regret per seed × regime × h (it does not depend on τ or side).
- Ties in r̂ (both zero): use action 0, the same convention as E5.

## Outputs (raw only; do not score or summarize verdicts)
- **Per seed and regime:** `results/letter/e6/raw/<seed>_<regime>.npz` with
  - `regret_hybrid[rep, L, side, tau, h]` (side ∈ {fresh, stale});
  - `regret_static[rep, L, h]`;
  - the axes arrays and a json with CPU and validation counts.
- **Overall:** `results/letter/e6/validation.json` and `results/letter/e6/run_summary.json` (CPU, wall, workers).
- **Before the full run:** pilot one cheap and one heavy regime (one chunk each) on one seed. Report the CPU, and project the total for 2 seeds × 17 regimes × 10 chunks.
  - Projection ≤ 2 CPU-h on 8 local workers: run the full set.
  - Otherwise: stop and report.

## Tests (`tests/test_letter_e6.py`)
- A toy check that the argmin with r̂ = constant equals M0's choice, ties excepted.
- The validation above on one small chunk.

## Final message (Vietnamese)
Validation result, pilot CPU and projection, whether the full run completed, the file list.
