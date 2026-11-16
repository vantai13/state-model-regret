# E4 results: fluid twin vs hybrid correction on GÉANT (Claude, 16/11/2026)

- **Run:** one truth run on GCP (n2-standard-32), seed 3000001, 17 regimes × 10 chunks, 16 min 47 s wall. Lock verified at run and score time (LOCK_PASS 27 files).
- **Commits:** card and lock fdb494ca; raw 4b6ad702 (checksums match the VM), committed before scoring; score 48b4ce01.
- **Independent rescore:** Codex, separate script, see the section at the end.
- Units: G_S and regret in % of C_ref = L(M1_new). G_S = L(stale) − L(fresh) (paper convention); negative means fresh telemetry hurts. Rows share instances, so they are not independent trials.

## 1. Mechanical verdicts (locked card, reported as is)
| Test | Result | Threshold | Verdict | Claude's forecast |
|---|---|---|---|---|
| E4-1 Hybrid (i), \|G_S\| ≤ 0.25% | 134/153 = 87.6% | 90% | **FAIL** | likely met: **wrong** |
| E4-2 Hybrid (i), regret ≤ 0.5% both sides | 130/153 = 85.0% | 90% | **FAIL** | likely met: **wrong** |
| E4-3 r̂ (ii) best action = (i), training | 14/17 = 82.4% | 90% | **FAIL** (known before truth) | not met: right |
| E4-4 Hybrid (ii), regret ≤ 0.5% both sides | 111/153 = 72.5% | 80% | **FAIL** | borderline ≈ 82%: **wrong** |
| E4-5, E4-6 | descriptive | | see §3 | E4-5 "most of the gain": **wrong** (≈ half on the fresh side) |

## 2. Where the failures are (all post-hoc analysis on the saved data)
**Hybrid (i): every failing unit is at h = 7·T_int.**

| h/T_int | 1 | 2 | 4 | **7** | **15** | **30** |
|---|---|---|---|---|---|---|
| E4-1 rule met (of 51) | 29 | 28 | 28 | 32 | **51** | **51** |
| E4-2 rule met (of 51) | 9 | 21 | 27 | 28 | **51** | **51** |
| median regret fresh / stale (%) | 10.3 / 15.4 | | 0.35 / 0.35 | 0 / 0 | 0 / 0 | 0 / 0 |

- At h = 7 the failing units come from 8 regimes: the 6 GÉANT G2/G3 regimes without a slow mode (s0), where Stay is the long-run best and the relative rate gap |r_Switch − r_Stay|/r_Stay is small (0.23–1.0), and the 2 near-empty regimes (b3_s1, r_a < 5 Mb).
- **Mechanism:** in 7 of these 8 regimes, fresh and stale hybrid decisions still differ on 0.4–3.8% of instances at h = 7 (τ = T_int), and on 0–0.8% at h = 15. This decays smoothly with h, as the probabilistic bound D(h) predicts. In the eighth (G3_r80_b3_s1) both sides choose the same action, and it is the wrong one (regret 11.6% on both sides, G_S = 0): a fluid transient error, not an age effect.
  - The convergence scale is the transient gap over the rate gap (M̂/|ŝ| in the proposition), not T_int alone.
  - In the CTMC this scale was 3–4·T_int; in these GÉANT regimes it is about 7–15·T_int.
  - The card's h ≥ 7 threshold was taken from the CTMC.
- **The residual is mostly not harm.** 18 of the 19 E4-1 failures have G_S > +0.25%, i.e. the fresh side is better: the value of fresh information has not yet vanished at h = 7. Read one-sidedly (post-hoc), G_S ≥ −0.25% holds in 152/153 units. The single negative unit (G3_r80_b3_s1, τ = 0.3, −1.40 ± 1.40%) comes from one instance.
- **Regret at h = 7 does not depend on the magnitude of r̂.** With r̂ scaled by 0.5, 0.75, 1.25 or 1.5, the E4-2 count at h = 7 stays at 28–29/51. So the remaining regret is the fluid model's transient error (the V̂ part), not the long-run term. This matches EV-D3 (the hybrid failed through fluid transient error). Scaling r̂ up raises the E4-1 count at h = 7 (32 → 37) but not regret.
- **Near-empty regimes are low resolution.** In G2_r80_b3_s1, C_ref ≈ 2.5 Mb·s at h = 7, and the 3.6% fresh regret is the net of 5 positive and 9 negative instance differences; one instance carries it. M1_new's finite rollouts also err (negative per-instance regret in 9–55 instances per regime).

