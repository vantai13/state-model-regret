# E4b results: replication of the E4 horizon profile on a new seed (Claude, 16/11/2026)

- **Run:** one truth run on GCP (n2-standard-32), seed 5000001, the same 17 GÉANT regimes and the same locked E4 code through `e4b_run.py`. 16 min 49 s wall, 24,750 CPU-s.
- **Commits:** card and lock f8c980d4 (30 files); raw 98c2f796 (checksums match the VM), committed before scoring; score and extra tests next commit (LOCK_PASS 30 files).
- **Units:** G_S = L_stale − L_fresh and regret are in % of C_ref = L(M1_new). The 102 units are regime × τ × h with h ∈ {15, 30}·T_int; they share instances, so they are not independent trials.

## 1. Mechanical verdicts (locked card, reported as is)
| Test | Result | Threshold | Verdict | Forecast |
|---|---|---|---|---|
| E4-1 Hybrid (i), \|G_S\| ≤ 0.25% | 97/102 = 95.1% | 90% | **PASS** | holds: right |
| E4-2 Hybrid (i), regret ≤ 0.5% both sides | 90/102 = 88.2% | 90% | **FAIL** | holds: **wrong** |
| E4-3 training only (carried over) | 14/17 | 90% | FAIL (known) | right |
| E4-4 Hybrid (ii), regret ≤ 0.5% | 81/102 = 79.4% | 80% | **FAIL** | borderline: right |
| X1 h = 7 pattern recurs | fast 9/9 pass, S8 8/8 miss | ≥ 8/9 and ≥ 6/8 | **HOLDS** | right |
| X2 Hybrid (ii) where r̂ (ii) orders correctly | 81/84 = 96.4% | 90% | **HOLDS** | right |
| X3 M0 harm reproduces | 0/102 meet rule 2; median G_S at 30·T_int −62.6% | ≤ 10%, ≤ −25% | **HOLDS** | right |

E4 (seed 3000001) had 102/102 on both E4-1 and E4-2 rules at h ∈ {15, 30}. **That did not fully replicate.**

## 2. Where the E4-2 failures are (post-hoc analysis on the saved data)
- **All 12 failing units come from the two near-empty regimes,** G2_r80_b3_s1 and G3_r80_b3_s1, 6 units each (3 ages × 2 horizons).
  - Long-run backlog there is tiny (training r_Stay = 0.66 and 0.43 Mb), so C_ref is only 6–17 Mb·s over the whole horizon. For comparison, it is about 119,000 Mb·s in G3_r90_b6_s0.
  - The hybrid stays almost everywhere, which is the long-run best action. In 1–7 of the 500 states (rare congested states), the true model (M1_new) switches and is right even over 15–30·T_int. A single instance can lose up to 180 Mb·s, against a mean C_ref of 6 Mb·s. The standard errors equal the means: one to a few instances carry each number.
  - The regret decays with h, as the hybrid proposition predicts (a bounded bias term divided by h·r_min). G3_r80_b3_s1: 11.5%, 5.6% and 1.4% at h = 7, 15 and 30. G2_r80_b3_s1 stale side: 24.7%, 10.6% and 1.9%.
  - In absolute terms the average loss is 0.2–0.7 Mb·s per decision.
- **Why E4 did not show it:** on seed 3000001 these rare states lost little at h ≥ 15 (G2: one instance at h = 15, none at h = 30). The near-empty result is instance noise around a small mean, not a regime-level difference between seeds.
- **E4-1:** 5 misses.
  - 3 in G2_r80_b3_s1 at h = 15, where G_S = +8 to +11%: the stale side is worse, from the same rare states.
  - 2 in G3_r90_b6_s0 at h = 15 (τ = 1 and 3), with G_S = +0.32% and +0.45%: fresh telemetry still helps, so not harm.
  - Read one-sidedly (post-hoc), G_S ≥ −0.25% holds in 102/102 units.
- **Excluding the near-empty regimes** (post-hoc split by a training quantity: r_Stay < 1 Mb gives G1_r80_b3_s1, G2_r80_b3_s1 and G3_r80_b3_s1; G1 passes because its Switch rate is 2,695 Mb, so the rate gap dominates): Hybrid (i) meets rule 2 in 84/84 units at h ∈ {15, 30} on both seeds.
- **E4-4:** 18 misses come from the 3 regimes where the closed form orders actions wrongly (as forecast). The other 3 are G2_r90_b3_s0 at h = 15 (fresh regret 0.64%), a slow s0 regime.

## 3. Conclusion (after the analysis)
- **Locked verdicts:** E4-1 PASS; E4-2 FAIL (88.2% against 90%); E4-4 FAIL (79.4% against 80%); X1, X2 and X3 hold.
- **What replicates across both seeds:**
  - the harm of the fluid twin (M0 never meets the regret rule at h ≥ 15; median G_S −50% and −63% at 30·T_int);
  - the h = 7 pattern, regime by regime;
  - Hybrid (ii) is as good as (i) where the closed form orders the actions correctly;
  - Hybrid (i) is near-optimal from 15·T_int in all 14 regimes that are not near-empty (84/84 per seed, post-hoc split by training r_Stay < 1 Mb).
- **What does not:**
  - "102/102 at h ≥ 15·T_int" was partly luck. In near-empty networks, rare congested states keep the normalized regret above 0.5% up to 30·T_int.
  - The loss is tiny in absolute terms, but large relative to a tiny reference cost.
- **Constructive reading:** the hybrid's normalized regret falls like B/(h·r_min). In a near-empty network r_min is small, so the horizon needed for a given normalized regret grows. A threshold should be stated in units of B/r_min (or by D(h)), not as a fixed multiple of T_int.
- **For the letter:** report both seeds. Give the 14 regimes that are not near-empty (84/84 per seed) and the near-empty exception with its cause and absolute size. Do not write "all regimes from 15·T_int".

## 4. Independent rescore
Codex, `experiments/letter/e4b_rescore.py` (no import of the scorer, simulator, wrapper or extra scorer): **MATCH**. Every field of cells/reductions/regimes and every verdict (E4-1…E4-4, X1–X3) identical; G_S sign convention agrees. This confirms the scoring from raw, not the simulator.
