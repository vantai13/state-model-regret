# E4b CARD: replication of the E4 horizon profile on a new seed (written before truth; Claude, 16/11/2026)

- **Why:** E4 (seed 3000001) failed its locked tests at h = 7·T_int, but post-hoc the hybrid (i) met both rules in 102/102 units at h ∈ {15, 30}·T_int (`results/letter/e4/RESULTS_E4.md`). That statement is post-hoc. E4b tests it on new instances before seeing them.
- **Author approval:** "oke vừa viết vừa chạy luôn được không" (16/11/2026), in reply to Claude's proposal of this run.
- **Same as E4:** code `experiments/letter/e4_geant.py` (byte-identical, locked in E4), the 17 GÉANT regimes, training quantities (seed 1), N = 500, K = 128, R_eval = 256, R_dec = 128, ages τ/T_int ∈ {0.3, 1, 3}, horizons h/T_int ∈ {1, 2, 4, 7, 15, 30}, all pipelines, onset θ = 0.5 (descriptive).
- **Only change:** test seed **5000001**, set by the thin wrapper `experiments/letter/e4b_run.py`; output `results/letter/e4b/`. `training_checks.json` is a byte copy of E4's (training seed 1).
- **Seen before this card:** everything from E4 on seed 3000001 (all cells, the analysis, the regime pattern). **Not seen:** anything on seed 5000001.
- **Scope:** new instances of the **same** regimes. This is a replication across instances, not a test of new regimes or of a horizon rule derived from the model. Rows share instances; they are not independent trials.

## Locked-scorer tests (machine card `CARD_E4B.json`, schema letter-e4-card-v1; unit = regime × τ × h, 17 × 3 × 2 = 102 units)
| ID | Pipeline | Pass if | E4 value (seen) | Forecast |
|---|---|---|---|---|
| E4-1 | Hybrid (i) | \|G_S\| ≤ 0.25% C_ref at h ∈ {15, 30}·T_int in ≥ 90% of units | 102/102 | holds |
| E4-2 | Hybrid (i) | regret ≤ 0.5% C_ref, fresh and stale, h ∈ {15, 30}, ≥ 90% | 102/102 | holds |
| E4-3 | r̂ (ii) vs (i), training only | ≥ 90% of regimes; carried over mechanically, **known FAIL (14/17)** | 14/17 | FAIL (known) |
| E4-4 | Hybrid (ii) | regret ≤ 0.5%, both sides, h ∈ {15, 30}, ≥ 80% | 83/102 = 81.4% | borderline: the 3 wrong-ordering regimes fix 18 failing units, so the maximum is 84/102 = 82.4% |
| E4-5, E4-6 | descriptive | as in E4 | | |

## Extra tests (`experiments/letter/e4b_extra.py`, written and locked before truth; reads the merged `cells.csv`)
Rule 2 = max(regret_fresh_pct, regret_stale_pct) ≤ 0.5.
- **X1 (pattern recurs).** S8 = the 8 regimes where Hybrid (i) missed rule 2 at h = 7·T_int on E4: G2_r80_b3_s1, G2_r80_b6_s0, G2_r90_b3_s0, G2_r90_b6_s0, G3_r80_b3_s1, G3_r80_b6_s0, G3_r90_b3_s0, G3_r90_b6_s0. Holds if, at h = 7·T_int, at least 8 of the other 9 regimes meet rule 2 at all three ages **and** at least 6 of S8 miss it at one age or more. Outcome-defined from E4; it tests recurrence, not a mechanism. Forecast: holds.
- **X2 (r̂ (ii) is as good as (i) where it orders correctly).** In the 14 regimes where r̂ (ii) picks the same best action as (i) on training, Hybrid (ii) meets rule 2 in ≥ 90% of the 84 units at h ∈ {15, 30}·T_int. E4: 83/84. Forecast: holds.
- **X3 (the harm reproduces).** M0 meets rule 2 in ≤ 10% of the 102 units at h ∈ {15, 30}·T_int, **and** the median of M0's G_S over the 51 units at h = 30·T_int is ≤ −25% C_ref. E4: 0/102 and −49.9%. Forecast: holds.
- Any regime incomplete → NOT_EVALUABLE for every test.

## What a failure would mean
- E4-1/E4-2 FAIL: the 15·T_int profile of E4 was partly instance noise; the letter states only the E4 numbers as observed.
- X1 FAIL: the slow-regime pattern does not recur; no regime-level explanation goes in the letter.
- X3 FAIL: the size of the harm is not stable across instances.

## Protocol
1. Lock `results/letter/e4b/lock.json`: E4's 27 input files (with this machine card in place of E4's) + the wrapper + `e4b_extra.py` + this file. Commit and push.
2. One run on GCP (n2-standard-32): `python3 -m experiments.letter.e4b_run run --workers 32 --chunks all --card results/letter/e4b/CARD_E4B.json --onset-theta 0.5`, then `merge`.
3. Commit raw + merge tables before scoring. Score: `e4b_run score --card …`, then `e4b_extra --write`. Independent rescore by Codex (the E4 rescore script with the E4b paths).
4. Analysis (`result-analysis`). VM back to n2-custom-12-49152, TERMINATED.
