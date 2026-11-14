# EV-A — closed loop (re-decision every Δ, lookahead h_p), ctmc-v1: card locked before truth (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`). Evaluator `closed_loop.py` written by Codex and
reviewed by Claude. The first-order closed-loop law `zero_fit_first_order` was written by Claude: it is the Poisson
analogue of T11.

**Question (THREATS K4).** The controller re-applies the contract's one-shot pipelines every Δ, with lookahead h_p. Does fresh state still harm the horizon-blind twin? Is the long-run harm rate predicted zero-fit?

**Panel.** 60 fresh regimes (seed 20261161; neg/band/pos 20 each), 0 overlap with every earlier list, N ≤ 600, T_int ≥ 4 s. Grid (Δ, h_p)/T_int: (½,½), (1,1), (3,3), (10,10), (½,10), (1,10), (3,10). c = 0.

**Predictions.** `predictions.csv` holds 420 zero-fit numbers (first-order law `pred1` and the Δ→∞ limit `pred_inf`), from M0, g, π and e^{Qτ} only.

**Calibration seen before the lock.** 4 exposed regimes from I_Δ round 3, at Δ = h_p ∈ {3, 10} T_int: pred1 within ≤ 0.13 pp, and ≤ 0.001 pp at 10 T_int.

**Measure.** G_S_CL = 100·(J00 − J10)/J11, where J is the long-run backlog rate.

| ID | Condition | Threshold |
|---|---|---|
| A1 | Δ ≥ 3 T_int (180 rows) | \|G_S_CL − pred1\| ≤ max(0.1 pp, 5% \|pred1\|) on ≥ 90% |
| A2 | Δ = 10 T_int, \|pred1\| ≥ 0.25 pp | sign agreement ≥ 90% (NOT_EVALUABLE if < 5 rows) |

- Fewer than 90% of jobs COMPLETED → INCONCLUSIVE.
- Descriptive only: Δ < 3 T_int (the feedback regime, outside the law's domain), and open- vs closed-loop harm.
- pred1 predicts mostly **help** at (Δ, h_p) = (½, 10) and (1, 10): 57/60 and 52/60 rows positive. This is recorded now, read later.
