# E5 and E5b results: long-run ordering from a replayed demand record (Claude, 17/11/2026)

Exploratory, under the author's delegation.
- **Cards:** `CARD_E5.md` (amended before the main run) and `CARD_E5b.md`.
- **Raw outputs committed before scoring:** 20cc4e33 (E5) and 24b9a1c4 (E5b).
- **Design:** one recorded demand path is replayed through both actions (ev_te.trajectory, common random numbers). The 17 GÉANT regimes get 200 records each; the truth is the long training simulation.

## E5: plain replay
| L/T_int | 1 | 3 | 10 | 30 | 100 | 300 |
|---|---|---|---|---|---|---|
| median accuracy | 0.61 | 0.62 | 0.735 | 0.885 | 0.955 | 1.00 |
| regimes with accuracy ≥ 0.95 (of 17) | 4 | 4 | 4 | 5 | 9 | 15 |

- **F1** (accuracy increases with L): holds.
- **F2** (≥ 0.95 at 100, ≤ 0.8 at 3): holds.
- **F3** (lowest accuracy at small relative gap): holds. At 300·T_int, the regimes with relative gap 0.23–0.55 reach 0.79–0.95.
- **F4** (implied regret ≤ 0.5% in ≥ 85% of 204 cells at 100·T_int): **does not hold**, 72/204. At 300·T_int: 110/204, median 0.
  - Cause: a misordering costs about the relative rate gap, from 22% up to more than 1000% of C_ref, so even a 4.5% misordering rate exceeds a 0.5% expected regret.
- **Tie artifact in near-empty regimes:** short records often see no congestion. Both estimates are then 0, and the argmin default (Stay) happens to be right, which inflates accuracy at short L.

## E5b: confidence-gated replay
A record accepts an ordering only when a 99% batch-means interval (B = 10) excludes zero. Counts over 17 regimes × 200 records are in `e5b_counts.json`.

| L/T_int | 10 | 30 | 100 | 300 |
|---|---|---|---|---|
| median share confident | 0.05 | 0.045 | 0.18 | 0.56 |
| median accuracy when confident | 0.91 | 1.00 | 1.00 | 1.00 |

- **G1** (accuracy when confident ≥ 0.98 at every L): **does not hold at 10·T_int**. There, batches are shorter than T_int and the interval is too narrow. It holds at 30, 100 and 300.
- **G2** (confident-and-wrong ≤ 2% per regime at 300·T_int): holds, with zero wrong.
- **G3** (small-gap regimes often never confident): holds. Regimes with gap < 0.5 are never confident within 300·T_int in 69–82% of records.

## Reading
**From a replayed record, an NDT can obtain the long-run ordering it needs, and it can tell when that ordering is reliable.**
- Orderings accepted by a 99% batch-means interval on records of 30–300·T_int were almost always correct (see the counts).
- Near-indifferent actions (relative gap < 0.5) need longer records. The twin should keep recording before applying the correction.

**What is not shown:**
- the regret of the gated rule when it falls back (not computed);
- measurement resolution of real traffic matrices (the replay here uses the exact demand path at the simulation step);
- real traces.

## Post-hoc: end-to-end expected regret (after the E5/E5b scores; `experiments/letter/e5_endtoend.py`, `endtoend_posthoc.json`)
**Approximation:** at h ≥ 7·T_int, the hybrid with an estimated ordering acts like Hybrid-i (ordering correct) or Hybrid-reversed (ordering wrong).

Long horizons (h = 15 and 30·T_int, 204 cells):

| Policy | 100·T_int records | 300·T_int records |
|---|---|---|
| M0 (fluid twin) | 0/204 ≤ 0.5%, median 71.6% | same |
| Hybrid with replayed ordering (ungated) | 72/204, median 4.1% | 110/204, median 0 |
| Gated, falling back to M0 when inconclusive | 0/204, median 44.9% | 24/204, median 21.4% |
| Hybrid with true ordering | 192/204, median 0 | same |

**Reading:**
- Even an uncertain replayed ordering cuts the fluid twin's regret sharply.
- Falling back to the fluid twin when the record is inconclusive is worse than using the uncertain ordering. The gate is a diagnostic (when to keep recording), not a better policy.
- Reaching the true-ordering result needs longer records for near-indifferent actions.
