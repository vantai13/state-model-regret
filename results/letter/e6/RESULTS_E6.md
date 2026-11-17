# E6 results: exact end-to-end regret with record-based rates (Claude, 17/11/2026)

**Commits:** card 1c6385f9; raw d6c9f553 (committed before scoring); score `experiments/letter/e6_score.py` → `score.json`.

## Run
- **Validation** (Codex): 0 of 4,284,000 decisions differ from the saved Hybrid-i, Hybrid-ii, reversed and four noise variants.
- **Inputs:** 340 chunks (2 seeds × 17 regimes × 10 chunks); 200 E5 records per regime, L ∈ {30, 100, 300}·T_int.
- **Compute:** 2128 CPU-s, 269 s wall, 8 local workers.
- **Independent raw audit** (Codex, `audit_raw.json`): differences of 0 in C_ref and in the stationary cost and regret.

## Locked outcomes (card definitions)
**Cell definition:** seed × regime × τ × h. For each record, take the hybrid's worse side; the cell value is the mean over the 200 records. Long horizon means h ∈ {15, 30}, 204 cells.

| Record length | Hybrid cells ≤ 0.5% | Hybrid median | Stationary, same records: cells ≤ 0.5% | Stationary median | Mixture approximation (R9) |
|---|---|---|---|---|---|
| 30·T_int | 45/204 | 13.49% | 48/204 | 14.18% | — |
| 100·T_int | **72/204** | **4.56%** | 72/204 | 4.13% | 72/204, median 4.13% |
| 300·T_int | **115/204** | **0.076%** | 108/204 | 0 | 110/204, median 0 |

Forecasts:
- **E6-1 held** (72 ≥ 72).
- **E6-2 held** (115 ≥ 110).
- **E6-3 did not hold.** At L = 30 it holds. At L = 100 and 300 the median of the hybrid cells exceeds the median of the stationary cells at h ≥ 7 (L = 100) and h ≥ 15 (L = 300); for example 4.66% vs 4.17% at L = 100, h = 30.

## Analysis (post hoc, after the scores)
**The two rules nearly coincide at long horizons.** The per-cell difference (hybrid − stationary) has median 0.000 at h = 7, 15 and 30 for L = 100 and 300. Its mean is +0.045 and +0.103 pp of C_ref at h = 15 and 30 for L = 100, and +0.051 and +0.075 pp for L = 300. E6-3 compared the medians of two distributions, not the median of the paired differences.

**At shorter horizons the hybrid is clearly better** in mean regret. At L = 100:
- h = 1: 46.0% vs 61.4%;
- h = 2: 26.1% vs 31.5%;
- h = 4: 15.3% vs 16.8%;
- h = 7: 11.1% vs 11.5%.

At L = 300 the means are 40.2 vs 54.7, 20.4 vs 25.1, 9.39 vs 10.55, and 5.12 vs 5.40.

The fresh side alone is better than the stationary rule in mean at every h for L = 100 (−0.11 pp at h = 30).

**Where the hybrid is worse at long horizons:**
- In all 18 near-indifferent cells (relative rate gap < 0.5) at h = 30, and in 28–30 of the 84 other cells.
- **Records with the correct ordering:** the hybrid costs +0.21 pp (L = 100, h = 30), because it still follows transient differences.
- **Records with the reversed ordering:** it gains −2.4 pp, because transient information limits the damage of a wrong ŝ.

**Change relative to the R9 mixture approximation:**
- L = 100: same count, median 4.56% instead of 4.13%.
- L = 300: 115 instead of 110, median 0.076% instead of 0.

## Letter (inclusion rule fixed in the card)
The E6 numbers replace the mixture numbers in the E5 paragraph, and the approximation clause is dropped. The paragraph also states the E6-3 outcome: the stationary rule from the same records reaches similar long-horizon regret; the hybrid helps at shorter horizons and is marginally worse at long holds.
