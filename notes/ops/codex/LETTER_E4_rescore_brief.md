# Codex brief LETTER-E4-RESCORE: independent rescore of the E4 truth run

From Claude for Doan Van Tai, 16/11/2026.
- cwd `/home/vantai/state-model-regret`, branch `letter`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh. Do not modify existing files.**
- **Do not import** `experiments.letter.e4_geant`, `experiments.letter.e4_rhat` or `experiments.ext_validity.ev_te`. Use only numpy, json, csv and the standard library. The point is a second implementation written from the definitions below.
- New script: `experiments/letter/e4_rescore.py`. Output: `results/letter/e4/rescore_independent.json` and `.md`.

## Inputs (read-only)
- `results/letter/e4/raw/<regime>_chunkNN.npz` and `.json`: 17 regimes × 10 chunks.
  - npz `V[instance, action, h]`: true per-action cost (mean of R_eval CRN rollouts from the fresh state).
  - npz `decisions[instance, pipeline, side, tau, h]` (int action index), `tie_flags` (same shape), `available[pipeline, side]`, `pipelines`, `sides` (`fresh`, `stale`), `tau_mult`, `h_mult`, `instance_id`.
  - json: `npz_sha256`, `onset_theta`, `T_int`, `regime`, `chunk`, `seed`, `pilot`.
- `e4_raw_sha256.txt` (written on the VM, paths relative to `results/letter/e4/`).
- `results/letter/e4/CARD_E4.json` (thresholds), `results/letter/e4/training_checks.json` (E4-3).
- The locked outputs to compare with: `results/letter/e4/score.json`, `cells.csv`, `reductions.csv`, `regimes.csv`.

## Definitions (from the paper; check them, do not copy the scorer)
- For pipeline p, side s ∈ {fresh, stale}, age τ and horizon h: $L_{p,s}=\frac1N\sum_n V[n, d_{p,s}(n,\tau,h), h]$ over all 500 instances of the regime; se = sample sd/√N.
- $C_{ref}=L_{\rm M1\_new,fresh}$ (the same for every τ at a given h).
- **Paper convention:** $G_S=L_{00}-L_{10}$, where index 0 = stale state and 1 = fresh state. So $G_S=L_{\rm stale}-L_{\rm fresh}$; negative means fresh telemetry hurts. `G_S_pct` = 100·G_S/C_ref.
- `regret_<side>_pct` = 100·(L_side − C_ref)/C_ref. Finite-rollout M1_new can give slightly negative regret; keep the sign.
- **Tests** (unit = regime × τ × h, h/T_int ∈ {7, 15, 30}, 17 × 3 × 3 = 153 units):
  - E4-1: Hybrid-i, |G_S_pct| ≤ 0.25 per unit; PASS if share ≥ 0.90.
  - E4-2: Hybrid-i, regret ≤ 0.5 on **both** sides; PASS if share ≥ 0.90.
  - E4-4: Hybrid-ii, regret ≤ 0.5 on both sides; PASS if share ≥ 0.80.
  - E4-3: from training_checks.json, the count of regimes where r̂ (ii) best action agrees with (i), ≥ 0.90 of 17.
  - Read the thresholds from `CARD_E4.json`; if they differ from the numbers above, report it.

## Do
1. Check every raw npz against its json `npz_sha256` and against `e4_raw_sha256.txt`. Check 17 regimes × 10 chunks, 500 unique instance ids per regime, `pilot` false, `onset_theta` equal to the card's.
2. Recompute every row of `cells.csv` (all pipelines, sides, τ, h) and compare field by field with relative tolerance 1e-12 (absolute 1e-9 for values near 0). Report the max difference per field and any mismatch.
3. Recompute E4-1…E4-4 counts and verdicts; compare with `score.json`.
4. Recompute tie shares per pipeline/side and compare.
5. Report anything that looks like a convention difference rather than an error.

## Final message (Vietnamese)
- Hash checks; rows compared; max differences; verdict table (yours vs locked); MATCH or the list of mismatches with causes.
