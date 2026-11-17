# Card V7-1: does h·|ŝ|/gap predict small regret better than h/T_int? (Claude, 17/11/2026)

Owner: **Doan Van Tai**. Plan: `letter_smr/briefs/V7_PLAN.md`, approved by the author 17/11.
**Status: post-hoc analysis with predictions written now.** Per-cell regrets were seen in aggregate (Figs. 3–4, 192/204). The new scale
variables (M̂, the |Δ̂| quantiles) have not been computed for any regime yet.

## Population (fixed)
- **CTMC:** W1b, level `true_s` hybrid. Cells: all 93 regimes × 5 ages × saved horizons.
- **GÉANT:** E4 and E4b, pipeline Hybrid-i. Cells: 17 regimes × 3 ages × 6 horizons × 2 seeds = 612.

## Variables (fixed)
- **Outcome Y:** 1 if both-side regret ≤ 0.5% of C_ref, else 0 (the existing definition).
- **ŝ:**
  - CTMC: true s;
  - GÉANT: level-(i) rate difference (training), in the twin's cost units.
- **Gap scales**, using the M0 gap without correction at the saturation horizon h̄ (or the largest saved horizon if h̄ is not stored):
  - **M̂:** the maximum of |Δ̂| over states. CTMC: all truncated states. GÉANT: the fresh instances (empirical max).
  - **Q90:** the 90th percentile of |Δ̂| pooled over the fresh gaps |Δ̂(h,X)| and the stale gaps |E[Δ̂|Y]|. CTMC: under the stationary/joint law. GÉANT: over saved instances.
- **Predictors per cell:**
  - P1 = h/T_int;
  - P2 = h·|ŝ|/Q90;
  - P3 = h·|ŝ|/M̂.

## Prediction (the test of this card) and forecasts
- **Test:** AUC(P2) > AUC(P1) for predicting Y, **in both datasets separately**. AUC is the Mann–Whitney statistic; ties count one half.
- **Forecasts (not tests):**
  - AUC(P3) lies between AUC(P1) and AUC(P2);
  - P2 ≥ 1 identifies Y = 1 with precision ≥ 0.9 on GÉANT.

**Dependence note:** cells share regimes. Within a regime the three predictors order the horizons identically, so the differences come from the cross-regime scale. Also report a regime-level version: the first saved horizon at which Y = 1 for every later horizon, against T_int and against Q90/|ŝ| (Spearman).

## Inclusion rule (fixed now)
The v7-1 version reports the AUC comparison and the threshold rule, **whatever the result**:
- **If the test holds:** Table II becomes a rule in h·|ŝ|/Q90, given in time units as well.
- **If it does not hold:** Table II stays based on T_int, and the text says that the M̂/|ŝ| scale did not improve prediction in the evaluated regimes.