**Hybrid (ii): two causes.**
- 27 failing units come from the 3 regimes where the Gaussian closed form orders the actions wrongly (known from training, I21). The regret there is large at every h: 72–84% (G2_r80_b6_s0), 317–383% (G3_r80_b3_s1) and 1035–1047% (G2_r80_b3_s1). C_ref ≈ E_stay in these regimes, so this is a real cost of choosing Switch, not a tiny-denominator artifact.
- The other 15 come from the same transient as for (i): 14 at h = 7 and 1 at h = 15 (G2_r90_b6_s0, τ = 0.3, stale regret 0.60%).
- Outside the 3 wrong-ordering regimes, (ii) matches (i) at h ≥ 7: 111/126 vs 112/126.
- The forecast of about 82% missed the h = 7 transient.

## 3. Descriptive (E4-5, E4-6)
- **The harm reproduces on a new seed.** M0's median G_S is −22% (h = 4), −39% (h = 7) and −50% (h = 30), with fresh regret 28 / 39 / 61%. The sign is mixed across regimes, as in EV-TE: the s0 regimes have G_S > 0.
- **Tie-breaking is not the whole correction.**
  - M0 ties are 48% (median) on the fresh side and 0% on the stale side.
  - Breaking ties toward the lowest r̂ (i) captures 50–57% of the hybrid's regret reduction on the fresh side (pooled; the median cell captures 0%, so the gain sits in a few regimes) and 0% on the stale side.
  - M0-tie-r̂ still has median fresh regret 14–19% at h ≥ 7.
- **Only the ordering of r̂ matters at long h.** Noise of ±50% on the r̂ magnitudes leaves the median regret at 0 for h ≥ 7.
  - Reversed ordering: median regret 163% (h = 7) to 186% (h = 30).
  - Its G_S is close to 0 (E4-1 rule met in 46/51 units at h = 30), so **G_S ≈ 0 does not mean a good decision**. This illustrates the wrong-sign proposition.
- **Onset-aware hybrid (θ = 0.5):** the same counts as the plain hybrid at h ≥ 15. At h = 7 it meets the E4-1 rule in slightly fewer units (30 vs 32; E4-2 the same, 28). At h = 4 it lowers the fresh median regret (0.18% vs 0.35%), and at h = 1 (6.4% vs 10.3%), but there it makes the median G_S nonzero (2.1%). Descriptive only, as in the card addendum.

## 4. Conclusion (after the analysis)
- **Locked verdicts:** E4-1, E4-2, E4-3 and E4-4 all FAIL. They stay as reported.
- **What the data support:**
  - On GÉANT, the hybrid correction with simulator-level r̂ removes the fresh-telemetry harm and is near-optimal from h ≈ 15·T_int (102/102 units on both rules).
  - At 7·T_int the median regret is already 0, but 8 of 17 regimes still carry 0.3–1.8% regret (up to 11.6% in a near-empty regime) through the fluid transient.
  - Even at 7·T_int, the residual G_S is a remaining value of fresh information (positive), not harm.
- **What would change the result:**
  - a horizon threshold set by M̂/|ŝ| (or by D(h)) instead of a fixed multiple of T_int;
  - a better transient model than the fluid twin for h < 15·T_int;
  - for r̂ (ii), a closed form that handles near-empty two-level sources (I21).
- **Not concluded:** that the correction "fails" on topology. Also not concluded: that 15·T_int is a general constant. It holds for these 17 regimes only.
- **For the letter:** report the h-profile (Fig. 4: regret vs h/T_int for M0, M0-tie-r̂, hybrid (i), hybrid (ii), reversed). State the onset at about 15·T_int on GÉANT vs 3–4·T_int in the CTMC, with the mechanism. Report the verdicts as locked.

## 5. Independent rescore (Codex, `experiments/letter/e4_rescore.py`, no import of the scorer or simulator)
- **MATCH.** Hashes: 340/340 against the VM manifest, 170/170 npz against their json, 27/27 locked files.
- Compared field by field: 6,120 rows of `cells.csv`, 1,224 of `reductions.csv`, 17 of `regimes.csv`. Max absolute difference 6.5×10⁻⁹ (C_ref, relative 2×10⁻¹⁵); 0 mismatches. Tie shares identical.
- Verdicts identical: E4-1 134/153, E4-2 130/153, E4-3 14/17, E4-4 111/153. G_S sign convention L_stale − L_fresh agrees.
- Self-test 9/9 PASS. This confirms the scoring from raw; it does not validate the simulator.
