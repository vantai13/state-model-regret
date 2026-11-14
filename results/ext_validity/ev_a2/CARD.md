# EV-A2 — zero-fit sign-reversal threshold Δ* of the closed loop: card locked before truth (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`).

**Claim under test.** With the lookahead fixed at h_p = 10 T_int and only the decision period Δ varying, the first-order closed-loop law (EV-A, `zero_fit_first_order`) gives

G_S_CL(Δ) = a + b/Δ.

So fresh telemetry harms when Δ > Δ* = −b/a, and helps when Δ < Δ*. Δ* is computed from M0, g, π and e^{Qτ} only.

**Panel.** Fresh harm-region regimes (Sobol seed 20261181, neg/pos), 0 overlap with every earlier list, N ≤ 600, T_int ≥ 4 s. Eligibility, decided by zero-fit numbers only:
- a < 0 < b;
- |a|/r_min ≥ 0.5%;
- Δ*/2 > 1.5 s;
- 2Δ* ≤ 30 T_int.

46 regimes scanned, 30 accepted. Δ*/T_int has median 1.13, range 0.61–2.85, so the Δ*/2 points lie in the feedback regime where EV-A showed the law is only about 80% sign-accurate.

**Prediction.** G_S_CL(Δ*/2) > 0 (fresh helps) **and** G_S_CL(2Δ*) < 0 (fresh harms).

**Z1:** both signs correct in ≥ 75% of COMPLETED regimes. NOT_EVALUABLE if fewer than 10 regimes complete.

- Descriptive: the relative error of the law at 2Δ*.
- One run, no rerun, no change after truth.
- Truth = exact closed-loop evaluator (`closed_loop.py`).
